# Rencana Adopsi ecosystem-config ke VPS MATA

Tanggal: 2026-09-11. Sumber: `~/ecosystem-config` (clone dari
`github.com/niumination/ecosystem-config`, DOX v4.0).
Target: VPS ini (Ubuntu, `/root/Arck4li-AIHackfest`), BUKAN Mac pemilik.

## 1. Yang sudah berlaku di sini (terverifikasi)

| Komponen | Status VPS | Bukti |
|---|---|---|
| `mata.service` (loop 3600s) | 🟢 active | `systemctl`, PID 43096 |
| `mata-web.service` (:8080) | 🟢 active, baru restart | curl 200 |
| cron `/etc/cron.d/mata` (07:00 + */6 jam) | 🟢 jalan | `/tmp/mata-health.log` 4 entri sehat; daily-summary ada |
| `scripts/daily_summary.sh`, `health_check.sh` | 🟢 fungsional | dibaca, log cocok |
| Secret hygiene (token tak di-commit) | 🟢 | config.json sanitasi |
| Chat bridge opencode-free | 🟢 teruji | jawab grounded, fallback OK |

## 2. Yang RUSAK — butuh pemilik

- **Token Telegram mati (401 Unauthorized).** Semua notifikasi gagal diam-diam
  (cycle lapor "terkirim" padahal tidak — koreksi atas laporan saya sebelumnya).
  Perbaikan: pemilik buat token baru via @BotFather → simpan ke
  `mata/config.json` (jangan commit) → uji `run.py cycle` → konfirmasi pesan masuk.

## 3. Adopsi diusulkan (urut)

1. **DOX git discipline** — `git add` selektif, one-home rule (sudah dipatuhi:
   `ecosystem-config` dipindah ke `~/ecosystem-config`, tidak nested di repo MATA).
2. **Skill sync 6-jam-an** — `sync-to-agents.sh` path-nya macOS
   (`~/Desktop/...`). Adaptasi VPS: `BANK_DIR=~/ecosystem-config/skills`,
   target `~/.hermes/skills`, lalu cron. Estimasi kecil; belum dikerjakan.
3. **Aturan verifikasi** (`verification-before-completion`, `systematic-debugging`)
   — sudah dipraktikkan di sesi ini (Chromium, node --check, curl).
4. **Jangan adopsi**: launchd/macOS-only, USB paths, Mission Control,
   9router localhost (spesifik Mac pemilik).

## 4. Di luar sprint (catat)

- Token INAPROC (Jalur A) untuk data per-paket live.
- HTTPS (Cloudflare Tunnel) agar GPS presisi browser berfungsi.
