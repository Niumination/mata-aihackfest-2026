"""Uji mandiri inaproc_pub (jalankan: python3 _test_inaporp.py) — tanpa framework.
Live dari SANDBOX = 403 (WAF) → jalur live diuji via mock; degradasi halus
(stale/empty) diuji langsung."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mata import inaproc_pub as M  # noqa: E402

FAIL = []


def ck(name, cond, extra=""):
    print(("  ✅ " if cond else "  ❌ ") + name + (f"  {extra}" if extra and not cond else ""))
    if not cond:
        FAIL.append(name)


FIXTURE = {
    "last-update": {"lastUpdate": "2026-09-12T02:47:55.571247+07:00"},
    "realisasi/table": {
        "filters": {"tahun": 2026, "jenisKlpd": ["4"], "instansi": "D6"},
        "tableState": {"offset": 0, "limit": 20},
        "tableRows": [
            {"nama_instansi": "KAB. ACEH TENGAH", "jenis_pengadaan": "Pekerjaan Konstruksi",
             "status_paket": "SELESAI", "tahun_anggaran": 2026, "total_nilai": 94553401,
             "nama_satuan_kerja": "DINAS PERUMAHAN DAN PERMUKIMAN - 1.04.1.03.0.00.01",
             "nama_paket": "PENGADAAN CONTOH JALAN", "nama_penyedia": "CV CONTOH UTAMA"},
            {"nama_instansi": "KAB. ACEH TENGAH", "jenis_pengadaan": "Pengadaan Barang",
             "status_paket": "DILAKSANAKAN", "tahun_anggaran": 2026, "total_nilai": 15000000,
             "nama_satuan_kerja": "BAPPEDA", "nama_paket": "BELANJA PERJALANAN", "nama_penyedia": ""},
        ],
    },
    "realisasi/summary": {"instansiOptions": [{"nama": "KAB. ACEH TENGAH", "kode": "D6"}]},
    "rup/table": {
        "tableRows": [
            {"cara_pengadaan": "Swakelola", "kode_rup": "42903570", "sumber_dana": "APBD",
             "tahun_anggaran": 2026, "nama_paket": "Belanja Perjalanan Dinas Dalam Kota",
             "produk_dalam_negeri": "-", "total_nilai": 15000000},
        ],
    },
}

orig_fetch = M.fetch_all
saved = M.CACHE_PATH
M.CACHE_PATH = saved + ".test"
try:
    if os.path.exists(M.CACHE_PATH):
        os.remove(M.CACHE_PATH)

    print("── load(): jalur live (mock fetch)")
    calls = {"n": 0}

    def fake(params=None, timeout=30):
        calls["n"] += 1
        return json.loads(json.dumps(FIXTURE))
    M.fetch_all = fake
    out = M.load()
    ck("status live", out["status"] == "live" and not out["stale"])
    ck("realisasi count", out["realisasi"]["count"] == 2)
    ck("rup count", out["rup"]["count"] == 1)
    ck("last_update", out["last_update"] == "2026-09-12T02:47:55.571247+07:00")
    out2 = M.load()
    ck("cache-hit (fetch tak diulang)", calls["n"] == 1 and out2["status"] == "live")

    print("── load(): degradasi (fetch gagal)")
    def boom(params=None, timeout=30):
        raise RuntimeError("403 WAF")
    M.fetch_all = boom
    # paksa cache tua agar load mencoba fetch (lalu gagal -> stale)
    with open(M.CACHE_PATH, encoding="utf-8") as f:
        old = json.load(f)
    old["fetched_at"] = time.time() - 99999
    with open(M.CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(old, f)
    out3 = M.load()
    ck("gagal -> stale + data lama", out3["status"] == "stale" and out3["realisasi"]["count"] == 2
       and out3["error"] == "403 WAF")

    os.remove(M.CACHE_PATH)
    out4 = M.load()
    ck("gagal + tanpa cache -> empty (halus)", out4["status"] == "empty"
       and out4["realisasi"]["count"] == 0)

    print("── LIVE sandbox (diperkirakan 403 WAF → harus tetap halus):")
    out5 = M.load()
    ck("tidak meledak; status di {live,stale,empty}", out5["status"] in ("live", "stale", "empty"),
       str(out5.get("status")))
    if out5["status"] == "live":
        ck("live sandbox: ada rows", out5["realisasi"]["count"] > 0)
        r0 = out5["realisasi"]["rows"][0]
        print("  contoh row[0] keys:", sorted(r0.keys()))
        print("  row[0]:", json.dumps(r0, ensure_ascii=False)[:300])
finally:
    if os.path.exists(M.CACHE_PATH):
        os.remove(M.CACHE_PATH)
    M.CACHE_PATH = saved
    M.fetch_all = orig_fetch

print()
if FAIL:
    print("❌ GAGAL:", FAIL)
    sys.exit(1)
print("✅ SEMUA LULUS")
