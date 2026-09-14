# WORKLOG MATA — record pekerjaan

## 2026-09-11 (Sesi Hermes)

### Status & sinkron repo
- Laporan kondisi MATA (48 record, 5 indikasi) terkirim.
- `git pull origin main` → fast-forward `72dc5b4..997f5f1` (v2: live API,
  LKPP open data, artikel, kit rekam). Stash lokal kedaluwarsa dibuang.
- Output diregenerasi dengan kode baru (presisi 27,5%).

### Fitur (semua terverifikasi tool, bukan klaim)
- Filter MBG: `mata/mata/mbg.py` + `--mbg/--keyword` di `live-collect`.
- Dashboard interaktif → tema codex → susunan hero+grid+graf+reader →
  boot sinematik + backsound WebAudio → tipografi konten → mobile 640px.
- Widget pengunjung + izin lokasi consent-first (UU PDP) + peta OSM/Leaflet.
- Kolektor open data v2: SIRUP, katalog, realisasi 12 bln + kurva, PDN,
  10 indeks nasional LKPP. Semua dari `data.lkpp.go.id` (tanpa auth).
- Tanya MATA: jembatan Hermes terisolasi (`--safe-mode --max-turns 1
  --run-budget`, jail dir, rate 5/jam, audit) via **opencode-free**
  (bukan mimo). Fallback lokal grounded bila backend gagal.
- Panel: rel 56px ala template, zoom dalam grid, scrollbox, collapse terbukti
  via Chromium sungguhan (screenshot + klik).

### Koreksi record (penting)
- **(20:xx) Klaim "notifikasi Telegram terkirim" SALAH.** Token di
  `config.json` mati (401 Unauthorized, diverifikasi via getMe).
  Notifikasi kron maupun manual GAGAL. Butuh token baru dari pemilik.
- Health monitoring (service+cron+skrip) ternyata SUDAH jalan — dugaan
  "belum dikerjakan" keliru; dibuktikan via log.

### Kebutuhan dari pemilik
1. Token bot Telegram baru (BotFather) → `mata/config.json`, jangan commit.
2. Token INAPROC (Jalur A) untuk data per-paket live.
3. HTTPS bila ingin GPS presisi browser.

### Perbaikan chat, opendata, iklim (sesi malam)
- **Bug chat "Di luar kemampuan MATA"** untuk "Bagaimana cara melapor?":
  akar = prompt terlalu sempit (aturan 4 menolak semua di luar angka).
  Perbaikan: prompt izinkan sapaan/definisi MATA/cara melapor + kanal
  pelaporan sebagai konteks valid; guard di `_run` ganti penolakan keliru
  dengan fallback spesifik. Teruji: lapor → panduan lokal; topik asing
  tetap ditolak.
- **Demo → opendata**: 48 baris paket kini link `opendata ↗` ke dataset SIRUP
  LKPP; panel konteks punya daftar "Sumber terbuka" (SIRUP/Katalog/Realisasi/
  PDN/IKP/Saing). CSS `.demo-tag` mati dihapus.
- **Iklim Gayo di panel peta**: `mata/mata/iklim.py` (port logika
  niu-gayo-agroclimate, 15 sentra, ambang identik), Open-Meteo via server +
  cache 30 mnt (IP pengunjung tak tersebar), endpoint `/api/iklim`,
  dropdown + advis kopi & siaga di bawah peta OSM. Teruji live
  (Takengon 16,8°C, Pegasing OK).
- **Bug lanjutan iklim (diperbaiki)**: (1) lencana risiko ter-escape jadi
  teks mentah (`row()` meng-escape HTML pil) → tambah `rowh()`;
  (2) seluruh isi iklim tak terbaca — `.orow`/`.dim` bertinta terang untuk
  panel gelap, panel peta terang → tambah override `.panel.light`.
  Teruji via Chromium + screenshot: baris + pil warna tampil.

### Skill & ekosistem
- Trust repo ke Hermes; impeccable proyek+global; DESIGN.md ditulis.
- `~/ecosystem-config` diklon + dipindah ke home (hindari nested repo).
- Rencana adopsi: `docs/RENCANA-ADOPSI-ECOSYSTEM.md`.
- Pilihan skill: `docs/SKILL-UNTUK-MATA.md`.

### Notifikasi per 3 jam (12 Sep)
- Rekap Telegram tiap siklus (per jam) terlalu berisik. `engine.py`:
  `NOTIFY_EVERY=3 jam` + `flags_sig`; kirim bila ≥3 jam ATAU indikasi
  berubah; `last_notify`/`flags_sig` tersimpan di status (cabang gagal
  ikut menjaga). Deteksi tiap jam tetap jalan. `mata.service` di-restart.
- Koreksi: token Telegram ternyata VALID (getMe 200) — pemilik tampaknya
  sudah memperbarui; klaim 401 dicabut.

### Adopsi refactor UI/UX M0–M6 (12 Sep, dari workspace pemilik)
- Paket `workspace-*.zip`: `web.py` baru (1445 baris, drop-in, sudah memuat
  iklim/opendata/rowh) + `DESIGN.md` v3 + `aihackfest/14-audit-uiux-dashboard.md`.
- Verifikasi di VPS (sandbox paket tak punya headless browser): compile bersih,
  120KB, rv-init 6, 0 f-string bocor, 0 warna lama, toast ada, 48 opendata,
  4 API 200; Playwright: desktop + chat + mobile 390px, 0 JS error.
  Screenshot: hero/ticker/3 panel/toast iklim OK; mobile 1 kolom rapi.
- Backup pra-swap: /tmp/web.py.bak.2026-09-12, /tmp/DESIGN.md.bak.2026-09-12.

### Jalur B SPSE live (12 Sep, dari mata-ai-3.zip)
- Modul baru `mata/mata/spse_pub.py` (parse/cache/token-push) + kolektor
  laptop `mata/scripts/spse_collect.py` (Jalur B, cookie browser) + panel
  "PBJ Kab. Aceh Tengah — SPSE Publik" (`/api/spse`, `/api/spse-push`).
- Teruji adaptasi `_test_spse.py`: parse 12/12, token gate, 2 endpoint,
  panel tampil. **Live dari VPS: 12 paket nyata** (6 tender + 6 non-tender,
  mis. Jembatan Pantan Reduk Rp1M, 3 tender ulang). Cache 30 mnt.
- Butuh dari pemilik: jalankan kolektor di laptop (cookie CF) + set
  `spse.push_token` bila ingin riwayat/pemenang; homepage publik sudah
  mengalir tanpa itu.

### SAPA + uji P0 (12 Sep, dari mata-ai-4.zip, dok 16)
- Modul `mata/mata/sapa_pub.py` + panel "INDIKATOR RESMI" (`/api/sapa`) +
  `mata/_test_sapa.py` + dok 15/16. Uji: SEMUA LULUS termasuk LIVE
  (2067 record, baseline APBD Rp 1,32 T). Produksi: `/api/sapa` live,
  38 OPD, 2022–2026.

### Jalur G edge + temuan BFF (12 Sep malam, dari mata-ai-5.zip, dok 17)
- `mata/mata/edge_feed.py` + `/api/edge` + `/api/edge-push` (token) +
  `scripts/edge_collect.py` + `scripts/rup_browser_collect.py` + dok 17.
  Token edge diset, `/api/edge` OK (n=0).
- RECON: shell 200 + 17 bundle JS → endpoint BFF `/dashboard-api/...`
  (`/rup/table`, `/realisasi/table`, ...). **Keduanya HTTP 200 dari VPS**:
  RUP per-paket (kode/nama/nilai/satker, filter satker jalan) +
  realisasi berpemenang (nama_penyedia, tahapan). Laptop mungkin tak perlu
  untuk 2 dataset ini — keputusan arsitektur di pemilik.

### Panel INAPROC live (12 Sep, dari mata-ai-6.zip)
- `mata/mata/inaproc_pub.py` + `/api/inaproc` + panel "REALISASI PENGADAAN"
  (badge LIVE · INAPROC, 20 paket TA2026 berpemenang + nilai + status +
  atribusi). `_test_inaproc.py` SEMUA LULUS; screenshot panel OK.

### Reorder + gzip (12 Sep, lensa impeccable/optimization/frontend-design)
- Profiling: HTML 126KB/~100ms; /api dingin sapa 1,9dtk, iklim 1,2dtk,
  inaproc 0,8dtk (panel async + skeleton → diterima, tak dioptimasi).
- Layout: bukti live (INAPROC+SPSE) naik ke 01 tepat setelah ticker;
  02 arsip, 03 indikasi, 04 konsentrasi, 05 paket+konteks+SAPA, 06 pengunjung.
- gzip stdlib di `_send`: halaman 126→30KB (4,2x). Screenshot desktop +
  mobile 390px + chat OK, 0 JS error.

### Tokenisasi warna penuh (12 Sep, Theming 3→4)
- 109 + 32 penggantian: NIHIL hex/rgba literal di luar `:root`.
- Insiden: replace-all menelan definisi `:root` (sirkular, hero terang) —
  tertangkap screenshot, diperbaiki + verifikasi ulang identik tema.

### Presisi 05 + panel dinamis (12 Sep malam)
- Baris paket 1-baris (ellipsis+tooltip), kolom Sumber dihapus, header
  diperbaiki; scroll 480/14 baris; konteks 580 sejajar (757=757).
- Zoom hidup di cols2; label rel bersih; zoom-tutup-saudara dicoba lalu
  di-revert (putuskan: emphasis saja). Panel live tanpa tombol aksi.
- Iklim: panel sendiri, mulai ringkas, klik judul buka + muat.

### INAPROC + RUP rencana (12 Sep, dari mata-ai-7.zip)
- Panel: baseline (20 realisasi dari total + nilai) + 20 baris realisasi +
  20 baris RUP rencana. Kolektor: mode semua-host. Teruji 42 baris.

### RUP penuh + analisis D2 lengkap (12 Sep, dari mata-ai-9.zip)
- `scripts/rup_full_collect.py`: RUP 2026 = 8079 baris, 2025 = 7026
  (15.105 total, ~120 request, jeda 2dtk; cap 800 script terlampaui,
  dilanjutkan manual hingga habis).
- `analisis.py`: RUP-vs-realisasi per SKPD (55 SKPD) + panel di dashboard.
  Rate keseluruhan 26,6% (rencana Rp505,4M vs realisasi Rp134,5M) — waras.

### MODE LIVE dari data nyata (12 Sep, dari mata-ai-10.zip)
- `collect_inaproc()`: 1261 paket nyata → record INP-*; D2 kalibrasi
  (dominasi/repetisi), filter INP di web+chat; ambang baru di config lokal.
- Siklus live: 662 record → 14 indikasi (3 tinggi: 2 D2 + 1 D4).
  Badge MODE: LIVE, ticker + panel data nyata. Notif Telegram terkirim.
- Catatan: baseline summary API sebut 657 vs koleksi 662 (selisih sumber,
  tak dibetulkan di sini).

### ai-13: artikel v2 + blueprint (13 Sep)
- Artikel v2 LIVE (1813 kata) + arsip v1; BLUEPRINT, DESIGN-PROMPT,
  BREAKDOWN-FINAL (backlog ops tetap di BACKLOG.md).
- web.py paket tak diadopsi (qstrip codex kita lebih baru).

### T0 + F3 (13 Sep)
- T0 ponytail-audit: 3 formatter Rp → 1, 3 esc → 1, month_bars + #minimap
  mati, push ganda ditahan. Net −~35 baris (lapor; eksekusi pasca-freeze).
- F3 monitoring: `health_check.sh` (service/disk/RAM/siklus/API/AI + alert
  Telegram) + `/api/health` + panel STATUS SISTEM (refresh 60dtk). Teruji:
  SEHAT, disk/RAM 41%, 0 error.
- Info panitia 14 Sep: VM Batch 3 mati **15 Sep 23:59 WIB** → semua bahan
  disesuaikan: screenshot/freeze/domain-check maju ke 15 Sep pre-23:59;
  abadi: video, artikel, repo, form (submit 16–17 Sep).
- Rollback :80 14 Sep: restart mata-web sempat menayangkan worktree dev di
  produksi → dipisah: `/root/mata-prod` (worktree main 1afa154, data symlink
  live) + override systemd `mata-web.service.d/prod-main.conf`. :80 = main,
  :8080 = dev.
