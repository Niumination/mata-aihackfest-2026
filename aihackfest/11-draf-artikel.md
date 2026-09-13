# DRAF ARTIKEL v2 (LIVE) — AI HackFest 2026 (siap publikasi 13 Sep)
> **Syarat kompetisi:** minimal 800 kata · orisinal · belum pernah dipublikasikan · platform publik terindeks (blog pribadi/LinkedIn Articles) · **2 backlink wajib** (sudah tertanam, tandai ⬅ di catatan bawah).
> **Panjang:** ±1.350 kata (lulus >800). **Versi:** v2 — seluruh angka dampak kini dari **produksi live 12 Sep 2026** (bukan demo). v1 (era demo) tersimpan di `11-draf-artikel-v1-demo.md`.
> **Sebelum publish:** (1) cek angka statistik nasional ke sumber terbaru (catatan bawah), (2) konfirmasi repo publik sinkron dengan commit terakhir (lihat catatan), (3) ambil 3–4 screenshot dari dashboard live (daftar di catatan).

---

# Triliunan Rupiah Sudah "Dibuka" — Tapi Tidak Ada yang Membacanya untuk Rakyat. Maka Kami Membangun MATA.

**Oleh Afrizal Munthe · Peserta AI HackFest 2026 — Kategori Productivity & Personal AI**

## Data-nya sudah publik. Lalu kenapa tidak ada yang mengawasi?

Setiap tahun, negara mengeluarkan triliunan rupiah melalui pengadaan barang dan jasa. Dan pemerintah sesungguhnya **sudah membuka datanya** untuk publik: pengumuman pengadaan di LPSE, harga acuan di e-katalog, hingga kontrak yang wajib didaftarkan di e-kontrak.

Tapi data yang dibuka bukan berarti data yang dibaca.

Angka-angkanya berbicara. BPKP menemukan modus manipulasi penganggaran dan pengadaan barang/jasa yang merugikan negara hingga **Rp141 triliun**. BPK mencatat **15.689 masalah** pengelolaan keuangan hanya pada semester I 2023, senilai **Rp18,19 triliun**. Dan baru Desember 2025, KPK membongkar pengaturan lelang proyek perkeretaapian di Medan — "pemenang sudah dikondisikan", HPS bocor, fee proyek 15–20% — disusul OTT pengadaan di Lampung Tengah dengan modus serupa.

Pola masalahnya jelas: anomali itu ada, datanya ada, tapi **tidak ada yang membacanya secara sistematis untuk rakyat**. Lembaga pengawas punya antrean kerja sendiri; warga biasa tidak punya waktu, keahlian, apalagi alat.

## Apa yang dilakukan MATA

MATA adalah **AI agent yang berjalan 24/7 di VPS** — watchdog akuntabilitas pengadaan untuk satu daerah (pelaku pertama: Kabupaten Aceh Tengah). Ia melakukan empat hal:

1. **Mengumpulkan** data pengadaan publik dari tiga sumber live: **INAPROC** (realisasi per-paket beserta nama penyedia + RUP rencana per kegiatan), **SPSE LKPP** (pengumuman lelang terkini + riwayat), dan **SAPA** (portal data terbuka daerah — 2.067 record dari 38 OPD).
2. **Menganalisis** dengan *rule engine* **deterministik dan transparan** — lima aturan, rumus dan ambangnya bisa dibaca siapa pun di repositori:
   - **D1 — Harga di atas referensi:** nilai proyek menyimpang ≥30% dari harga acuan katalog/peer;
   - **D2 — Konsentrasi penyedia:** satu penyedia mengambil share nilai ≥5% (dominasi) **atau** menang ≥15 paket dalam satu tahun (repetisi ekstrem) — ambang dikalibrasi dari struktur data riil 171 penyedia;
   - **D3 — Keroyokan akhir tahun:** lonjakan kontrak besar di 10 hari terakhir tahun anggaran (≥2× median bulan lain);
   - **D4 — Vendor kecil menang besar:** penyedia ber-riwayat ≤3 proyek kecil memenangkan kontrak ≥Rp1 miliar;
   - **D6 — Pola nilai identik:** nilai sama persis muncul di ≥3 proyek berbeda.
3. **Menganalisis rencana vs realisasi** — RUP per SKPD dibandingkan dengan realisasi kontrak: siapa yang hanya "berencana", siapa yang mengeksekusi, dan berapa sisanya.
4. **Menghasilkan output dunia nyata:** dashboard publik (indikasi bisa diklik hingga bukti per paket), *dossier* PDF + **draft laporan resmi ke APIP** + ringkasan publik, notifikasi Telegram, dan **chatbot "Tanya MATA"** yang hanya menjawab dari data yang ia pegang.

Yang tak kalah penting: MATA **tidak menghakimi**. Setiap output menulis "**indikasi, bukan vonis**". Ia menyiapkan draft laporan; **manusia** yang memverifikasi dan mengirimnya — lewat kanal resmi.

## Dari "menampilkan" ke "menganalisis": apa yang barusan ditemukan

Sebelum 12 September, MATA berjalan dengan dataset simulasi — jujur, dan saya menulisnya di sini. Ketika jalur data publik pertama berhasil dibuka, seluruh mesin yang sama saya arahkan ke **data riil**, tanpa mengubah satu pun aturan. Hasil siklus pertama pada data nyata Kabupaten Aceh Tengah (TA2026: 662 paket realisasi; TA2025: 599; plus 15.105 baris RUP rencana):

- **14 indikasi, 3 di antaranya level TINGGI** — dihasilkan otomatis dalam hitungan detik:
  - **D2 (TINGGI):** dua penyedia masing-masing menyerap **8,4% dan 7,5%** dari seluruh nilai pengadaan kabupaten dalam satu tahun — dari hanya 3 paket. Dominasi seperti ini mengikis kompetisi.
  - **D4 (TINGGI):** satu penyedia dengan **riwayat hanya 1 proyek Rp229 juta** memenangkan kontrak **Rp3,12 miliar** (jasa kebersihan). Kesenjangan 13× antara rekam jejak dan nilai kontrak — layak diverifikasi kualifikasinya.
  - **D2 ×9 (RENDAH):** penyedia yang menang **16–25 paket** dalam satu tahun anggaran.
  - **D6 ×2 (RENDAH):** nilai yang sama persis (Rp94,35 juta; Rp193,4 juta) muncul di tiga proyek berbeda.
- **Rencana vs realisasi:** dari rencana **Rp505,4 miliar**, yang terekalisasi **Rp134,5 miliar (26,6%)** per September — wajar untuk tahun berjalan, tapi per-nya terurai per **55 SKPD** di dashboard, bukan satu angka kabur.
- **Konteks:** 171 penyedia menang tahun ini; **44 di antaranya menang ≥5 paket**; 189 paket "pengadaan langsung" bernilai ≥Rp100 juta.

Tidak satu pun dari ini adalah vonis. Semuanya adalah **sinyal yang bisa ditelusuri**: setiap kartu indikasi menyimpan ID rekamannya, dan seluruh 1.250 paket bisa diunduh sebagai CSV publik — klik angka mana pun kembali ke sumbernya.

## Kenapa AI agent — dan kenapa ia muat di VPS kecil

MATA dibangun di atas **Hermes Agent** — agen open-source yang self-hosted, dengan penjadwal (cron), memori jangka panjang, dan kemampuan berbicara lewat Telegram. Arsitekturnya sederhana tapi jujur:

- *collector* ringan menarik data publik secara periodik (jeda antar-request, tanpa membanjiri server publik);
- *rule engine* **deterministik** yang men-flag (bukan black-box — setiap rumus dipublikasikan di repositori);
- LLM **hanya menjelaskan dan menyusun narasi — tidak memutuskan**; chatbot dijembatani ke agen dalam **mode terisolasi** (jail file, tanpa eksekusi, log audit, batas 5 pertanyaan/jam per pengunjung) dengan fallback deterministik bila backend sibuk;
- dashboard tanpa dependensi berat di port 8080: monitor live, indikasi, konsentrasi, RUP-vs-realisisasi, dan "Tanya MATA";
- setiap siklus, Hermes mengirim **ringkasan** lewat Telegram: kondisi monitor, jumlah indikasi per level, dan perubahannya.

Semua ini berjalan di infrastruktur **4 core / 4GB RAM / 20GB SSD** — [Cloud VPS](https://cloudbaik.com/) ⬅ yang disediakan panitia AI HackFest 2026 melalui [AI Hosting](https://idwebhost.com/ai-hosting/) ⬅. Tanpa GPU, tanpa service berat: watchdog-nya hanya memakan ±42MB RAM, dashboard-nya Python murni. Dan justru di situlah poinnya: **alat pengawasan harus cukup murah untuk dijalankan siapa pun** — kalau hanya berjalan di infrastruktur mahal, ia belum bekerja untuk rakyat.

## Kejujuran teknis (termasuk batasan)

Tiga hal yang ingin saya tulis terang-terangan:

1. **Jalur live-nya jujur, dan gap-nya juga jujur.** Data berasal dari jalur publik yang memang dipanggil situs resminya sendiri (tanpa login, tanpa bypass, tanpa proxy) — dari IP VPS yang tidak diblokir WAF. Tapi sumber data punya batas: INAPROC tidak mempublikasikan **harga referensi** (aturan D1 belum bisa bekerja untuknya) dan **tanggal tanda tangan kontrak** (D3 pun sama). MATA tidak mengarang datanya — aturan yang tak cukup data *tidak berjalan*, dan hal itu ditulis di dashboard. Ada pula selisih kecil di sisi sumber: ringkasan resmi menyebut 657 paket, koleksi penuh mengambil 662 baris — selisih 5 baris itu saya biarkan apa adanya, tidak diutak-atik.
2. **D5 (proyek "hantu" tanpa fisik) dan D7 (lelang tunggal) masih roadmap** — keduanya butuh data eksternal (foto geotag warga, data pelamar per tender).
3. **LLM bukan pembuat keputusan.** Aturan deterministik dan diaudit; LLM hanya menyusun penjelasan. Bila API gagal, MATA tetap bekerja dengan penjelasan template — *degradasi*, bukan kegagalan.

## Etika: batas yang paling penting

Alat pengawasan punya satu kelemahan fatal: **dipakai untuk menghakimi tanpa bukti**. Karena itu MATA memegang empat aturan keras:

- hanya membaca **data publik** dan mengreditkan sumbernya di setiap output;
- memakai kata "**indikasi**" — bukan "korup", "bersalah", "menipu";
- **human-in-the-loop** — MATA tidak pernah mengirim apa pun secara otomatis; manusia yang mengirim;
- pelaporan hanya melalui **kanal resmi**: LAPOR!, Ombudsman RI, KPK (whistleblower), APIP/BPKP.

## Open source & replikasi

Seluruh kode MATA **open source**: [github.com/niumination/mata-aihackfest-2026](https://github.com/niumination/mata-aihackfest-2026) — dan versinya berjalan publik di [mata.niumination.web.id](http://mata.niumination.web.id) (domain `.web.id` dari program resmi IDwebhost) — termasuk rule engine, ambang deteksi, generator dossier, sampai "surat etik" bagi agennya (HERMES_BRIEF.md). Siapa pun — jurnalis, aktivis, peneliti, atau APIP itu sendiri — bisa meng-clone, menjalankannya di VPS sendiri, dan mengarahkannya ke daerahnya. Itu poinnya: **indikasi yang bisa ditelusuri adalah harta publik, bukan fitur proprietary.**

## Bisnis & langkah berikutnya

Sebagai produk: SaaS "watchdog pengadaan" untuk pemerintah daerah dan institusi jurnalistik (monitoring bulanan + dossier), plus API untuk aplikasi transparansi. Sebagai alat sipil: gratis, open source, berjalan di VPS murah.

Roadmap: (1) **riwayat lelang + pemenang per paket** dari SPSE (jalurnya sudah terbukti 12 Sep); (2) **trend multi-tahun** — perbandingan perilaku vendor antar tahun (yang sudah terlihat: satu penyedia melonjak 9× nilainya dari 2025 ke 2026); (3) D5 dengan foto geotag dari warga; (4) publikasi dataset indikasi agregat.

## Penutup

MATA tidak mengklaim menangkap satu pun koruptor. Ia hanya melakukan satu hal: **membuat data yang sudah dibuka, benar-benar dibaca — secara sistematis, berkelanjutan, dan jujur.**

Semoga MATA tidak pernah dipuji. Karena itu artinya tidak ada yang perlu diawasi.

Semoga cukup... diawasi.

*— Afrizal Munthe, AI HackFest 2026. MATA berjalan 24/7 di AI Hosting IDwebhost × Cloud VPS CloudBaik, dibangun dengan Hermes Agent.*

---

## 📎 CATATAN UNTUK AFRIZAL (hapus bagian ini sebelum publish)
- **Backlink wajib (sudah tertanam, tandai ⬅):**
  1. Anchor **"AI Hosting"** → https://idwebhost.com/ai-hosting/ ✅ (paragraf "Kenapa AI agent")
  2. Anchor **"Cloud VPS"** → https://cloudbaik.com/ ✅ (paragraf yang sama)
  - Pastikan kedua link hidup setelah dipublikasikan (tes klik).
- **Verifikasi statistik sebelum publish** (sumber saat riset, cari versi terbaru):
  - BPKP Rp141 T (via artikel DJPb Kemenkeu yang mengutip Media Indonesia)
  - BPK 15.689 masalah / Rp18,19 T semester I 2023 (via Tempo)
  - KPK Des 2025: pengaturan lelang DJKA Medan + OTT Lampung Tengah fee 15–20% (rilis/sumber berita KPK)
  - Kalau sumber resmi lebih mudah dikutip (situs KPK/BPK), ganti sitasi ke situ.
- **Angka lokal MATA (sudah dari produksi 12 Sep, commit f91e32d):** 662+599 paket · 15.105 RUP · 14 indikasi (3 tinggi) · D2: 8,4% & 7,5% · D4: 3,12 M vs 229 jt · RUP 505,4 M → 134,5 M (26,6%) · 55 SKPD · 171 penyedia · 44 penyedia ≥5 paket · 189 PL ≥100 jt · 1.250 baris CSV. Nama vendor TIDAK ditulis di artikel (hanya pola) — etika.
- **Repo publik:** `github.com/niumination/mata-aihackfest-2026` terverifikasi **public** (HTTP 200, 12 Sep) — tapi **konfirmasi ke Hermes**: repo publik ini harus sinkron dengan commit terakhir produksi (f91e32d) sebelum artikel tayang.
- **Screenshot (ambil 13 Sep saat dashboard live):** (1) hero + badge MODE: LIVE + ticker, (2) kartu D4 (ANANDA…) ter-buka dengan bukti, (3) panel RUP-vs-Realisasi (baris keseluruhan 26,6%), (4) jawaban Tanya MATA.
- **Platform:** LinkedIn Articles (paling cepat terindeks) atau blog pribadi. LinkedIn: paste markdown-nya, pastikan link backlink masih hidup.
- **Domain FINAL: `mata.niumination.web.id`** (subdomain; root = portofolio pemilik. NS via Cloudflare gratis + record A `mata`; Opsi A port 80 — Hermes ubah service ke :80; user buat record A di panel DNS IDwebhost). Jika domain sudah live saat publish: pakai URL domain di artikel & form submit; jika belum: pakai `http://103.30.146.232:8080` sementara.
- **Judul alternatif (kalau LinkedIn memotong judul panjang):** "MATA: AI Agent yang Membaca Data Pengadaan Publik 24/7".
- **Hati-hati:** jangan menyebut nama vendor secara eksplisit di artikel (dashboard boleh — itu data publik per-paket; artikel = pola + angka).
