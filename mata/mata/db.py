"""Lapis data MATA: SQLite ringan (cukup untuk VPS 4GB)."""
import os
import json
import sqlite3
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "mata.db")
STATUS_PATH = os.path.join(BASE_DIR, "data", "status.json")
FLAGS_PATH = os.path.join(BASE_DIR, "data", "flags_latest.json")

SCHEMA = """
CREATE TABLE IF NOT EXISTS announcements (
  id TEXT PRIMARY KEY,
  project TEXT NOT NULL,
  agency TEXT NOT NULL,
  kpa TEXT,
  region TEXT,
  value REAL NOT NULL,
  method TEXT,
  vendor TEXT,
  date_signed TEXT,
  date_start TEXT,
  date_end TEXT,
  ref_price REAL,
  source TEXT,
  url TEXT,
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT,
  n_records INTEGER,
  n_flags INTEGER,
  status TEXT
);
"""


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def init_db():
    conn = get_db()
    conn.commit()
    conn.close()


def upsert_records(records):
    conn = get_db()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    for r in records:
        conn.execute(
            """INSERT INTO announcements (id, project, agency, kpa, region, value, method,
               vendor, date_signed, date_start, date_end, ref_price, source, url, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 project=excluded.project, value=excluded.value, vendor=excluded.vendor,
                 date_signed=excluded.date_signed, ref_price=excluded.ref_price,
                 source=excluded.source, url=excluded.url""",
            (
                r["id"], r["project"], r["agency"], r.get("kpa"), r.get("region"),
                r["value"], r.get("method"), r.get("vendor"), r.get("date_signed"),
                r.get("date_start"), r.get("date_end"), r.get("ref_price"),
                r.get("source"), r.get("url"), now,
            ),
        )
    conn.commit()
    n = conn.execute("SELECT COUNT(*) c FROM announcements").fetchone()["c"]
    conn.close()
    return n


def load_records(fiscal_year=None, id_prefix=None):
    conn = get_db()
    q = "SELECT * FROM announcements"
    args = []
    if id_prefix:
        q += " WHERE id LIKE ?"
        args.append(f"{id_prefix}%")
    elif fiscal_year:
        q += " WHERE date_signed LIKE ?"
        args.append(f"{fiscal_year}%")
    q += " ORDER BY date_signed"
    rows = [dict(r) for r in conn.execute(q, args).fetchall()]
    conn.close()
    return rows


def log_run(n_records, n_flags, status="ok"):
    conn = get_db()
    conn.execute(
        "INSERT INTO runs (ts, n_records, n_flags, status) VALUES (?,?,?,?)",
        (datetime.datetime.now().isoformat(timespec="seconds"), n_records, n_flags, status),
    )
    conn.commit()
    conn.close()


def write_status(payload):
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    payload["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_flags(flags):
    os.makedirs(os.path.dirname(FLAGS_PATH), exist_ok=True)
    with open(FLAGS_PATH, "w", encoding="utf-8") as f:
        json.dump(flags, f, ensure_ascii=False, indent=2)


def read_flags():
    if not os.path.exists(FLAGS_PATH):
        return []
    with open(FLAGS_PATH, encoding="utf-8") as f:
        return json.load(f)
