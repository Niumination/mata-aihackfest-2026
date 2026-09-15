# BLUEPRINT MATA — AI Agent Watchdog Akuntabilitas Pengadaan

> Dokumentasi sistem lengkap: dari nol hingga produksi.
> Fakta, bukan klaim — setiap klaim merujuk ke kode, data, atau log
> (`aihackfest/15-jalur-sumber-data-legal.md` §7, `docs/WORKLOG.md`).
> Produksi: **mata.niumination.web.id** (sebelumnya `http://103.30.146.232:8080/`).
> Konteks: AI HackFest 2026 — kategori Productivity & Personal AI.

---

## 1. Visi & masalah

**Masalah:** data pengadaan pemerintah sudah publik, tetapi tidak ada yang
membacanya secara sistematis untuk rakyat. Lembaga pengawas punya antrean
kerja; warga tidak punya waktu, keahlian, atau alat. (Angka konteks: BPKP —
kerugian manipulasi penganggaran/pengadaan hingga Rp141 T; KPK Des 2025 —
pengaturan lelang perkeretaapian Medan.)

**Jawaban MATA:** AI agent 24/7 di VPS murah yang (1) mengumpulkan data
pengadaan publik, (2) menganalisis dengan aturan deterministik yang
transparan, (3) menerbitkan **indikasi yang bisa ditelusuri per paket** —
bukan vonis.

**Daerah fokus pertama:** Kabupaten Aceh Tengah (asal pembangun; pola
sistemnya multi-wilayah).

## 2. Prinsip (dipatuhi, tidak dipajang saja)

1. **Indikasi, bukan vonis.** Setiap output memakai kata "indikasi";
   rekomendasi selalu "verifikasi ke sumber dulu, laporkan via kanal resmi".
2. **Transparan & bisa diaudit.** Aturan = kode deterministik; rumus + ambang
   dipublikasikan di repositori (dan di artikel). LLM **tidak memutuskan** —
   hanya menyusun narasi.
3. **Data publik saja, jalur yang sah.** Hanya endpoint yang memang dipanggil
   situs publiknya sendiri (tanpa login, tanpa bypass, tanpa proxy pihak
   ketiga, tanpa eksekusi di browser pengguna). Jika jalur diblokir WAF, MATA
   **tidak memaksanya** — degradasi halus + catat (bukti: `data.inaproc.id`
   dari IP datacenter 403 → jalur G2 laptop & VPS-direk dipilih, keduanya
   legal karena path-nya tidak diblokir).
4. **Human-in-the-loop.** MATA tidak mengirim apa pun secara otomatis ke
   pihak luar; notifikasi internal (Telegram) hanya ringkasan.
5. **Jujur tentang gap.** Aturan yang kekurangan data (D1, D3) **tidak
   berjalan** — dan hal itu ditulis di dashboard/artikel, bukan disembunyikan.
6. **Murah & reproducible.** 4 core / 4GB / 20GB; deterministik; bisa
   di-clone dan dijalankan siapa pun.

## 3. Arsitektur

```
                     ┌────────────────────────────────────────────┐
  SUMBER PUBLIK      │              VPS (4c/4GB, idwebhost)       │
 ┌──────────────┐    │                                              │
 │ INAPROC BFF  │────┼─► collectors ─► SQLite (announcements) ─   │
 │ data.inaproc │  HTTP│  (urllib, jeda, dedup, idempoten)      │   │
 │ .id (tanpa   │    │                              ▼           │   │
 │  login)      │    │                     rules.py            │   │
 ├──────────────┤    │   D1–D6 deterministik  ▼                │   │
 │ SPSE LKPP    │────┼─► spse_pub ─► cache JSON ─► /api/spse   │   │
 │ (lelang+riot)│    │                     ▼                    ▼   │
 ├──────────────┤    │              inaproc_pub ─► flags_latest.json
 │ SAPA (OPD)   │────┼─► sapa_pub ─► cache (2.067 rec)  ┌──────────┴───┐
 └──────────────┘    │                                │  web.py :8080  │
  data/*.json (kol.  │                                │  dashboard    │
  penuh: 1.250 paket │                                │  (Python,     │
  + 15.105 RUP)      │                                │  tanpa depend.│
        │            │                                │  berat)       │
        └──────────────► collect_inaproc (file) ─────►  │  + /api/*   │
                     │  (deterministik, offline)        └──────┬───────┘
                     │                                          │
                     │  cycle (cron + run.py cycle):            │
                     │  collect → rules → narrative →           │
                     │  dossier (PDF+draft APIP) → notify ──────┤
                     │  (Telegram tiap 3 jam, fail-safe)        │
                     └──────────────────────────────────────────┘
```

**Alur satu siklus** (`run.py cycle`):
1. **Koleksi** — `collectors.run_collect(cfg)` sesuai mode (`inaproc`: file
   deterministik 1.250 paket; `synthetic`: 48 record demo; idempoten via PK).
2. **Analisis** — `rules.run_rules()` pada rekaman fiskal aktif → daftar
   `Flag` (rule_id, severity, evidence, record_ids, metrics).
3. **Narasi** — `narrative.explain()` template deterministik (LLM opsional,
   fallback otomatis).
4. **Dossier** — PDF + draft laporan APIP + ringkasan publik (`output/`).
5. **Notifikasi** — Telegram bila indikasi berubah atau ≥3 jam; token kosong
   = no-op (fail-safe, siklus tetap sukses).

## 4. Komponen

| File | Peran |
|---|---|
| `mata/collectors.py` | Kolektor (synthetic / **inaproc** dari file koleksi penuh; vendor sampah difilter) |
| `mata/inaproc_pub.py` | Sumber inti per-paket: BFF `data.inaproc.id/dashboard-api` (tanpa auth) + cache 10 mnt + stale |
| `mata/spse_pub.py` | SPSE LKPP Aceh Tengah (pengumuman terkini + jalur riwayat `B'` terbukti 12 Sep) |
| `mata/sapa_pub.py` | SAPA daerah — 2.067 record, 38 OPD (baseline APBD, indikator PBJ) |
| `mata/rules.py` | Rule engine D1–D6 (deterministik, ambang dari config) |
| `mata/narrative.py` | Penjelasan per indikasi (template; LLM opsional) |
| `mata/engine.py` | Orkestrasi siklus 5 langkah |
| `mata/web.py` | Dashboard + semua `/api/*` (Python stdlib, tanpa framework) |
| `mata/chat.py` | "Tanya MATA" — jembatan terisolasi ke agen Hermes (lihat §7) |
| `mata/dossier.py` | PDF + draft APIP + ringkasan publik |
| `mata/notify.py` | Telegram (ringkasan, dedup sinyal) |
| `mata/analisis.py` | Agregasi deterministik D2 + RUP-vs-Realisasi + repeat lintas tahun |
| `mata/edge_feed.py` | Jalur G (backup): push dari browser IP-ISP, fail-closed (token) |
| `mata/db.py` | SQLite ringan (announcements, runs, chat_log) |
| `scripts/rup_full_collect.py` | Kolektor RUP penuh (VPS; limit=100+offset, jeda 2 s) |
| `scripts/spse_collect.py` | Kolektor SPSE periodik |

## 5. Sumber data & legalitas (bukti, bukan asumsi)

| Sumber | Jalur | Bukti (12 Sep) | Etika |
|---|---|---|---|
| INAPROC `data.inaproc.id` | BFF publik yang dipanggil SPA-nya sendiri (`/dashboard-api/*`, tanpa auth). WAF memutuskan **per-IP**: IP VPS tidak diblokir untuk path ini | 200 + data riil (662+599 paket; 15.105 RUP); last-update harian ±02:47 WIB | 4 request/refresh; limit=100 dihormati; jeda 2 s saat koleksi; atribusi di panel |
| SPSE `spse.inaproc.id/acehtengahkab` | Sesi anonim `SPSE_SESSION` + `authenticityToken` (resep komunitas `pyproc`) | `GET /lelang` 200; `POST /dt/lelang` 200 (riwayat) | hanya data publik; rate-limit sopan |
| SAPA `api-splp.layanan.go.id` | API daftar data terbuka (tanpa auth) | 200, 2.067 record, 38 OPD | cache 10 mnt |

**Bukan bypass:** tidak ada proxy, tidak ada tool pemblokir-bypass, tidak ada
login pihak ketiga, tidak ada eksekusi JavaScript di sisi pengguna. Red-line
ini tertulis di `HERMES_BRIEF.md` dan dipatuhi.

## 6. Rule engine (dipublikasikan)

| Rule | Definisi | Ambang (config) | Status di data riil TA2026 |
|---|---|---|---|
| D1 | Harga di atas referensi | deviasi ≥30%, nilai ≥Rp500 jt | **Belum bisa** — sumber tak mempublikasikan ref harga (jujur, tertulis) |
| D2 | Konsentrasi penyedia | share ≥5% (dominasi) **atau** ≥15 paket (repetisi ekstrem) — kalibrasi 170 penyedia | **Aktif**: 2× tinggi (8,4%; 7,5%) + 9× rendah (16–25 paket) |
| D3 | Keroyokan akhir tahun | 10 hari, kontrak ≥Rp1 M, ≥2× median bulan lain | **Belum bisa** — sumber tak mempublikasikan tanggal tanda tangan |
| D4 | Vendor kecil menang besar | riwayat ≤3 proyek (terbesar <Rp400 jt) & kontrak ≥Rp1 M | **Aktif**: 1× tinggi (Rp3,12 M vs riwayat 1×Rp229 jt) |
| D6 | Pola nilai identik | nilai sama di ≥3 proyek | **Aktif**: 2× rendah (Rp94,35 jt ×3; Rp193,4 jt ×3) |
| D5/D7 | Proyek "hantu" / lelang tunggal | — | Roadmap (butuh foto geotag warga / data pelamar) |

Catatan data riil (jujur): ringkasan resmi menyebut 657 paket, koleksi penuh
mengambil 662 baris — selisih 5 baris dibiarkan apa adanya (di sisi sumber);
11 kode paket duplikat di TA2025 (kualitas data sumber).

## 7. Keamanan & etika

- **Chatbot terisolasi** (`chat.py`): pertanyaan pengunjung = **DATA** di
  prompt (bukan perintah); subproses agen `--safe-mode`, jail filesystem,
  `--max-turns 1`, tanpa aksi; batas 5 pertanyaan/jam per pengunjung
  (IP-hash); **setiap tanya-jawab di-audit** (`chat_log`); fallback
  deterministik bila backend sibuk (tidak pernah mengarang angka).
- **Kredensial**: `config.json` git-ignored; token edge **fail-closed**
  (tanpa token valid = tolak); token tak pernah dicetak di log/panel.
- **Red-line data**: tidak ada residential proxy / tool bypass / vendor
  pihak ketiga untuk data yang diblokir; jalur yang dipilih harus sah (bukti
  per jalur di doc-15 §7).
- **Bahasa output**: "indikasi", "perlu verifikasi", "laporkan via LAPOR! /
  Ombudsman / KPK / APIP" — tidak pernah "korup/bersalah/menipu".

## 8. Deployment & operasi

- **Infrastruktur:** VPS 4 core / 4GB / 20GB — [Cloud VPS](https://cloudbaik.com/)
  via [AI Hosting](https://idwebhost.com/ai-hosting/) (program AI HackFest
  2026); domain **mata.niumination.web.id** (gratis, program resmi IDwebhost —
  Instagram official).
- **Service:** systemd (`deploy/mata.service`) menjalankan web + loop; cron
  memanggil `run.py cycle` periodik; notifikasi Telegram tiap ≤3 jam.
- **API publik:** `/api/flags` (indikasi), `/api/analisis` (agregasi + RUP
  vs realisasi), `/api/inaproc`, `/api/spse`, `/api/sapa`, `/api/edge`,
  `/api/chat` (POST + GET poll), `/api/records.csv` (1.250 baris — verifikasi
  publik per paket).
- **Degradasi:** cache + stale badge; file hilang = panel kosong rapi;
  token kosong = no-op; backend chat mati = fallback lokal.

## 9. Timeline dari nol → produksi

| Tanggal | Milestone (bukti di doc-15 §7) |
|---|---|
| 11 Sep | Hari-1 sprint: arsitektur, rule engine, dashboard, Hermes Agent, deploy VPS (`:8080`) |
| 12 Sep siangnya | P0 jalur data: SPSE `B'` terpecah (authenticityToken), SAPA live, INAPROC VPS-direk dikonfirmasi (WAF per-IP) |
| 12 Sep malam | Koleksi penuh realisasi (662+599) + RUP (15.105 baris); analisis D2; **integrasi inti** (data riil → aturan → 14 indikasi); **MODE: LIVE** produksi; artikel v2 |
| 13 Sep | Domain `mata.niumination.web.id` (port 80), artikel publish, audit final (T0) |
| 14–15 Sep | Video demo (sebelum akhir masa VPS) |
| 15 Sep 23:59 WIB | **Titik final / freeze** — keadaan submit (VM Batch 3 dinonaktifkan panitia) |

## 10. Reproduksi (1 terminal)

```bash
git clone https://github.com/niumination/mata-aihackfest-2026 mata && cd mata/mata
cp config.example.json config.json          # mode sudah "inaproc"
python3 run.py cycle                         # 5 langkah; flags di data/flags_latest.json
python3 run.py web -p 8080                   # dashboard
```
File data (`data/realisasi_*_full.json`, `data/rup_*_full.json`) sudah ikut
repositori → siklus deterministik dan **offline-capable**.

## 11. Kutipan harian (F1) & keterbatasan (jujur) & roadmap

**F1 — widget kutipan harian:** strip tipis di bawah ticker; 5 kutipan
kurasi (QS An-Nisā' 4:58 & 4:29; hadis Muttafaq 'Alaih — Bukhari & Muslim:
2928/6860/1829, 6413, 6094/2607) dengan sumber kitab/numasi eksplisit;
rotasi harian deterministik (tanpa state). **Rollback instan:** hapus
`data/kutipan.json` (widget hilang di render berikutnya) atau `git revert`
commit F1.



**Keterbatasan:** D1 & D3 belum bisa berjalan pada sumber ini (tanpa ref
harga / tanggal); SPSE riwayat belum jadi kolektor periodik (jalurnya sudah
terbukti); a11y belum diuji manusia penuh; single-region.

**Roadmap (urutan di `docs/BACKLOG.md` §3):** F3 monitoring health ·
T2 HTTPS (Cloudflare Tunnel) · T3 token
INAPROC via Diskominfo · kolektor riwayat SPSE · trend multi-tahun · a11y
20/20 · D5 (foto geotag warga) & D7 (pelamar per tender).
