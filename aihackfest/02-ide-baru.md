# AI HackFest 2026 — 3 IDE BARU (Ronde 2)
**Untuk:** Afrizal Munthe · Batch 3 (11–15 Sep 2026) · Productivity & Personal AI · Hermes Agent

> Ide-ide ini **tidak tumpang tindih** dengan 10 ide di `01-10-ide-menang.md`.
> Kriteria yang sama dipakai: dampak nyata + teknologi terbaru + vibecoding-friendly + nilai jual + integrasi OSS + menarik 3 juri (Ogi: bisnis, Eko: teknis, Onno: open source & public good).

---

## IDE A — **KostSiaga**: "Satu nomer WhatsApp = satu kos terkendali" 🏠 (REKOMENDASI UTAMA RONDE 2)

### Pitch
Pemilik kos (10–50 kamar) hidup dari satu nomor WhatsApp yang kebanjiran: *"Bu, udah ingetin kamar 12 ya"*, *"AC kamar 7 bocor"*, *"Depositnya kapan balik?"*, *"Kamar mana yang kosong?"*. KostSiaga adalah **agen pengelola kos pribadi**:
1. **Penagihan otomatis & etis** — jadwal sewa per penyewa + cron pengingat H-3/H-1/H+1 (nada sopan, jam wajar, eskalasi maks 3×).
2. **Pencocokan transfer otomatis** — penyewa kirim screenshot transfer → **Vision LLM** cocokkan nominal+nama → konfirmasi 1-tap ke pemilik → status "lunas" tercatat.
3. **Triase maintenance** — *"AC bocor"* tercatat sebagai work order, diprioritaskan (kebakaran/kebocoran listrik = URGENT, langsung dibunyikan ke pemilik), status di-update sampai selesai, riwayat per kamar.
4. **Status kamar** — kosong/terisi/segero lepas; cron: *"Kamar 12 lepas bulan depan, mau saya draft info untuk list calon?"*
5. **Laporan akhir bulan** — rekap per penyewa (lunas/terlambat), arus kas, daftar work order belum selesai → PDF 1-klik.

### Ciri khas (yang tidak dimiliki peserta lain)
- **Multi-aktor**: satu agen melayani pemilik + N penyewa dengan "wajah" dan aturan berbeda per pihak — arsitektur multi-tenant mini di level agent (langka di hackathon).
- **Ledger yang mencocokkan bukti transfer sendiri** (Vision LLM) — bukan sekadar pengingat, tapi *reconciliation*.
- **Work order dengan prioritas keselamatan** — twist yang membuat demo terasa "hidup".

### Dampak nyata & metrik demo
- Pasar: hunian informal (kost) di kota besar Indonesia mencapai ratusan ribu unit (estimasi tidak resmi — carilah sumber/angka terbaru untuk artikel; Jakarta saja sering dikutip 300.000+ unit). Pendapatan pemilik kos bocor karena tagihan telat; penyewa kecewa karena complaint "hilang".
- Metrik (demo 20 kamar): 20 jadwal tagihan berjalan, 15 screenshot transfer dicocokkan (catat akurasinya), 5 work order datriase (termasuk 1 URGENT), 1 laporan bulanan: 2 jam manual → 30 detik.

### Teknologi & integrasi OSS
- Hermes Agent: gateway WhatsApp/Telegram, cron, memory, **subagent** (pencocokan transfer paralel).
- **Vision LLM** (cek model default; jika tidak support → API vision murah, biayamu).
- **Postgres** (ringkas) atau **SQLite** + **Grafana** (dashboard okupansi — adegan video yang bagus) + PDF (weasyprint).
- Opsional: **ERPNext** (punya modul property sungguhan — tapi berat untuk RAM 4GB; lebih ringan: custom + Grafana).

### Risiko & syarat khusus
- **UU PDP (penyewa):** nama+kamar+status bayar = data pribadi → self-hosted di VPS sendiri, data minimal, **jangan pernah memposting penyunggut secara publik** (aturan etik di sistem + disebut eksplisit di artikel = nilai plus).
- **Kesalahan matching transfer** → step konfirmasi wajib 1-tap; yang ambigu TIDAK tercatat otomatis.
- **RAM 4GB** → stack ringan: Hermes + SQLite/Postgres + Grafana; tes beban hari 1–2.
- **Kepatuhan kanal chat:** gunakan jalur gateway yang disediakan Hermes; di artikel sebutkan komitmen ToS.
- Consent penyewa saat onboarding (pemilik = data controller) → satu paragraf di artikel.

### Kelayakan 5 hari: **TINGGI** — tanpa OCR dokumen eksternal, tanpa sumber data pihak ketiga; semua data internal yang bisa kamu buat sendiri (20 kamar, 15 "penyewa" sintetis).

### Nilai jual
Rp50–100rb/bln per kos (ROI jelas: 1 kamar tagihan yang tertagih menutup biaya 1–2 bulan); B2B: operator kos/boarding chain; add-on masa depan: mini-app penyewa.

### Kenapa juri suka
- **Ogi:** business model & ROI terucap dalam 1 kalimat; pasar jelas.
- **Eko:** vision-matching + cron + work-order system = desain sistem nyata, bukan chatbot.
- **Onno:** 100% stack open source, sisi "fairness penyewa" (transparansi, anti-permalukan) = public good.

---

## IDE B — **Beasiswain**: "Agen pemburu beasiswa yang belajar dari penolakanmu" 🎓

### Pitch
Agen untuk mahasiswa/SMA yang **berburu beasiswa untukmu**:
1. **Radar panggilan resmi** — cron memantau pengumuman beasiswa dari sumber resmi (KIP-Kuliah, LPDP, Kemendikbud, beasiswa daerah, korporasi) — halaman resmi/pengumuman terbuka (ToS-safe); mode **hibrida jujur**: user bisa paste pengumuman mana pun, agen langsung memproses.
2. **Matching profil** — RAG atas transkrip, sertifikat, esai, kegiatan → *"Ini cocok untukmu: skor kamu X, syarat minimal Y"* + daftar kekurangan yang harus dilengkapi.
3. **Kalender aplikasi** — countdown cron per deadline + checklist dokumen per beasiswa.
4. **Draf dokumen** — DPA, letter of intent, daftar kegiatan — dalam gaya tulisanmu (style memory), finalisasi olehmu.
5. **Post-mortem penolakan** (twist-nya!) — setelah ditolak, agent mengompilasi umpan balik + pola kegagalan → *laporan "pelajaran"* untuk ronde berikutnya. **Learning loop yang manusiawi** — showcase fitur self-improvement Hermes dengan cara yang belum pernah ditunjukkan siapa pun.

### Dampak nyata & metrik
- Biaya pendidikan adalah penghalang nyata; banyak siswa **eligible tapi tidak mendaftar** karena gap informasi (KIP-Kuliah sendiri menjangkau ratusan ribu mahasiswa/tahun — verifikasi angka untuk artikel).
- Metrik demo: 20 panggilan aktif terpantau, 10 ter-match profil, 5 dokumen ter-draf, 100% deadline ter-prompt, 1 post-mortem contoh.

### Teknologi & integrasi OSS
- Hermes (cron, memory, **subagent paralel** untuk multi-sumber) + RAG (pgvector/Qdrant) + LLM drafting + PDF.
- **Paperless-ngx** (arsip dokumen aplikasi) + **BookStack** (knowledge base "tips per beasiswa" yang tumbuh) + Grafana (timeline aplikasi).

### Risiko & syarat khusus
- **ToS scraping** → hanya halaman pengumuman resmi/terbuka; mode hibrida (paste) sebagai jalur utama yang jujur; jangan klaim "auto-submit" ke portal pihak ketiga.
- **PDP:** transkrip & data ekonomi keluarga = sensitif → **demo 100% data sintetis** + narasi consent.
- Kualitas draf → selalu human-finalized; posisi "asisten, bukan jagoan".
- Musiman → demo pakai panggilan yang **sedang terbuka** saat periode batch (cek H-1 mulai).

### Kelayakan 5 hari: **SEDANG-TINGGI** (risiko: hunting sumber pengumuman yang benar-benar buka).

### Nilai jual
Freemium Rp10–20rb/bln (mahasiswa); uang beneran di **B2B2C**: career center kampus (BKK), SMK, bimbel — mereka beli untuk ribuan siswanya.

### Kenapa juri suka
- **Onno:** pendidikan + data terbuka + open source = jantungnya.
- **Ogi:** B2B ke institusi = pasar jelas.
- **Eko:** "post-mortem penolakan" = learning loop yang benar-benar dipakai, bukan gimmick.

---

## IDE C — **KontrakPintar**: "Sudah sehat kontrakmu?" — cek kesehatan kontrak pribadi 📄

### Pitch
Orang Indonesia menandatangani kontrak (sewa kamar/rumah, kerja, pinjaman, langganan) **tanpa membacanya**. KontrakPintar = "dokter kontrak" personal:
1. Foto/PDF kontrak → **OCR + ekstraksi klausa** (sewa, deposit, masa kontrak, penalti, pemutusan, pemeliharaan).
2. **Laporan "Cek Up" 3 warna** — Hijau/Yellow/Red per klausa: apa artinya dalam bahasa manusia + **kenapa** berisiko (mis. *"Deposit 3 bulan tapi klausul pengembalian tidak menyebut tenggat" → RED + saran negosiasi*).
3. **Coach negosiasi** — draft pertanyaan/balasan negosiasi sopan ke pemilik/HR.
4. **Radar tanggal kunci** — cron: H-60/H-30 sebelum perpanjangan sewa, akhir masa percobaan, jatuh tempo denda.
5. Arsip di **Paperless-ngx** + bisa ditanya kapan pun (*"Di kontrak apartemenku, siapa yang tanggung biaya servis AC?"*).

### Ciri khas
- Metafora **medis** (report card hijau/kuning/merah) — instant understandable, bagus untuk video.
- Bukan sekadar analisis: **menghasilkan tawa-nego** (draft negosiasi) → aksi nyata.
- 100% domain "Personal AI" — paling pas dengan kategori.

### Dampak nyata & metrik
- Sengketa deposit/pemeliharaan sewa & ketidaktahuan klausul kerja adalah pain umum. Metrik demo: 20 kontrak dianalisis, X red flag terdeteksi (idealnya **divalidasi 1–2 pengacara** → kredibilitas niscaya di artikel), waktu paham kontrak: ±1 jam → 30 detik, 5 tanggal kunci terjadwal.

### Teknologi & integrasi OSS
- **PaddleOCR/Tesseract** + LLM ekstraksi + **RAG "playbook" per jenis kontrak** (sewa/kerja/utang — playbook-nya bisa kamu tulis sendiri dari aturan umum → konten unik yang bisa di-open-source-kan) + cron + PDF report.
- **Paperless-ngx** + LibreOffice.

### Risiko & syarat khusus
- **Bukan nasihat hukum** → disclaimer tegas + positioning "literasi hukum" (edukasi), bukan legal service. Ini justru narasi yang disukai Onno (literasi = public good).
- Kesalahan model di teks hukum (high-stakes) → selalu sertakan "verifikasi ke profesional untuk keputusan besar"; red flag diberi penjelasan alasannya (transparan, bukan black-box).
- Kerahasiaan kontrak → self-hosted, enkripsi at-rest; **demo pakai kontrak sintetis** (kamu bikin 5 kontrak sewa contoh dengan red flag yang ditanam = konten demo yang sangat bagus & 100% aman).

### Kelayakan 5 hari: **SEDANG-TINGGI**.

### Nilai jual
Pay-per-use Rp15–30rb/analisis (orang bayar di momen pain) atau langganan; B2B: platform sewa, HR, lembaga keuangan mikro (fitur edukasi).

### Kenapa juri suka
- **Eko:** pipeline OCR + ekstraksi terstruktur + RAG playbook = solid.
- **Ogi:** pay-per-use di momen pain = model bisnis yang rapi.
- **Onno:** literasi hukum terbuka + playbook open source = public good yang konkret.

---

## Perbandingan Ronde 2 (dan vs ronde 1)

| Ide | Bisnis (Ogi) | Teknis (Eko) | Dampak (Onno) | Unik | Feasible 5 hari |
|-----|----|----|----|----|----|
| **KostSiaga** (A) | 9.5 | 9 | 8.5 | 9 | 9 |
| **Beasiswain** (B) | 8 | 8.5 | 9.5 | 9 | 8 |
| **KontrakPintar** (C) | 8.5 | 9 | 8.5 | 9.5 | 8.5 |
| *(banding)* KasPintar | 9 | 8.5 | 9 | 8.5 | 8.5 |
| *(banding)* Klienin | 9.5 | 9.5 | 8 | 8 | 8 |

**Rekomendasi:**
- **KostSiaga** = pilihan paling seimbang (bisnis + teknis + feasible), dan demonya paling "menyala" karena multi-aktor (pemilik + beberapa penyewa berinteraksi dengan agen yang sama).
- **Beasiswain** = pilihan paling emosional & edukatif (kalau kamu ingin cerita yang bikin juri merinding).
- **KontrakPintar** = pilihan paling "personal AI murni" & paling aman secara data (demo 100% sintetis).
