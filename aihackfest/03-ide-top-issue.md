# AI HackFest 2026 — Ide dari TOP ISSUE Indonesia (Ronde 3)
**Untuk:** Afrizal Munthe · Batch 3 (11–15 Sep 2026) · Productivity & Personal AI · Hermes Agent

## 1. Masalah PALING MASIF di Indonesia (peta target)

> Angka harus diverifikasi sumber terbarunya saat menulis artikel (BPS/OJK/kementerian). Angka di bawah = perkiraan dari data publik terakhir.

| # | Masalah | Skala (perkiraan) | Muat di "Productivity & Personal AI"? |
|---|---------|-------------------|----------------------------------------|
| 1 | **Ekonomi informal / UMKM** — 99% badan usaha, ~64 juta pekerja, ±97% penyerapan tenaga kerja | **PALING MASIF** (BPS) | ✅ Sangat — produktivitas mikro-bisnis & pekerja |
| 2 | **Pinjol / over-indebtedness** — 10+ juta peminjam, penagihan brutal, pinjol ilegal marak | Nasional, topic panas (OJK) | ✅ Personal AI finansial |
| 3 | **Perumahan** — defisit ±12 juta unit; puluhan juta penyewa; deposit "hilang" tiap tahun | Nasional (KemenPUPR) | ✅ (sisi penyewa) |
| 4 | Kualitas pendidikan — 36+ juta siswa, kesenjangan luar Jawa | Nasional | ✅ (sudah ada: WaliKelas) |
| 5 | Stunting ~19% (prioritas negara) | Nasional | ❌ kategori Healthcare/Agriculture |
| 6 | Scam digital — puluhan ribu laporan/bln | Nasional | ❌ kategori Digital Safety |
| 7 | Birokrasi/surat-menyurat | Kronis, semua orang | ✅ (sudah ada: BiroSurat/Arsipin) |

**Konsolidasi 13 ide sebelumnya:** hampir semua sudah "sisi pemilik bisnis" (kasir, PO, kos, klien). **Ruang kosong terbesar = sisi PEKERJA & KONSUMEN yang rentan** — di situlah ide juara yang belum dipikirkan peserta lain.

---

## 2. IDE UTAMA — **GajiTepat**: "Slip gaji untuk 64 juta pekerja informal" 👷 (REKOMENDASI)

### Akar masalah (paling masif #1)
Pekerja informal (bengkel, katering, kontraktor, laundry, armada ojek, pabrik kecil) bekerja tanpa jejak formal:
- **Gaji sering telat & tidak tertulis** → sengketa upah & kerja lembur.
- **Tidak ada bukti penghasilan** → tidak bisa buka rekening dengan layak, tidak bisa ajukan KUR/kartu kredit, tidak bisa urus BPJS → **terkunci di luar inklusi keuangan**.
- Pemilik UMKM kecil juga pusing: hitung gaji manual (10–30 pekerja × lembur × potongan) saat payday = 2 jam + rawan salah hitung.

### Pitch
Agen **payroll + proteksi pekerja** untuk pemberi kerja mikro (3–30 pekerja), berjalan di WhatsApp:
1. **Absensi ringan** — pekerja chat *"check-in"* (opsional: foto/lokasi, default = chat saja agar ringan & tidak invasif); owner bisa mencatat dari HP-nya kapan pun.
2. **Mesin hitung upah sesuai aturan** — owner set sekali: gaji harian/harian per posisi, aturan lembur, bonus/potongan. Agen menghitung otomatis **mengikuti rumus UU Ketenagakerjaan** (OT jam ke-1 = 1,5×, dst.) — *rule engine*, bukan black-box (juri Eko & Onno suka transparansi).
3. **Payday engine (cron)** — tanggal gajian: agen menyusun **rekap transfer** per pekerja, **owner WAJIB approve** sebelum final (ethical by design), lalu **slip gaji digital** (PDF + QR verifikasi) terkirim ke masing-masing pekerja + arsip owner.
4. **Slip gaji = bukti penghasilan** — pekerja menyimpannya; bisa dipakai untuk aplikasi KUR/perbankan/BPJS. Inilah hook-nya: *"slip yang membuat pekerja informal menjadi bankable."*
5. **Laba kerja (labor report)** bulanan ke owner + pengingat iuran BPJS Ketenagakerjaan (rekap manual — jujur, tanpa klaim integrasi yang tidak ada).
6. **Transparansi dua arah** — pekerja bisa tanya: *"Lembur saya bulan ini berapa jam, dapat berapa?"* → agen jawab dari data yang sama dengan owner. Data sama = sengketa berkurang.

### Ciri khas (yang tidak dimiliki peserta lain)
- **Sisi pekerja, bukan sisi pemilik** — semua peserta lain membangun alat untuk bos; ini membangun **jaring pengaman** untuk pekerjanya.
- **Inklusi keuangan**: slip digital = bukti penghasilan pertama dalam hidup banyak pekerja.
- **Rule engine ketenagakerjaan** yang terbuka & bisa diaudit.
- **Multi-rol dalam satu grup WA** (owner + N pekerja) — demo yang hidup.

### Dampak nyata & metrik (demo)
- 20 pekerja sintetis, 1 bulan absensi, 1 siklus payday penuh:
  - Hitung lembur vs aturan UU: **100% sesuai** (bisa ditunjukkan di demo: hitungan terbuka).
  - Payday: 2 jam manual → **5 menit** (approve 1-klik).
  - 20 slip digital terbit + terverifikasi QR.
  - 3 query pekerja terjawab otomatis (transparansi).
- Cerita dampak (untuk artikel): sengketa upah yang rutin, pekerja yang "tidak bisa tunjukkan penghasilan", BPJS informal yang rendah.

### Teknologi & integrasi OSS
- Hermes Agent: gateway WA, cron, memory (profil per pekerja: gaji, posisi, aturan), subagent (rekap paralel saat payday).
- Python (mesin upah & OT) + **Postgres** (ringkas) / SQLite + **Grafana** (dashboard kehadiran & biaya tenaga kerja — adegan video) + **WeasyPrint** (PDF slip) + QR (open standard).
- Jalan di VPS 4GB: Hermes + Postgres + Grafana = cukup (uji beban hari 1–2; drop Grafana jika perlu).
- **Tanpa OCR, tanpa data pihak ketiga, tanpa scraping** → paling aman dari risiko aturan kompetisi.

### Risiko & syarat khusus
- **Hukum ketenagakerjaan** (UU Ketenagakerjaan / Cipta Kerja, UMK tiap daerah): rule engine + **UMK di-set owner** + disclaimer *"cek UMK daerahmu"*; **approval owner wajib** sebelum rekap final — bukan "otomatis membayarkan".
- **UU PDP**: data pekerja (nama, absensi, gaji) sensitif → self-hosted di VPS sendiri, data minimal, consent saat onboarding, slip hanya terlihat oleh pemegangnya; demo 100% data sintetis.
- **Posisi etis**: TIDAK merekomendasikan "kurangi gaji" — agen justru **menghitung hak pekerja** (ini diferensiasi moral yang kuat di depan juri).
- Kanal WA: patuhi jalur gateway yang disediakan platform.
- Batas 5 hari: fitur QR & Grafana = *polish* (jika mepet, core = absensi → hitung → payday → slip sudah lebih dari cukup).

### Kelayakan 5 hari: **TINGGI** (paling aman dari 14 ide sejauh ini: semua internal, deterministik, tidak bergantung API pihak ketiga).

### Nilai jual
Rp50–150rb/bln per UMKM (tier per jumlah pekerja); free tier 10 pekerja (jalur adopsi cepat). B2B2C: bank/KUR (slip sebagai data partner), koperasi, dinas ketenagakerjaan. **TAM: 64 juta pekerja.**

### Kenapa juri suka
- **Onno:** proteksi pekerja + inklusi keuangan + open source + standar terbuka (QR slip) + community (format slip bisa di-open-source) = selaras DNA-nya (RT/RW-Net, open course, AI for Humanity).
- **Ogi:** TAM 64 juta, pricing jelas, ROI owner jelas (hemat 2 jam/payday + hindari salah hitung), 24/7 di VPS AI Hosting.
- **Eko:** mesin upah + rule engine hukum + multi-rol + approval flow = desain sistem nyata & jujur.

### Kenapa ini belum dipikirkan peserta lain
Semua yang masuk kategori Productivity akan membangun "alat bos" (kasir/PO/inventori/kos). **Alat yang melindungi pekerja + menjadikannya bankable** adalah ruang kosong — dan ceritanya membuat juri berdiri: *"ini AI yang bekerja untuk orang kecil."*

---

## 3. IDE ALTERNATIF DARI TOP ISSUE (ringkas)

### B. **AntiBoncos** — Personal CFO anti boncos (akar: pinjol/over-indebtedness, masalah #2)
Peta utang (screenshot statement/penawaran → Vision + RAG) → total beban & **efektif interest rate** per pinjaman → **cek legalitas** (bunga di atas ketentuan → flag + **draft pengaduan OJK**) → rencana bayar (metode avalanche) + cron reminder → draft surat negosiasi → "budget guard".
- Dampak: 10+ juta peminjam pinjol; penagihan ilegal = masalah sosial nasional.
- Ciri khas: "draf pengaduan OJK" + "deteksi bunga tidak wajar" — belum ada peserta yang berani.
- Risiko: **bukan nasihat keuangan** (positioning: edukasi + alat dokumen + simulasi); PII sangat berat (self-hosted, demo sintetis); tanpa API bank → user forward sendiri (posisi jujur).
- Nilai jual: freemium Rp20rb/bln; B2B2C fintech/bank (fitur financial health), lembaga perlindungan konsumen.
- Feasible 5 hari: SEDANG-TINGGI (butuh Vision LLM).

### C. **SewaSiaga** — Juru pelihara penyewa (akar: perumahan, masalah #3)
Untuk penyewa (sisi lemah): cek kesehatan kontrak sewa (playbook ala KontrakPintar) → checklist verifikai pemilik → cron H-90/H-60/H-30 perpanjangan + **draft surat renegosiasi** → eskalasi maintenance yang diabaikan → **checklist ke luar + tuntutan pengembalian deposit** (draft surat + bukti kronologis).
- Dampak: defisit perumahan ±12 juta unit; deposit "hilang" tiap tahun = pain universal penyewa kota.
- Ciri khas: **agen di sisi penyewa** (lawannya = pemilik/agen properti) — simetris dengan KostSiaga tapi melindungi yang lemah.
- Risiko: data pribadi ringan (aman); jangan klaim "mencari kos" (ToS platform listing) — fokus di dokumen & negosiasi; demo pakai kontrak sintetis.
- Nilai jual: pay-per-move Rp50rb/keperluan (momen pain) atau langganan; B2B: platform properti (fitur proteksi penyewa).
- Feasible 5 hari: TINGGI (mirip KontrakPintar + cron).

---

## 4. Perbandingan & Rekomendasi

| Ide | Masalah induk | Skala masalah | Bisnis (Ogi) | Teknis (Eko) | Dampak (Onno) | Unik | Feasible |
|-----|--------------|---------------|----|----|----|----|----|
| **GajiTepat** | Ekonomi informal | **64 jt pekerja** | 9 | 9 | 9.5 | 9.5 | 9.5 |
| **AntiBoncos** | Pinjol | 10 jt+ peminjam | 8 | 8.5 | 9 | 9 | 8 |
| **SewaSiaga** | Perumahan | 12 jt unit defisit | 7.5 | 8.5 | 8.5 | 8.5 | 9 |

**Rekomendasi: GajiTepat.**
Alasan juara: (1) akar masalah paling masif di Indonesia; (2) ruang kosong "sisi pekerja" yang belum disentuh semua peserta; (3) hook cerita yang membuat juri berdiri — *inklusi keuangan via slip gaji*; (4) teknis paling deterministik & aman untuk 5 hari di RAM 4GB; (5) triple-win 3 juri sekaligus.

**Taktik bonus (opsional):** di akhir artikel, sebutkan roadmap: *"GajiTepat → data slip terverifikasi → kemitraan KUR bank"* — menunjukkan skala dampak yang bisa dibayangkan (Ogi & Onno sangat menyukai "efek ekor" seperti ini).
