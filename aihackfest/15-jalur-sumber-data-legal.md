# 15 — Investigasi Komprehensif Sumber Data: Jalur Legal untuk MATA
### 12 Sep 2026 · fokus: masalah penarikan data dari sumber publik, cara legal, referensi komunitas, tools & skills Hermes

Misi: menemukan **celah yang pas** — akses data PBJ per-paket (terutama Kab. Aceh Tengah) yang
**legal, sustainable, dan bisa dijalankan VPS**. Semua klaim di bawah punya dasar: probe langsung
(log §7) atau referensi publik (URL). Yang belum terverifikasi diberi status eksplisit.

---

## 0. Eksekutif — "celah yang pas" yang ditemukan

| Peringkat | Jalur | Mekanisme | Legalitas | Status 12 Sep | Data yang didapat |
|---|---|---|---|---|---|
| **★1** | **Jalur C — Satu Data eProc** (`isb.lkpp.go.id/isb-2/api/satudata/…`) | API resmi LKPP, **tanpa pendaftaran** | **Tertulis & eksplisit**: UU 14/2008 KIP + lisensi CC BY-NC-SA 4.0 + S&T resmi | ⚠️ **UNTERSTUD** — 403 dari sandbox (IP datacenter); **harus dites dari VPS** (IP berbeda) | Tender Umum Publik **per-paket, per-LPSE, per-tahun** (20+ field: HPS, pagu, satker, metode, jumlah pendaftar/penawar/kualifikasi, lokasi, durasi) + **Daftar Hitam** (penyedia tersanksi) + Master LPSE/KLPD |
| **★1b** | **Jalur S — SAPA SPLP** (`api-splp.layanan.go.id/sapa/1.0/api/daftar_data`) | API resmi SPLP/SAPA Pemkab, **tanpa auth** | Resmi (sistem pemerintah; sudah produksi di `sapa-ai` milik pemilik) | ✅ **LIVE 200 dari sandbox (datacenter!)**, 629KB | **2.067 indikator resmi Kab. Aceh Tengah** per OPD (38) × tahun (2022–2026): PDRB, IPM, stunting, kopi, **realisasi Belanja APBD 1,318 T**, pengadaan CPPD — baseline anggaran & cross-check sinyal MATA |
| **★2** | **Jalur C' — SPSE terpadu, sesi anonim** (`spse.inaproc.id/acehtengahkab/dt/lelang`) | POST + header XHR + **token sesi anonim** (`SPSE_SESSION`/`___AT`) yang terbit otomatis saat membuka `/lelang` (mekanisme terdokumentasi di source `pyproc`) | Publik; robots.txt `Allow: /`; bukan bypass autentikasi (token anonim untuk pengunjung) | ⚠️ **UNTERSTUD** — probe VPS sebelumnya pakai GET tanpa sesi (mungkin itu penyebab "Terjadi Kesalahan"); **test P0 §6** | **Semua**: riwayat per-tahun, filter `rekanan` (nama penyedia!), `kontrakStatus` (selesai/pemutusan/penghentian), kategori, satker → **D1–D6 semua** |
| ★3 | Jalur C (produksi) — SPSE homepage | GET halaman utama, UA browser | Publik, robots Allow | ✅ **LIVE di produksi** (commit 3ed634f, 12 paket nyata) | Daftar paket terkini (tanpa riwayat/detail) |
| ★4 | Jalur B — kolektor laptop | Browser + cookie CF → push via token | Koneksi sendiri, manusia di depan, traffic rendah | ✅ Siap (`spse_collect.py`); push_token belum dipasang | Sama seperti C' + detail halaman |
| ★5 | Jalur A — API Gateway INAPROC (Data Integrator) | JWT + registrasi IP pemanggil | **Resmi & paling kuat** (surat permohonan LKPP) | 🔶 Terbuka untuk **Surat Tugas Diskominfo** (post-kompetisi) | JSON rapi nasional + endpoint kontrak |
| ★6 | Jalur D — OPD/PPID pemkab | CKAN `opendata.acehtengahkab.go.id` + permohonan PPID (UU 14/2008) | **Paling kuat secara hukum** (hak akses informasi) | ✅ Portal hidup (200); **belum ada dataset PBJ** (0 hasil "pengadaan"/"lelang") | Lever adopsi: pemkab menerbitkan open data PBJ → MATA tampil |
| ★7 | Jalur E — CKAN LKPP & Provinsi | `data.lkpp.go.id` + `data.acehprov.go.id` (API CKAN standar) | Publik, tanpa auth | ✅ 200 dari sandbox | Agregat K/L/PD (RUP vs realisasi) + dataset provinsi ("Rencana Umum Pengadaan", "Data Realisasi Tender") |

**Rekomendasi urutan eksekusi:** test P0 (§6) di VPS hari ini →
jika **C' (sesi anonim)** lulus: MATA punya seluruh D1–D6 **server-side, tanpa laptop, tanpa token, publik**.
Jika **C (Satu Data)** lulus: fallback resmi yang paling "bersih" secara legal (S&T tertulis).
Jika keduanya 403 dari VPS: Jalur B (laptop) tetap jalan; pertimbangkan FlareSolverr (§4, Tier 2).
Jalur A & D = fase adopsi pasca-kompetisi (dan justru memperkuat narasi adopsi).

---

## 1. Kerangka hukum — apa yang legal, apa yang tidak

**Tidak ada satu undang-undang "scraping" di dunia maupun di Indonesia.** Pola risikonya (konsisten
di yurisdiksi besar): (a) **hukum hacking** — mem-bypass gate akses/autentikasi; (b) **kontrak** —
melanggar ToS yang sudah diterima; (c) **hak cipta** — menerbitkan ulang konten kreatif; (d) **PII** —
memproses data pribadi. **Fakta (harga, tanggal, nilai paket, nama perusahaan dalam data pengadaan
publik) umumnya bebas** — yang dilindungi adalah ekspresi kreatif, bukan fakta.

**Preseden kunci (AS, rujukan komunitas):**
- *hiQ Labs v. LinkedIn* — mengakses **data publik** (tanpa login) bukan pelanggaran CFAA.
- *Van Buren v. US* (2021) — memperluas: "akses tanpa izin" = melewati kontrol akses yang ada;
  halaman publik = kontrolnya terbuka.
- *Meta v. Bright Data* (2024/2025) — scraping halaman publik diperkuat; **risiko yang tersisa
  bergeser ke kontrak (ToS) & hak cipta**, bukan kriminal.
- Konsensus forum (r/webscraping, r/NewsAPI, r/PrivatePackets): cek robots.txt, identifikasi bot
  (UA + kontak), kumpulkan hanya yang dibutuhkan, hindari PII, hormati ToS, gunakan API resmi bila ada.

**Indonesia (dasar yang berlaku untuk MATA):**
- **UU 14/2008 Keterbukaan Informasi Publik** — data pemerintah yang tidak masuk kategori
  dirahasiakan adalah **hak publik**; S&T resmi Satu Data eProc secara eksplisit berdasar UU ini
  ("dapat dikategorikan sebagai domain publik").
- **PP 38/2016** — kewajiban Pemda menyediakan **Pemerintah Open Data** (portal OPD = wujudnya;
  `opendata.acehtengahkab.go.id` sudah hidup).
- **UU ITE Pasal 30** — mengakses **sistem komputer milik orang lain tanpa izin** = pidana.
  Garis pembeda untuk MATA: membaca halaman/API **publik** ≠ intrusi sistem; **memaksakan bypass
  kontrol akses (login, CAPTCHA yang dijebol, pembatasan IP yang ditembus dengan agresif) = zona
  risiko** — tidak dilakukan MATA.
- **UU PDP (27/2022)** — PII tetap hati-hati: MATA hanya memakai data perusahaan/instansi (subjek
  hukum, data korporasi), bukan data pribadi.
- **S&T Satu Data eProc** (inaproc.id/satudata) — izin tertulis eksplisit: boleh dipakai untuk
  "penelitian, pengambilan keputusan, **dan pengawasan**" (pasukan pas untuk watchdog MATA),
  **wajib atribusi**: *"Layanan ini menggunakan API Satu Data eProc ({Nama API} dan {Tanggal Update API})"*,
  lisensi CC BY-NC-SA 4.0 (non-komersial — MATA = edukasi/awasan, cocok).
- **Norma komunitas Indonesia** (README `yfktn/spse-scraper`, proyek PNS Pemprov Kalteng):
  *"penggunaan tool ini diharapkan dilakukan dengan **sepengetahuan dan seizin System Admin LPSE**"*
  → MATA: traffic rendah (rate-limit + jitter + cache 30 mnt + hanya 1 LPSE), UA teridentifikasi,
  dan (fase adopsi) seizin LPSE/Diskominfo.

**Garis merah MATA (tetap):** tidak bypass login/CAPTCHA; tidak membanjiri server (throttle);
tidak mengambil PII; tidak menjual data; atribusi sesuai S&T; semua sumber & cakupan ditampilkan
di dashboard ("indikasi, bukan vonis").

---

## 2. Inventaris sumber (detail teknis per jalur)

### ★1. Satu Data eProc — **API resmi tanpa pendaftaran** (temuan utama sesi ini)
- **Apa**: layanan LKPP/INAPROC "Satu Data eProc" — data PBJ nasional yang terbuka, sumbernya SPSE.
- **Endpoint (terverifikasi dari source pyproc, MIT)**:
  - `https://isb.lkpp.go.id/isb-2/api/satudata/MasterLPSE` — daftar LPSE + `repoId`
  - `https://isb.lkpp.go.id/isb-2/api/satudata/MasterKLPD` — master K/L/PD
  - `https://isb.lkpp.go.id/isb-2/api/satudata/TenderUmumPublik/{tahunAnggaran}/{kdLpse}` — **GET polos, JSON/CSV**
  - (dikutip juga: `satudata.inaproc.id/service/tenderUmumPublik?repoId=…&tahunAnggaran=…`)
  - **Sanksi Daftar Hitam** (field: NPWP, nama penyedia, alamat, instansi asal, jenis pelanggaran
    sesuai PerLKPP, masa sanksi) — **sangat bernilai untuk monitoring D-vendor MATA**.
- **Field Tender Umum Publik**: Kode Tender, LPSE, Status (aktif/ditutup), Nama Paket, **Pagu, HPS**,
  tanggal dibuat/tayang, Kategori, Metode Pemilihan/Pengadaan/Evaluasi, Cara Pembayaran,
  **Jenis Penetapan Pemenang**, **Instansi & Satker (jsonb)**, Konsolidasi, Anggaran (sumber dana,
  nilai, kode rekening), Lokasi (prov/kab/ket), **Jumlah Pendaftar/Penawar/Kirim Kualifikasi**,
  Durasi Tender, Versi SPSE.
- **Jangkauan**: nasional (semua LPSE) × per tahun anggaran (contoh docs: data sejak 2011).
- **Bukti**: spec resmi inaproc.id/satudata (fetch §7) + endpoint dari source pyproc + probe 403
  Apache dari sandbox (IP datacenter ditolak server — **bukan** Cloudflare; bisa jadi allowlist IP).
- **Tindak lanjut**: test P0 §6 dari VPS. Jika lulus → integrasi `mata/satudata.py`
  (pola `spse_pub.py`: cache 30 mnt + stale badge + atribusi S&T di footer panel).

### ★2. SPSE terpadu — **sesi anonim untuk `/dt/lelang`** (mekanisme dari source `wakataw/pyproc`)
- **Apa yang terjadi di browser** (direplikasi pyproc, MIT, 43⭐, 442 commit, aktif Jun 2026):
  1. `GET {base}/lelang` → server menyetel cookie **`SPSE_SESSION`** berisi **`___AT=<token>`**
     (token anonim pengunjung — **bukan** login; ini yang tidak pernah dites di probe VPS 12 Sep).
  2. `POST {base}/dt/lelang` (DataTables) dengan header:
     `X-Requested-With: XMLHttpRequest`, `Referer: {base}/lelang`, `Sec-Fetch-Mode: cors`,
     `Sec-Fetch-Site: same-origin` + parameter `draw/start/length/columns[i][search][value]` + filter.
- **Filter yang tersedia** (dari source): `tahun`, `kategoriId`, **`rekanan` (nama penyedia!)**,
  **`kontrakStatus` (0=selesai, 1=pemutusan, 2=penghentian)**, `instansiId`, keyword, paging.
  → Ini menutup **D1 (pengumuman), D2 (konsentrasi vendor), D3 (pemenang vs HPS), D4 (vendor baru
  dapat besar), D5/D6 (pola pemenang/nilai berulang)** — semua dari satu endpoint.
- **Mengapa probe VPS sebelumnya gagal** ("Terjadi Kesalahan"): kemungkinan besar karena (a) GET
  alih-alih POST, (b) tanpa sesi `___AT`, (c) tanpa header XHR/Referer. **Semua tiga sudah
  terdokumentasi dari source pyproc** — test P0 §6 mengujinya langsung.
- **Legalitas**: data publik; robots.txt SPSE `Allow: /` (termasuk path LPSE eksplisit); bukan
  bypass autentikasi (token anonim memang mekanisme resmi portal); risiko = ToS/kebijakan LKPP
  terhadap beban server → mitigasi: rate-limit + jitter + cache + hanya 1 LPSE.
- **Alternatif eksekusi**: `pip install pyproc` lalu CLI/MCP-nya (§4) — atau replikasi 30 baris
  di `mata/spse_pub.py` (kontrol penuh, tanpa dependensi).

### ★3. SPSE homepage (produksi ✅)
Sudah online (12 paket, cache 30 mnt, stale-safe). Tetap jadi **fallback utama** saat jalur lain
gagal — arsitektur multi-sumber dengan degradasi halus.

### ★4. Kolektor laptop (Jalur B, siap)
`scripts/spse_collect.py` — cookie CF dari browser manusia (cf_clearance/__cf_bm), ambil homepage +
detail + `/dt/lelang`, push via `/api/spse-push` (token). Catatan: dengan temuan sesi anonim (§2),
Jalur B bisa **disederhanakan** — mungkin tanpa cookie cukup (tunggu hasil test P0).

### ★1b. Jalur S — SAPA SPLP (LIVE, tanpa auth) ✅

**Endpoint:** `GET https://api-splp.layanan.go.id/sapa/1.0/api/daftar_data` — **dibuktikan 200 langsung dari datacenter** (12 Sep, tanpa token, tanpa header khusus; UA browser cukup). Ini sistem **SAPA = Satu Pintu Akses** — platform data resmi Pemkab yang di-host di `layanan.go.id` (infrastruktur layanan pemerintah), **bukan** scraping.

**Respons terukur (12 Sep, 629.467 B):** `{"api_status":1,"api_message":"success","data":[2067 record]}`. Field per record: `id_kode_indikator`, `kode_indikator_kode_indikator` (kode SDI), `kode_indikator_nama_indikator`, `opds_nama_opd` (38 OPD), `jadwal_pemutakhiran`, `satuan`, `tahun` (2022–2026; 780 record tanpa tahun), `variabel` (**nilainya**).

**Isi yang langsung bernilai untuk MATA:**
- **Realisasi Belanja APBD 1.317.811.348.177,38** (BPKAD) → **baseline anggaran** untuk rasio D2 (share vendor vs anggaran) dan konteks besaran.
- Realisasi per kategori: Belanja Pegawai 618,7 M; Barang & Jasa 267,9 M; Modal 109,3 M; Hibah 31,9 M; Bantuan Sosial 17,6 M; BTT 8,1 M.
- Pengadaan CPPD 2,4 Ton (Dinas Pangan), Data Realisasi Investasi (DPMPTSP), 25 indikator "realisasi*", 20 indikator kopi, 10 PDRB.
- 10 OPD terbesar: Dinkes 294, KB/PPPA 192, PUPR 172, Dispora 164, Perpustakaan 92, Disdik 87, Dinkop UKM 81, Perkebunan 79, BPKAD 77, RSUD Datu Beru 66.

**Bukti aksesibilitas produksi:** API ini **sudah live-produksi** menggerakkan `sapa-smart-ai.vercel.app` (repo `Niumination/sapa-ai`) — pola yang dipakai: `fetch daftar_data` → LRU cache 10 menit per instance → 503 graceful bila mati → status jujur. OAuth opsional ada (`POST https://sapa.acehtengahkab.go.id/oauth/token`, `client_credentials`, client_id `3`, secret via env) untuk endpoint terlindungi di masa depan — **tidak dibutuhkan** untuk `daftar_data`.

**Endpoint lain:** semua tebakan lain 404 (`daftar_opd`, `nilai_data`, `detail_data`, `v2/…`) → `daftar_data` adalah satu-satunya endpoint publik saat ini (dump penuh sudah mencakup nilai).

**Posisi dalam arsitektur MATA:** **pelengkap resmi** (bukan inti PBJ per-paket — itu SPSE/ISB). Panel "Indikator Resmi Kabupaten" + cross-check: sinyal MATA (mis. pola tender jalan) ↔ indikator jalan/Dinas PUPR; share vendor ↔ baseline APBD. Narasi adopsi kuat: *"MATA mengonsumsi API SAPA resmi Pemkab — sumber yang sama dengan dashboard SAPA Smart AI."*

**Kendala:** hanya indikator agregat (bukan per-paket); 780 record tanpa tahun (perlu normalisasi); update bulanan (jadwal_pemutakhiran).

### ★5. API Gateway INAPROC (Jalur A)
Tidak berubah: role **Data Integrator** → Surat Permohonan LKPP (meterai, PIC) → approval admin
instansi → token + **registrasi IP pemanggil** (VPS). Untuk MATA: **Surat Tugas Kepala Diskominfo
→ surat Pemkab Aceh Tengah → approval admin LPSE Aceh Tengah** (koordinasi internal — pengguna
bekerja di Diskominfo). Timeline 1–2 minggu; fase pasca-kompetisi. Nilai tambah vs C/C': JSON
resmi, endpoint kontrak (nama penyedia, nilai kontrak, addendum), cakupan nasional, tanpa risiko
scraping sama sekali.

### ★6. OPD + PPID Kab. Aceh Tengah (Jalur D)
- `opendata.acehtengahkab.go.id` = **CKAN hidup (200)** dari datacenter — tapi datasetnya statistik
  (BPS/peta/bencana); **0 dataset "pengadaan"/"lelang"**.
- `data.acehprov.go.id` = CKAN hidup; **12 dataset "pengadaan" + 1 "kontrak"**, termasuk
  **"Rencana Umum Pengadaan"** dan **"Data Realisasi Tender"** (sumber eWalidata) — periksa apakah
  mencakup satker Kab. Aceh Tengah.
- **Lever adopsi (paling kuat hukumnya)**: usulkan ke Pemkab (lewat Diskominfo) penerbitan
  dataset PBJ di portal OPD (kewajiban PP 38/2016) — MATA langsung mengonsumsi CKAN API-nya.
  Data spesifik (mis. daftar kontrak per-satker) bisa juga lewat **permohonan PPID** (UU 14/2008) —
  formal, gratis, dan pengguna punya akses internal.

### ★7. CKAN LKPP (Jalur E, agregat)
`data.lkpp.go.id` terverifikasi (658 K/L/PD RUP vs realisasi; Aceh Tengah 484,6 M → 138,6 M / 28,6%).
Sudah jadi "konteks" di dashboard. Tetap relevan sebagai baseline agregat.

### ★8. `data.go.id` — Portal Satu Data Indonesia (nasional) — **re-investigasi 12 Sep**
Portal OPD **nasional** (Perpres 39/2019 Satu Data Indonesia). Dulu saya coret terlalu cepat
(cuma 2–3 tebakan path API) — investigasi ulang membongkar arsitekturnya:
- **Portal hidup & bisa diakses dari datacenter** (200, tanpa CF): katalog **670.326 dataset**
  dengan filter (Walidata 436 ds, Data Prioritas, 36 kategori, 500 tags, format resource).
  URL dataset: `data.go.id/dataset/dataset/<slug>`.
- **Arsitektur** (dari reverse bundle JS): Next.js → `POST /api/proxy`
  (`{endpoint, method, body, token}`) → backend NestJS + **CKAN internal**
  (`ckan.app.svc.cluster.local:5000`, k8s — **saat ini error 500 di sisi mereka**) + file storage
  **AWS S3 `file.data.go.id`** (bucket `data`; listing 403, object publik-read).
- **Portalmu 2017 memang CKAN publik** (Wayback: `/api/3/action/package_list` = 200) — API
  CKAN publik-nya kini tidak lagi di-expose; proxy-nya hidup tapi backend CKAN-nya down.
- Subdomain langsung (`cur.`, `catalog.`, `api.`, `file.data.go.id`) = **403 Apache/S3 dari
  datacenter** (pola IP-restrict sama dengan `isb.lkpp.go.id`) → mungkin lolos dari IP
  residential (laptop) — worth 1 baris test bila diperlukan.
- **Nilai untuk MATA: pelengkap, bukan inti PBJ.** Isinya dataset indikator/kebijakan
  (pangan, BSSN, imigrasi, pariwisata, eWalidata 436 ds — sumber sama dengan
  `data.acehprov.go.id`). Tidak ada per-paket tender. Manfaat: konteks makro & dataset
  Walidata; integrasi programmatik tertunda (backend CKAN mereka down + endpoint search
  belum di-reverse) — UI portal tetap bisa dirujuk manual.

**Sumber mati (catatan, jangan diulang):** `lpse.acehtengahkab` (530, turun), `panda/kontrak/e-kontrak
.lkpp` (NXDOMAIN), `sirup.lkpp.go.id` (gagal koneksi dari sandbox), `e-katalog.lkpp` (no-data
anonim). `data.go.id` **bukan mati** — re-investigasi §2★8: portal hidup, API programmatik
tersendat (backend CKAN internal mereka down 500).

**Portal saudara kabupaten (12 Sep):** `satudata.acehtengahkab.go.id` = portal SDI Pemkab Aceh
Tengah, Next.js SPA (bukan CKAN, `/api/3` 404), **API `GET /api/dataset` terbuka (200) tapi
`{"rows":[],"count":0}`** — katalog masih dikurasi (pola "kurasi dataset" sama dengan
data.go.id). **Watchlist mingguan**: bila dataset muncul, jadi mirror lokal terakses-ringan.

---

## 3. Peta kebutuhan D1–D6 → sumber

| Indikator MATA | Field yang dibutuhkan | Sumber terbaik (urutan) |
|---|---|---|
| D1 — Pengumuman | nama paket, HPS, pagu, satker, metode, jadwal | C' `/dt/lelang` → C TenderUmumPublik → C-home (produksi) |
| D2 — Konsentrasi vendor | nama penyedia + nilai per vendor | C' filter `rekanan` → A (endpoint kontrak) → B detail |
| D3 — Pemenang ≈ HPS / nilai tinggi | nama pemenang, nilai kontrak vs HPS | C' (detail/tahap) + `kontrakStatus` → A kontrak → B |
| D4 — Vendor baru dapat paket besar | riwayat vendor + nilai | C' `tahun` multi + `rekanan` → A |
| D5 — Pemenang berulang | pola pemenang lintas paket/tahun | C' per-tahun (2013–2026 tersedia di filter) → C TenderUmumPublik per tahun |
| D6 — Nilai berulang/pola | nilai & metode per paket | C' → C |
| Ekstra — Sanksi vendor | daftar hitam, pelanggaran, masa sanksi | **C Sanksi Daftar Hitam** (unik!) → A |

---

## 4. Tools & skills untuk Hermes VPS (referensi 2026)

### Tier 1 — pakai sekarang (ringan, legal-bersih)
- **`pyproc`** (MIT, PyPI/GitHub `wakataw/pyproc`) — **temuan terpenting**: client SPSE terpadu +
  Satu Data sudah jadi; CLI + **MCP server** (bisa dicolok ke Hermes!); SQLite FTS index lokal;
  worker stealth (20 UA × 5 profil, rate-limiter dengan jitter — sopan); `pip install pyproc`.
  Referensi implementasi sesi anonim ada di `pyproc/lpse.py`.
- **`curl_cffi`** (Python) — impersonasi TLS/JA4; berguna jika 403 bersifat fingerprint-TLS
  (bukti: panduan 2026 `asadfix.github.io/scraping-guide` — "curl_cffi exists because of JA4").
- **CKAN client** — `requests` + `/api/3/action/package_search` (OPD/Prov/LKPP).
- Skill Hermes: **replikasi sesi anonim** (GET /lelang → ekstrak `___AT` → POST XHR) — 30 baris
  Python, tanpa dependensi baru, masuk `mata/spse_pub.py`.

### Tier 2 — jika VPS tetap diblokir (browser-grade; zona etis: gunakan volume rendah & identifikasi)
- **FlareSolverr** (GitHub `FlareSolverr/FlareSolverr`, Docker; fork aktif `AlexFozor/FlareSolverr`) —
  proxy solver Cloudflare: browser nyata menyelesaikan challenge, kembalikan HTML + cookie;
  arsitektur: VPS → FlareSolverr (session pool) → `spse_pub.py` memakai cookie+UA yang dikembalikan.
  Catatan README resmi: cookie clearance **wajib dipakai dengan UA yang sama**.
- **Scrapling** (BSD-3, ~75k⭐; `solve_cloudflare` built-in) — framework modern, tier HTTP+browser.
- **Camoufox** (MPL-2; Firefox C++ anti-fingerprint, ~11k⭐) / **Patchright** (Apache-2; Playwright
  patched) — perbandingan teknis: `github.com/pim97/anti-detect-browser-tools-tech-comparison`
  (Camoufox/Patchright/SeleniumBase/Botasaurus/XDriver/Obscura/Scrapling — klaim vs bukti per vendor).
- **Crawl4AI** (Apache-2, ~70k⭐) / **Crawlee** (Apache-2, ~24k⭐) / **Scrapy** (BSD-3, ~63k⭐) —
  jika volume membesar (multi-LPSE) — daftar: `scrapfly.io/blog/posts/best-open-source-web-scrapers`.
- **supacrawl** (MIT) — contoh stack 3-tier (Playwright→Patchright→Camoufox) + MCP, zero-infra.
- Skill Hermes: **session pooling & cookie reuse** (challenge sekali, reuse berhari-hari),
  **rate-limit + jitter**, **circuit breaker + stale-cache** (sudah ada di `spse_pub.py`),
  **normalisasi CSV/JSON → skema D1–D6**, **validasi silang** (HPS vs pagu, duplikasi kode tender).

### Tier 3 — managed API (terakhir; legal-clean tapi berbayar & pihak ketiga)
Zyte/ScrapingBee/ScraperAPI/Firecrawl — hanya jika Tier 1–2 gagal total; data pemerintah via
pihak ketiga menambah jejak yang sulit dijelaskan — **tidak disarankan** untuk MATA.

### Apa yang TIDAK perlu
- Proxy residential berbayar, CAPTCHA solving service, bot fleet — volumenya (1 LPSE, ~100 req/jam
  puncak) tidak membutuhkan itu; justru melanggar garis etik MATA.

---

## 5. Arsitektur yang direkomendasikan (multi-sumber, degradasi halus)

```
┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
│ C' /dt/lelang│  │ C Satu Data  │  │ C-home      │  │ B laptop     │
│ (sesi anonim)│  │ isb.lkpp     │  │ (produksi)  │  │ (push token) │
└─────────────┘  ──────┬───────┘  └────────────┘  └──────┬───────┘
       └────────────┬────┴─────────┬───────┴────────────────┘
              mata/spse_pub.py  (resolver berjenjang: C' → C → C-home → cache stale)
                    normalisasi skema D1–D6 + dedup by kode_tender
                    cache 30 mnt (data/spse_cache.json) + atribusi sumber per baris
                               │
                    /api/spse → panel "PBJ KAB. ACEH TENGAH"
                    (badge: LIVE / CACHE LAMA / sumber: …)  + toast error (M4)
```
- **Resolver berjenjang**: tiap fetch, coba C' → jika gagal C → jika gagal C-home → jika gagal
  cache lama + badge "CACHE LAMA". Panel tidak pernah kosong (prinsip yang sudah terbukti).
- **cron**: C-home 30 mnt; C' 60 mnt (lebih berat); C (CSV tahunan) harian.
- **Atribusi** (wajib S&T Satu Data): footer panel menampilkan API + tanggal update.
- **Hermes skills** yang harus dimiliki: (1) sesi anonim SPSE, (2) CKAN API, (3) FlareSolverr
  opsional, (4) normalisasi+validasi data, (5) monitoring staleness (alert Telegram — setelah
  token baru).
- **Sumbu konteks paralel (SAPA):** `mata/sapa_pub.py` (mirip `spse_pub.py`: fetch
  `daftar_data` 1× + LRU/cache 10 mnt + stale badge) → `/api/sapa` → panel "Indikator Resmi
  Kabupaten" (38 OPD, baseline APBD 1,318 T, kopi/PDRB/jalan) → **cross-check** sinyal MATA
  (pola tender jalan ↔ indikator Dinas PUPR; share vendor D2 ↔ baseline APBD). Sudah terbukti
  bisa diakses dari datacenter (200, no-auth) — **satu-satunya sumber resmi yang live diuji
  hari ini di luar panel SPSE homepage**. Pola kode: tiru `src/lib/sapa-client.ts` dari
  `Niumination/sapa-ai` (fetch → LRU 10 mnt → 503 graceful → status jujur).

---

## 6. Test P0 — jalankan di VPS (paste-ready, urut)

```bash
cd /root/Arck4li-AIHackfest/mata
# ── A) Satu Data eProc (C) — apakah IP VPS lolos? ──
curl -s -o /tmp/ml.json -w "MasterLPSE: HTTP %{http_code} (%{size_download}B)\n" \
  --max-time 20 "https://isb.lkpp.go.id/isb-2/api/satudata/MasterLPSE"
head -c 300 /tmp/ml.json; echo
# cari repoId Aceh Tengah (jika A lulus):
python3 - <<'EOF'
import json
try:
    d = json.load(open('/tmp/ml.json'))
    rows = d if isinstance(d, list) else d.get('data', d.get('result', []))
    for r in rows:
        s = json.dumps(r, ensure_ascii=False).lower()
        if 'aceh tengah' in s: print(json.dumps(r, ensure_ascii=False))
except Exception as e: print('parse:', e)
EOF

# ── B) SPSE sesi anonim (C') — replikasi mekanisme pyproc ──
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
B='https://spse.inaproc.id/acehtengahkab'
curl -s -c /tmp/cj.txt -H "User-Agent: $UA" "$B/lelang" -o /dev/null
echo "cookie: $(grep -o 'SPSE_SESSION[^ ]*' /tmp/cj.txt | head -1 | cut -c1-40)…"
curl -s -b /tmp/cj.txt -X POST "$B/dt/lelang" \
  -H "User-Agent: $UA" -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: $B/lelang" -H "Sec-Fetch-Mode: cors" -H "Sec-Fetch-Site: same-origin" \
  --data "draw=1&start=0&length=5&columns[0][data]=kode_paket&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=nama_paket&columns[1][search][value]=&columns[1][search][regex]=false&tahun=2026" \
  -w "\nPOST /dt/lelang: HTTP %{http_code}\n" | head -c 600

# ── C) pyproc (jika A/B mau dikonfirmasi dengan tool siap-pakai) ──
pip install pyproc -q && pyproc --help | head -20
pyproc satudata masterlpse --query "aceh tengah" 2>&1 | head -5
```

**Kirim hasilnya ke saya** — berdasarkan A/B/C langsung saya bangun `mata/satudata.py` +
resolver berjenjang di `spse_pub.py` + panel (pola yang sudah terbukti di commit 3ed634f).

---

## 7. Log probe sesi ini (bukti)

| Probe | Hasil |
|---|---|
| `data.go.id/api/3/action/*` | 404 — bukan CKAN; mati (konfirmasi) |
| `data.lkpp.go.id/api/3/action/package_list` | 200 (175B) — CKAN hidup |
| `data.acehprov.go.id/api/3/action/package_list` | 200 — CKAN hidup; 12 ds "pengadaan" (termasuk "Rencana Umum Pengadaan", "Data Realisasi Tender"), 1 ds "kontrak" |
| `opendata.acehtengahkab.go.id` | 200 — CKAN hidup; ds = statistik (0 "pengadaan"/"lelang") |
| `ppid.acehtengahkab.go.id` | 200 — hidup |
| `sirup.lkpp.go.id` | 000 — gagal koneksi dari sandbox |
| `satudata.inaproc.id/*` | 000 (DNS ok: 180.233.156.53, koneksi ditolak) |
| `inaproc.id/satudata` | 403 Cloudflare dari sandbox; **fetch proxy ok** — spec resmi: 4 layanan (KLPD, LPSE, Sanksi Daftar Hitam, Tender Umum Publik), **tanpa pendaftaran**, UU 14/2008, CC BY-NC-SA 4.0, kewajiban atribusi |
| `isb.lkpp.go.id/isb-2/api/satudata/{MasterLPSE,MasterKLPD}` | **403 Apache dari sandbox** (IP-based, bukan CF) → **test VPS** |
| `spse.inaproc.id/acehtengahkab/robots.txt` | `User-agent: * / Allow: /` + Allow eksplisit per-LPSE |
| `data.go.id/` + bundle JS (26 chunk) | 200 dari datacenter; arsitektur terpetakan: `POST /api/proxy` → NestJS + CKAN internal (k8s) + S3 `file.data.go.id` (bucket `data`) |
| `data.go.id/api/proxy` (POST, endpoint CKAN) | Proxy **bekerja** dari sandbox; meneruskan ke `ckan.app.svc.cluster.local:5000` → **500 I/O error (down di sisi mereka)**; path NestJS lain 404 rapi |
| `data.go.id/dataset?search=pengadaan` (render) | Katalog hidup: **670.326 dataset**, filter Walidata 436 ds; URL `data.go.id/dataset/dataset/<slug>` |
| `cur/catalog/api/file.data.go.id` | 403 Apache/S3 dari datacenter (IP-restrict; S3 = AWS us-east, bucket `data`) |
| Wayback `data.go.id/api/3/action/package_list` (2017) | 200 — portal lama memang CKAN publik (konfirmasi sejarah) |
| `satudata.acehtengahkab.go.id/api/dataset` | **200 `{"rows":[],"count":0}`** — portal SDI kab. live, katalog kosong (kurasi); `/api/kategori|opd|indikator` 404 | 12 Sep |
| `api-splp.layanan.go.id/sapa/1.0/api/daftar_data` | **200, 629.467 B, 2.067 record** (38 OPD, 2022–2026) **tanpa auth, dari datacenter**; endpoint lain (`daftar_opd`, `nilai_data`, `detail_data`, `v2/…`) 404 | 12 Sep |
| `Niumination/sapa-ai` (repo user) | `src/lib/sapa-client.ts`: pola produksi (fetch `daftar_data` + LRU 10 mnt + 503 graceful + status jujur); OAuth opsional `sapa.acehtengahkab.go.id/oauth/token` (client_credentials, client_id `3`) | 12 Sep |
| `mata/sapa_pub.py` (dibangun 12 Sep) | Modul MATA: fetch `daftar_data` + cache 10 mnt + stale + digest (baseline APBD, indikator PBJ) — **teruji**: 27 cek unit/mock ✅ + E2E `/api/sapa` live (2067 record, APBD Rp 1,32 T) + panel dashboard | 12 Sep |
| Source `pyproc/lpse.py` (raw) | endpoint Satu Data (`isb.lkpp.go.id/isb-2/api/satudata/…`); sesi anonim `SPSE_SESSION`/`___AT` dari `GET /lelang`; POST `/dt/{jenis}` + header XHR; filter `rekanan`, `kontrakStatus`, `tahun`, `kategoriId` |

## 8. Daftar referensi

**Komunitas / proyek (GitHub):**
- `github.com/wakataw/pyproc` — PyProc MCP (SPSE + Satu Data, MIT) + `pypi.org/project/pyproc`
- `github.com/topics/lpse` — ekosistem: `seimpairiyun/LPSE-2E`, `aansubarkah/ssa_agentic_lpse`,
  `venusdipagihari-ops/LPSEtenderscheduler-extension-` (Jul 2026), `smallest87/LPSE-Table-Scraper`
  (bypass validasi sesi dengan klik natif), `ramichaa/LPSE-Scraper`
- `github.com/sonicskye/lpse-parser`, `github.com/yfktn/spse-scraper` (norma izin admin LPSE),
  `github.com/ismaya/lkpp-lpse-grab` (pemenang lelang, 2014)
- `github.com/FlareSolverr/FlareSolverr` (+ fork `AlexFozor/FlareSolverr`; ekosistem: `camouflare`,
  `Solverr`, `cfsolver`, `limit-break`)
- `github.com/pim97/anti-detect-browser-tools-tech-comparison` — Camoufox/Patchright/dll (klaim vs bukti)
- `scrapfly.io/blog/posts/best-open-source-web-scrapers` (10 OSS 2026: Scrapy, Crawlee, Playwright,
  Camoufox, Crawl4AI, Scrapling, Colly, Maxun) · `nodemaven.com/blog/14-open-source-github-repos-for-web-scraping-in-2026`
- `supacrawl` (PyPI) — 3-tier engine + MCP · `asadfix.github.io/scraping-guide` (Cloudflare/Akamai 2026)

**Reddit / forum:**
- r/webscraping — "What am I legally and not legally allowed to scrape?" (Mar 2025)
- r/NewsAPI — "The Ultimate Guide to Legal and Ethical Web Scraping"
- r/PrivatePackets — "Is web scraping legal? A guide to laws and compliance" (Nov 2025)
- r/selfhosted — "Lightweight Flaresolverr replacement" (Nov 2024)
- `redditapis.com/blogs/is-scraping-reddit-legal-in-2026` — kerangka ToS vs hacking-law (Meta v. Bright Data)

**Resmi:**
- `inaproc.id/satudata` — S&T + lisensi + daftar layanan Satu Data eProc
- `latihan-lpse.lkpp.go.id/inaproclat/satudata` — spec API (field, parameter)
- UU 14/2008 (KIP) · PP 38/2016 (OPD) · UU ITE Pasal 30 · UU PDP 27/2022
- Preseden: hiQ v. LinkedIn · Van Buren v. US · Meta v. Bright Data

---
*Disusun dengan standar: setiap hasil punya dasar valid (probe langsung di §7, atau referensi ber-URL di §8).
Yang belum terverifikasi ditandai ⚠️ dan masuk test P0 §6 — tidak ada asumsi yang diloloskan.*
