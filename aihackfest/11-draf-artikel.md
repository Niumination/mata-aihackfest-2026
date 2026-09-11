# DRAF ARTIKEL — AI HackFest 2026 (siap publikasi)
> **Syarat kompetisi:** minimal 800 kata · orisinal · belum pernah dipublikasikan · platform publik terindeks (blog pribadi/LinkedIn Articles) · **2 backlink wajib** (sudah tertanam, tandai ⬅ di catatan bawah).
> **Panjang draf:** ±1.150 kata. **Sebelum publish:** (1) verifikasi angka statistik ke sumber terbaru (catatan di bagian akhir), (2) pastikan repo GitHub sudah public, (3) ganti nama platform sesuai tujuan publikasi.

---

# Triliunan Rupiah Sudah "Dibuka" — Tapi Tidak Ada yang Membacanya untuk Rakyat. Maka Kami Membangun MATA.

**Oleh Afrizal Munthe · Peserta AI HackFest 2026 — Kategori Productivity & Personal AI**

## Data-nya sudah publik. Lalu kenapa tidak ada yang mengawasi?

Setiap tahun, negara mengeluarkan triliunan rupiah melalui pengadaan barang dan jasa. Dan pemerintah sesungguhnya **sudah membuka datanya** untuk publik: pengumuman pengadaan di LPSE, harga acuan di e-katalog, hingga kontrak yang wajib didaftarkan di e-kontrak.

Tapi data yang dibuka bukan berarti data yang dibaca.

Angka-angkanya berbicara. BPKP menemukan modus manipulasi penganggaran dan pengadaan barang/jasa yang merugikan negara hingga **Rp141 triliun**. BPK mencatat **15.689 masalah** pengelolaan keuangan hanya pada semester I 2023, senilai **Rp18,19 triliun**. Dan baru Desember 2025, KPK membongkar pengaturan lelang proyek perkeretaapian di Medan — "pemenang sudah dikondisikan", HPS bocor, fee proyek 15–20% — disusul OTT pengadaan di Lampung Tengah dengan modus serupa.

Pola masalahnya jelas: anomali itu ada, datanya ada, tapi **tidak ada yang membacanya secara sistematis untuk rakyat**. Lembaga pengawas punya antrean kerja sendiri; warga biasa tidak punya waktu, keahlian, apalagi alat.

## Apa yang dilakukan MATA

MATA adalah **AI agent yang berjalan 24/7 di VPS**. Ia melakukan tiga hal:

1. **Mengumpulkan** data pengadaan publik — pengumuman, harga acuan, dan kontrak terdaftar.
2. **Mendeteksi** anomali dengan *rule engine* yang **transparan dan dapat diaudit**. Lima aturan, ambangnya bisa dibaca siapa pun:
   - **D1 — Harga di atas pasar:** nilai proyek menyimpang ≥30% dari referensi katalog/peer;
   - **D2 — Konsentrasi vendor:** satu penyedia menang ≥10 proyek dengan porsi nilai ≥25%;
   - **D3 — Keroyokan akhir tahun:** lonjakan kontrak besar di 10 hari terakhir tahun anggaran (≥2× median bulan lain);
   - **D4 — Vendor kecil menang besar:** penyedia ber-riwayat ≤3 proyek kecil memenangkan kontrak ≥Rp3 miliar;
   - **D6 — Pola nilai identik:** nilai sama persis muncul di ≥3 proyek berbeda instansi.
3. **Menghasilkan output dunia nyata:** *dossier* PDF (bukti + kalkulasi + langkah lanjut per indikasi), **draft laporan resmi ke APIP**, dan ringkasan publik — semuanya dengan tautan sumber yang bisa ditelusuri.

Yang tak kalah penting: MATA **tidak menghakimi**. Ia berkata "indikasi, bukan vonis". Ia menyiapkan draft laporan; **manusia** yang memutuskan dan mengirimnya — lewat kanal resmi.

## Kenapa AI agent — dan kenapa ia muat di VPS kecil

MATA dibangun di atas **Hermes Agent** — agen open-source yang self-hosted, dengan penjadwal (cron), memori jangka panjang, dan kemampuan berbicara lewat Telegram. Arsitekturnya sederhana tapi jujur:

- *collector* ringan menarik data publik setiap jam (loop cron);
- *rule engine* **deterministik** yang men-flag (bukan black-box — setiap rumus dipublikasikan di repositori);
- LLM **hanya menjelaskan dan menyusun narasi — tidak memutuskan**;
- dashboard tanpa dependensi berat di port 8080: status monitor, indikasi, konsentrasi vendor, dan grafik nilai per bulan (jendela Desember disorot merah);
- setiap pagi pukul 07.00, Hermes mengirim **ringkasan harian** lewat Telegram: kondisi monitor, jumlah pengumuman, indikasi per level, dan perubahan dari hari sebelumnya.

Semua ini berjalan di infrastruktur **4 core / 4GB RAM / 20GB SSD** — [Cloud VPS](https://cloudbaik.com/) ⬅ yang disediakan panitia AI HackFest 2026 melalui [AI Hosting](https://idwebhost.com/ai-hosting/) ⬅. Tanpa GPU, tanpa service berat: watchdog-nya hanya memakan ±42MB RAM, dashboard-nya Python murni. Dan justru di situlah poinnya: **alat pengawasan harus cukup murah untuk dijalankan siapa pun** — kalau hanya berjalan di infrastruktur mahal, ia belum bekerja untuk rakyat.

## Dampak terukur (dari satu siklus demo)

Pada dataset demo (48 pengumuman pengadaan, TA 2025), satu siklus MATA menghasilkan:

- **5 indikasi** (2 tinggi, 2 sedang, 1 rendah) — otomatis, dalam hitungan detik;
- **D1:** proyek jalan Rp2,7 miliar vs referensi Rp800 juta → **deviasi +238%** (rumus: (nilai − referensi)/referensi ≥ 30%);
- **D2:** satu penyedia menang **10 dari 48 proyek** (27,5% total nilai, Rp17 miliar);
- **D3:** 6 kontrak ≥Rp1 miliar di 10 hari terakhir Desember → **3,4× median** bulan lain;
- **D4:** penyedia ber-riwayat 2 proyek kecil (terbesar Rp350 juta) menang kontrak **Rp4,8 miliar**;
- **D6:** 3 proyek lintas instansi bernilai **persis Rp999.999.999**.

Semuanya dibungkus dossier 3 halaman + draft laporan APIP + ringkasan publik. Beban kerja analis manusia yang bisa memakan berhari-hari — selesai dalam hitungan detik, **dan bisa diulang 24/7**.

## Kejujuran teknis (termasuk batasan)

Tiga hal yang ingin saya tulis terang-terangan:

1. **Demo menggunakan dataset simulasi.** Saya menguji tiga sumber live publik dari VPS kompetisi: portal pengumuman PBJ nasional (DNS tidak teresolusi), e-katalog (HTTP 403 — memblokir klien non-browser), dan LPSE daerah (gagal handshake SSL — domain tampaknya berpindah). Ketiganya belum bisa diakses secara programatik tanpa risiko melanggar ToS. Maka saya bangun dataset simulasi deterministik yang mengikuti pola data PBJ — dan saya menuliskannya di sini, alih-alih berpura-pura live. **Integrasi live adalah roadmap minggu pertama.**
2. **D5 (proyek "hantu" tanpa fisik) dan D7 (lelang tunggal) masih roadmap** — keduanya butuh data eksternal (foto geotag warga, data pelamar per tender).
3. **LLM bukan pembuat keputusan.** Aturan deterministik dan diaudit; LLM hanya menyusun penjelasan. Bila API gagal, MATA tetap bekerja dengan penjelasan template — *degradasi*, bukan kegagalan.

## Etika: batas yang paling penting

Alat pengawasan punya satu kelemahan fatal: **dipakai untuk menghakimi tanpa bukti**. Karena itu MATA memegang empat aturan keras:

- hanya membaca **data publik** dan mengreditkan sumbernya di setiap output;
- memakai kata "**indikasi**" — bukan "korup", "bersalah", "menipu";
- **human-in-the-loop** — MATA tidak pernah mengirim apa pun secara otomatis; manusia yang mengirim;
- pelaporan hanya melalui **kanal resmi**: LAPOR!, Ombudsman RI, KPK (whistleblower), APIP/BPKP.

## Open source & replikasi

Seluruh kode MATA **open source**: [github.com/niumination/mata-aihackfest-2026](https://github.com/niumination/mata-aihackfest-2026) — termasuk rule engine, ambang deteksi, generator dossier, sampai "surat etik" bagi agennya (HERMES_BRIEF.md). Siapa pun — jurnalis, aktivis, peneliti, atau APIP itu sendiri — bisa meng-clone, menjalankannya di VPS sendiri, dan mengarahkannya ke daerahnya. Itu poinnya: **indikasi yang bisa ditelusuri adalah harta publik, bukan fitur proprietary.**

## Bisnis & langkah berikutnya

Sebagai produk: SaaS "watchdog pengadaan" untuk pemerintah daerah dan institusi jurnalistik (monitoring bulanan + dossier), plus API untuk aplikasi transparansi. Sebagai alat sipil: gratis, open source, berjalan di VPS murah.

Roadmap: (1) integrasi live — Panda LKPP / LPSE / e-katalog setelah asesmen ToS; (2) multi-wilayah dengan perbandingan antardaerah; (3) D5 dengan foto geotag dari warga; (4) publikasi dataset indikasi agregat.

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
- **Platform:** LinkedIn Articles (paling cepat terindeks) atau blog pribadi (apablog.com/medium/blogspot). LinkedIn: paste markdown-nya, pastikan link backlink masih hidup.
- **Status repo:** pastikan `github.com/niumination/mata-aihackfest-2026` **public** saat artikel tayang.
- **Waktu publish:** 13–14 Sep (sesuai sprint), lalu copy tautannya ke form submit.
- Judul alternatif (kalau LinkedIn memotong judul panjang): *"MATA: AI Agent yang Membaca Data Pengadaan Publik 24/7"*.
