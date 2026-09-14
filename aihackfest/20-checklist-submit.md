# CHECKLIST SUBMIT — MATA · AI HackFest 2026 (14 Sep 2026)
> **Deadline resmi (dari form): 30 Sep 2026, 23.59 WIB.** Target kirim: 16–17 Sep (aman dari edge).
> Struktur di bawah = **persis 16 halaman form** (diekstrak dari `FB_PUBLIC_LOAD_DATA`, 14 Sep 2026).
> Status: ✅ siap · 🟡 draft/menunggu eksekusi · 👤 input user (data registrasi) · ⏳ menyusul (punya tanggal)

## A. 5 syarat wajib dari halaman pembuka form

| # | Syarat form | Status | Bukti/catatan |
|---|---|---|---|
| 1 | Data sesuai saat **registrasi** | 👤 | Nama, email, WA, instansi, kota — salin PERSIS dari registrasi (halaman 3, 7–10 form) |
| 2 | Video demo **bisa diakses publik** (bukan private) | ⏳ | Rekam 14–15 Sep; unggah YouTube **PUBLIK** (bukan unlisted — form eksplisit "tidak private") |
| 3 | Artikel **dipublikasikan** & bisa diakses | 🟡 | Draf v3 siap (`11-draf-artikel.md`); publish di LinkedIn Articles → link publik |
| 4 | **Backlink** di dalam artikel | ✅ | 2 backlink tertanam: "AI Hosting"→idwebhost.com/ai-hosting + "Cloud VPS"→cloudbaik.com (tes klik pasca-publish) |
| 5 | **Semua link** bisa dibuka tim juri | 🟡 | Domain ✅ live · GitHub ✅ public · video & artikel = cek pasca-upload (link Google Drive/YouTube private akan GAGAL syarat ini) |

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
| 13 | **Link Video Demo** (wajib publik) | URL YouTube (setelah rekaman 14–15 Sep; naskah siap: `10-naskah-video.md` v2 LIVE) | ⏳ 15 Sep |
| 14 | **Link Artikel** (wajib publik) | URL LinkedIn Articles (setelah publish; draf v3 siap) | ⏳ 14–15 Sep |
| 15 | Deskripsi Singkat (**maks 150 karakter**) | **"AI agent 24/7 pembaca data pengadaan publik Kab. Aceh Tengah yang menghasilkan indikasi anomali terverifikasi per paket. Indikasi, bukan vonis."** (143 karakter ✅ terukur) | ✅ |
| 16 | Pesan untuk Dewan Juri (opsional) | Draft di bawah (salin) | ✅ |

**Draft halaman 16 (Pesan untuk Dewan Juri):**
> Terima kasih, Dewan Juri. MATA tidak mengklaim menangkap koruptor — ia hanya membuat data yang sudah dibuka benar-benar dibaca: 662 paket pengadaan TA2026 satu kabupaten, 14 indikasi yang lahir otomatis, dan setiap angka bisa ditelusuri hingga record ID + CSV publik. Alat ini open source, berjalan di VPS 4GB, dan bisa direplikasi untuk daerah mana pun dengan satu perintah. Semoga MATA tidak pernah dipuji — karena itu artinya tidak ada yang perlu diawasi.

## C. Bahan pendukung (tidak di form, tapi dibutuhkan form/artikel)

| Item | Status | Catatan |
|---|---|---|
| 4 screenshot (hero+LIVE, kartu D4, RUP-vs-Realisasi 26,6%, Tanya MATA) | ⏳ **menyusul → submodule media** (LFS) | Ambil dari `https://mata.niumination.web.id` (main :80) — **jangan** dari mockup Vercel/designarena |
| Video (5–10 mnt, naskah v2 LIVE) | ⏳ 14–15 Sep (HARD) | Naskah: `aihackfest/10-naskah-video.md` |
| Artikel v3 (±1.350 kata, 2 backlink) | 🟡 siap publish | `aihackfest/11-draf-artikel.md` — angka sudah selaras dashboard pasca-patch (170/43/41,6%) |
| Repo publik sinkron | ✅ | main `1afa154` (produksi :80) + dev `da8cdfd` (etalase, desain terkunci) — ls-remote 14 Sep |
| Dashboard live | ✅ | `https://mata.niumination.web.id` — MODE: LIVE, 14 indikasi, semua API 200 |
| Form terisi + terkirim | ⏳ target 16–17 Sep | Setelah video + artikel tayang |

## D. Urutan eksekusi (14 → 17 Sep)

1. **14 Sep (hari ini):** publish artikel (LinkedIn Articles, PUBLIK) → tes 2 backlink + copy URL.
2. **14–15 Sep:** rekam video (naskah v2) → unggah YouTube **PUBLIK** → copy URL. (HARD)
3. **15–16 Sep:** 4 screenshot dari domain produksi → commit ke submodule media (LFS, `git add -f`).
4. **16 Sep:** freeze — cek final semua link (video/artikel/repo/domain) bisa dibuka tanpa login.
5. **16–17 Sep:** isi form 16 halaman (identitas = persis registrasi) → **submit** (deadline resmi 30 Sep 23.59 WIB — buffer 2 minggu).

## E. Red-line pengisi form (jangan dilanggar)
- Identitas (nama/email/WA/instansi/kota) **persis** sama dengan registrasi — form halaman 6 = "VERIFIKASI DATA".
- Link video & artikel harus **publik** (juri tanpa akun Google/YouTube pun bisa membuka).
- Jangan tempel token/URL internal VPS (IP 103.30.146.232, port 8080, path /opt/mata) di form — cukup domain publik + repo.
- Nama vendor: boleh di video/screenshot (data publik per-paket), **jangan** di teks artikel.
