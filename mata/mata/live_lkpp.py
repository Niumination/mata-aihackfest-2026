"""MATA — Live collector v1: LKPP OPEN DATA (data.lkpp.go.id).

Jalur TANPA registrasi/token/aplikasi:
- Portal open data resmi LKPP (CKAN) dengan API publik tanpa auth
- Terbukti reachable dari IP datacenter (VPS) — tidak ada WAF
- Dataset: "Nilai Perencanaan dan Realisasi Pengadaan Barang/Jasa"
  per K/L/PD (Kementerian, Lembaga, Provinsi, Kota, Kabupaten) — 658 region
- Update berkala (terverifikasi: 2026-03-31 untuk TA 2025)

Kredit sumber (wajib di output): LKPP — https://data.lkpp.go.id

Batasan jujur (terverifikasi 11 Sep 2026):
- Level data = AGREGAT per K/L/PD (rencana vs realisasi), BUKAN per paket
  → sinyal: kesenjangan rencana-realisi per daerah, konteks serapan akhir tahun
- Data per-paket (pemenang, nilai kontrak per proyek) hanya di API INAPROC
  (butuh token) atau situs LPSE (lihat 13-sumber-data-live-terverifikasi.md)
"""
import csv
import datetime
import io
import json
import os
import urllib.request

UA = {"User-Agent": "MATA/0.2 (AI HackFest 2026; watchdog akuntabilitas pengadaan)"}
API = "https://data.lkpp.go.id/api/3/action/package_show?id={pkg}"
DEFAULT_PKG = "nilai-perencanaan-dan-realisasi-pengadaan-barang-jasa"
CREDIT = "Sumber: LKPP — data.lkpp.go.id (open data, akses tanpa registrasi)"


class LkppOpenError(RuntimeError):
    pass


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_package_meta(cfg):
    """Metadata CKAN: nama dataset, tanggal update, URL resource CSV."""
    pkg = (cfg.get("lkpp_open") or {}).get("package", DEFAULT_PKG)
    body = json.loads(_get(API.format(pkg=pkg)))
    if not body.get("success"):
        raise LkppOpenError(f"CKAN error: {body}")
    d = body["result"]
    csv_res = next((r for r in d["resources"]
                    if (r.get("format") or "").upper() == "CSV"), None)
    if not csv_res:
        raise LkppOpenError("Resource CSV tidak ditemukan di dataset")
    return {
        "name": d.get("title"),
        "updated": (d.get("metadata_modified") or "")[:10],
        "csv_url": csv_res["url"],
    }


def fetch_rows(cfg):
    """Unduh + parse CSV → list dict {nama, jenis, rup, realisasi}."""
    meta = fetch_package_meta(cfg)
    rows = []
    for r in csv.reader(io.StringIO(_get(meta["csv_url"]).decode("utf-8", "replace"))):
        if len(r) < 4 or not r[0].strip():
            continue
        if r[0].strip().lower().startswith("nama"):  # baris header
            continue
        try:
            rows.append({
                "nama": r[0].strip(),
                "jenis": (r[1] or "").strip(),
                "rup": float(r[2] or 0),
                "realisasi": float(r[3] or 0),
            })
        except ValueError:
            continue
    if not rows:
        raise LkppOpenError("CSV kosong / format berubah — cek dataset")
    return meta, rows


def save_snapshot(cfg, meta, rows, out_dir):
    """Raw + parsed snapshot (audit: setiap angka telusur)."""
    d = os.path.join(out_dir, "live_lkpp")
    os.makedirs(d, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(d, f"snapshot_{ts}.json"), "w", encoding="utf-8") as f:
        json.dump({"fetched_at": ts, "dataset": meta, "rows": rows}, f,
                  ensure_ascii=False, indent=1)
    return os.path.join(d, f"snapshot_{ts}.json")


def regional_view(rows, region_focus="Aceh"):
    """Baris yang cocok dengan fokus region (substring, case-insensitive)."""
    kw = region_focus.lower()
    hit = [r for r in rows if kw in r["nama"].lower()]
    return hit


def format_rp(v):
    return f"Rp {v/1e9:,.1f} M" if v >= 1e9 else f"Rp {v:,.0f}"


def run_report(cfg, out_dir):
    """Lengkap: fetch → snapshot → highlight region + nasional. Return summary str."""
    meta, rows = fetch_rows(cfg)
    snap = save_snapshot(cfg, meta, rows, out_dir)
    region = (cfg.get("lkpp_open") or {}).get("region_focus", cfg.get("region", "Aceh"))
    lines = [
        "=" * 70,
        "MATA — MODE LIVE (open data agregat) — TANPA registrasi",
        CREDIT,
        "=" * 70,
        f"Dataset   : {meta['name']}",
        f"Update    : {meta['updated']}",
        f"Region    : {len(rows)} K/L/PD "
        f"({sum(1 for r in rows if r['jenis']=='Kabupaten')} kabupaten, "
        f"{sum(1 for r in rows if r['jenis']=='Kota')} kota, "
        f"{sum(1 for r in rows if r['jenis']=='Provinsi')} provinsi)",
        f"Snapshot  : {snap}",
        "",
        f"── FOKUS: {region} ──",
    ]
    for r in regional_view(rows, region):
        pers = r["realisasi"] / r["rup"] * 100 if r["rup"] else 0
        gap = r["rup"] - r["realisasi"]
        lines.append(
            f"  {r['nama']} ({r['jenis']}): RUP {format_rp(r['rup'])} · "
            f"Realisasi {format_rp(r['realisasi'])} ({pers:.1f}%) · "
            f"sisa {format_rp(gap)}"
        )
    # Nasional: 5 daerah dengan serapan terendah (min RUP Rp 100 M agar berarti)
    valid = [r for r in rows if r["rup"] >= 1e11]
    worst = sorted(valid, key=lambda r: r["realisasi"] / r["rup"])[:5]
    lines += ["", "── NASIONAL: 5 K/L/PD serapan terendah (min RUP Rp100 M) ──"]
    for r in worst:
        pers = r["realisasi"] / r["rup"] * 100 if r["rup"] else 0
        lines.append(f"  {r['nama']} ({r['jenis']}): {pers:.1f}% "
                     f"(RUP {format_rp(r['rup'])}, realisasi {format_rp(r['realisasi'])})")
    lines.append("")
    lines.append("Catatan: level agregat per K/L/PD — bukan per paket/proyek. "
                 "Rule engine per-paket (D1-D6) tetap mode demo/synthetic.")
    return "\n".join(lines)
