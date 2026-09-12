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
