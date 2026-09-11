# NASKAH VIDEO DEMO — MATA (5–10 menit)
**AI HackFest 2026 · target durasi: ±8 menit · 16:9 · 1080p**
Aset siap pakai di workspace: **`assets/watermark_idwebhost.png`** (corner) & **`assets/lowerthird_aihosting.png`** (lower-third "AI Hosting IDwebhost × Cloud VPS CloudBaik 24/7").

---

## A. CHECKLIST KEWAJIBAN (satu-satu, jangan bolong)
- [ ] Durasi 5–10 menit · landscape 16:9 · ≥1080p
- [ ] Proses agent **end-to-end** terlihat (bukan slide-only)
- [ ] ≥1 adegan **environment VPS AI Hosting**: dashboard panel CloudBaik/IDwebhost **DAN** terminal (→ S6, sudah disusun)
- [ ] Sebut **"AI Hosting IDwebhost"** ≥1× — **verbal di S6** + lower-third (pengaman ganda)
- [ ] **Watermark logo IDwebhost** di corner (aset sudah jadi) — tempel dari detik 0
- [ ] Upload **YouTube/TikTok/IG Reels — publik atau unlisted** (bukan private)
- [ ] **Tanpa musik berhak cipta** — naskah ini didesain tanpa musik (hanya suara + terminal); kalau mau musik, pakai royalty-free (YouTube Audio Library)
- [ ] Tidak ada footage orang/pihak lain

## B. SETUP REKAMAN (30 menit sebelum rekam)
1. **OBS** (atau serupa): canvas 1920×1080, 30fps, output MP4 (H.264) bitrate ≥ 8000 kbps.
2. **Terminal 1 (protagonis)**: font besar (28–32), tema gelap. Prompt menampilkan hostname VPS (`ubuntu24-hermes-6f8c0444` — mengandung "hermes", bukti instance AI Hosting).
   ```bash
   ssh -p <PORT-SSH> root@<IP-VPS>      # isi nilai dari email panitia
   cd /root/Arck4li-AIHackfest/mata && . .venv/bin/activate
   ```
3. **Terminal 2 (latar, opsional)**: `journalctl -u mata -f` — menunjukkan service 24/7 "napas".
4. **Browser**: buka dashboard `http://127.0.0.1:8080` (lewat SSH tunnel `ssh -L 8080:localhost:8080 -p <PORT-SSH> root@<IP-VPS>` bila port luar belum dibuka) + tab dossier PDF (`output/dossier_*.pdf`).
5. **Hermes**: buka sesi chat (TUI/gateway) di satu window.
6. Kondisi awal bersih: `rm -f output/dossier_*.pdf` (biar PDF "terlahir" di depan kamera) + pastikan `/etc/cron.d/mata` berisi 2 baris yang benar (sudah diperbaiki Hari-1 — jangan dihapus).
7. Screenshot/layar siap: hasil `run.py probe` (untuk S6/opsi live).

## C. NASKAH PER ADEGAN
> VO = voiceover (baca natural, jangan kaku). [TEKS] = teks di layar. Durasi total ≈ 8:00.

### S0 — HOOK (0:00–0:40) · layar gelap, angka muncul satu-satu
[TEKS berurutan]:
- "Pengadaan pemerintah: **triliunan rupiah** per tahun."
- "BPKP: modus manipulasi penganggaran & pengadaan = **Rp141 triliun**."
- "KPK (Des 2025): 'pemenang sudah dikondisikan' — HPS bocor, fee 15–20%."
- "Datanya? **Sudah dibuka untuk publik.**"
- (jeda 1 dtk) — "**Tapi tidak ada yang membacanya untuk rakyat.**"

**VO:** *"Setiap tahun, negara mengeluarkan triliunan rupiah lewat pengadaan. Dan pemerintah sudah membuka datanya untuk publik. Masalahnya bukan data tidak ada. Masalahnya: tidak ada yang membacanya untuk kita. Ini MATA — yang membacanya, 24 jam, tanpa lelah."*
[TEKS besar]: **MATA — Watchdog Akuntabilitas Pengadaan**

### S1 — APA INI (0:40–1:20) · dashboard :8080 muncul (slow zoom)
**VO:** *"MATA adalah AI agent yang berjalan 24/7 di VPS. Ia memantau data pengadaan publik — pengumuman LPSE, e-katalog, e-kontrak — lalu menjalankan aturan deteksi yang **transparan dan bisa diaudit**. Bukan black-box: setiap rumus dan ambangnya bisa kamu baca. Hasilnya bukan vonis — tapi **indikasi, lengkap dengan bukti dan angkanya**."*
[TEKS]: "Data publik · Aturan transparan · Indikasi, bukan vonis"

### S2 — DEMO: PINDAI & DETEKSI (1:20–2:30) · Terminal 1, **satu take**
Jalankan (di depan kamera):
```bash
python3 run.py cycle
```
Biarkan 5 baris `[1/5]...[5/5]` selesai. Jangan potong di tengah — biarkan "hidup".
**VO:** *"Coba kita jalankan satu siklus. MATA mengumpulkan data, menjalankannya lewat rule engine, dan — lihat — lima indikasi terdeteksi. Dua di antaranya tingkat tinggi. Semuanya dari data yang **sudah bisa diakses siapa pun** — hanya tidak pernah dibaca secara sistematis."*
[TEKS kecil di bawah]: `48 pengumuman → 5 indikasi · rule engine transparan`

### S3 — INDIKASI 1: "HARGA DI PASAR" (2:30–3:20) · zoom baris D1
Zoom ke baris D1 (atau `python3 run.py analyze | head` kalau mau lebih tenang).
**VO:** *"Indikasi pertama: sebuah proyek rehabilitasi jalan senilai 2,7 miliar. Harga referensinya dari katalog: 800 juta. Deviasinya: **238 persen** — dan ini bukan tebakan: rumusnya (nilai minus referensi) dibagi referensi, dengan ambang 30 persen yang bisa kamu ubah di config. Setiap angkanya punya ID record dan tautan sumbernya."*
[TEKS]: `Rp2,7 M vs referensi Rp800 jt → +238% · rumus & ambang dipublikasikan`

### S4 — INDIKASI 2: "SATU VENDOR, BANYAK KONTRAK" (3:20–4:10) · terminal + dashboard vendor
Pindah ke tab dashboard :8080, bagian "Konsentrasi penyedia".
**VO:** *"Indikasi kedua lebih visual. Satu penyedia — PT Bebesen Abadi — memenangkan 10 dari 48 proyek, dengan porsi nilai lebih dari seperempat total pengadaan. Dalam pengadaan yang sehat, tidak seharusnya ada satu nama yang sedominan itu. Prinsipnya sederhana: terbuka, transparan, **kompetitif**."*
[TEKS]: `1 vendor = 10/48 proyek · ≥10 proyek & ≥25% nilai = flag`

### S5 — OUTPUT DUNIA NYATA: DOSSIER (4:10–5:10) · buka PDF, scroll perlahan
Buka `output/dossier_*.pdf` (yang barusan lahir di S2), scroll: halaman indikasi → lampiran.
**VO:** *"Yang MATA buat bukan sekadar notifikasi. Ini dossier: per indikasi ada buktinya, kalkulasinya, penjelasan, dan langkah lanjutnya. Dan ini — draft laporan resmi ke APIP. Perhatikan: MATA **menyiapkan**, tapi **kamu** yang memutuskan dan mengirim. Tidak ada yang auto-kirim ke siapa pun. Karena akuntabilitas yang serius berjalan lewat **kanal resmi** — bukan vonis dari satu aplikasi."*
[TEKS]: `Dossier PDF · Draft laporan APIP · Human-in-the-loop`

### S6 — PANGGUNG: 24/7 DI AI HOSTING (5:10–6:20) · **ADEGAN WAJIB** — 3 shot cepat
1. **Terminal: identitas VPS** (10 dtk):
   ```bash
   hostname && nproc && free -h | head -2 && df -h / | tail -1
   ```
   → hostname terbaca `...-hermes-...` (VPS AI Hosting) + 4 core + 4GB + 20GB.
2. **Terminal: service 24/7** (20 dtk):
   ```bash
   systemctl status mata
   journalctl -u mata -n 10
   ```
   → baris `active (running)` + log siklus; kalau baris **auto-restart** terlihat, biarkan — itu bukti keandalan.
3. **Dashboard :8080** (15 dtk): badge "MONITOR ONLINE" + grafik nilai per bulan (Desember merah).

**VO:** *"Dan ini panggungnya. MATA berjalan 24 jam nonstop di **AI Hosting IDwebhost** — VPS Hermes: empat core, empat gigabyte, dua puluh gigabyte SSD, dan lihat di hostname-nya — ini instance AI Hosting yang disediakan panitia. Bukan laptop yang matinya tergantung tidurku. Ini service: kalau mati, dia restart sendiri — baris itu barusan terjadi di depan kalian. Kalau data sumber bermasalah, dia melapor jujur — 'monitor offline, coba lagi satu menit lagi' — bukan pura-pura bekerja. Keandalan yang jujur."*
→ **Tempel lower-third `assets/lowerthird_aihosting.png` di adegan ini** (syarat sebut nama terpenuhi 2×: verbal + lower-third).
> Catatan: panel CloudBaik tidak tersedia untuk VPS kompetisi (terkonfirmasi via email admin) — shot 1 (hostname+spec) + terminal + dashboard :8080 sudah memenuhi syarat "environment VPS AI Hosting (dashboard & terminal)". Bila panel tiba-tiba tersedia, tambahkan 5 detik B-roll.

### S7 — HERMES: AGEN YANG BISA DITANYAI (6:20–7:00) · chat Hermes
Ketik ke Hermes di depan kamera: *"Bagaimana kondisi MATA hari ini?"*
Tunggu jawabannya (dengan angka + penutup etika). Kalau sempat, tunjukkan juga screenshot cron 07.00.
**VO:** *"Karena MATA dibangun di atas Hermes Agent, ia tidak diam di balik dashboard. Kamu bisa bertanya langsung: 'Bagaimana kondisi hari ini?' — dan dia menjawab dengan angka, bukan basa-basi. Tiap pagi jam tujuh, dia mengirim ringkasan harian sendiri: berapa yang dipindai, apa yang baru terdeteksi, apa yang berubah."*
[TEKS]: `Hermes Agent · cron 07.00 · ringkasan harian otomatis`

### S8 — ETIKA (7:00–7:30) · kartu teks (satu per satu)
[TEKS berurutan]:
1. "Hanya data **publik** — setiap klaim punya tautan sumber."
2. "**Indikasi, bukan vonis.** Tidak ada yang divonis satu aplikasi."
3. "**Human-in-the-loop** — MATA menyiapkan, manusia yang mengirim."
4. "Pelaporan via **kanal resmi**: LAPOR!, Ombudsman, KPK, APIP/BPKP."

**VO:** *"Ada satu hal yang lebih penting daripada fitur: batas. MATA hanya membaca data publik. Ia menyebut 'indikasi', bukan 'bersalah'. Dan ia tidak pernah mengirim apa pun tanpa manusia yang memutuskan. Akuntabilitas publik tidak boleh berubah jadi alat menghakimi."*

### S9 — PENUTUP (7:30–8:00) · layar gelap
[TEKS]: *"Semoga tidak pernah dipuji. Semoga cukup diawasi."*
**VO:** *"MATA — AI agent yang mengawasi agar uang kita diawasi. Dibangun dengan AI Hosting IDwebhost di AI HackFest 2026. Semoga ia tidak pernah dipuji — karena artinya tidak ada yang perlu diawasi. Semoga cukup... diawasi."*
[TEKS akhir]: `MATA · AI HackFest 2026 · Productivity & Personal AI · Hermes Agent`

---

## D. RUN-OF-SHOW HARI REKAM (±45 menit)
1. Boot VPS, cek `systemctl is-active mata mata-web` (aktif keduanya).
2. `rm -f output/dossier_*.pdf`; pastikan dashboard :8080 & panel CloudBaik & Hermes siap di tab.
3. Tes suara (rekam 10 dtk) → cek volume & gaung.
4. **Rekam satu take panjang** S0–S9 (±10–12 menit mentah; dipotong jadi 8 menit).
   - Tips: di S2–S4, **jangan** mempercepat terminal; biarkan jeda — juri suka melihat proses, bukan keajaiban.
   - Kalau salah ketik: jangan panik, ketik lagi — kesalahan kecil justru manusiawi (atau cut ke take kedua).
5. Rekam **B-roll 20 dtk** (untuk cut): `journalctl -u mata -f` yang "bernapas"; kursor di panel VPS.
6. Pasang **watermark** di corner sejak detik 0 (aset sudah ada).
7. Review mentah → cut per adegan → export 1080p.

## E. PLAN B (kalau live macet)
- `run.py cycle` gagal → jalankan `python3 run.py demo` (skenario ter-orchestrate, deterministik) — narasi S2–S5 tetap valid.
- Dashboard :8080 tak bisa diakses → tunjukkan lewat SSH tunnel (`ssh -L 8080:localhost:8080 ...`) dari browser lokal.
- Hermes lambat/tak bisa jawab (token AI belum masuk) → pakai **screenshot percakapan** + VO ("ini jawaban MATA saat ditanya...") — tetap sah; selesaikan token sebelum 15 Sep.
- Panel CloudBaik tidak tersedia (terkonfirmasi) → shot 1 S6 (`hostname/nproc/free/df`) + terminal + dashboard :8080 sudah memenuhi syarat "environment VPS (dashboard & terminal)".

## F. UPLOAD & PUBLIKASI
- **YouTube** (utama): judul opsional:
  1. "MATA — AI Agent yang Membaca Data Pengadaan Triliunan, 24/7"
  2. "Rp141 Triliun Tersimpan di Data Publik. MATA Membacanya untuk Kita."
- Deskripsi (template):
  ```
  MATA — Watchdog Akuntabilitas Pengadaan. AI agent (Hermes) 24/7 di VPS
  yang memantau data pengadaan publik (LPSE, e-Katalog, e-Kontrak),
  mendeteksi indikasi anomali dengan aturan transparan, dan menyusun
  dossier + draft laporan ke kanal resmi. Indikasi, bukan vonis.
  Dibangun dengan AI Hosting IDwebhost × Cloud VPS CloudBaik — AI HackFest 2026.
  #AIIHackFest2026 #AIHosting #CloudVPS #AIAgent
  ```
- **Status: publik atau unlisted** (bukan private) + simpan tautan untuk form submit.
- **TikTok/IG Reels** (opsional, 60–90 dtk): potong S0 (hook) + potongan S2 + S5 (dossier) + S9.
- Upload **paling telat 14–15 Sep** (VM dimatikan setelah batch — semua adegan VPS harus sudah terekam).

## G. URUTAN PEKERJAAN SESUAI BOBOT (pengingat)
| Bobot | Di video ini |
|-------|--------------|
| Efektivitas 30% | S2–S5: pipeline nyata, PDF lahir di depan kamera |
| Teknis 20% | S6 (24/7, journalctl, "keandalan yang jujur") + S3 (rumus dipajang) |
| Relevansi 20% | S0 (angka BPK/BPKP/KPK) + S1 |
| Kreativitas 15% | Konsep "data jadi tindakan" + S7 (agen yang bisa ditanya) |
| Storytelling 15% | Naskah VO + S8 (etika) + S9 (penutup yang dikenang) |
