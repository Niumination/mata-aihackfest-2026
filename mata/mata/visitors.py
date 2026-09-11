"""Statistik pengunjung dashboard MATA (stdlib only, privasi-minimal).

Disimpan: waktu (UTC), path, hash IP (8 char, untuk hitung unik — IP asli
TIDAK disimpan), keluarga browser & OS dari User-Agent.
Tampil: online (5 mnt terakhir), hari ini, total, halaman teratas, kunjungan terkini.
"""
import datetime
import hashlib

from . import db

ONLINE_WINDOW_S = 300


def init_table():
    con = db.get_db()
    con.execute("""CREATE TABLE IF NOT EXISTS visits (
      ts TEXT, day TEXT, path TEXT, iphash TEXT, browser TEXT, os TEXT)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_visits_day ON visits(day)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_visits_ts ON visits(ts)")
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


def log_visit(ip, ua, path):
    try:
        init_table()
        now = datetime.datetime.now(datetime.timezone.utc)
        iphash = hashlib.sha256((ip or "?").encode()).hexdigest()[:8]
        con = db.get_db()
        con.execute("INSERT INTO visits VALUES (?,?,?,?,?,?)",
                    (now.strftime("%Y-%m-%dT%H:%M:%S"), now.strftime("%Y-%m-%d"),
                     (path or "/")[:80], iphash, _brand(ua), _os(ua)))
        con.commit()
        con.close()
    except Exception:
        pass  # statistik tidak boleh merusak request


def stats():
    """Return dict ringkas untuk widget/API."""
    try:
        init_table()
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
        recent = con.execute("SELECT ts, path, browser, os FROM visits "
                             "ORDER BY ts DESC LIMIT 8").fetchall()
        con.close()
        return {"online": online, "today_hits": dh, "today_unique": du,
                "total_hits": th, "total_unique": tu,
                "top_today": [{"path": p, "hits": c} for p, c in top],
                "recent": [{"ts": t, "path": p, "browser": b, "os": o}
                           for t, p, b, o in recent]}
    except Exception:
        return {"online": 0, "today_hits": 0, "today_unique": 0,
                "total_hits": 0, "total_unique": 0, "top_today": [], "recent": []}
