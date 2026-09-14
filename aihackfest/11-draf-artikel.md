# DRAF ARTIKEL v3 (LIVE) — AI HackFest 2026 (siap publikasi)
> **Syarat kompetisi:** minimal 800 kata · orisinal · belum pernah dipublikasikan · platform publik terindeks (blog pribadi/LinkedIn Articles) · **2 backlink wajib** (sudah tertanam, tandai ⬅ di catatan bawah).
> **Panjang:** ±1.350 kata (lulus >800). **Versi:** v3 — seluruh angka dampak dari **produksi live** dan sudah diselaraskan dgn dashboard pasca-patch 14 Sep 2026 (170 penyedia / 43 ≥5 paket / top-10 41,6%). v2 (12 Sep) → v1 (era demo) tersimpan di `11-draf-artikel-v1-demo.md`.
> **Sebelum publish:** (1) cek angka statistik nasional ke sumber terbaru (catatan bawah), (2) konfirmasi repo publik sinkron dengan commit terakhir (lihat catatan), (3) ambil 3–4 screenshot dari dashboard live (daftar di catatan).

---

# Triliunan Rupiah Sudah "Dibuka" — Tapi Tidak Ada yang Membacanya untuk Rakyat. Maka Kami Membangun MATA.

**Oleh Afrizal Munthe · Peserta AI HackFest 2026 — Kategori Productivity & Personal AI**

## Data-nya sudah publik. Lalu kenapa tidak ada yang mengawasi?

Setiap tahun, negara mengeluarkan triliunan rupiah melalui pengadaan barang dan jasa. Dan pemerintah sesungguhnya **sudah membuka datanya** untuk publik: pengumuman pengadaan di LPSE, harga acuan di e-katalog, hingga kontrak yang wajib didaftarkan di e-kontrak.

Tapi data yang dibuka bukan berarti data yang dibaca.

Angka-angkanya berbicara. Pengawasan BPKP tahun 2023 menemukan lebih dari separuh perencanaan dan penganggaran pemerintah daerah tidak efektif-efisien — total ketidakefisienan melebihi **Rp141 triliun**. BPK dalam IHPS I 2023 mencatat **15.689 masalah** pengelolaan keuangan (9.261 temuan) hanya pada semester I 2023, senilai **Rp18,19 triliun**. Dan Desember 2025, KPK menahan tersangka dalam kasus pengaturan pemenang proyek jalur kereta DJKA wilayah Medan (TA 2021–2024) — "pemenang sudah dikondisikan", HPS bocor — plus OTT pengadaan di Lampung Tengah dengan modus fee proyek **15–20%**.

Pola masalahnya jelas: anomali itu ada, datanya ada, tapi **tidak ada yang membacanya secara sistematis untuk rakyat**. Lembaga pengawas punya antrean kerja sendiri; warga biasa tidak punya waktu, keahlian, apalagi alat.

## Apa yang dilakukan MATA

MATA adalah **AI agent yang berjalan 24/7 di VPS** — watchdog akuntabilitas pengadaan untuk satu daerah (pelaku pertama: Kabupaten Aceh Tengah). Ia melakukan empat hal:

1. **Mengumpulkan** data pengadaan publik dari tiga sumber live: **INAPROC** (realisasi per-paket beserta nama penyedia + RUP rencana per kegiatan), **SPSE LKPP** (pengumuman lelang terkini + riwayat), dan **SAPA** (portal data terbuka daerah — 2.067 record dari 38 OPD).
2. **Menganalisis** dengan *rule engine* **deterministik dan transparan** — lima aturan, rumus dan ambangnya bisa dibaca siapa pun di repositori:
   - **D1 — Harga di atas referensi:** nilai proyek menyimpang ≥30% dari harga acuan katalog/peer;
   - **D2 — Konsentrasi penyedia:** satu penyedia mengambil share nilai ≥5% (dominasi) **atau** menang ≥15 paket dalam satu tahun (repetisi ekstrem) — ambang dikalibrasi dari struktur data riil 170 penyedia;
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
- **Konteks:** 170 penyedia menang tahun ini; **43 di antaranya menang ≥5 paket**; 189 paket "pengadaan langsung" bernilai ≥Rp100 juta.

Tidak satu pun dari ini adalah vonis. Semuanya adalah **sinyal yang bisa ditelusuri**: setiap kartu indikasi menyimpan ID rekamannya, dan seluruh 1.250 paket bisa diunduh sebagai CSV publik — klik angka mana pun kembali ke sumbernya.

## Kenapa AI agent — dan kenapa ia muat di VPS kecil

MATA dibangun di atas **Hermes Agent** — agen self-hosted (tanpa dependensi cloud) dengan penjadwal (cron), memori jangka panjang, dan kemampuan berbicara lewat Telegram. Arsitekturnya sederhana tapi jujur:

- *collector* ringan menarik data publik secara periodik (jeda antar-request, tanpa membanjiri server publik);
- *rule engine* **deterministik** yang men-flag (bukan black-box — setiap rumus dipublikasikan di repositori);
- LLM **hanya menjelaskan dan menyusun narasi — tidak memutuskan**; chatbot dijembatani ke agen dalam **mode terisolasi** (jail file, tanpa eksekusi, log audit, batas 5 pertanyaan/jam per pengunjung) dengan fallback deterministik bila backend sibuk;
- dashboard Python murni tanpa dependensi berat, tayang publik di domain resmi (port 80): monitor live, indikasi, konsentrasi, RUP-vs-realisasi, dan "Tanya MATA";
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

Seluruh kode MATA **open source**: [github.com/niumination/mata-aihackfest-2026](https://github.com/niumination/mata-aihackfest-2026) — dan versinya berjalan publik di [mata.niumination.web.id](https://mata.niumination.web.id) (domain `.web.id` dari program resmi IDwebhost) — termasuk rule engine, ambang deteksi, generator dossier, sampai "surat etik" bagi agennya (HERMES_BRIEF.md). Siapa pun — jurnalis, aktivis, peneliti, atau APIP itu sendiri — bisa meng-clone, menjalankannya di VPS sendiri, dan mengarahkannya ke daerahnya. Itu poinnya: **indikasi yang bisa ditelusuri adalah harta publik, bukan fitur proprietary.**

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
- **Statistik nasional — TERVERIFIKASI 14 Sep 2026, sumber resmi tersedia:**
  - **BPK:** rilis pers resmi BPK (5 Des 2023): "9.261 temuan senilai Rp18,19 triliun, IHPS I 2023" — https://www.bpk.go.id/news/bpk-ungkap-9261-temuan-senilai-rp1819-triliun-pada-semester-i-tahun-2023 · angka 15.689 masalah = data story Tempo (https://www.tempo.co/data/data/kerugian-negara-berdasarkan-pengelola-anggaran-dalam-temuan-bpk-di-semester-i-2023--991965)
  - **BPKP Rp141 T:** hasil pengawasan BPKP 2023 — "lebih dari separuh perencanaan & penganggaran pemda tidak efektif-efisien; total ketidakefisienan > Rp141 T" (medcom.id, kolom "Masalah Laten Kebocoran Anggaran"; juga dikutip DJPb Kemenkeu). Teks artikel sudah dirapikan: "ketidakefisienan" (bukan "merugikan negara").
  - **KPK Medan:** rilis resmi KPK (14 Des 2025): "KPK Kembali Tahan Tersangka Pengaturan Pemenang Proyek Jalur Kereta Api Wilayah Medan" — https://www.kpk.go.id/id/ruang-informasi/berita/kpk-kembali-tahan-tersangka-pengaturan-pemenang-proyek-jalur-kereta-api-wilayah-medan · modus "pemenang sudah dikondisikan" + HPS bocor (TA 2021–2024).
  - **OTT Lampung Tengah:** fee proyek 15–20% (Des 2025) — sumber berita OTT; sudah dipisah dari kalimat Medan di teks.
- **Angka lokal MATA (produksi, konsisten dgn dashboard pasca-patch 14 Sep):** 662+599 paket · 15.105 RUP (8.079 TA26 + 7.026 TA25) · 14 indikasi (3 tinggi) · D2: 8,4% & 7,5% · D4: 3,12 M vs 229 jt (13×) · RUP 505,4 M → 134,5 M (26,6%) · 55 SKPD · **170 penyedia · 43 penyedia ≥5 paket · top-10 share 41,6%** · 189 PL ≥100 jt (TA26) · 1.250 paket (CSV 1.251 baris incl. header). Semua angka di atas sudah diverifikasi terhadap `/api/analisis` produksi 14 Sep. Nama vendor TIDAK ditulis di artikel (hanya pola) — etika.
- **Repo publik:** `github.com/niumination/mata-aihackfest-2026` terverifikasi **public** — main produksi = **`1afa154`** (final, 13 Sep) & dev etalase = `da8cdfd` (14 Sep, desain terkunci + patch integritas data). Sudah sinkron (ls-remote 14 Sep). Sebelum publish, pastikan tidak ada commit baru di main.
- **Screenshot (ambil dari `https://mata.niumination.web.id` — domain sudah LIVE; jangan dari mockup Vercel/designarena):** (1) hero + badge MODE: LIVE + ticker, (2) kartu D4 (ANANDA…) ter-buka dengan bukti, (3) panel RUP-vs-Realisasi (baris keseluruhan 26,6%), (4) jawaban Tanya MATA. Nama vendor boleh muncul di screenshot (data publik per-paket), tapi jangan di teks artikel.
- **Platform:** LinkedIn Articles (paling cepat terindeks) atau blog pribadi. LinkedIn: paste markdown-nya, pastikan link backlink masih hidup.
- **Domain FINAL: `mata.niumination.web.id` — SUDAH LIVE (terverifikasi 200, MODE: LIVE).** Root = portofolio pemilik, jangan disentuh. Artikel & form submit pakai URL domain (bukan IP:8080).
- **Judul alternatif (kalau LinkedIn memotong judul panjang):** "MATA: AI Agent yang Membaca Data Pengadaan Publik 24/7".
- **Hati-hati:** jangan menyebut nama vendor secara eksplisit di artikel (dashboard boleh — itu data publik per-paket; artikel = pola + angka).
