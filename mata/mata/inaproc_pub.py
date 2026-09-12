"""MATA — INAPROC dashboard-api (jalur VPS-direk; dikonfirmasi 12 Sep 2026).

Sumber: BFF publik `data.inaproc.id/dashboard-api` (same-origin, TANPA auth) —
API publik yang dipanggil SPA data.inaproc.id sendiri. **Bukan bypass**: WAF
TIDAK memblokir path ini dari IP VPS MATA (bukti 12 Sep: HTTP 200 + data
realisasi berpemenang, RUP per-paket). IP sandbox/datacenter lain 403 total →
modul ini efektif hanya di VPS; dari tempat lain ia degradasi halus
(stale/empty + badge) tanpa merusak dashboard.

Endpoint (terkonfirmasi 200 dari VPS): realisasi/{table,summary},
realisasi-rup/{table,summary}, rup/{table,summary}, afirmasi/{table,summary},
last-update. Param: tahun, jenis_klpd (4=kabupaten), instansi (D6=Kab. Aceh
Tengah), offset, limit. `last-update` = waktu refresh data (teramati harian
±02:47 WIB).

Peran: SUMBER INTI PBJ per-paket (melengkapi jalur SPSE): realisasi dengan
status & nilai per satker → sinyal D2–D6; RUP sebagai rencana.
Etik: 4 request per refresh (bukan crawl), cache 10 mnt, atribusi di panel.
"""
import json
import os
import time
import urllib.parse
import urllib.request

BASE = "https://data.inaproc.id/dashboard-api"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(BASE_DIR, "data", "inaproc_cache.json")
TTL = 600  # 10 menit; data di sisi mereka refresh harian
SOURCE = "https://data.inaproc.id (INAPROC — dashboard-api publik)"

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

REFERER = {
    "last-update": "https://data.inaproc.id/",
    "realisasi/table": "https://data.inaproc.id/realisasi",
    "realisasi/summary": "https://data.inaproc.id/realisasi",
    "rup/table": "https://data.inaproc.id/rup",
}

DEFAULTS = {"tahun": 2026, "jenis_klpd": "4", "instansi": "D6"}
NAMA_INSTANSI = "KAB. ACEH TENGAH"


def _get(path, params=None, timeout=30):
    url = BASE + "/" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, headers=dict(UA, Referer=REFERER.get(path, "https://data.inaproc.id/")))
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def fetch_all(params=None, timeout=30):
    """4 request ringan per refresh (bukan crawl)."""
    p = dict(DEFAULTS, **(params or {}))
    out = {}
    out["last-update"] = _get("last-update", timeout=timeout)
    out["realisasi/table"] = _get("realisasi/table", p, timeout=timeout)
    out["realisasi/summary"] = _get("realisasi/summary", p, timeout=timeout)
    out["rup/table"] = _get("rup/table", p, timeout=timeout)
    return out


def _write(raw, tahun):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": time.time(), "tahun": tahun, "raw": raw},
                  f, ensure_ascii=False)
    os.replace(tmp, CACHE_PATH)


def _read():
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            c = json.load(f)
        if isinstance(c, dict) and isinstance(c.get("raw"), dict):
            return c
    except Exception:
        pass
    return {}


def _digest(raw, params):
    rel = raw.get("realisasi/table") or {}
    rup = raw.get("rup/table") or {}
    rows = rel.get("tableRows") or []
    rrows = rup.get("tableRows") or []
    return {
        "source": SOURCE,
        "fetched_at": time.time(),
        "last_update": (raw.get("last-update") or {}).get("lastUpdate"),
        "tahun": params.get("tahun"),
        "instansi": NAMA_INSTANSI,
        "realisasi": {"count": len(rows), "rows": rows},
        "rup": {"count": len(rrows), "rows": rrows},
    }


def load(max_age=TTL, tahun=None, jenis_klpd=None, instansi=None):
    """Cache-first; segar bila perlu. Gagal => cache lama + stale (halus)."""
    params = dict(DEFAULTS)
    if tahun:
        params["tahun"] = tahun
    if jenis_klpd:
        params["jenis_klpd"] = jenis_klpd
    if instansi:
        params["instansi"] = instansi

    cache = _read()
    fresh = (time.time() - cache.get("fetched_at", 0)) < max_age \
        and cache.get("tahun") == params["tahun"]
    if fresh:
        d = _digest(cache["raw"], params)
        d["stale"] = False
        d["status"] = "live"
        d["error"] = None
        d["fetched_at"] = cache.get("fetched_at")
        return d
    try:
        raw = fetch_all(params)
        _write(raw, params["tahun"])
        d = _digest(raw, params)
        d["stale"] = False
        d["status"] = "live"
        d["error"] = None
        return d
    except Exception as e:
        if cache.get("raw"):
            d = _digest(cache["raw"], params)
            d["stale"] = True
            d["status"] = "stale"
            d["error"] = str(e)[:160]
            d["fetched_at"] = cache.get("fetched_at")
            return d
        return {"source": SOURCE, "status": "empty", "stale": True,
                "fetched_at": None, "error": str(e)[:160],
                "last_update": None, "tahun": params["tahun"],
                "instansi": NAMA_INSTANSI,
                "realisasi": {"count": 0, "rows": []},
                "rup": {"count": 0, "rows": []}}
