"""MATA — Kolektor OPEN DATA v2 (100% akses publik, tanpa token/registrasi).

Sumber (terverifikasi reachable dari VPS, Sep 2026):
1. data.lkpp.go.id (CKAN API publik) — dataset "Data SIRUP":
   RUP per K/L/PD {instansi, jenis, total nilai RUP, total paket} — 631 baris.
2. data.lkpp.go.id — dataset "Produk Tayang di Katalog Elektronik":
   {kategori, komoditas, jumlah produk} — ~109 ribu baris (hitung per daerah).

Output:
- output/open_data/<tanggal>-<nama>.xlsx  (snapshot mentah = audit)
- data/open_context.json  (fokus region config: помощь dashboard + chat kelak)

Batasan jujur: level AGREGAT (per daerah/kategori), BUKAN per paket.
Deteksi anomali per paket tetap butuh INAPROC API (token) atau kolektor laptop.
"""
import datetime
import json
import os
import urllib.request

UA = {"User-Agent": "MATA/0.3 (AI HackFest 2026; watchdog akuntabilitas pengadaan)"}
CKAN_SHOW = "https://data.lkpp.go.id/api/3/action/package_show?id={pkg}"
PKG_SIRUP = "data-sirup-sistem-informasi-rencana-umum-pengadaan"
PKG_PRODUK = "produk-tayang-di-katalog-elektronik"
PKG_REALISASI = "nilai-realisasi-pengadaan-barang-jasa-pemerintah-menurut-instansi-pusat-dan-pemerintah-daerah"
PKG_PDN = "data-penggunaan-produk-dalam-negeri-pdn-pada-rencana-umum-pengadaan-rup"
PKG_IKP = "indeks-kinerja-pengadaan"
PKG_SAING = "persentase-tingkat-persaingan-penyedia-umkk"
# Indeks nasional tambahan (JSON satu-angka; yang tak punya JSON dilewati)
PKG_NASIONAL = [
    ("digital", "persentase-digitalisasi-proses-pelaksanaan-pengadaan-barang-jasa"),
    ("efisiensi", "persentase-efisiensi-paket-konsolidasi"),
    ("regulasi", "indeks-efektivitas-implementasi-regulasi-pengadaan-barang-jasa"),
    ("puas", "indeks-kepuasan-pengguna-platform-pengadaan-nasional"),
    ("kelola", "indeks-penerapan-tata-kelola-pengadaan"),
    ("probity", "skor-efektivitas-probity-advice-dan-advokasi"),
    ("pdn95", "persentase-klpd-yang-menerapkan-belanja-pengadaan-untuk-pdn-minimal-95-persen"),
    ("umkk40", "persentase-klpd-yang-menerapkan-belanja-pengadaan-untuk-umkk-minimal-40-persen"),
]
CREDIT = "Sumber: LKPP — data.lkpp.go.id (open data, tanpa registrasi)"


class OpenDataError(RuntimeError):
    pass


def _get(url, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        if r.status != 200:
            raise OpenDataError(f"HTTP {r.status}: {url}")
        return r.read()


def _xlsx_resource(pkg):
    body = json.loads(_get(CKAN_SHOW.format(pkg=pkg), timeout=60))
    if not body.get("success"):
        raise OpenDataError(f"CKAN error: {body}")
    d = body["result"]
    res = next((r for r in d["resources"]
                if (r.get("format") or "").upper() == "XLSX"), None)
    if not res:
        raise OpenDataError(f"Resource XLSX tidak ada di {pkg}")
    return {"updated": (d.get("metadata_modified") or "")[:10], "url": res["url"]}


def _xlsx_resources(pkg):
    """Semua resource XLSX sebuah dataset, urut nomor file (1..12)."""
    import re
    body = json.loads(_get(CKAN_SHOW.format(pkg=pkg), timeout=60))
    if not body.get("success"):
        raise OpenDataError(f"CKAN error: {body}")
    d = body["result"]
    res = [r for r in d["resources"] if (r.get("format") or "").upper() == "XLSX"]

    def _num(r):
        m = re.search(r"/(\d+)\.-", r.get("url", ""))
        return int(m.group(1)) if m else 999

    res.sort(key=_num)
    if not res:
        raise OpenDataError(f"Resource XLSX tidak ada di {pkg}")
    return {"updated": (d.get("metadata_modified") or "")[:10],
            "urls": [r["url"] for r in res]}


def _parse_pdn(path, region_key):
    """RUP PDN baris region (kolom nama=1, nilai=3)."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = [s for s in wb.sheetnames if s.lower() != "keterangan"]
    ws = wb[sheets[0]]
    val = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row and len(row) > 3 and row[1] and region_key in str(row[1]).lower():
            val = _num(row[3])
            break
    wb.close()
    return val


def _parse_realisasi(path, region_key):
    """Nilai realisasi baris region (satu file = satu periode)."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = [s for s in wb.sheetnames if s.lower() != "keterangan"]
    ws = wb[sheets[0]]
    val = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row and row[0] and region_key in str(row[0]).lower():
            val = _num(row[2] if len(row) > 2 else None)
            break
    wb.close()
    return val


def _fetch_json_value(pkg):
    """Dataset JSON satu-angka nasional: return (nama, angka, updated)."""
    body = json.loads(_get(CKAN_SHOW.format(pkg=pkg), timeout=60))
    if not body.get("success"):
        raise OpenDataError(f"CKAN error: {body}")
    d = body["result"]
    res = next((r for r in d["resources"]
                if (r.get("format") or "").upper() == "JSON"), None)
    if not res:
        return None
    rows = json.loads(_get(res["url"], timeout=60))
    if not rows:
        return None
    r0 = rows[0]
    val = r0.get("nilai", r0.get("persentase"))
    return {"nama": r0.get("nama_data", pkg), "tahun": r0.get("tahun"),
            "nilai": val, "updated": (d.get("metadata_modified") or "")[:10]}


def _download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    data = _get(url, timeout=300)
    with open(dest, "wb") as f:
        f.write(data)
    return dest


def _num(v, default=0):
    try:
        return float(v) if v is not None and str(v).strip() != "" else default
    except (TypeError, ValueError):
        return default


def _parse_sirup(path, region_key):
    """Return (aceh_row_dict_or_None, n_rows)."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    found, n = None, 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[1]:
            continue
        n += 1
        if region_key in str(row[1]).lower():
            found = {"instansi": str(row[1]), "jenis": str(row[2] or ""),
                     "rup_total": _num(row[3]), "paket_total": int(_num(row[4]))}
    wb.close()
    return found, n


def _parse_produk(path, region_key, top_n=8):
    """Return {komoditas_count, top_categories[(kat, jumlah)]} untuk region."""
    import openpyxl
    from collections import Counter
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    cats, n = Counter(), 0
    for row in ws.iter_rows(min_row=5, values_only=True):
        if not row or len(row) < 3 or not row[1]:
            continue
        if region_key in str(row[1]).lower():
            n += 1
            cats[str(row[0] or "Lainnya")] += int(_num(row[2]))
    wb.close()
    return {"komoditas_count": n, "produk_total": sum(cats.values()),
            "top_categories": cats.most_common(top_n)}


def run_collect(cfg, out_dir):
    """Unduh + parse + tulis open_context.json. Return ringkasan string."""
    region = (cfg.get("region") or "Aceh Tengah").lower()
    today = datetime.date.today().isoformat()
    snap = os.path.join(out_dir, "open_data")
    os.makedirs(snap, exist_ok=True)

    sirup_meta = _xlsx_resource(PKG_SIRUP)
    sirup_path = _download(sirup_meta["url"], os.path.join(snap, f"{today}-sirup.xlsx"))
    aceh, n_klpd = _parse_sirup(sirup_path, region)

    produk_meta = _xlsx_resource(PKG_PRODUK)
    produk_path = _download(produk_meta["url"], os.path.join(snap, f"{today}-produk-katalog.xlsx"))
    kat = _parse_produk(produk_path, region)

    real_meta = _xlsx_resources(PKG_REALISASI)
    monthly = []
    for i, url in enumerate(real_meta["urls"], 1):
        rp = _download(url, os.path.join(snap, f"{today}-realisasi-{i:02d}.xlsx"))
        monthly.append(_parse_realisasi(rp, region))

    nasional = {}
    for key, pkg in (("ikp", PKG_IKP), ("saing_umkk", PKG_SAING), *PKG_NASIONAL):
        try:
            v = _fetch_json_value(pkg)
            if v and v.get("nilai") is not None:
                nasional[key] = v
        except OpenDataError:
            pass

    pdn_meta = _xlsx_resource(PKG_PDN)
    pdn_path = _download(pdn_meta["url"], os.path.join(snap, f"{today}-pdn.xlsx"))
    pdn = _parse_pdn(pdn_path, region)

    ctx = {"fetched_at": today, "region": cfg.get("region", ""),
           "sirup": {"updated": sirup_meta["updated"], "n_klpd": n_klpd, "aceh": aceh},
           "katalog": {"updated": produk_meta["updated"], **kat},
           "realisasi": {"updated": real_meta["updated"], "monthly": monthly},
           "pdn": {"updated": pdn_meta["updated"], "rup_pdn": pdn},
           "nasional": nasional,
           "credit": CREDIT,
           "batas": "Agregat per daerah/kategori, bukan per paket. "
                    "Deteksi per paket butuh INAPROC API (token)."}
    base = os.path.dirname(os.path.abspath(__file__))
    ctx_path = os.path.join(os.path.dirname(base), "data", "open_context.json")
    os.makedirs(os.path.dirname(ctx_path), exist_ok=True)
    with open(ctx_path, "w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, indent=1)

    lines = [f"[open-data] {today} · {CREDIT}",
             f"  SIRUP: {n_klpd} K/L/PD (update {sirup_meta['updated']})"]
    if aceh:
        lines.append(f"  → {aceh['instansi']}: RUP Rp {aceh['rup_total']:,.0f} · {aceh['paket_total']} paket")
    lines.append(f"  Katalog: {kat['komoditas_count']} komoditas {cfg.get('region','')} "
                 f"({kat['produk_total']} produk, update {produk_meta['updated']})")
    got = [m for m in monthly if m]
    if got:
        lines.append(f"  Realisasi 2025: {len(got)} periode, Jan Rp {got[0]:,.0f} → "
                     f"Des Rp {got[-1]:,.0f}")
    if pdn:
        lines.append(f"  PDN dalam RUP: Rp {pdn:,.0f}")
    lines.append(f"  Indeks nasional terisi: {len(nasional)} dataset")
    for key in ("ikp", "saing_umkk"):
        if key in nasional:
            v = nasional[key]
            lines.append(f"  Nasional: {v['nama']} {v['tahun']} = {v['nilai']}")
    lines.append(f"  Konteks tersimpan: data/open_context.json · snapshot: output/open_data/")
    return "\n".join(lines)
