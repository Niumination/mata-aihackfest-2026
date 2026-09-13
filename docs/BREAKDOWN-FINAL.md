# DOX — BACKLOG & BREAKDOWN FINAL (13 Sep 2026)

> Dokumen induk perencanaan: breakdown semua permintaan terbuka + backlog
> pre-freeze & pasca-kompetisi. Sumber kebenaran untuk urutan kerja.
> Konteks: VPS bertahan ±3–4 hari lagi · titik final (freeze) = **16 Sep** ·
> submit ≤ 30 Sep.

---

## 0. Status repo & sinkronisasi (per 13 Sep)

| Lokasi | Commit | Catatan |
|---|---|---|
| VPS (produksi) | `92baf7a` | **T1 SELESAI** (label panel eksplisit `data-lbl`), MODE: LIVE, 14 indikasi |
| Mirror publik `niumination/mata-aihackfest-2026` | `92baf7a` | Terverifikasi **public** (HTTP 200), berisi kode+data penuh |
| Sandbox (workspace ini) | tersinkron ke `92baf7a` + commit baru | web.py T1, data RUP penuh 2 tahun, state produksi, artikel v2 |

**Gap yang ditemukan & diperbaiki:** artifact runtime VPS (`flags_latest.json`,
`status.json`, `output/*`) di commit terakhir masih versi demo → state riil
(14 indikasi) di-regenerasi deterministik di sandbox dan di-commit, agar zip
berikutnya membawa state produksi utuh.

**Domain .web.id** — konteks kompetisi (ditulis di artikel/form submit):
domain **gratis dari program resmi IDwebhost (Instagram official @idwebhost)**
— melengkapi narasi infrastruktur: VPS via [AI Hosting](https://idwebhost.com/ai-hosting/)
+ domain .web.id dari program IDwebhost. Ini nilai plus "ekosistem" untuk juri.

---

## 1. Breakdown permintaan (5 item)

### R1 — Domain .web.id → MATA produksi · **P0 (13–14 Sep)**
**Apa:** arahkan domain `.web.id` ke dashboard `103.30.146.232:8080`.
**Kenapa:** URL profesional untuk artikel (publish 13 Sep), video (14–15), dan
form submit; bonus narasi ekosistem IDwebhost.
**Efort:** ~15 menit (DNS) + ~10 menit (Hermes: port) · **Risiko:** rendah
(DNS publik, tidak menyentuh kode).

**PANDUAN KONFIGURASI:**
1. **Panel DNS IDwebhost** (dashboard hosting → tab Domain/DNS untuk domain
   `.web.id`-mu) → tambahkan record:
   - `A` · host `@` (akar) · value `103.30.146.232` · TTL 3600
   - (opsional) `A` · host `www` · value sama.
2. **Keputusan port** — dua opsi, pilih satu:
   - **Opsi A (rekomendasi, URL bersih):** Hermes alihkan service MATA dari
     `:8080` ke `:80` (ubah port di `deploy/mata.service` + restart; amankan
     firewall: biarkan 80, 22; 8080 boleh ditutup). URL: `https://domain-mu.web.id`
   - **Opsi B (paling aman, 5 menit):** tetap `:8080` → URL
     `http://domain-mu.web.id:8080`. Tidak ada perubahan di VPS.
3. **Verifikasi (setelah DNS menyebar, 5–30 menit):**
   `dig +short domain-mu.web.id` → harus `103.30.146.232`;
   buka URL di browser → badge MODE: LIVE terlihat.
4. **HTTPS (jika sebelum video):** lanjut T2 — Cloudflare Tunnel
   (lihat item T2 di §3). Jika domain belum siap saat video: pakai URL Opsi A/B
   apa adanya.
5. **Saat submit:** tulis di form: "produksi: `domain-mu.web.id`
   (domain .web.id dari program IDwebhost, gratis)".

### BLOK EKSEKUSI — USER (NS → Cloudflare, ±15–20 mnt)
> Panel IDwebhost hanya menu registry (ubah NS/lock/kontak) — record A
> dikelola di **Cloudflare (gratis)**. Domain final: **subdomain**
> `mata.niumination.web.id` (root `niumination.web.id` = cadangan
> portofolio/bisnis user, TIDAK disentuh MATA).
```
1. cloudflare.com → login → Add a site: niumination.web.id → plan Free
   → salin DUA name server yang ditampilkan Cloudflare
2. IDwebhost member area → niumination.web.id → Ubah Name Server
   → ganti dengan dua NS Cloudflare → simpan
3. Cloudflare: tunggu status Active (menit–jam). Lalu DNS → Add record:
     Type A | Name "mata" | Content 103.30.146.232 | TTL Auto | DNS only
   (JANGAN record "@" — root milik portofolio user)
4. (Opsional, T2 cepat) SSL/TLS → Overview → Flexible → https: aktif
Verifikasi: dig +short mata.niumination.web.id → 103.30.146.232
```

### BLOK PASTE-READY — HERMES VPS (port 80, ~10 mnt)
```bash
cd /root/Arck4li-AIHackfest/mata
grep -n "8080" deploy/mata.service        # lihat dulu baris port-nya
sed -i 's/-p 8080/-p 80/' deploy/mata.service   # sesuaikan dgn baris hasil grep
sudo systemctl daemon-reload && sudo systemctl restart mata
curl -s --max-time 5 http://127.0.0.1:80/ | grep -o "MODE: LIVE" && echo "PORT 80 OK"
sudo ufw allow 80/tcp 2>/dev/null || true
# SELESAI: http://mata.niumination.web.id (setelah DNS menyebar)
# (8080 boleh dibiarkan; domain tidak bergantung padanya)
```

### R2 — Master design prompt untuk designarena.ai · **P1 (siap dieksekusi)**
**Apa:** satu prompt desain komprehensif (bahasa Inggris, optimal untuk tool AI
desain) agar hasil desain sesuai karakter MATA + nilai plus juri.
**Kenapa:** aspek penilaian UI/UX; desain yang konsisten dengan narasi
"watchdog tenang, data-dense, bukan korporat-cantikan" = poin.
**Ruang lingkup prompt (akan ditulis di `docs/DESIGN-PROMPT-MATA.md`):**
- Persona & tone: "penjaga uang publik" — tenang, faktual, kredibel; BUKAN
  neon-fintech, BUKAN government-klise.
- Prinsip visual: data-dense tapi bernapas; hierarki angka besar (rupiah,
  %); satu aksen (merah-ember untuk sinyal) di atas netral gelap/terang.
- Sistem komponen wajib: badge MODE: LIVE, ticker indikasi, kartu indikasi
  (rule D1–D6 + severity), tabel top-penyedia, baris RUP-vs-Realisasi per SKPD,
  chatbot "Tanya MATA", ticker, footer atribusi + "indikasi, bukan vonis".
- Konten nyata utk di-render dalam mockup (angka produksi: 662 paket, 14
  indikasi, 26,6%, top-10 42,5%) — agar desain dinilai dengan data sungguhan.
- Constraint kompetisi: harus terasa "dibuat orang, untuk rakyat" — bukan
  template; aksesibilitas kontras AA; mobile-first secondary.
- Output: 1 page utama (dashboard) + 3 varian section + token warna/typo.

### R3 — Triase item hold (F/T/A11y) · **keputusan di §2**
| Item | Status | Rekomendasi | Alasan |
|---|---|---|---|
| F1 widget kutipan islami | desain disetujui | **BACKLOG** (kecuali user minta) | butuh kurasi hadist **shahih + sumber kitab** — risiko kekeliruan riwayat tinggi; nilai kompetisi < risiko; lebih aman pasca-kompetisi dengan kurasi teliti |
| F2 iframe agroclimate | menunggu build | **BACKLOG** | butuh build statis/Vercel (infra baru); panel IKLIM GAYO sudah menggantikan |
| F3 monitoring health | belum dibangun | **BACKLOG** | VPS mati beberapa hari lagi — monitoring tak berguna sebelum VPS baru; jadi item pertama pasca-kompetisi |
| T0 ponytail-audit | skill tersimpan | **PRE-FREEZE (14 Sep, ±20 mnt)** | audit kode sebelum freeze = deteksi bug terakhir; murah & mengurangi risiko di 16 Sep |
| T1 label panel | — | **SELESAI** `92baf7a` ✅ | — |
| T2 HTTPS (Cloudflare Tunnel) | butuh tunnel | **PRE-FREEZE, kondisional** | HANYA jika domain siap 13–14 Sep; URL https di video = nilai plus; jika tidak siap: skip (http sudah cukup untuk submit) |
| T3 token INAPROC Jalur A | pasca-kompetisi | **BACKLOG** | via Diskominfo — proses resmi, tidak kejar waktu |
| Artikel v2 LIVE | **MASUK REPO** `aihackfest/11-…` ✅ | **EKSEKUSI 13 Sep (user publish)** | tinggal publish + 4 screenshot |
| A11y penuh 20/20 | T1 sudah dikerjakan | **BACKLOG** (sisa) | butuh uji manusia; T1 menutup sebagian besar |

### R4 — Dokumentasi lengkap sistem (blueprint → production) · **P1 (siap dieksekusi)**
**Apa:** paket dokumentasi resmi di `docs/`:
- `docs/BLUEPRINT.md` — visi, masalah, prinsip (indikasi bukan vonis),
  arsitektur (diagram komponen + alur data), diagram alur siklus,
  keamanan & etika (isolasi chatbot, red-line data), timeline dari nol →
  produksi (hari 1 → 12 Sep, milestone riil), cara reproduksi (1 perintah),
  API endpoints, config, roadmap.
- Sumber: kode + log §7 doc-15 + WORKLOG (fakta, bukan klaim).
**Kenapa:** juri menilai kelengkapan & proses; juga aset submit (tautan repo
dengan dokumentasi = profesional).
**Efot:** ~1 sesi (file 2–3, tanpa mengubah kode).

### R5 — Artikel v2 LIVE · **SELESAI (siap publish 13 Sep)**
`aihackfest/11-draf-artikel.md` (1.355 kata, 2 backlink, angka produksi).
Sisa = eksekusi user: publish + 4 screenshot (daftar di catatan bawah artikel).

---

## 2. Urutan eksekusi → freeze 16 Sep

| Hari | Aksi | Pelaku |
|---|---|---|
| **13 Sep** | (1) User: record DNS `mata.niumination.web.id` + publish artikel + 4 screenshot + tes backlink. (2) Hermes: port 80 (blok di atas) + sinkron mirror publik + T2 jika domain siap. (3) **R2 + R4 + F1 SUDAH DISELESAIKAN di sandbox** (file di repo) | user/Hermes/sandbox |
| **14 Sep** | T0 ponytail-audit (hasil → fix kecil jika ada) + **REKAM VIDEO** | Hermes/user |
| **15 Sep** | buffer video (re-take jika perlu) + finalisasi form submit (URL artikel, URL domain, URL repo, video) | user |
| **16 Sep** | **TITIK FINAL / FREEZE** — tidak ada perubahan kode; sistem dalam keadaan submit | semua |

## 3. Backlog pasca-kompetisi (urutan)
1. F3 monitoring health (VPS baru: systemd + uptime check + alert Telegram)
2. F1 — evaluasi hasil: kalau sesuai, tambah kutipan + kurasi lanjutan; kalau tidak, rollback (lihat §4)
3. T2 HTTPS (jika belum) + T3 token INAPROC via Diskominfo
4. Kolektor riwayat lelang SPSE (jalur B' sudah terbukti 12 Sep)
5. Trend multi-tahun + perbandingan vendor antar TA
6. A11y 20/20 (uji manusia + screen reader)
7. F2 agroclimate (build statis/Vercel)
8. D5 (foto geotag warga) & D7 (pelamar per tender)

## 4. Keputusan yang dibutuhkan user
1. **Nama domain** `.web.id` yang dimiliki?
2. Domain **sekarang** (masuk artikel/video) atau **pasca-kompetisi**?
   (Rekomendasi: sekarang, Opsi A port 80 — 15 menit, URL bersih.)
3. **R2 + R4** dieksekusi sekarang (file di repo, tidak menyentuh VPS)?
4. F1: tetap backlog (rekomendasi) atau mau dipaksa pre-freeze?
