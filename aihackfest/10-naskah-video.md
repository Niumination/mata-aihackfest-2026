# NASKAH VIDEO DEMO v3 — MATA (LIVE, 5–10 menit)
**AI HackFest 2026 · Batch 3 · target durasi ±8 menit · 16:9 · 1080p**
> **v3 = SELURUHNYA DATA RIIL PRODUKSI** (ganti naskah demo: 48/5/238%/Bebesen Abadi LUPA, tidak boleh muncul).
> Aset: `assets/watermark_idwebhost.png` (corner, detik 0) & `assets/lowerthird_aihosting.png` (lower-third).
> **Upload paling telat 15 Sep 2026 SEBELUM 23.59 WIB (HARD — VM mati) · status YouTube: PUBLIK (form eksplisit "tidak private").**

Angka resmi utk VO (sudah diverifikasi 14 Sep — SELARAS dgn artikel & dashboard):
662 paket TA2026 (Rp 134,5 M) · 599 paket TA2025 · 8.079 baris RUP (Rp 505,4 M) · realisasi 26,6% ·
14 indikasi (3 tinggi) · 170 penyedia · konsentrasi top-10 = 41,6% · D2: 8,4% & 7,5% ·
D4: Rp 229 jt → Rp 3,12 M (13×) · D6: Rp 94,35 jt & Rp 193,4 jt identik di 3 proyek · CSV 1.250 paket.

---

## A. CHECKLIST KEWAJIBAN (satu-satu, jangan bolong)
- [ ] Durasi 5–10 menit · landscape 16:9 · ≥1080p
- [ ] Proses agent **end-to-end** terlihat (bukan slide-only)
- [ ] ≥1 adegan **environment VPS AI Hosting**: terminal (hostname hermes + spec) **DAN** dashboard (→ S6)
- [ ] Sebut **"AI Hosting IDwebhost"** ≥1× — **verbal di S6** + lower-third (pengaman ganda) + pengucapan ulang di S9
- [ ] **Watermark logo IDwebhost** di corner sejak detik 0
- [ ] Upload YouTube — **PUBLIK** (bukan unlisted/private — form eksplisit "tidak private")
- [ ] Tanpa musik berhak cipta (naskah didesain tanpa musik; kalau mau, royalty-free YouTube Audio Library)
- [ ] Tidak ada footage orang/pihak lain
- [ ] **Tidak ada angka demo** (48, 5 indikasi, 238%, "Bebesen Abadi", "999.999.999") — cek ulang akhir-akhir

## B. SETUP REKAMAN (30 menit sebelum rekam)
1. **OBS** (atau serupa): canvas 1920×1080, 30fps, MP4 (H.264) bitrate ≥ 8000 kbps.
2. **Terminal 1 (protagonis)**: font besar (28–32), tema gelap. Prompt menampilkan hostname VPS (`ubuntu24-hermes-…` — mengandung "hermes", bukti instance AI Hosting).
   ```bash
   ssh -p <PORT-SSH> root@<IP-VPS>
   cd /root/Arck4li-AIHackfest/mata && . .venv/bin/activate
   ```
3. **Terminal 2 (latar, opsional)**: `journalctl -u mata -f` — service 24/7 "bernafas".
4. **Browser**: tab 1 = dashboard **https://mata.niumination.web.id** (domain publik — tidak perlu tunnel) · tab 2 = dossier PDF terbaru (`/opt/mata/output/dossier_*.pdf` via `curl -O` ke laptop, atau tunjukkan path di terminal) · tab 3 = artikel LinkedIn (untuk S9).
5. **Kondisi awal bersih** (biar artefak "terlahir" di depan kamera):
   ```bash
   rm -f output/dossier_*.pdf output/laporan_*.txt output/ringkasan_*.md
   ls -la output/
   ```
6. Uji satu siklus **sebelum** kamera: `python3 run.py cycle` → pastikan keluaran 14 indikasi (3 tinggi) & PDF lahir.
7. Siapkan 1 pertanyaan utk Tanya MATA (S7), contoh: "Berapa indikasi level tinggi saat ini, dan dari aturan mana saja?"

## C. NASKAH PER ADEGAN (LIVE)
> VO = voiceover (natural). [TEKS] = teks di layar. Total ≈ 8:00.

### S0 — HOOK (0:00–0:40) · layar gelap, angka muncul satu-satu
[TEKS berurutan]:
- "Pengadaan pemerintah: **triliunan rupiah** per tahun."
- "Pengawasan BPKP (2023): ketidakefisienan perencanaan & anggaran pemda > **Rp141 triliun**."
- "BPK (IHPS I 2023): **15.689 masalah** pengelolaan keuangan — **Rp18,19 triliun**."
- "KPK (Des 2025): proyek kereta DJKA Medan — 'pemenang sudah dikondisikan', HPS bocor."
- "Datanya? **Sudah dibuka untuk publik.**"
- (jeda 1 dtk) — "**Tapi tidak ada yang membacanya untuk rakyat.**"

**VO:** *"Setiap tahun, negara mengeluarkan triliunan rupiah lewat pengadaan barang dan jasa. Pemerintah sudah membuka datanya untuk publik. Masalahnya bukan data tidak ada — masalahnya: tidak ada yang membacanya secara sistematis, untuk kita. Ini MATA — yang membacanya. Dua puluh empat jam, tanpa lelah."*
[TEKS besar]: **MATA — Watchdog Akuntabilitas Pengadaan**

### S1 — APA INI (0:40–1:20) · dashboard https://mata.niumination.web.id (slow zoom hero)
Tampilkan: badge **MODE: LIVE**, headline "Uang itu uangmu. MATA membacanya.", tile **662 pengumuman · 14 indikasi**, ticker indikasi berjalan.
**VO:** *"MATA adalah AI agent yang berjalan 24/7 di VPS. Ia membaca data pengadaan publik Kabupaten Aceh Tengah — enam ratus enam puluh dua paket realisasi tahun dua ribu dua puluh enam, nama penyedia, nilai, sampai rencana RUP-nya. Lalu menjalankan aturan deteksi yang transparan dan bisa diaudit. Bukan black-box: setiap rumus dan ambangnya bisa kamu baca di repositori. Dan hasilnya bukan vonis — tapi indikasi, lengkap dengan bukti dan angkanya."*
[TEKS]: "Data publik · Aturan transparan · Indikasi, bukan vonis"

### S2 — DEMO: SATU SIKLUS HIDUP (1:20–2:30) · Terminal 1, **satu take**
Jalankan di depan kamera:
```bash
python3 run.py cycle
```
Biarkan [1/5]…[5/5] selesai utuh (±30–60 dtk) — jangan potong. Tutup dengan:
```bash
ls -la output/ | head
```
→ dossier PDF + draft laporan APIP "terlahir" di depan kamera.
**VO:** *"Coba kita jalankan satu siklus. MATA mengumpulkan data dari sumber publik, menjalankannya lewat rule engine, dan — lihat — siklus selesai. Empat belas indikasi tersimpan, tiga di antaranya level tinggi. Dan lihat di folder output: dossier PDF dan draft laporan resmi ke APIP baru saja lahir, di depan mata kita. Semuanya dari data yang sudah bisa diakses siapa pun — hanya tidak pernah dibaca secara sistematis."*
[TEKS kecil]: `run.py cycle → 14 indikasi (3 tinggi) · dossier + draft APIP`

### S3 — INDIKASI ANDALAN: "VENDOR KECIL, KONTRAK JUMBO" (2:30–3:20) · dashboard, kartu flag D4
Scroll ke seksi **Indikasi**, buka kartu **[D4] TINGGI** (ter-buka: bukti numerik).
**VO:** *"Ini indikasi yang paling gampang dijelaskan. Satu penyedia dengan riwayat hanya satu proyek — dua ratus sembilan juta rupiah — memenangkan kontrak tiga koma dua miliar rupiah. Kesenjangan tiga belas kali lipat antara rekam jejak dan nilai kontrak. MATA menandainya, menyimpan ID record-nya, dan menulis langkah lanjutnya: verifikasi kualifikasi. Ini bukan tuduhan — ini sinyal yang bisa kamu telusuri sendiri."*
[TEKS]: `riwayat 1 proyek Rp 229 jt → kontrak Rp 3,12 M (13×) · record ID terekam`

### S4 — KONSENTRASI: "SATU NAMA, BANYAK NILAI" (3:20–4:10) · dashboard, D2 + panel konsentrasi
Tampilkan kartu [D2] TINGGI + bar konsentrasi (8,4% / 7,5%).
**VO:** *"Yang kedua lebih halus. Dua penyedia masing-masing menyerap delapan koma empat dan tujuh koma lima persen dari SELURUH nilai pengadaan kabupaten — dari hanya tiga paket. Dan kalau dijumlah, sepuluh penyedia teratas memegang empat puluh satu koma enam persen nilai. Dalam pengadaan yang sehat — terbuka, transparan, kompetitif — tidak seharusnya segini terkonsentrasi. Aturan D2: ambang lima persen, atau lima belas paket dalam setahun. Rumusnya ada di config, silakan diubah, silakan di-audit."*
[TEKS]: `D2: share ≥5% atau ≥15 paket/tahun · top-10 = 41,6% nilai`

### S5 — RENCANA vs REALISASI (4:10–5:00) · dashboard, panel "RENCANA (RUP) vs REALISASI PER SKPD"
Scroll baris **Keseluruhan**: rencana Rp 505,4 M · realisasi Rp 134,5 M · **tercapai 26,6%**; tunjukkan 1–2 baris ekstrem (Dinas Perumahan ±70% vs kecamatan 0%).
**VO:** *"Lalu yang paling penting untuk rakyat: dari rencana lima ratus lima miliar rupiah, yang terekalisasi seratus tiga puluh empat miliar — dua puluh enam koma enam persen, wajar untuk tahun berjalan. Tapi perinciannya beda jauh antar dinas: ada yang hampir tujuh puluh persen, ada yang nol persen. MATA memetakannya per satker, per dinas, sampai kecamatan — bukan satu angka kabur."*
[TEKS]: `RUP Rp 505,4 M → realisasi Rp 134,5 M (26,6%) · per 55 SKPD`

### S6 — PANGGUNG: 24/7 DI AI HOSTING (5:00–6:10) · **ADEGAN WAJIB** — 3 shot cepat
1. **Terminal: identitas VPS** (10 dtk):
   ```bash
   hostname && nproc && free -h | head -2 && df -h / | tail -1
   ```
   → hostname `…-hermes-…` (instance AI Hosting) + 4 core + 4GB + 20GB.
2. **Terminal: service 24/7** (20 dtk):
   ```bash
   systemctl status mata
   journalctl -u mata -n 10
   ```
   → `active (running)` + log siklus; kalau baris **auto-restart** terlihat, biarkan — itu bukti keandalan.
3. **Dashboard** (15 dtk): badge MODE: LIVE + "Siklus terakhir" (bukti loop berjalan) + status kesehatan.

**VO:** *"Dan ini panggungnya. MATA berjalan dua puluh empat jam nonstop di AI Hosting IDwebhost — VPS Hermes: empat core, empat gigabyte, dua puluh gigabyte SSD — dan lihat hostname-nya, ini instance AI Hosting yang disediakan panitia. Bukan laptop yang matinya tergantung tidurku. Ini service: kalau mati, dia restart sendiri. Kalau sumber data bermasalah, dia melapor jujur — 'monitor offline, coba lagi' — bukan pura-pura bekerja. Keandalan yang jujur."*
→ **Tempel lower-third `assets/lowerthird_aihosting.png` di adegan ini** (syarat sebut nama: verbal + lower-third + ulang di S9).
> Catatan: panel CloudBaik tidak tersedia untuk VPS kompetisi (terkonfirmasi) — shot 1–3 sudah memenuhi syarat "environment VPS AI Hosting (dashboard & terminal)".

### S7 — BISA DITANYA: TANYA MATA (6:10–6:50) · dashboard, panel chat
Ketik di depan kamera: *"Berapa indikasi level tinggi saat ini, dan dari aturan mana saja?"*
Tunggu jawaban (dari data, bukan basa-basi; ≤5 kalimat, tone tenang).
**VO:** *"MATA tidak diam di balik dashboard. Kamu bisa bertanya langsung — dan dia menjawab dari data yang ia pegang: aturan apa, ambang berapa, record mana. Chatbot-nya dijaga: terisolasi, tercatat, dan dibatasi lima pertanyaan per jam per pengunjung. Jawaban bisa salah, tapi jejaknya selalu ada."*
[TEKS]: `Tanya MATA · hanya menjawab dari data · rate-limit 5/jam`

### S8 — ETIKA (6:50–7:20) · kartu teks (satu per satu)
1. "Hanya data **publik** — setiap klaim punya tautan sumber."
2. "**Indikasi, bukan vonis.** Tidak ada yang divonis satu aplikasi."
3. "**Human-in-the-loop** — MATA menyiapkan, manusia yang mengirim."
4. "Pelaporan via **kanal resmi**: LAPOR!, Ombudsman, KPK, APIP/BPKP."

**VO:** *"Ada satu hal yang lebih penting daripada fitur: batas. MATA hanya membaca data publik. Ia menyebut 'indikasi', bukan 'bersalah'. Dan ia tidak pernah mengirim apa pun tanpa manusia yang memutuskan. Akuntabilitas publik tidak boleh berubah jadi alat menghakimi."*

### S9 — PENUTUP (7:20–8:00) · layar gelap
[TEKS]: *"Semoga tidak pernah dipuji. Semoga cukup diawasi."*
**VO:** *"Seluruh kodenya terbuka, dashboardnya publik, dan setiap angka bisa ditelusuri sampai record ID-nya. MATA — dibangun dengan AI Hosting IDwebhost, di AI HackFest dua ribu dua puluh enam. Semoga ia tidak pernah dipuji — karena artinya tidak ada yang perlu diawasi. Semoga cukup… diawasi."*
[TEKS akhir]: `MATA · mata.niumination.web.id · github.com/niumination/mata-aihackfest-2026 · AI HackFest 2026`

---

## D. RUN-OF-SHOW HARI REKAM (±45 menit)
1. Boot VPS, cek `systemctl is-active mata` (aktif).
2. `rm -f output/dossier_*.pdf output/laporan_*.txt output/ringkasan_*.md` (biar artefak lahir di depan kamera).
3. Tes suara (rekam 10 dtk) → cek volume & gaung.
4. **Rekam satu take panjang** S0–S9 (±10–12 mnt mentah → cut jadi 8 mnt).
   - S2–S5: **jangan** percepat terminal; biarkan jeda — juri suka proses, bukan keajaiban.
   - Salah ketik = manusiawi; ulangi tenang atau cut ke take kedua.
5. B-roll 20 dtk: `journalctl -u mata -f` yang "bernafas"; kursor di dashboard.
6. Watermark corner sejak detik 0.
7. Review mentah → cut per adegan → export 1080p.
8. **QC akhir (wajib)**: cari "238", "48 pengumuman", "5 indikasi", "Bebesen" di final — harus 0.

## E. PLAN B (kalau live macet)
- `run.py cycle` gagal (sumber down) → `python3 run.py demo` (skenario ter-orchestrate, deterministik) — VO S2 tetap valid, TAPI sebut "mode demonstrasi" di layar.
- Domain lemot/tak bisa diakses → buka `http://127.0.0.1:8080` di VPS via SSH tunnel (`ssh -L 8080:localhost:8080 …`).
- Tanya MATA lambat/gagal → tunjukkan screenshot percakapan + VO — tetap sah.
- Panel CloudBaik tak tersedia (terkonfirmasi) → shot S6 sudah memenuhi syarat.

## F. UPLOAD & PUBLIKASI (≤ 15 Sep 23:59 WIB)
- **YouTube PUBLIK** (bukan unlisted/private). Judul opsi:
  1. "MATA — AI Agent yang Membaca Data Pengadaan Triliunan, 24/7"
  2. "Rp141 Triliun Tersimpan di Data Publik. MATA Membacanya untuk Kita."
- Deskripsi:
  ```
  MATA — Watchdog Akuntabilitas Pengadaan. AI agent (Hermes) 24/7 di VPS AI Hosting IDwebhost
  yang membaca data pengadaan publik Kabupaten Aceh Tengah — 662 paket realisasi TA2026,
  8.079 baris RUP — mendeteksi 14 indikasi anomali dengan aturan transparan (bukan black-box),
  dan menyusun dossier + draft laporan resmi ke APIP. Indikasi, bukan vonis.

  Dashboard: https://mata.niumination.web.id
  Kode (open source): https://github.com/niumination/mata-aihackfest-2026
  Artikel: https://www.linkedin.com/pulse/triliunan-rupiah-sudah-dibuka-tapi-tidak-ada-yang-membacanya-kali-0v7xc

  Dibangun dengan AI Hosting IDwebhost × Cloud VPS CloudBaik — AI HackFest 2026, Batch 3.
  #AIHackFest2026 #AIHosting #CloudVPS #AIAgent #TransparansiPBJ
  ```
- Thumbnail: `aihackfest/22-thumbnail-youtube.png` (1280×720, brand MATA).
- Simpan URL YouTube → isi form submit.
- **TikTok/IG Reels (opsional, 60–90 dtk):** S0 hook + potongan S2 + S3 + S9.

## G. BOBOT JURI vs ADEGAN (pengingat)
| Bobot | Ditutup oleh |
|-------|--------------|
| Efektivitas 30% | S2–S5: siklus nyata, PDF lahir di depan kamera, 4 jenis output |
| Teknis 20% | S6 (24/7, journalctl, "keandalan jujur") + S4 (rumus/ambang dipajang) |
| Relevansi 20% | S0 (angka BPKP/BPK/KPK) + S5 (rencana vs realisasi utk rakyat) |
| Kreativitas 15% | Konsep "data jadi tindakan" + S7 (agen yang bisa ditanya & ter-jaga) |
| Storytelling 15% | VO S0–S9 + penutup "semoga cukup diawasi" |
