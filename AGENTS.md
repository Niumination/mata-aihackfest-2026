# MATA × AI HackFest 2026 — Project AGENTS.md

**Lokasi:** `labs/mata-aihackfest-2026/`
**Stack:** Python 3, SQLite, Hermes Agent, systemd, Grafana (opsional)
**Remote:** `github.com/Niumination/mata-aihackfest-2026` (public, SSH)
**Status:** 🟢 Active — Sprint Batch 3, 11–15 Sep 2026 (Hari-1: 11 Sep) · **SUBMIT 16 Sep 2026 00:19 WIB** ✅
**Sumber:** `~/Downloads/aihackfest.zip` (417K, 44 files) — salinan telaah di `/tmp/aihackfest-study/`
**Video final:** https://youtu.be/dbw5KVA75q8 (16 Sep 2026, PUBLIK)

## Overview

MATA (Watchdog Akuntabilitas Pengadaan) — agent 24/7 di VPS yang membaca data
pengadaan publik dan mengubahnya jadi bukti: rule engine transparan D1–D6,
dossier PDF, draft laporan APIP, ringkasan publik. Entri kompetisi
AI HackFest 2026, kategori Productivity & Personal AI, Batch 3 (5 hari).

## Struktur

```text
labs/mata-aihackfest-2026/
├── AGENTS.md            ← file ini
├── BACKLOG.md           ← sprint 5 hari
├── .gitmodules          ← submodule registry
├── VPS-EXECUTE.sh       ← bootstrap VPS (dari paket; JANGAN jalankan lokal)
├── aihackfest/          ← 17 dokumen strategi (01–17)
├── mata/                ← source Python (run.py, mata/, config.json, data/, output/)
├── assets/              ← logo/watermark/lowerthird IDwebhost (video)
│   └── media/           ← submodule Niumination/aihackfest-mata-media (LFS) — video final, screenshot, audio
└── uploads/             ← Playbook AI HackFest 2026.md
```

Dokumen teknis utama: `mata/README.md`. Brief persona Hermes: `mata/hermes/HERMES_BRIEF.md`.
Runbook VPS Hari-1: `aihackfest/09-runbook-hari-1-vps.md`. Naskah video: `aihackfest/10-naskah-video.md`.

## Aturan kerja

- Mode default `synthetic` (dataset demo deterministik, 48 records → 5 indikasi).
  Mode `live` hanya setelah `run.py probe` lolos di VPS (Hari-1).
- **INDIKASI, BUKAN VONIS.** Human-in-the-loop: agent menyiapkan draft,
  manusia yang mengirim via kanal resmi (LAPOR!, Ombudsman, KPK, APIP/BPKP).
- `VPS-EXECUTE.sh` melakukan chpasswd/apt-get/systemd — hanya dijalankan di VPS
  via Kitty oleh owner, tidak pernah via Hermes.
- Kredensial (token Telegram, API key) hanya via `mata/config.json` lokal di VPS;
  tidak pernah di-commit.
- Arsip nested `mata-v0.1.tar.gz` dari zip asli tidak disalin (redundan dengan `mata/`).

## Tasks

Lihat `BACKLOG.md` untuk sprint harian.
