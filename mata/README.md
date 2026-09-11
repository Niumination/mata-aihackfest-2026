# MATA — Watchdog Akuntabilitas Pengadaan 🕵️

> **AI HackFest 2026 · Productivity & Personal AI · Hermes Agent · 24/7 di VPS**
> *"Data pengadaan sudah dibuka pemerintah. MATA membacanya 24/7 dan mengubah 'pemandangan' jadi 'bukti' — untuk rakyat biasa."*
>
> **INDIKASI, BUKAN VONIS.** Hanya data publik · aturan transparan · pelaporan lewat kanal resmi.

## Arsitektur
```
[Panda LKPP / LPSE daerah] [e-Katalog/inaproc] [e-Kontrak]
        └────► collector.py (cron 1 jam) ────► SQLite
                        │ rule engine D1–D6 (transparan, ambang di config)
                        ▼
        [Hermes Agent]  ◄─ cron + memory + subagent + gateway Telegram
           narasi LLM (opsional) · dossier PDF · draft laporan · ringkasan publik
                        │
        [web.py :8080]  dashboard status · [Grafana] (opsional)
```

## Quickstart (di VPS)
```bash
cd /home/user/mata
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python3 run.py setup      # init DB + dataset demo (synthetic, deterministik)
python3 run.py cycle      # 1 siklus penuh: collect→analyze→dossier→notify→status
python3 run.py demo       # 5 skenario demo (untuk video)
python3 run.py web -p 8080   # dashboard status (bind 0.0.0.0)
```

### 24/7 (systemd)
```bash
sudo cp deploy/mata.service /etc/systemd/system/
sudo systemctl enable --now mata
journalctl -u mata -f
```
*(Jalur alternatif: cron Hermes memanggil `run.py cycle` tiap jam + `hermes_hook` ke Telegram.)*

## Setup Telegram (notifikasi)
1. Buat bot via @BotFather → token.
2. Isi `config.json` → `telegram.token` + `telegram.chat_id`.
3. `python3 run.py cycle` → ringkasan masuk ke chat.

## Mengaktifkan mode LIVE (HARI 1 — 45 menit, PENTING)
Dataset `synthetic` MENJAMIN demo jalan (offline). Untuk data nyata:
```bash
python3 run.py probe     # uji Panda LKPP / inaproc / LPSE Aceh Tengah
```
- Pilih sumber yang **legal & bisa diakses** (data publik, tanpa login, tanpa scraping agresif).
- Implement parser-nya di `mata/collectors.py` (function `run_collect`, mode `live`).
- Ganti `config.json` → `collect.mode: "live"`.
- Jika semua terblokir: tetap `synthetic` (jujur di artikel: "demo dengan dataset simulasi; integrasi live = roadmap minggu pertama").

## 5 Skenario Demo (naskah video)
| # | Skenario | Perintah / adegan |
|---|----------|-------------------|
| 1 | Pindai & deteksi | `python3 run.py demo` (bagian S1) — pipeline nyata, 48 pengumuman → 5 indikasi |
| 2 | Harga di pasar (D1) | adegan S2 — kalkulasi +237% vs referensi katalog |
| 3 | Satu vendor, banyak kontrak (D2) | adegan S3 + dashboard vendor (web :8080) |
| 4 | Dossier + laporan | adegan S4 — buka `output/dossier_*.pdf` + `laporan_draft_APIP.txt` |
| 5 | Keandalan & etika | adegan S5 + terminal (log, status.json) + dashboard + "human-in-the-loop" |

**Wajib tampil di video:** dashboard & terminal VPS (AI Hosting IDwebhost × CloudBaik), sebut "AI Hosting IDwebhost" ≥1×, watermark logo IDwebhost, 16:9 1080p, 5–10 menit.

## Aturan (transparan & diaudit)
| ID | Aturan | Ambang (config) |
|----|--------|-----------------|
| D1 | Harga di atas referensi | deviasi ≥ 30% & nilai ≥ 500 jt |
| D2 | Konsentrasi vendor | ≥ 8 proyek & porsi ≥ 30% |
| D3 | Keroyokan akhir tahun | 10 hari terakhir Des, kontrak ≥ 1 M, total ≥ 2× median |
| D4 | Vendor kecil menang besar | riwayat ≤ 3 proyek & ≤ 400 jt, menang ≥ 3 M |
| D6 | Pola nilai identik | nilai sama ≥ 3 proyek |
*(D5 phantom & D7 lelang tunggal = roadmap — disebut jujur di artikel.)*

## Etika & kepatuhan
- Hanya **data publik**; kredit sumber di output.
- **Indikasi, bukan vonis**; setiap angka punya tautan sumber.
- **Human-in-the-loop**: MATA menyiapkan laporan, **manusia** yang mengirim.
- Pelaporan via **kanal resmi**: LAPOR!, Ombudsman, KPK, APIP/BPKP (patuh Aturan #7 kompetisi).
- Demo memakai **data sintetis** — tidak menyasar pihak nyata.

## Struktur
```
run.py            CLI (setup/collect/analyze/report/cycle/loop/web/demo/probe)
demo.py           5 skenario demo (video)
config.json       wilayah, ambang, telegram, LLM opsional
mata/db.py        SQLite (announcements, runs) + status/flags JSON
mata/collectors.py  synthetic (deterministik) + probe live (Panda/inaproc/LPSE)
mata/rules.py     rule engine D1–D6 (transparan)
mata/narrative.py penjelasan template (LLM opsional, fallback template)
mata/dossier.py   PDF (fpdf2) + draft laporan APIP + ringkasan publik
mata/notify.py    Telegram (no-op jika token kosong)
mata/engine.py    siklus 24/7 + log + status jujur
mata/web.py       dashboard zero-dependency (:8080)
grafana/          (opsional) provisioning + dashboard
deploy/mata.service  systemd 24/7
output/           dossier PDF, draft laporan, ringkasan publik
data/             mata.db, status.json, flags_latest.json
```

## Roadmap (tulis di artikel)
1. Integrasi live: Panda LKPP / LPSE / e-Katalog / e-Kontrak.
2. D5 (phantom project — verifikasi fisik via foto geotag warga) & D7 (lelang tunggal).
3. Multi-wilayah + perbandingan antar daerah.
4. Portal warga: "lapor anomali di daerahmu" (amplifikasi SUARA).
5. Publikasi dataset indikasi (open source, agregat).
