# CHECKLIST SUBMIT — MATA · AI HackFest 2026 (14 Sep 2026)
> **Deadline resmi form: 30 Sep 2026, 23.59 WIB. TAPI target submit: 15 Sep SEBELUM 23.59 WIB — sesuai jadwal VM (per keputusan 14 Sep).**
> ⚠️ **Info panitia: VM peserta Batch 3 dinonaktifkan mulai 15 Sep 23:59 WIB.** Semua yang butuh VM/domain (rekam adegan VPS, screenshot produksi, link domain) HARUS tuntas sebelum itu. Yang abadi: video, artikel, repo, form.
> Struktur di bawah = **persis 16 halaman form** (diekstrak dari `FB_PUBLIC_LOAD_DATA`, 14 Sep 2026).
> Status: ✅ siap · 🟡 draft/menunggu eksekusi · 👤 input user (data registrasi) · ⏳ menyusul (punya tanggal)

## A. 5 syarat wajib dari halaman pembuka form

| # | Syarat form | Status | Bukti/catatan |
|---|---|---|---|
| 1 | Data sesuai saat **registrasi** | 👤 | Nama, email, WA, instansi, kota — salin PERSIS dari registrasi (halaman 3, 7–10 form) |
| 2 | Video demo **bisa diakses publik** (bukan private) | ⏳ | Rekam 14–15 Sep; unggah YouTube **PUBLIK** (bukan unlisted — form eksplisit "tidak private") |
| 3 | Artikel **dipublikasikan** & bisa diakses | ✅ | **TAYANG 14 Sep**: https://www.linkedin.com/pulse/triliunan-rupiah-sudah-dibuka-tapi-tidak-ada-yang-membacanya-kali-0v7xc — audit publik 3× (14 Sep): angka benar, 0 sisa draf |
| 4 | **Backlink** di dalam artikel | ✅ | "AI Hosting"→idwebhost.com/ai-hosting + "Cloud VPS"→cloudbaik.com — terverifikasi tertanam & klik di versi publik |
| 5 | **Semua link** bisa dibuka tim juri | 🟡 | Domain ✅ live (hanya sampai VM mati 15 Sep 23:59 WIB — setelah itu juri pakai video/screenshot) · GitHub ✅ public · video & artikel = cek pasca-upload (link Google Drive/YouTube private akan GAGAL syarat ini) |

## B. Isi per halaman form (16 halaman)

| Hal | Pertanyaan | Isi yang disiapkan | Status |
|---|---|---|---|
| 1 | Solo atau Squad? | **Solo** | ✅ (sesuai registrasi) |
| 3 | Nama Lengkap (sesuai registrasi) | Afrizal Munthe — **cek ejaan persis dgn registrasi** | 👤 |
| 7 | Alamat Email (registrasi) | — | 👤 |
| 8 | Nomor HP (WhatsApp) (registrasi) | — | 👤 |
| 9 | Asal Sekolah/Kampus/Instansi/Perusahaan (registrasi) | — | 👤 |
| 10 | Kota/Kabupaten Domisili (registrasi) | — | 👤 |
| 12 | Judul AI Agent | **MATA — Watchdog Akuntabilitas Pengadaan** (bisa juga: "MATA: AI Agent yang Membaca Data Pengadaan Publik 24/7") | ✅ |
|| 13 | **Link Video Demo** (wajib publik) | https://youtu.be/dbw5KVA75q8 (TAYANG 16 Sep 2026, akses publik ✅) | ✅ |
| 14 | **Link Artikel** (wajib publik) | https://www.linkedin.com/pulse/triliunan-rupiah-sudah-dibuka-tapi-tidak-ada-yang-membacanya-kali-0v7xc (TAYANG 14 Sep, akses publik ✅) | ✅ |
| 15 | Deskripsi Singkat (**maks 150 karakter**) | **"AI agent 24/7 pembaca data pengadaan publik Kab. Aceh Tengah yang menghasilkan indikasi anomali terverifikasi per paket. Indikasi, bukan vonis."** (143 karakter ✅ terukur) | ✅ |
| 16 | Pesan untuk Dewan Juri (opsional) | Draft di bawah (salin) | ✅ |

**Draft halaman 16 (Pesan untuk Dewan Juri):**
> Terima kasih, Dewan Juri. MATA tidak mengklaim menangkap koruptor — ia hanya membuat data yang sudah dibuka benar-benar dibaca: 662 paket pengadaan TA2026 satu kabupaten, 14 indikasi yang lahir otomatis, dan setiap angka bisa ditelusuri hingga record ID + CSV publik. Alat ini open source, berjalan di VPS 4GB, dan bisa direplikasi untuk daerah mana pun dengan satu perintah. Semoga MATA tidak pernah dipuji — karena itu artinya tidak ada yang perlu diawasi.

**Status submit**: ✅ **TERKIRIM 16 Sep 2026 00:19 WIB** via Google Form AI HackFest 2026 — konfirmasi: screenshot di cache Hermes

## C. Bahan pendukung (tidak di form, tapi dibutuhkan form/artikel)

| Item | Status | Catatan |
|---|---|---|
| 4 screenshot (hero+LIVE, kartu D4, RUP-vs-Realisasi 26,6%, Tanya MATA) | ✅ **SIAP 14 Sep** (file di workspace, siap sync ke VM) | `screenshots/01-hero-live.png` · `02-flag-d4-ananda.png` · `03-rup-vs-realisasi.png` · `04-tanya-mata.png` — diambil langsung dari `https://mata.niumination.web.id` (main :80, 2× retina, 0 error, modal geo ditutup). **02–04 sudah final; **01-hero harus re-capture setelah hero baru tayang di :80** (langkah D.2). Commit ke submodule media (LFS, `git add -f`) di VM sebelum 15 Sep 23:59.** |
| **Snapshot statis dashboard** (jaring pengaman pasca-VM) | ✅ **SIAP** — `snapshot/dashboard-live-2026-09-14.html` (1.8 MB, self-contained, 0 error) | **Commit ke repo sebelum 15 Sep 23:59** (git add snapshot/). Bisa di-run ulang utk data final: `python3 scripts/make_snapshot.py`. Deploy cadangan Netlify/Vercel: `21-snapshot-dan-deploy-cadangan.md` |
| Video (5–10 mnt, naskah v3 LIVE) | ⏳ 14–15 Sep (HARD) — **naskah + aset SIAP** | Naskah final: `aihackfest/10-naskah-video.md` (v3 LIVE, angka riil, adegan S0–S9 termasuk Tanya MATA) · Thumbnail YouTube: `aihackfest/22-thumbnail-youtube.png` (1280×720) |
| Artikel v3 (±1.350 kata, 2 backlink) | ✅ TAYANG 14 Sep | LinkedIn Pulse (link di atas) — audit publik: angka benar, backlink hidup, 0 sisa draf |
| Repo publik sinkron | ✅ | main `1afa154` (produksi :80) + dev `b9ecc95` (etalase + docs info panitia) — ls-remote 14 Sep |
| Dashboard live | ✅ (hingga VM mati 15 Sep 23:59 WIB) | `https://mata.niumination.web.id` — MODE: LIVE, 14 indikasi, semua API 200 |
| Form terisi + terkirim | ⏳ **target 15 Sep SEBELUM 23.59 WIB** (sesuai jadwal VM) | Setelah video tayang; identitas = persis registrasi |

## D. Urutan eksekusi — SEMUA tuntas 15 Sep SEBELUM 23.59 WIB (VM mati)

1. **14 Sep — SELESAI ✅:** artikel publish + 2 backlink terverifikasi di versi publik.
2. **14 Sep (sekarang, SEBELUM rekam video):** hero baru sudah di `mata/mata/web.py` (tagline selaras thumbnail & cover: "Uang itu uangmu. MATA membacanya.") → **sync ke VM, deploy ke :80 (restart servis), verifikasi di browser** → **re-capture `screenshots/01-hero-live.png`** dari produksi → **regenerate snapshot** (`python3 scripts/make_snapshot.py`) → commit semua.
3. **14–15 Sep (HARD, paling kritis):** rekam video (naskah v3 LIVE; adegan VPS dashboard + terminal WAJIB terekam SEBELUM VM mati) → unggah YouTube **PUBLIK** + thumbnail `22-thumbnail-youtube.png` → copy URL.
4. **15 Sep (sebelum 23.59 WIB):** 4 screenshot final dari domain produksi → commit ke submodule media (LFS, `git add -f`).
5. **15 Sep (sebelum 23.59 WIB):** freeze — cek final semua link (video/artikel/repo/domain) bisa dibuka tanpa login.
6. **15 Sep (sebelum 23.59 WIB):** isi form 16 halaman (identitas = persis registrasi) → **submit**.
   - Deadline resmi form 30 Sep tetap berlaku, TAPI link domain/dashboard hanya hidup sampai 15 Sep 23.59 WIB → submit sebelum VM mati agar seluruh tautan yang dikirim masih bisa dibuka juri saat dicek.

## E. Red-line pengisi form (jangan dilanggar)
- Identitas (nama/email/WA/instansi/kota) **persis** sama dengan registrasi — form halaman 6 = "VERIFIKASI DATA".
- Link video & artikel harus **publik** (juri tanpa akun Google/YouTube pun bisa membuka).
- Jangan tempel token/URL internal VPS (IP 103.30.146.232, port 8080, path /opt/mata) di form — cukup domain publik + repo.
- Nama vendor: boleh di video/screenshot (data publik per-paket), **jangan** di teks artikel.
