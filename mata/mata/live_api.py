"""MATA — Client INAPROC API Gateway (data.inaproc.id, v1) — MODE LIVE.

Sumber resmi e-procurement LKPP (pengumuman tender, e-Kontrak, e-Katalog, RUP).
Dokumentasi: https://data.inaproc.id/docs/spesifikasi-api
Akses: JWT Bearer (peran Data Integrator + Surat Permohonan Akses ke LKPP).
  - Ajukan: akun.inaproc.id → role Data Integrator → Developer Portal
  - Token request WAJIB mendaftarkan IP publik pemanggil (VPS-mu).

Prinsip:
- Hanya data PUBLIK, tanpa login ke sistem lain
- Polite: limit ≤1000/halaman, backoff saat 429 (rate limit)
- Audit: setiap respons API disimpan raw di output/live_raw/ (setiap angka telusur)
"""
import datetime
import json
import time
from pathlib import Path

import requests

BASE_DEFAULT = "https://data.inaproc.id/api/v1"
UA = "MATA/0.2 (AI HackFest 2026; watchdog akuntabilitas pengadaan)"


class LiveError(RuntimeError):
    pass


def _token(cfg):
    icfg = cfg.get("inaproc") or {}
    tok = icfg.get("jwt_token", "")
    if not tok:
        raise LiveError(
            "Token INAPROC belum diset (config.json → inaproc.jwt_token). "
            "Proses akses: akun.inaproc.id → role Data Integrator → "
            "Surat Permohonan ke LKPP → Developer Portal."
        )
    return tok


def _base_url(cfg):
    return (cfg.get("inaproc") or {}).get("base_url", BASE_DEFAULT)


def get_page(cfg, endpoint, params, raw_dir=None, timeout=30, _retry=3):
    """Ambil SATU halaman (max 1000 baris). Return (data, meta)."""
    r = requests.get(
        f"{_base_url(cfg)}/{endpoint}",
        params=params,
        headers={
            "Authorization": f"Bearer {_token(cfg)}",
            "Accept": "application/json",
            "User-Agent": UA,
        },
        timeout=timeout,
    )
    if r.status_code == 429 and _retry > 0:
        wait = int(r.headers.get("Retry-After", "30") or 30)
        print(f"  [429 rate-limit] menunggu {wait}s ...")
        time.sleep(wait)
        return get_page(cfg, endpoint, params, raw_dir, timeout, _retry - 1)
    if r.status_code in (401, 403):
        raise LiveError(
            f"HTTP {r.status_code} — token ditolak/IP tidak terdaftar. "
            f"Cek: token aktif? IP publik VPS terdaftar di request token? "
            f"body: {r.text[:200]}"
        )
    if r.status_code != 200:
        raise LiveError(f"HTTP {r.status_code}: {r.text[:300]}")
    body = r.json()
    if not body.get("success", False):
        raise LiveError(f"API error: {body}")
    data, meta = body.get("data", []), body.get("meta", {})
    if raw_dir:
        d = Path(raw_dir)
        d.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        (d / f"{endpoint.replace('/', '_')}_{ts}.json").write_text(
            json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    return data, meta


def iter_all(cfg, endpoint, params, raw_dir=None, max_pages=100):
    """Loop cursor pagination — yield semua record endpoint."""
    p = dict(params)
    p.setdefault("limit", 1000)
    seen = 0
    for _ in range(max_pages):
        data, meta = get_page(cfg, endpoint, p, raw_dir)
        yield from data
        seen += len(data)
        if not meta.get("has_more") or not meta.get("cursor"):
            return
        p["cursor"] = meta["cursor"]
    print(f"  (berhenti di max_pages={max_pages}, {seen} record terkumpul)")


# ---------------------------------------------------------------------------
# Normalisasi → skema record MATA (kolom tabel `announcements`).
# Detail lengkap tetap tersimpan di raw snapshot output/live_raw/ (audit).
# ---------------------------------------------------------------------------
SOURCE = "INAPROC API (data.inaproc.id)"


def _d(s):
    """Ambil tanggal YYYY-MM-DD dari berbagai format."""
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


def _base(r, value, ref_price, date, vendor, url, region, method, source=SOURCE):
    return {
        "id": r["id"],
        "project": r.get("project"),
        "agency": r.get("agency"),
        "kpa": None,
        "region": region,
        "value": value or 0,
        "method": method,
        "vendor": vendor,
        "date_signed": date,
        "date_start": None,
        "date_end": None,
        "ref_price": ref_price,
        "source": source,
        "url": url,
    }


def norm_pengumuman(r, region=""):
    """tender/pengumuman → record (belum ada pemenang; HPS = ref_price)."""
    return _base(
        {"id": f"INP-P-{r.get('kd_tender')}-{r.get('kd_klpd')}"},
        value=r.get("pagu") or r.get("hps"),
        ref_price=r.get("hps"),
        date=_d(r.get("tgl_pengumuman_tender")),
        vendor=None,
        url=r.get("url_lpse"),
        region=region or r.get("nama_klpd"),
        method=r.get("mtd_pemilihan"),
    )


def norm_kontrak(r, hps_map=None, region=""):
    """tender-ekontrak / non-tender-ekontrak-kontrak → record (ada pemenang).

    D1 live: nilai_kontrak vs HPS (referensi resmi pemerintah).
    """
    hps = None
    if hps_map is not None:
        hps = hps_map.get(str(r.get("kd_tender") or r.get("kd_nontender")))
    return _base(
        {"id": f"INP-K-{r.get('kd_tender') or r.get('kd_nontender')}-{r.get('kd_klpd')}"},
        value=r.get("nilai_kontrak"),
        ref_price=hps,
        date=_d(r.get("tgl_kontrak")),
        vendor=r.get("nama_penyedia"),
        url=None,
        region=region or r.get("nama_klpd"),
        method=r.get("mtd_pengadaan"),
    )
