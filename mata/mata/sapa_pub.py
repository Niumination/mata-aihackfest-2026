"""MATA — SAPA SPLP (API indikator resmi Pemkab Aceh Tengah, TANPA auth).

Sumber: sistem SAPA (Satu Pintu Akses) di infrastruktur layanan pemerintah
(`api-splp.layanan.go.id`) — API resmi, tanpa login, tanpa token; akses dari
datacenter dibuktikan live (12 Sep 2026, HTTP 200, tanpa header khusus).
Sumber yang sama sudah live-produksi di sapa-smart-ai.vercel.app
(repo Niumination/sapa-ai) — pola diambil dari `src/lib/sapa-client.ts`
(fetch → cache 10 mnt → degradasi stale → status jujur).

Peran dalam MATA: SUMBER KONTEKS RESMI, bukan inti PBJ per-paket (itu jalur
SPSE/ISB di spse_pub.py):
  - baseline anggaran: Realisasi Belanja APBD → memberi makna rasio D2
    (share vendor terhadap total anggaran kabupaten),
  - cross-check: sinyal MATA (mis. pola tender jalan) ↔ indikator OPD
    (Dinas PUPR) dari sumber independen.

Respons API: `{"api_status":1,"data":[...]}` — dump penuh 2.067 indikator
(38 OPD, 2022–2026), field per record: `kode_indikator_nama_indikator`,
`opds_nama_opd`, `satuan`, `tahun`, `variabel` (=nilainya), `jadwal_pemutakhiran`.
Dump penuh disimpan di data/sapa_cache.json; /api/sapa mengembalikan digest
ringan (baseline + indikator PBJ-relevan bernilai numerik).
"""
import json
import os
import re
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(BASE_DIR, "data", "sapa_cache.json")
API_URL = "https://api-splp.layanan.go.id/sapa/1.0/api/daftar_data"
TTL = 600  # 10 menit — selaras pola sapa-ai (LRU 10 mnt)
SOURCE = API_URL

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Content-Type": "application/json"}

# Indikator yang relevan konteks anggaran/PBJ (bukan per-paket, tapi baseline
# & cross-check untuk sinyal MATA).
_PBJ_RX = re.compile(
    r"pengadaan|lelang|kontrak|realisasi|belanja|APBD|defisit|surplus|"
    r"hibah|bantuan|pendapatan", re.I)


def fetch(timeout=30):
    """Ambil dump penuh dari SAPA SPLP. Gagal => raise (dijadikan stale)."""
    req = urllib.request.Request(API_URL, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        payload = json.loads(r.read().decode("utf-8", "replace"))
    if not isinstance(payload, dict) or payload.get("api_status") != 1:
        raise RuntimeError("SAPA API status != 1: %s"
                           % str(payload.get("api_message") if isinstance(payload, dict) else payload)[:120])
    data = payload.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("SAPA API tanpa data")
    return data


def _num(v):
    """'1317811348177,38' / '263.553.257.225.00' / '2.4' / '5406240000' -> float|None."""
    if v is None:
        return None
    s = str(v).strip().replace("Rp", "").replace("rupiah", "").replace(" ", "")
    if not s or re.fullmatch(r"[-–/()]*", s):
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")  # titik=ribuan, koma=desimal
    elif "," in s:
        s = s.replace(",", ".")  # koma desimal
    elif "." in s:
        m = re.fullmatch(r"(\d{1,3}(?:\.\d{3})*)\.(\d{1,2})", s)
        if m:  # ribuan + desimal 1–2 digit: 263.553.257.225.00
            s = m.group(1).replace(".", "") + "." + m.group(2)
        elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
            s = s.replace(".", "")  # murni ribuan
    try:
        return float(s)
    except ValueError:
        return None


def _rup(v):
    if v is None:
        return "—"
    if v >= 1e12:
        return "Rp %.2f T" % (v / 1e12)
    if v >= 1e9:
        return "Rp %.1f M" % (v / 1e9)
    if v >= 1e6:
        return "Rp %.0f jt" % (v / 1e6)
    return "Rp %s" % format(v, ",.0f")


def digest(records):
    """Digest ringan dari dump penuh: metadata + baseline APBD + indikator kunci."""
    opds = set()
    tahun = set()
    for r in records:
        if r.get("opds_nama_opd"):
            opds.add(r["opds_nama_opd"])
        t = str(r.get("tahun") or "").strip()
        if t:
            tahun.add(t)

    apbd = None
    kategori = []
    pbj = []
    for r in records:
        nama = str(r.get("kode_indikator_nama_indikator") or "")
        if not nama:
            continue
        nilai = _num(r.get("variabel"))
        if "Realisasi Belanja APBD" in nama and apbd is None:
            apbd = nilai
        elif re.fullmatch(r"Jumlah realisasi Belanja [A-Z][a-z ]+", nama) and nilai is not None:
            kategori.append({"nama": re.sub(r"^Jumlah realisasi ", "", nama),
                             "nilai": nilai, "str": _rup(nilai)})
        elif _PBJ_RX.search(nama) and nilai is not None:
            pbj.append({"indikator": nama, "opd": r.get("opds_nama_opd"),
                        "nilai": nilai, "satuan": r.get("satuan") or "",
                        "tahun": str(r.get("tahun") or "") or None})

    kategori.sort(key=lambda k: -k["nilai"])
    pbj.sort(key=lambda k: -k["nilai"])

    return {
        "count": len(records),
        "n_opd": len(opds),
        "tahun": sorted(tahun),
        "baseline": {
            "apbd_realisasi": apbd,
            "apbd_str": _rup(apbd),
            "kategori": kategori[:8],
        },
        "pbj": pbj[:15],
    }


def _write(records):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": time.time(), "records": records}, f, ensure_ascii=False)
    os.replace(tmp, CACHE_PATH)


def _read():
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            c = json.load(f)
        if isinstance(c, dict) and c.get("records"):
            return c
    except Exception:
        pass
    return {}


def load(max_age=TTL):
    """Cache-first; segar dari SAPA bila perlu. Gagal => cache lama + stale."""
    cache = _read()
    if (time.time() - cache.get("fetched_at", 0)) < max_age:
        out = {"source": SOURCE, "status": "live", "stale": False,
               "fetched_at": cache["fetched_at"], "error": None}
        out.update(digest(cache["records"]))
        return out
    try:
        records = fetch()
        _write(records)
        out = {"source": SOURCE, "status": "live", "stale": False,
               "fetched_at": time.time(), "error": None}
        out.update(digest(records))
        return out
    except Exception as e:
        if cache.get("records"):
            out = {"source": SOURCE, "status": "stale", "stale": True,
                   "fetched_at": cache.get("fetched_at"), "error": str(e)[:160]}
            out.update(digest(cache["records"]))
            return out
        return {"source": SOURCE, "status": "empty", "stale": True,
                "fetched_at": None, "error": str(e)[:160], "count": 0,
                "n_opd": 0, "tahun": [], "baseline": {"apbd_realisasi": None,
                                                       "apbd_str": "—", "kategori": []},
                "pbj": []}
