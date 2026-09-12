"""MATA — SPSE Publik LKPP (jalur live per-paket TANPA izin).

Sumber: portal SPSE terpadu LKPP, halaman publik LPSE Kab. Aceh Tengah
(https://spse.inaproc.id/acehtengahkab) — tanpa login, tanpa token, tanpa
approval KLPD. Ini jalur alternatif Jalur A (token INAPROC) untuk data
per-paket di kabupaten sendiri.

Cakupan server-side (VPS): hanya daftar paket TERKINI dari halaman utama.
DataTables AJAX (/dt/lelang) dan halaman detail terblokir Cloudflare/sesi
untuk curl dari datacenter (temuan 12 Sep, commit 11e40ee) — data penuh
(riwayat, detail, pemenang berkontrak) datang dari kolektor laptop:
`scripts/spse_collect.py` (Jalur B) yang push ke /api/spse-push.

Etik sama dengan modul lain: indikasi, bukan vonis; data dicatat apa adanya
beserta sumber & cakupan.
"""
import html as _html
import json
import os
import re
import secrets
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
CACHE_PATH = os.path.join(BASE_DIR, "data", "spse_cache.json")
TTL = 1800  # 30 menit, selaras iklim.py
DEFAULT_SLUG = "acehtengahkab"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

_LINKS = (
    ("tender", re.compile(r'href="[^"]*/lelang/(\d+)/pengumumanlelang"[^>]*>(.*?)</a>', re.S)),
    ("nontender", re.compile(r'href="[^"]*/nontender/(\d+)/pengumumanpl"[^>]*>(.*?)</a>', re.S)),
)
_RUP = re.compile(r"Rp\.?\s?([\d.]+),\d{2}")
_DATE = re.compile(r"(\d{1,2}\s+[A-Z][a-z]+\s+\d{4}\s+\d{2}:\d{2})")


def _txt(s):
    return _html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def fetch_homepage(slug=DEFAULT_SLUG, timeout=25):
    url = "https://spse.inaproc.id/" + slug
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def parse_packages(page_html, slug=DEFAULT_SLUG):
    """Urai baris tabel tender + non-tender dari HTML halaman utama."""
    out = []
    for kind, rx in _LINKS:
        for m in rx.finditer(page_html):
            code = m.group(1)
            # konteks baris: dari <tr> sebelumnya sampai </tr> berikutnya
            a = page_html.rfind("<tr", 0, m.start())
            b = page_html.find("</tr>", m.end())
            row = page_html[a:b if b != -1 else m.end() + 1200]
            hps = _RUP.search(row)
            dt = _DATE.search(row)
            seg = "lelang" if kind == "tender" else "nontender"
            out.append({
                "kode": code,
                "nama": _txt(m.group(2)),
                "jenis": kind,
                "hps": int(hps.group(1).replace(".", "")) if hps else None,
                "hps_str": ("Rp. " + hps.group(1) + ",00") if hps else None,
                "tutup": dt.group(1) if dt else None,
                "ulang": "Tender Ulang" in row or "SELEKSI ULANG" in row.upper(),
                "url": "https://spse.inaproc.id/%s/%s/%s/%s" % (
                    slug, seg, code,
                    "pengumumanlelang" if kind == "tender" else "pengumumanpl"),
            })
    out.sort(key=lambda p: (p["jenis"] != "tender", p["kode"]))
    return out


def _write(data):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, CACHE_PATH)


def load(slug=DEFAULT_SLUG, max_age=TTL):
    """Cache-first; segar dari halaman utama bila perlu. Gagal => cache lama + stale."""
    cache = {}
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        pass
    fresh = (cache.get("slug") == slug and cache.get("count") is not None
             and time.time() - cache.get("fetched_at", 0) < max_age)
    if fresh:
        cache["stale"] = False
        return cache
    try:
        pk = parse_packages(fetch_homepage(slug), slug)
        data = {
            "slug": slug,
            "source": "https://spse.inaproc.id/" + slug,
            "fetched_at": time.time(),
            "scope": "daftar paket terkini dari halaman utama (publik); "
                     "riwayat & pemenang via kolektor (jalur B) / API INAPROC (jalur A)",
            "packages": pk,
            "tender": [p for p in pk if p["jenis"] == "tender"],
            "nontender": [p for p in pk if p["jenis"] == "nontender"],
            "count": len(pk),
            "stale": False,
        }
        _write(data)
        return data
    except Exception as e:
        if cache.get("slug") == slug and cache.get("count"):
            cache["stale"] = True
            cache["error"] = str(e)[:160]
            return cache
        return {"slug": slug, "source": "https://spse.inaproc.id/" + slug,
                "fetched_at": None, "packages": [], "tender": [], "nontender": [],
                "count": 0, "stale": True, "error": str(e)[:160]}


def _expected_token():
    env = os.environ.get("MATA_SPSE_PUSH_TOKEN")
    if env:
        return env
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return (json.load(f).get("spse") or {}).get("push_token") or None
    except Exception:
        return None


def push(token, payload):
    """Penerima data kolektor laptop (Jalur B). Fail-closed: tanpa token => tolak."""
    want = _expected_token()
    if not want or not token or not secrets.compare_digest(str(token), str(want)):
        return {"ok": False, "error": "token tidak valid"}
    if not isinstance(payload, dict) or not payload.get("packages"):
        return {"ok": False, "error": "bentuk payload salah (wajib: {packages: [...]})"}
    slug = payload.get("slug") or DEFAULT_SLUG
    data = dict(payload)
    data.update({"slug": slug, "fetched_at": time.time(), "stale": False,
                 "source": payload.get("source") or "https://spse.inaproc.id/" + slug})
    data["count"] = len(data["packages"])
    _write(data)
    return {"ok": True, "count": data["count"]}
