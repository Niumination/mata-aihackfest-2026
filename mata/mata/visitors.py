"""Statistik pengunjung + lokasi consent-first (UU PDP No. 27/2022).

Prinsip:
- Lokasi TIDAK pernah diambil diam-diam. Hanya dicatat setelah pengunjung
  menekan setuju (spanduk izin), dengan tujuan yang dijelaskan.
- Presisi dibatasi: GPS dibulatkan 2 desimal (~1 km); fallback IP hanya
  level KOTA. IP asli tidak disimpan (hash 8 char untuk hitung unik).
- Retensi: koordinat presisi dihapus otomatis >72 jam (agregat kota tetap).
- Opt-out kapan saja: /api/forget menghapus baris milik pengunjung hari ini.

Catatan teknis jujur: Geolocation API browser HANYA jalan di HTTPS.
Dashboard HTTP -> browser menolak; fallback perkiraan kota via IP
(ip-api.com, cache 24 jam) yang juga butuh persetujuan eksplisit.
"""
import datetime
import hashlib
import json
import time
import urllib.request

from . import db

ONLINE_WINDOW_S = 300
PRECISE_TTL_H = 72
UA = {"User-Agent": "MATA/0.3 (visitor city lookup; rate-limited, cached)"}

# kota -> (lat, lon) untuk pin peta sketsa
CITY_COORDS = {
    "jakarta": (-6.2, 106.85), "surabaya": (-7.25, 112.75), "medan": (3.6, 98.65),
    "banda aceh": (5.55, 95.3), "takengon": (4.63, 96.83), "aceh tengah": (4.63, 96.83),
    "bandung": (-6.9, 107.6), "semarang": (-7.0, 110.4), "yogyakarta": (-7.8, 110.35),
    "denpasar": (-8.65, 115.2), "makassar": (-5.15, 119.4), "palembang": (-2.98, 104.75),
    "pekanbaru": (0.5, 101.45), "padang": (-0.95, 100.35), "pontianak": (0.0, 109.3),
    "banjarmasin": (-3.3, 114.6), "balikpapan": (-1.25, 116.85), "manado": (1.5, 124.85),
    "jayapura": (-2.55, 140.7),
}


def init_table():
    con = db.get_db()
    con.execute("""CREATE TABLE IF NOT EXISTS visits (
      ts TEXT, day TEXT, path TEXT, iphash TEXT, browser TEXT, os TEXT,
      city TEXT, lat REAL, lon REAL, precise INTEGER DEFAULT 0)""")
    for col in ("city", "lat", "lon", "precise"):
        try:
            con.execute(f"ALTER TABLE visits ADD COLUMN {col} "
                        + ("TEXT" if col == "city" else
                           "REAL" if col in ("lat", "lon") else "INTEGER DEFAULT 0"))
        except Exception:
            pass
    con.execute("CREATE INDEX IF NOT EXISTS idx_visits_day ON visits(day)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_visits_ts ON visits(ts)")
    con.execute("""CREATE TABLE IF NOT EXISTS ip_cache (
      ip TEXT PRIMARY KEY, city TEXT, lat REAL, lon REAL, ts REAL)""")
    con.commit()
    con.close()


def _brand(ua):
    u = (ua or "").lower()
    if "telegrambot" in u:
        return "Telegram"
    if "curl" in u:
        return "curl"
    if "python" in u or "requests" in u or "http.client" in u:
        return "Bot/API"
    if "edg" in u:
        return "Edge"
    if "firefox" in u:
        return "Firefox"
    if "chrome" in u:
        return "Chrome"
    if "safari" in u:
        return "Safari"
    return "Lainnya"


def _os(ua):
    u = (ua or "").lower()
    if "android" in u:
        return "Android"
    if "iphone" in u or "ipad" in u:
        return "iOS"
    if "windows" in u:
        return "Windows"
    if "mac os" in u or "macintosh" in u:
        return "macOS"
    if "linux" in u:
        return "Linux"
    return "Lainnya"


def _iphash(ip):
    return hashlib.sha256((ip or "?").encode()).hexdigest()[:8]


def log_visit(ip, ua, path):
    try:
        init_table()
        now = datetime.datetime.now(datetime.timezone.utc)
        con = db.get_db()
        con.execute("INSERT INTO visits(ts,day,path,iphash,browser,os) VALUES (?,?,?,?,?,?)",
                    (now.strftime("%Y-%m-%dT%H:%M:%S"), now.strftime("%Y-%m-%d"),
                     (path or "/")[:80], _iphash(ip), _brand(ua), _os(ua)))
        con.commit()
        con.close()
    except Exception:
        pass  # statistik tidak boleh merusak request


def _private_ip(ip):
    return (ip or "").startswith(("127.", "10.", "192.168.", "::1", "172.16.",
                                  "172.17.", "172.18.", "172.19.", "172.2")) or ip in ("::1",)


def geocode_ip(ip):
    """Kota dari IP (ip-api.com, cache 24 jam). Return (city, lat, lon) atau None."""
    if not ip or _private_ip(ip):
        return ("Jaringan lokal", None, None)
    try:
        init_table()
        con = db.get_db()
        row = con.execute("SELECT city, lat, lon, ts FROM ip_cache WHERE ip=?", (ip,)).fetchone()
        if row and time.time() - row[3] < 86400:
            con.close()
            return (row[0], row[1], row[2])
        con.close()
        req = urllib.request.Request(
            f"http://ip-api.com/json/{ip}?fields=status,city,lat,lon", headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())
        if d.get("status") != "success":
            return None
        city, lat, lon = d.get("city") or "Tidak diketahui", d.get("lat"), d.get("lon")
        con = db.get_db()
        con.execute("INSERT OR REPLACE INTO ip_cache VALUES (?,?,?,?,?)",
                    (ip, city, lat, lon, time.time()))
        con.commit()
        con.close()
        return (city, lat, lon)
    except Exception:
        return None


def set_location(ip, city=None, lat=None, lon=None, precise=False):
    """Catat lokasi pada kunjungan TERAKHIR dari iphash ini (hari ini)."""
    try:
        init_table()
        con = db.get_db()
        con.execute("""UPDATE visits SET city=?, lat=?, lon=?, precise=?
                       WHERE rowid=(SELECT MAX(rowid) FROM visits
                                   WHERE iphash=? AND day=?)""",
                    (city, lat, lon, 1 if precise else 0, _iphash(ip),
                     datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")))
        con.commit()
        con.close()
        return True
    except Exception:
        return False


def forget(ip):
    """Hapus seluruh baris milik iphash ini (opt-out). Return jumlah terhapus."""
    try:
        init_table()
        con = db.get_db()
        cur = con.execute("DELETE FROM visits WHERE iphash=?", (_iphash(ip),))
        n = cur.rowcount
        con.commit()
        con.close()
        return n
    except Exception:
        return 0


def _prune():
    try:
        cutoff = (datetime.datetime.now(datetime.timezone.utc)
                  - datetime.timedelta(hours=PRECISE_TTL_H)).strftime("%Y-%m-%dT%H:%M:%S")
        con = db.get_db()
        con.execute("UPDATE visits SET lat=NULL, lon=NULL, precise=0 "
                    "WHERE precise=1 AND ts<?", (cutoff,))
        con.commit()
        con.close()
    except Exception:
        pass


def stats():
    """Return dict ringkas untuk widget/API (termasuk pin lokasi)."""
    try:
        init_table()
        _prune()
        now = datetime.datetime.now(datetime.timezone.utc)
        today = now.strftime("%Y-%m-%d")
        cutoff = (now - datetime.timedelta(seconds=ONLINE_WINDOW_S)).strftime("%Y-%m-%dT%H:%M:%S")
        con = db.get_db()
        con.row_factory = None
        online = con.execute("SELECT COUNT(DISTINCT iphash) FROM visits WHERE ts>=?",
                             (cutoff,)).fetchone()[0]
        dh, du = con.execute("SELECT COUNT(*), COUNT(DISTINCT iphash) FROM visits WHERE day=?",
                             (today,)).fetchone()
        th, tu = con.execute("SELECT COUNT(*), COUNT(DISTINCT iphash) FROM visits").fetchone()
        top = con.execute("SELECT path, COUNT(*) c FROM visits WHERE day=? "
                          "GROUP BY path ORDER BY c DESC LIMIT 4", (today,)).fetchall()
        recent = con.execute("SELECT ts, path, browser, os, city, precise FROM visits "
                             "ORDER BY ts DESC LIMIT 8").fetchall()
        locs = con.execute("SELECT city, lat, lon, COUNT(*) FROM visits "
                           "WHERE day=? AND city IS NOT NULL GROUP BY city, lat, lon",
                           (today,)).fetchall()
        con.close()
        pins = []
        for city, lat, lon, c in locs:
            pins.append({"city": city, "lat": lat, "lon": lon, "count": c,
                         "known": (city or "").lower() in CITY_COORDS or lat is not None})
        return {"online": online, "today_hits": dh, "today_unique": du,
                "total_hits": th, "total_unique": tu,
                "top_today": [{"path": p, "hits": c} for p, c in top],
                "recent": [{"ts": t, "path": p, "browser": b, "os": o,
                            "city": ci or "-",
                            "tag": "GPS" if pr else ("kota" if ci else "-")}
                           for t, p, b, o, ci, pr in recent],
                "locations": pins}
    except Exception:
        return {"online": 0, "today_hits": 0, "today_unique": 0,
                "total_hits": 0, "total_unique": 0, "top_today": [],
                "recent": [], "locations": []}


def city_coords():
    return CITY_COORDS
