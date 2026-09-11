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

    ctx = {"fetched_at": today, "region": cfg.get("region", ""),
           "sirup": {"updated": sirup_meta["updated"], "n_klpd": n_klpd, "aceh": aceh},
           "katalog": {"updated": produk_meta["updated"], **kat},
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
    lines.append(f"  Konteks tersimpan: data/open_context.json · snapshot: output/open_data/")
    return "\n".join(lines)
