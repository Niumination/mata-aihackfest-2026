# 📡 SUMBER DATA LIVE — VERIFIKASI & RANCANGAN (terverifikasi 11 Sep 2026)

**Verdict: sumber data pengadaan LIVE dapat diakses — melalui API Gateway resmi INAPROC
(`data.inaproc.id`) dengan token JWT. Tidak ada asumsi di dokumen ini: setiap klaim
memiliki bukti (log probe, respons API asli, atau halaman dokumentasi resmi).**

---

## 1. LOG BUKTI (semua dijalankan 11 Sep 2026)

| # | Pengujian | Hasil | Bukti |
|---|-----------|-------|-------|
| 1 | `panda.lkpp.go.id`, `kontrak.lkpp.go.id`, `e-kontrak.lkpp.go.id`, `spse.lkpp.go.id` via DNS global (Google DoH) | **NXDOMAIN** — subdomain lama LKPP sudah diturunkan, bukan masalah jaringan VPS | Response DNS `Status: 3` (NXDOMAIN) untuk keempatnya |
| 2 | `e-katalog.lkpp.go.id` via DoH | **NODATA** — tidak ada A record (bermigrasi) | `Status: 0` tanpa Answer |
| 3 | `inaproc.id` (e-Katalog 6.0) dari jaringan datacenter | **403 Cloudflare** (WAF; UA browser pun 403) | `curl` → 403; halaman error Cloudflare |
| 4 | `inaproc.id` dari **laptop pengguna (IP residensial)** | **TERBUKA** setelah verifikasi manusia | Laporan uji coba pengguna, 11 Sep 2026 |
| 5 | `lpse.acehtengahkab.go.id` | CNAME → `ars.inaproc.id`; **origin error** (http 530 / TLS gagal) — situs LPSE-nya sendiri bermasalah, bukan jaringan klien | `dig` + `curl` |
| 6 | `data.go.id` (portal open data nasional) | **200 OK**, `robots.txt: Allow: /` | `curl` + isi robots.txt |
| 7 | **`data.inaproc.id` — API Gateway INAPROC** — request nyata tanpa token | **GATEWAY HIDUP**: menjawab `{"error": "Authorization field missing"}` (respons JSON API, bukan halaman WAF) | `GET /api/v1/tender/pengumuman?limit=2` → JSON tersebut |
| 8 | Dokumentasi resmi API (halaman docs) | Terbaca: pendahuluan, spesifikasi 30+ endpoint, skema respons, proses akses, data freshness | `data.inaproc.id/docs/*` (link di §3) |
| 9 | Uji client MATA `live-test`/`live-collect` (kode baru) | Error handling bersih; skema normalisasi cocok dengan kolom DB (smoke test lolos); regresi `demo` utuh | Output test 11 Sep |

**Kenyataan penting (jujur):** seluruh zona `*.inaproc.id` di balik Cloudflare → dari
IP datacenter (sandbox/VPS) responsnya 403 **sebelum** autentikasi. Alur resmi meminta
**IP publik pemanggil didaftarkan saat request token** — artinya IP yang disetujui
diharapkan dilewati WAF. Poin ini **baru bisa diverifikasi setelah token turun**
(`run.py live-test` di VPS adalah uji buktinya).

---

## 2. APA ITU INAPROC API GATEWAY

Platform integrasi resmi LKPP (suksesor ISB LKPP, `isb.lkpp.go.id`) — satu titik akses
terstandarisasi untuk data pengadaan pemerintah: **Tender (tender & non-tender),
Vendor/Penyedia, RUP, E-Katalog, E-Kontrak**.

- Base URL: `https://data.inaproc.id/api/v1/` (ada juga `legacy` — hanya s.d. 31 Jan 2026; **pakai v1**)
- Autentikasi: `Authorization: Bearer <JWT_TOKEN>` (standar RFC 6750)
- Paginasi: **cursor** — `meta.cursor` + `meta.has_more`; `limit` 1–1000 (default 10)
- Envelope: `{success, data: [...], meta: {limit, has_more, cursor}}`
- Error codes terdokumentasi: 400/401/403/**429 (rate limit)**/500/503
- **Data freshness (docs resmi): "Periodic — beberapa jam s.d. 1 hari"** untuk endpoint tender/RUP/e-purchasing yang berubah harian → cocok dengan siklus MATA (jam/hari)
- Filter region: parameter **`kode_klpd`** (kode KLPD) → **bisa memantau Kabupaten Aceh Tengah spesifik**

### Endpoint kunci → aturan MATA (skema respons terdokumentasi di docs)

| Aturan MATA | Endpoint INAPROC | Field kunci (dari docs) |
|---|---|---|
| Feed utama (pengumuman) | `GET /api/v1/tender/pengumuman` | `nama_paket`, `nama_klpd`, `nama_satker`, `pagu`, **`hps`**, `kd_tender`, `kd_klpd`, `mtd_pemilihan`, `sumber_dana`, `status_tender`, `tgl_pengumuman_tender`, **`url_lpse`** (tautan sumber!) |
| **D1** harga vs referensi | `tender/pengumuman` (**`hps`**) + `tender/tender-ekontrak` (**`nilai_kontrak`**) | Deviasi `nilai_kontrak` vs `hps` = sinyal markup/HPS tidak wajar |
| **D2** konsentrasi vendor | `tender/tender-ekontrak`, `tender/non-tender-ekontrak-kontrak` | **`nama_penyedia`**, `nilai_kontrak`, `tgl_kontrak`, `no_kontrak`, `status_kontrak` |
| **D3** keroyokan akhir tahun | endpoint kontrak di atas (filter `tgl_kontrak` 22–31 Des) | tanggal + nilai kontrak |
| **D4** vendor kecil menang besar | endpoint kontrak + `ekatalog/penyedia-detail` (profil/track-record penyedia) | `nama_penyedia`, `nilai_kontrak`, `bentuk_usaha_penyedia`, `alasan_addendum` |
| **D6** pola nilai identik | endpoint kontrak (Counter atas `nilai_kontrak`) | `nilai_kontrak` |
| Bonus (RUP = rencana) | `rup/paket-penyedia`, `rup/paket-penyedia-terumumkan`, `rup/master-satker` | deteksi "direncanakan vs terealisasi" + **master satker = cara mencari kode_klpd Aceh Tengah** |
| Bonus (harga katalog) | `ekatalog/paket-e-purchasing`, `ekatalog/list-produk-penyedia` | referensi harga pasar untuk D1 (lebih kuat dari HPS) |
| Health API | `dashboard/last-update` | monitor kesegaran data |

Link docs:
- Pendahuluan: https://data.inaproc.id/docs/dokumentasi
- Spesifikasi API (semua endpoint): https://data.inaproc.id/docs/spesifikasi-api
- Contoh endpoint (skema lengkap): https://data.inaproc.id/docs/spesifikasi-api/api-v1/tender/list-pengumuman-get
- Migrasi ISB (mapping lama→baru): https://data.inaproc.id/docs/dokumentasi/guides/migration-from-isb
- Proses akses: https://data.inaproc.id/docs/dokumentasi/mulai-integrasi (+ halaman `access-verification`, `generate-token`)
- Data freshness: https://data.inaproc.id/docs/dokumentasi/tutorial/caching-strategy
- Developer Portal (token): https://data.inaproc.id/portal · Akun: https://akun.inaproc.id

---

## 2b. JALUR C — OPEN DATA LKPP (TANPA REGISTRASI, TERVERIFIKASI 11 Sep 2026)

**`data.lkpp.go.id`** — portal open data resmi LKPP (CKAN), API publik **tanpa auth,
tanpa WAF, reachable langsung dari IP datacenter** (bukti: `curl` → 200;
`package_list`/`package_search` menjawab JSON).

Dataset terverifikasi (diunduh + diinspeksi isinya):
| Dataset | Isi (bukti) | Update |
|---|---|---|
| **Nilai Perencanaan dan Realisasi PBJ** | 658 K/L/PD × {RUP, Realisasi}: 415 kabupaten, 93 kota, 38 provinsi, 59 kementerian, 53 lembaga — **termasuk Kabupaten Aceh Tengah (RUP Rp 484,6 M; realisasi Rp 138,6 M = 28,6%, TA 2025)** | **2026-03-31** |
| Data E-Katalog | 631 instansi × total realisasi e-purchasing (agregat) | 2025-03-04 |
| Data Monitoring PBJ KLPD | 632 K/L/PD × RUP vs realisasi TA 2023 (agregat) | 2025-03-04 |
| "Daftar Pemenang Konstruksi" | ⚠️ hanya 4 baris agregat jumlah penyedia — **bukan** data per-paket | 2025-03-04 |

**Implikasi jujur:** jalur C memberi MATA **mode LIVE v1 = monitoring agregat
per K/L/PD** (kesenjangan rencana vs realisasi, konteks serapan, ranking daerah) —
bukan deteksi anomali per paket. Data per-paket tetap hanya di Jalur A (token)
atau Jalur B (laptop).

**Sudah dibangun & teruji (11 Sep):** `mata/mata/live_lkpp.py` + `run.py live-open`
— fetch CSV via API CKAN → snapshot audit `output/live_lkpp/` → laporan fokus
Aceh + 5 K/L/PD serapan terendah nasional. Output nyata: Kabupaten Aceh Tengah
Rp 484,6 M → Rp 138,6 M (28,6%); terbawah nasional: Kab. Yahukimo 0,0%.

---

## 3. PROSES AKSES RESMI (Jalur A — production 24/7 di VPS)

1. **Daftar/verifikasi akun** di `akun.inaproc.id`
2. **Ajukan peran "Data Integrator"** (di Manajemen Akses)
   - Catatan jujur dari docs: *"Layanan ini diutamakan bagi instansi KLPD"* → sebagai
     individu, **persetujuan tidak dijamin**. Framing pengajuan: proyek open-data/
     kepentingan publik (watchdog akuntabilitas pengadaan), bukan komersial.
3. **Kirim Surat Permohonan Akses ke LKPP** (formulir: info organisasi, penanggung
   jawab, tujuan integrasi, estimasi volume; surat bermeterai — untuk individu: surat
   pengantar pribadi + KTP; cek checklist di halaman `access-verification`)
4. **Developer Portal** (`data.inaproc.id/portal`) → **request JWT token**:
   - **Daftarkan IP publik VPS** (wajib — ini yang menentukan VPS bisa memanggil API)
   - Pilih API yang dibutuhkan (minimal: `tender`, `ekatalog`, `rup`)
5. **Review admin LKPP**: token 1–3 hari kerja (role bisa lebih lama)
6. **Uji bukti**: `python3 run.py live-test` di VPS → harus menampilkan baris pengumuman nyata

**Estimasi total: beberapa hari kerja** → tidak masuk sprint 5 hari; ini jalur
production pasca-kompetisi. **Ajukan SEKARANG** supaya proses review berjalan paralel
dengan sprint.

### Jalur B — sekarang (human-in-the-loop), jika token belum turun
Kolektor berjalan di **laptop (IP residensial, manusia yang lewat verifikasi)** →
data disinkronkan ke VPS → MATA menganalisis 24/7. Arsitektur sah & sesuai etika MATA.
Butuh: pengamatan endpoint yang dipanggil SPA (DevTools → Network) — prosedur di pesan
terdahulu. Jalur ini menjadi fallback sampai Jalur A aktif.

---

## 4. KODE YANG SUDAH SIAP (teruji 11 Sep 2026)

| File | Fungsi |
|---|---|
| `mata/mata/live_api.py` | Client INAPROC v1: Bearer JWT, cursor pagination (limit 1000), backoff 429, timeout, **raw snapshot per respons** di `output/live_raw/` (audit: setiap angka telusur), normalisasi → skema `announcements` MATA |
| `run.py live-test` | Uji koneksi 5 baris → bukti token+IP bekerja end-to-end |
| `run.py live-collect` | Kumpulkan `tender/pengumuman` + `tender/tender-ekontrak` + `tender/non-tender-ekontrak-kontrak` (filter `tahun`+`kode_klpd`) → upsert DB + raw snapshot |
| `config.json → inaproc` | `base_url`, `jwt_token`, `tahun`, `kode_klpd` (token = rahasia, tidak pernah di-commit) |

Alur setelah token turun:
```bash
# 1) isi config.json: inaproc.jwt_token + kode_klpd (cari "Aceh Tengah" via rup/master-satker)
python3 run.py live-test          # bukti: 5 baris pengumuman nyata
python3 run.py live-collect       # data LIVE masuk DB (raw snapshot di output/live_raw/)
python3 run.py cycle              # rule engine D1-D6 membaca data LIVE — kode aturan TIDAK berubah
```
Dashboard menampilkan badge **MODE: LIVE** (penambahan kecil di `web.py` saat data live ada).

**D1 live didefinisikan jujur**: `nilai_kontrak` vs `hps` (referensi resmi pemerintah)
— bukan harga pasar bebas. Referensi harga katalog (`paket-e-purchasing`) ditambahkan
jika endpoint-nya terbuka untuk token kita.

---

## 5. RISA & KEJUJURAN (tanpa poles)

1. **Approval tidak dijamin** (prioritas KLPD). Mitigasi: ajukan dengan framing kepentingan publik + Jalur B sebagai fallback.
2. **WAF datacenter**: VPS mungkin tetap 403 walau token valid, jika IP tidak masuk allowlist. Mitigasi: daftarkan IP publik VPS dengan benar saat request token; uji `live-test` = bukti biner (bisa/tidak).
3. **Data e-Katalog = kontrak & pengumuman, bukan seluruh pengadaan** (swakelola via `pencatatan-swakelola` tersedia terpisah — bisa ditambah).
4. **Kompetisi**: video & artikel tetap mode synthetic + framing jujur (tidak diubah); dokumen ini memperkuat bagian "Kejujuran teknis" artikel: portal lama diturunkan (bukti NXDOMAIN), API resmi ditemukan & dialirkan pengajuannya, collector source-agnostic.

---

## 6. AKSI (urut)

| Kapan | Aksi | Siapa |
|---|---|---|
| **Hari ini (12 Sep pagi)** | Daftar `akun.inaproc.id` → ajukan Data Integrator → kirim Surat Permohonan (daftar **IP publik VPS**) | Pengguna (±30 mnt) |
| Hari ini | Sync `live_api.py` + `run.py` ke VPS (blok di pesan chat) | Pengguna |
| Malam ini | **Rekam video** (tanpa perubahan — kit 12 tetap berlaku) | Pengguna |
| Minggu | Upload video + publish artikel (bagian Kejujuran teknis diperbarui dgn fakta §1–§2) | Keduanya |
| Token turun (1–3+ hari kerja) | `live-test` di VPS → `live-collect` → mode LIVE aktif | Keduanya |
| Pasca-kompetisi | Pilot live 2 minggu (Aceh Tengah), validasi kualitas manual, lalu perluas daerah | Keduanya |
