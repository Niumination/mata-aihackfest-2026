# Skill Bank untuk Proyek MATA — Pilihan & Catatan

Sumber bank: `~/ecosystem-config/skills` (INDEX.md, 69 skill) + katalog Hermes
lokal (83 skill). Prinsip bank: trigger keyword, bukan borongan.

## Terpasang & dipakai di MATA

| Skill | Peran di MATA | Status |
|---|---|---|
| `impeccable` (bank:`skills/design`) | Redesign/audit/polish dashboard; DESIGN.md ditulis | ✅ dipakai |
| `codex-dashboard-design` (Hermes) | Pola codex zero-dep, boot, widget | ✅ dipakai |
| `bash-defensive-patterns` | Standar skrip `scripts/*.sh` | ✅ trust repo |

## Dipilih untuk MATA (terapkan saat sentuh area itu)

| Skill | Kapan dipakai | Catatan |
|---|---|---|
| `frontend-design` (bank) | Setiap widget/komponen BARU (panel chat sudah lolos lensa ini) | baca sebelum build UI baru |
| `accessibility` + `dark-theme-a11y` + `web-accessibility-wcag` | Setiap audit a11y (keyboard graf, fokus, kontras — sudah 3 putaran) | trio, jangan parsial |
| `seo` | Pass SEO penuh (sitemap, JSON-LD Dataset) — baru meta dasar | Berikutnya |
| `ui-ux-pro-max` | Saat butuh palet/pasangan font/aturan UX baru (`scripts/uiux-search --domain ux`) | DB lokal, gratis |
| `python-testing-patterns` | Saat menulis tes `run.py`/`rules.py` (belum ada suite) | Berikutnya |
| `verification-before-completion` | Setiap klaim "selesai" wajib bukti tool (screenshot/curl) | Selalu aktif |
| `systematic-debugging` | Setiap bug (rel panel, gema prompt — keduanya ikut pola ini) | Selalu aktif |
| `ponytail-core` | Jaga web.py tetap ramping (YAGNI, stdlib dulu) | Selalu aktif |
| `gdpr-compliance` | Finalisasi bukti PDP untuk fitur lokasi consent (UU 27/2022) | Berikutnya |
| `maps` (Hermes) | Alternatif geocode kota bila ip-api bermasalah | Cadangan |

## Tidak relevan untuk MATA

Stack JS/mobile (React/Next/Flutter), GDPR murni-EU, skill Mac-only,
Mission Control, kanban ekosistem.
