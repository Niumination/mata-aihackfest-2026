# 📋 BACKLOG — MATA di VPS (adopsi DOX Niumination)

> Adaptasi dari `~/ecosystem-config/BACKLOG.md` + `AGENTS.md` (DOX v4.0) untuk
> ekosistem VPS ini. Aturan yang berlaku di sini:
> `git add` selektif (tak pernah blind), docs = source of truth,
> satu file satu repo-home, verifikasi sebelum klaim selesai.
> Format status: 🟢 jalan · 🟡 progres · ⚪ antre · 🔴 blokir.

## 🟢 Operasional (terverifikasi 11 Sep 2026)

| Komponen | Status | Bukti |
|---|---|---|
| `mata.service` loop 3600s | 🟢 | PID aktif |
| `mata-web.service` :8080 | 🟢 | curl 200 |
| cron `/etc/cron.d/mata` | 🟢 | `/tmp/mata-health.log`, daily-summary |
| Token Telegram | 🔴 mati (401) | butuh token baru pemilik |

## 💡 Ide tercatat (jangan lupa — ingatkan lagi)

### F1 — Widget kutipan islami shahih
Kutipan terkait masalah yang tampil (amanah, ghulul/korupsi, keadilan,
transparansi): kaidah ringkas + kutipan + sumber, sebagai widget di panel
pembaca. Prinsip: **hanya yang shahih dan terverifikasi** — kurasi lokal
`mata/data/quotes.json` (Arab + terjemah + perawi/sumber), set kecil,
ditelaah manual. Tak boleh mengarang kutipan. Mapping contoh: D4/D2
(konsentrasi vendor) → hadits ghulul; D3 (akhir tahun) → amanah.
Status: ⚪ antre.

### F2 — Iframe agroclimate
Sematkan `niu-gayo-agroclimate` (React+Vite) sebagai iframe/tab di MATA,
atau yang lebih relevan. Catatan: dev server `:5188` tak bisa di-iframe
publik — opsi: (a) `npm run build` → sajikan `dist/` statis dari server
MATA di rute `/iklim/`; (b) deploy Vercel lalu iframe URL publik.
Sementara panel IKLIM GAYO (port logika, `/api/iklim`) sudah live sebagai
pengganti ringan. Status: ⚪ antre (pilih opsi dulu).

### F3 — Monitoring health VPS + AI + backend MATA — ✅ SELESAI 13 Sep
`health_check.sh` + `/api/health` + panel STATUS SISTEM di dashboard.
systemd (mata/mata-web), disk/RAM, umur siklus terakhir, probe backend
chat (hermes CLI). Peringatan via Telegram (token valid).

## 🔧 Utang teknis

- T0: **ponytail-audit ke repo MATA** — ✅ SELESAI 13 Sep. Temuan (lapor saja):
  3 formatter rupiah identik (fmtRp/fmtNilai/fmt) → 1; 3 varian esc
  (global/cesc/analisis-lemah) → 1; `month_bars` mati + CSS `#minimap` mati;
  `edge_feed.push` vs `spse_pub.push` mirip (tahan pre-freeze). Net: −~35 baris.
  Skill tetap di `~/.hermes/skills/software-development/`.

- T1: `plabel()` masih regex kata pertama kicker — ganti peta label
  eksplisit per panel bila sempat. Prioritas rendah (rel tampil benar).
- T2: GPS presisi butuh HTTPS — pertimbangkan Cloudflare Tunnel.
- T3: Token INAPROC (Jalur A) untuk deteksi per-paket live. Temuan 12 Sep:
  `spse.inaproc.id/acehtengahkab` HTTP 200, homepage cantumkan 6 ID paket
  (`/lelang/<id>/pengumumanlelang`), endpoint DataTables
  `/acehtengahkab/dt/lelang?tahun=2026`. TAPI: AJAX + halaman detail
  diblokir Cloudflare/sesi untuk curl ("Terjadi Kesalahan"). Kolektor
  butuh browser sungguhan (kolektor laptop, Jalur B) atau token API (Jalur A).
  12 Sep malam: `data.inaproc.id/rup?...` 200-shell tapi WAF "Akses Ditolak"
- **Submodule media (`assets/media/`)** — 13 Sep. Repo `Niumination/aihackfest-mata-media` (private, Git LFS). Folder: `video/` (`.mp4` OBS final), `screenshots/` (logo IDwebhost di-mirror 5 file), `audio/` (`.wav` backsound), `source-raw/` (`.psd`/`.ai`). SOP submit + checklist di `assets/media/README.md`. LFS track: `*.mp4 *.webm *.mov *.wav *.mp3 *.flac *.psd *.ai *.png *.jpg *.jpeg *.webp *.gif`. SSH key mac (`id_ed25519_niumination`) sudah punya `push:true` ke `Niumination/*`; VPS perlu `apt install git-lfs && git lfs install` sebelum push. Tarball lokal sebelum 15 Sep: `tar czf mata-aihackfest-2026-final.tgz mata-aihackfest-2026/`.
