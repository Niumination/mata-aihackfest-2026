"""Uji mandiri sapa_pub (jalankan: python3 _test_sapa.py) — tanpa framework."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mata import sapa_pub as S  # noqa: E402

FAIL = []


def ck(name, cond, extra=""):
    print(("  ✅ " if cond else "  ❌ ") + name + (f"  {extra}" if extra and not cond else ""))
    if not cond:
        FAIL.append(name)


print("── _num()")
ck("koma desimal", S._num("1317811348177,38") == 1317811348177.38, str(S._num("1317811348177,38")))
ck("titik ribuan", S._num("263.553.257.225.00") == 263553257225.0, str(S._num("263.553.257.225.00")))
ck("desimal tunggal", S._num("2.4") == 2.4, str(S._num("2.4")))
ck("bulat polos", S._num("5406240000") == 5406240000.0, str(S._num("5406240000")))
ck("campur 1.234,5", S._num("1.234,5") == 1234.5, str(S._num("1.234,5")))
ck("n/a -> None", S._num("n/a") is None)
ck("None -> None", S._num(None) is None)
ck("Rp prefix", S._num("Rp 12.500,00") == 12500.0, str(S._num("Rp 12.500,00")))

print("── _rup()")
ck("triliun", S._rup(1317811348177.38) == "Rp 1.32 T", S._rup(1317811348177.38))
ck("miliar", S._rup(618700433221.0) == "Rp 618.7 M", S._rup(618700433221.0))
ck("jt", S._rup(186000000.0) == "Rp 186 jt", S._rup(186000000.0))
ck("None", S._rup(None) == "—")

print("── digest() (rekaman sintetis)")
RECS = [
    {"kode_indikator_nama_indikator": "Jumlah Realisasi Belanja APBD",
     "opds_nama_opd": "Badan Pengelolaan Keuangan", "satuan": "rupiah", "tahun": "2025",
     "variabel": "1317811348177,38"},
    {"kode_indikator_nama_indikator": "Jumlah realisasi Belanja Pegawai",
     "opds_nama_opd": "Badan Pengelolaan Keuangan", "satuan": "rupiah", "tahun": None,
     "variabel": "618.700.433.221.00"},
    {"kode_indikator_nama_indikator": "Jumlah pengadaan Cadangan Pangan Pemerintah Daerah (CPPD)",
     "opds_nama_opd": "Dinas Pangan", "satuan": "Ton", "tahun": None, "variabel": "2.4"},
    {"kode_indikator_nama_indikator": "Jumlah Data Penduduk",
     "opds_nama_opd": "Dukcapil", "satuan": "jiwa", "tahun": "2026", "variabel": "780000"},
    {"kode_indikator_nama_indikator": "Indeks yang tak bernilai",
     "opds_nama_opd": "Dinas X", "satuan": "", "tahun": None, "variabel": "n/a"},
]
d = S.digest(RECS)
ck("count", d["count"] == 5)
ck("n_opd", d["n_opd"] == 4, str(d["n_opd"]))
ck("tahun", d["tahun"] == ["2025", "2026"], str(d["tahun"]))
ck("baseline APBD", d["baseline"]["apbd_realisasi"] == 1317811348177.38,
   str(d["baseline"]["apbd_realisasi"]))
ck("baseline str", d["baseline"]["apbd_str"] == "Rp 1.32 T", d["baseline"]["apbd_str"])
ck("kategori", d["baseline"]["kategori"][0]["nama"] == "Belanja Pegawai"
   and d["baseline"]["kategori"][0]["nilai"] == 618700433221.0)
ck("pbj memuat CPPD", any("CPPD" in r["indikator"] for r in d["pbj"]))
ck("pbj memuat realisasi BTT? (tidak ada — benar)",
   not any("BTT" in r["indikator"] for r in d["pbj"]))
ck("non-pbj tak masuk pbj", not any("Data Penduduk" in r["indikator"] for r in d["pbj"]))

print("── load(): jalur live (mock fetch)")
import mata.sapa_pub as M  # noqa: E402

orig_fetch = S.fetch  # simpan sebelum di-mock
saved = S.CACHE_PATH
S.CACHE_PATH = saved + ".test"
try:
    if os.path.exists(S.CACHE_PATH):
        os.remove(S.CACHE_PATH)
    calls = {"n": 0}

    def fake_fetch(timeout=30):
        calls["n"] += 1
        return RECS
    M.fetch = fake_fetch
    out = S.load()
    ck("status live", out["status"] == "live" and not out["stale"])
    ck("count", out["count"] == 5)
    out2 = S.load()
    ck("cache-hit (fetch tak dipanggil ulang)", calls["n"] == 1 and out2["status"] == "live")

    def boom(timeout=30):
        raise RuntimeError("jaringan mati")
    # paksa cache "tua" agar load() mencoba fetch (lalu gagal -> stale)
    with open(S.CACHE_PATH, encoding="utf-8") as f:
        old = json.load(f)
    old["fetched_at"] = time.time() - 99999
    with open(S.CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(old, f)
    M.fetch = boom
    out3 = S.load()
    ck("gagal -> stale + cache lama", out3["status"] == "stale" and out3["count"] == 5
       and out3["error"] == "jaringan mati")
    ck("stale flag", out3["stale"] is True)

    os.remove(S.CACHE_PATH)
    out4 = S.load()
    ck("gagal + tanpa cache -> empty", out4["status"] == "empty" and out4["count"] == 0)
finally:
    if os.path.exists(S.CACHE_PATH):
        os.remove(S.CACHE_PATH)
    S.CACHE_PATH = saved
    M.fetch = orig_fetch  # kembalikan fungsi asli

print("── LIVE (opsional, butuh internet):")
try:
    recs = S.fetch(timeout=25)
    dl = S.digest(recs)
    ck(f"live: {len(recs)} record", len(recs) > 500, str(len(recs)))
    ck("live: baseline APBD ~1,3 T", dl["baseline"]["apbd_realisasi"] and 1.2e12 < dl["baseline"]["apbd_realisasi"] < 1.5e12,
       str(dl["baseline"]))
    ck("live: >= 10 indikator PBJ", len(dl["pbj"]) >= 10, str(len(dl["pbj"])))
    print("  contoh pbj[0]:", json.dumps(dl["pbj"][0], ensure_ascii=False)[:140])
except Exception as e:
    print("  ⚠️ live dilewati:", e)

print()
if FAIL:
    print("❌ GAGAL:", FAIL)
    sys.exit(1)
print("✅ SEMUA LULUS")
