#!/usr/bin/env python3
"""MATA — Kolektor RUP penuh (jalur VPS-direk, 12 Sep 2026).

Koleksi RUP rencana per-tahun dari BFF publik data.inaproc.id/dashboard-api
(sama persis jalur yang sudah terbukti utk realisasi: HTTP 200 dari VPS,
tanpa auth, tanpa bypass — path ini tidak diblokir WAF utk IP VPS).

Pagination teruji: limit=100 dihormati, offset bergeser → loop step-100.
Etik: jeda 2 s antar request, cap 800 baris/tahun, dedup kode_rup.
Estimasi: ~14 request utk 2 tahun (TA2026 ±657, TA2025 ±599 rencana).

Jalankan HANYA dari VPS MATA (IP lain 403 di edge WAF):
  python3 scripts/rup_full_collect.py                 # 2026 + 2025
  python3 scripts/rup_full_collect.py --tahun 2026    # satu tahun
Output: mata/data/rup_{tahun}_full.json  (daftar baris, skema asli INAPROC)
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://data.inaproc.id/dashboard-api"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
REFERER = "https://data.inaproc.id/rup"
LIMIT, STEP, CAP, JEDA = 100, 100, 800, 2
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def get_rows(offset, tahun):
    url = (BASE + "/rup/table?" + urllib.parse.urlencode(
        {"tahun": tahun, "jenis_klpd": "4", "instansi": "D6",
         "offset": offset, "limit": LIMIT}))
    req = urllib.request.Request(url, headers=dict(UA, Referer=REFERER))
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode("utf-8", "replace"))
    return d.get("tableRows") or []


def collect(tahun):
    seen, rows, offset, nreq = {}, [], 0, 0
    while offset < CAP:
        batch = get_rows(offset, tahun)
        nreq += 1
        for row in batch:
            k = str(row.get("kode_rup") or row.get("kode") or id(row))
            if k not in seen:
                seen[k] = True
                rows.append(row)
        print(f"  TA{tahun}: offset {offset} → {len(batch)} baris (total {len(rows)})", flush=True)
        if len(batch) < LIMIT:
            break
        offset += STEP
        time.sleep(JEDA)
    out = os.path.join(DATA_DIR, f"rup_{tahun}_full.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    print(f"  ✓ {out}: {len(rows)} baris ({os.path.getsize(out)//1024} KB), {nreq} request")
    return nreq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tahun", type=int, action="append",
                    help="Tahun anggaran (default: 2026 dan 2025)")
    a = ap.parse_args()
    tahun_list = a.tahun or [2026, 2025]
    total = sum(collect(t) for t in tahun_list)
    print(f"Selesai: {total} request total, jeda {JEDA}s.")


if __name__ == "__main__":
    sys.exit(main())
