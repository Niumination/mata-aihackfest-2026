"""Collector MATA: sumber data (semua data PUBLIK, patuh ToS).

- mode "synthetic": dataset demo yang realistis & deterministik (seed tetap) —
  jalur yang MENJAMIN demo jalan (offline), dengan anomali yang ditanam untuk
  membuktikan rule engine bekerja.
- mode "live": probe ke sumber publik (Panda LKPP / LPSE daerah / inaproc).
  PENTING: uji akses dari VPS pada HARI 1 (lihat README). Probe di sini
  best-effort & sopan (rate limit, user-agent jelas, hanya data publik).
"""
import random
import datetime

REGION = "Kabupaten Aceh Tengah"
FY = 2025

AGENCIES = [
    "Dinas PUPR", "Dinas Pendidikan", "Dinas Kesehatan",
    "Dinas Perhubungan", "Bappeda", "Dinas Pekerjaan Umum & Penataan Ruang",
]

# Vendor "normal" (track record beragam)
VENDORS_NORMAL = [
    "CV Gayo Karya", "PT Kutacane Bangun Perkasa", "CV Linge Konstruksi",
    "PT Takengon Presisi", "CV Lut Tawar Sejahtera", "PT Bebesen Infrastruktur",
]
# Vendor "buruk" (D2: konsentrasi) & vendor "baru" (D4)
VENDOR_CONCENTRATED = "PT Bebesen Abadi"
VENDOR_NEW = "CV Sileu Karya"

# Proyek normal (realistis untuk kabupaten pegunungan)
NORMAL_PROJECTS = [
    ("Rehabilitasi Jalan Kabupaten Ruas X–Y", "Dinas PUPR", 900_000_000),
    ("Pembangunan Drainase Kota Takengon Paket 1", "Dinas PUPR", 1_400_000_000),
    ("Rehabilitasi Gedung SMPN 3 Takengon", "Dinas Pendidikan", 750_000_000),
    ("Pengadaan Alat Kesehatan Puskesmas Bebesen", "Dinas Kesehatan", 620_000_000),
    ("Pemeliharaan Jembatan Sesa Ruas A", "Dinas PUPR", 480_000_000),
    ("Pengadaan Komputer SD Se-Kecamatan Pegasing", "Dinas Pendidikan", 380_000_000),
    ("Penerangan Jalan Umum Jl. Merdeka", "Dinas Perhubungan", 540_000_000),
    ("Normalisasi Sungai Kekecutan Paket 2", "Dinas PUPR", 1_100_000_000),
    ("Pengadaan Mobil Ambulans Puskesmas Ketol", "Dinas Kesehatan", 890_000_000),
    ("Rehabilitasi Pasar Tradisional Linge", "Dinas Perhubungan", 1_250_000_000),
    ("Pembangunan MCK Sekolah Desa Sumber", "Dinas Pendidikan", 310_000_000),
    ("Pengadaan Alat Berat Excavator", "Dinas PUPR", 2_900_000_000),
    ("Perbaikan Tanggul Banjir Sesa", "Dinas PUPR", 980_000_000),
    ("Renovasi Ruang Perinatologi RSUD", "Dinas Kesehatan", 1_600_000_000),
    ("Pengadaan Mebel kantor kecamatan", "Bappeda", 210_000_000),
    ("Pembangunan Saluran Irigasi Sawah Linge", "Dinas PUPR", 830_000_000),
    ("Perbaikan Akses Jl. Hip Burger Segmen C", "Dinas PUPR", 1_750_000_000),
    ("Pengadaan Tablet Siswa Kurang Mampu", "Dinas Pendidikan", 560_000_000),
    ("Rehabilitasi Posyandu Se-Kabupaten (Tahap 1)", "Dinas Kesehatan", 420_000_000),
    ("Pembangunan Tandon Air Desa Siliwangi", "Dinas PUPR", 290_000_000),
    ("Pelican Crossing & Rambu Kawasan Sekolahan", "Dinas Perhubungan", 180_000_000),
    ("Pengadaan Server Data Daerah (e-Gov)", "Bappeda", 730_000_000),
    ("Perbaikan Bangsal IGD RSUD", "Dinas Kesehatan", 1_950_000_000),
    ("Pengaspalan Jl. Desa Blangkejeren", "Dinas PUPR", 640_000_000),
    ("Dokumentasi & Survei Kadastral", "Bappeda", 350_000_000),
]


def _date(rng, month=None, day=None):
    m = month or rng.randint(1, 12)
    d = day or rng.randint(1, 28)
    return f"{FY}-{m:02d}-{d:02d}"


def generate_synthetic(seed=42):
    """48 pengumuman PBJ FY2025 dengan 5 anomali ter-plant (deterministik).

    Anomali yang ditanam:
      D1: "Rehabilitasi Jalan Ruas X–Y (Kerjasama)" — nilai 2,7 M vs ref 800 jt (deviasi +237%)
      D2: VENDOR_CONCENTRATED menang 10 proyek (porsi nilai terbesar)
      D3: 6 kontrak besar ditandatangani 22–31 Des (keroyokan akhir tahun)
      D4: VENDOR_NEW (2 kontrak kecil) menang kontrak 4,8 M
      D6: 3 proyek dengan nilai identik Rp999.999.999
    """
    rng = random.Random(seed)
    recs = []

    def add(project, agency, value, vendor, date_signed, method, ref_price=None,
            kpa=None, url_id=None):
        rid = f"AT-{FY}-{len(recs)+1:04d}"
        recs.append({
            "id": rid,
            "project": project,
            "agency": agency,
            "kpa": kpa or "KPA " + agency,
            "region": REGION,
            "value": float(value),
            "method": method,
            "vendor": vendor,
            "date_signed": date_signed,
            "date_start": date_signed,
            "date_end": _date(rng, rng.randint(1, 12)),
            "ref_price": ref_price,
            "source": "synthetic-demo",
            "url": f"https://lpse.acehtengahkab.go.id/pengumuman/{url_id or rid}",
        })
        return rid

    # --- 25 proyek normal (sebaran Jan–Nov, vendor beragam, ref mendekati nilai) ---
    for i, (proj, ag, base) in enumerate(NORMAL_PROJECTS[:25]):
        value = int(base * rng.uniform(0.85, 1.15))
        vendor = rng.choice(VENDORS_NORMAL)
        add(proj, ag, value, vendor, _date(rng, month=rng.randint(1, 11)),
            rng.choice(["tender", "e-katalog"]),
            ref_price=int(value * rng.uniform(0.92, 1.10)))

    # --- D2: vendor ter-konsentrasi — 10 proyek, sebaran setahun ---
    for m in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        proj = f"Paket {chr(65 + m)} — {rng.choice(['Jalan lingkungan', 'Genteng sekolah', 'Saluran air', 'Rehab ruang kelas', 'Taman publik', 'Drainase lingkungan', 'Perbaikan talud', 'Pengadaan meubelair', 'Rehab musala desa', 'Paving jalan desa'])} (Tahap {m})"
        value = int(rng.uniform(1_400_000_000, 2_200_000_000))
        add(proj, rng.choice(AGENCIES), value, VENDOR_CONCENTRATED,
            _date(rng, month=m, day=rng.randint(5, 20)), "tender",
            ref_price=int(value * rng.uniform(0.95, 1.12)))

    # --- D3: keroyokan akhir tahun — 6 kontrak besar, 22–31 Des ---
    for i in range(6):
        proj = f"Proyek Prioritas Akhir Tahun {i+1} — {rng.choice(['Jalan strategis', 'Ruang rawat inap', 'Infrastruktur irigasi', 'Jembatan desa', 'Gedung serbaguna', 'Jaringan PJU'])}"
        value = int(rng.uniform(1_200_000_000, 2_500_000_000))
        add(proj, rng.choice(AGENCIES), value, rng.choice(VENDORS_NORMAL),
            _date(rng, month=12, day=rng.randint(22, 31)), "tender",
            ref_price=int(value * rng.uniform(0.90, 1.05)))

    # --- D1: harga di pasar (HPS jauh di atas referensi katalog) ---
    add("Rehabilitasi Jalan Ruas Takengon–Bintang (Kerjasama)", "Dinas PUPR",
        2_700_000_000, "PT Kutacane Bangun Perkasa", _date(rng, month=3, day=14),
        "tender", ref_price=800_000_000)

    # --- D4: vendor baru/kecil menang kontrak besar ---
    add("Pengadaan Mobil Operasional (Riwayat 1)", "Bappeda", 350_000_000,
        VENDOR_NEW, _date(rng, month=2, day=9), "e-katalog", ref_price=340_000_000)
    add("Perbaikan Plafon & Cat Kantor (Riwayat 2)", "Bappeda", 280_000_000,
        VENDOR_NEW, _date(rng, month=4, day=21), "e-katalog", ref_price=290_000_000)
    add("Pembangunan Gedung Poliklinik RSUD Tipe B", "Dinas Kesehatan",
        4_800_000_000, VENDOR_NEW, _date(rng, month=11, day=18), "tender",
        ref_price=4_200_000_000)

    # --- D6: nilai identik (pola copy-paste anggaran) ---
    for i, ag in enumerate(["Dinas Pendidikan", "Dinas Kesehatan", "Dinas PUPR"]):
        add(f"Paket {i+1} — Pengadaan Barang Operasional", ag, 999_999_999,
            rng.choice(VENDORS_NORMAL), _date(rng, month=rng.randint(1, 11)),
            "e-katalog", ref_price=990_000_000)

    return recs


# ---------------------------------------------------------------------------
# Probe LIVE (best-effort) — WAJIB uji akses dari VPS pada HARI 1.
# Hanya data PUBLIK, user-agent jelas, tanpa login, tanpa scraping agresif.
# ---------------------------------------------------------------------------
import requests  # noqa: E402

UA = "MATA-watchdog/0.1 (demo AI HackFest 2026; data publik; kontak: peserta)"


def probe_panda_lkpp():
    """Probe portal pengumuman PBJ nasional (Panda LKPP).

    Catatan: endpoint publik bisa berubah. Uji dari VPS:
      curl -s -A "$UA" https://panda.lkpp.go.id | head
    Jika ada JSON API → implement di sini; jika hanya HTML publik → parse
    halaman pengumuman secara terbatas & sopan (hanya halaman yang diizinkan).
    """
    try:
        r = requests.get("https://panda.lkpp.go.id", headers={"User-Agent": UA}, timeout=10)
        return {"ok": r.status_code == 200, "status": r.status_code,
                "note": "cek struktur halaman/JSON; implement parser sesuai yang tersedia"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def probe_inaproc():
    """Probe e-Katalog (inaproc) — data harga & spesifikasi publik."""
    try:
        r = requests.get("https://inaproc.id", headers={"User-Agent": UA}, timeout=10)
        return {"ok": r.status_code == 200, "status": r.status_code}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def probe_lpse_region(host):
    """Probe LPSE daerah (mis. lpse.acehtengahkab.go.id / LPSE Prov. Aceh)."""
    try:
        r = requests.get(f"https://{host}", headers={"User-Agent": UA}, timeout=10)
        return {"ok": r.status_code == 200, "status": r.status_code}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def collect_inaproc():
    """Record dari koleksi penuh INAPROC realisasi (file deterministik, offline).

    Sumber: data/realisasi_{tahun}_full.json — koleksi VPS dari BFF publik
    data.inaproc.id (12 Sep 2026; 662 + 599 paket, 16 field asli).
    TANPA tanggal tandatangan (sumber tidak mempublikasikan) → aturan yang
    butuh tanggal (D3) otomatis tak berjalan untuk record ini; TANPA harga
    referensi (D1) — keduanya jujur, bukan disembunyikan.
    ID: INP-{tahun_anggaran}-{kode_paket} (prefiks INP- dikenali oleh
    `_mode()` di web.py untuk badge MODE: LIVE).
    """
    import json
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = []
    for t in (2026, 2025):
        p = os.path.join(base, "data", f"realisasi_{t}_full.json")
        try:
            with open(p, encoding="utf-8") as f:
                rows = json.load(f)
        except Exception:
            continue
        for r in rows:
            if not isinstance(r, dict):
                continue
            kode = r.get("kode_paket")
            if not kode:
                continue
            vendor = (r.get("nama_penyedia") or "").strip()
            if vendor in ("", "-", "-1", "0"):
                vendor = None
            out.append({
                "id": "INP-%s-%s" % (r.get("tahun_anggaran") or t, kode),
                "project": r.get("nama_paket") or "?",
                "agency": r.get("nama_satuan_kerja") or REGION,
                "kpa": None,
                "region": REGION,
                "value": float(r.get("total_nilai") or 0),
                "method": r.get("metode_pengadaan"),
                "vendor": vendor,
                "date_signed": None,
                "date_start": None,
                "date_end": None,
                "ref_price": None,
                "source": "INAPROC realisasi (data.inaproc.id)",
                "url": "https://data.inaproc.id/realisasi",
            })
    return out


def run_collect(cfg):
    """Kembalikan list record sesuai mode config."""
    mode = cfg.get("collect", {}).get("mode", "synthetic")
    if mode == "synthetic":
        return generate_synthetic()
    if mode == "inaproc":
        return collect_inaproc()
    # mode live (probe jaringan) — tidak dipakai; jalur file deterministik sudah dipilih
    raise NotImplementedError(
        "Mode 'live' belum diimplementasikan — gunakan 'synthetic' (demo) "
        "atau 'inaproc' (koleksi file deterministik).")


if __name__ == "__main__":
    import json
    print(json.dumps({
        "panda": probe_panda_lkpp(),
        "inaproc": probe_inaproc(),
        "lpse-acehtengah": probe_lpse_region("lpse.acehtengahkab.go.id"),
    }, indent=2))
