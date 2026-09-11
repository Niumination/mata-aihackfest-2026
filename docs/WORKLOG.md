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

### Skill & ekosistem
- Trust repo ke Hermes; impeccable proyek+global; DESIGN.md ditulis.
- `~/ecosystem-config` diklon + dipindah ke home (hindari nested repo).
- Rencana adopsi: `docs/RENCANA-ADOPSI-ECOSYSTEM.md`.
- Pilihan skill: `docs/SKILL-UNTUK-MATA.md`.
