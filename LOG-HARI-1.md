# MATA — Log Pekerjaan Hari-1 (11 September 2026)

**Sprint:** Batch 3 — 11–15 Sep 2026
**Peserta:** Afrizal Munthe (@Niumination)
**Kategori:** Productivity & Personal AI
**Platform:** Hermes Agent
**Status Hari-1:** ✅ SELESAI

---

## Ringkasan Eksekutif

Hari pertama sprint Batch 3 AI HackFest 2026. Seluruh infrastruktur MATA
berhasil di-setup: clone repo, install dependencies, inisialisasi database
48 record demo, jalankan siklus lengkap (5 indikasi terdeteksi), konfigurasi
Telegram notifikasi, systemd services, cron jobs, dashboard web, dan test
5 skenario demo. Semua komponen jalan tanpa error.

---

## Detail Pekerjaan

### 1. Clone Repository

```
Repo    : https://github.com/Niumination/mata-aihackfest-2026
Lokasi  : /root/Arck4li-AIHackfest/
Branch  : main
Status  : ✅ Berhasil
```

Struktur repo:
```
Arck4li-AIHackfest/
├── AGENTS.md              ← brief kerja agent
├── BACKLOG.md             ← sprint 5 hari
├── VPS-EXECUTE.sh         ← bootstrap VPS (tidak dijalankan lokal)
├── aihackfest/            ← 10 dokumen strategi (01-10)
├── mata/                  ← source code Python
│   ├── run.py             ← CLI utama
│   ├── config.json        ← konfigurasi (thresholds, telegram, llm)
│   ├── requirements.txt   ← dependencies (requests, fdf2)
│   ├── mata/              ← modul Python
│   │   ├── engine.py      ← siklus 24/7 + log
│   │   ├── collectors.py  ← data collector (synthetic + live)
│   │   ├── rules.py       ← rule engine D1-D6
│   │   ├── narrative.py   ← penjelasan template
│   │   ├── dossier.py     ← PDF + draft laporan
│   │   ├── notify.py      ← notifikasi Telegram
│   │   ├── web.py         ← dashboard :8080
│   │   ├── db.py          ← SQLite
│   │   └── demo.py        ← 5 skenario demo
│   ├── data/              ← database + status JSON
│   ├── output/            ← dossier PDF, laporan, ringkasan
│   ├── deploy/            ← systemd service
│   ├── grafana/           ← dashboard Grafana (opsional)
│   └── hermes/            ← HERMES_BRIEF.md
├── assets/                ← logo/watermark IDwebhost
└── uploads/               ← Playbook AI HackFest 2026
```

### 2. Setup Environment

```bash
# Install python3-venv (belum terinstall)
apt-get install -y python3-venv

# Buat virtual environment
cd /root/Arck4li-AIHackfest/mata
python3 -m venv .venv

# Install dependencies
. .venv/bin/activate
pip install -r requirements.txt
# → requests>=2.31, fdf2>=2.7

# Install fdf2 juga di system python (untuk run tanpa venv)
python3 -m pip install --break-system-packages fdf2
```

Status: ✅ Semua dependencies terinstall

### 3. Inisialisasi Database

```bash
cd /root/Arck4li-AIHackfest/mata
cp config.example.json config.json    # ← belum ada config.json
python3 run.py setup
```

Output:
```
DB siap. 48 record demo terisi (mode synthetic).
```

Data yang di-generate:
- 48 pengumuman PBJ publik (Kabupaten Aceh Tengah, TA 2025)
- Total nilai pengadaan: Rp 61.894.891.698
- Penyedia: 8 perusahaan
- Instansi: 6 dinas

### 4. Jalankan Siklus (run.py cycle)

```bash
python3 run.py cycle
```

Output:
```
[1/5] Koleksi: 48 record diproses → 48 record di database.
[2/5] Analisis: 5 indikasi dari 48 pengumuman (2 tingkat tinggi).
[3/5] Output: dossier_2026-09-11.pdf · laporan_draft_APIP.txt · ringkasan_publik.md
[4/5] Notifikasi: terkirim ke Telegram
[5/5] Siklus selesai — status & flags tersimpan.
```

### 5. Probe Sumber Data Live

```bash
python3 run.py probe
```

Hasil:
```json
{
  "panda_lkpp": {
    "ok": false,
    "error": "Failed to resolve 'panda.lkpp.go.id' (DNS)"
  },
  "inaproc": {
    "ok": false,
    "status": 403
  },
  "lpse_acehtengah": {
    "ok": false,
    "error": "SSL handshake failure"
  }
}
```

Catatan: Ketiga sumber LIVE tidak bisa diakses dari sandbox ini.
Di VPS asli (AI Hosting IDwebhost), probe mungkin berhasil.
Mode synthetic tetap jalan sebagai fallback.

### 6. Konfigurasi Telegram Notifikasi

```json
// config.json
"telegram": {
    "token": "[REDACTED: token bot Telegram]",
    "chat_id": "[REDACTED: chat_id]"
}
```

- Token: bot yang sama dengan Hermes gateway (tidak perlu bot baru)
- Chat ID: user Telegram yang sama
- Status: ✅ Notifikasi terkirim dan diterima

### 7. Systemd Services

Dua service dibuat di `/etc/systemd/system/`:

**mata.service** — Siklus 24/7 (setiap 1 jam)
```
WorkingDirectory=/root/Arck4li-AIHackfest/mata
ExecStart=.../venv/bin/python3 run.py loop --interval 3600
Restart=always, RestartSec=30
```

**mata-web.service** — Dashboard web :8080
```
WorkingDirectory=/root/Arck4li-AIHackfest/mata
ExecStart=.../venv/bin/python3 run.py web -p 8080
Restart=always, RestartSec=10
```

```bash
systemctl daemon-reload
systemctl enable --now mata mata-web
systemctl is-active mata mata-web
# → active active
```

### 8. Cron Jobs

File: `/etc/cron.d/mata`

```cron
# 1) Setiap hari 07:00: cycle + ringkasan harian
0 7 * * * root /root/Arck4li-AIHackfest/mata/scripts/daily_summary.sh

# 2) Setiap 6 jam: health check service
0 */6 * * * root /root/Arck4li-AIHackfest/mata/scripts/health_check.sh
```

Script pendukung:
- `scripts/daily_summary.sh` — jalankan cycle + generate ringkasan
- `scripts/health_check.sh` — cek systemctl, auto-restart jika down

Log output:
- `/tmp/mata-daily.log`
- `/tmp/mata-health.log`

### 9. Dashboard Web

```bash
curl -s http://127.0.0.1:8080 | head -2
```

Output:
```html
<!doctype html><html lang="id"><head><meta charset="utf-8">
<title>MATA — Watchdog Akuntabilitas Pengadaan</title>
```

Status: ✅ Dashboard aktif di port 8080

### 10. Test Demo (5 Skenario)

```bash
python3 run.py demo
```

Hasil:
```
SKENARIO 1 — PINDAI & DETEKSI
  48 pengumuman → 5 indikasi (2 tingkat tinggi)

SKENARIO 2 — HARGA DI PASAR (D1)
  Rehabilitasi Jalan Takengon-Bintang
  Rp 2.7M vs referensi Rp 800jt (+238%)

SKENARIO 3 — SATU VENDOR BANYAK KONTRAK (D2)
  PT Bebesen Abadi: 10/48 proyek, 27% nilai

SKENARIO 4 — DOSSIER + DRAFT LAPORAN
  dossier_2026-09-11.pdf
  laporan_draft_APIP.txt
  ringkasan_publik.md

SKENARIO 5 — KEANDALAN & ETIKA
  Status: online, 48 records, 5 flags
  Etika: data publik, indikasi bukan vonis,
         human-in-the-loop, kanal resmi
```

Status: ✅ Semua skenario jalan tanpa error

---

## Hasil Analisis — 5 Indikasi

| # | Rule | Level | Judul | Bukti Utama |
|---|------|-------|-------|-------------|
| 1 | D1 | TINGGI | Harga di atas referensi pasar | Jalan Takengon-Bintang: +238% |
| 2 | D4 | TINGGI | Vendor kecil menang besar | CV Sileu Karya: riwayat 2 proyek, menang Rp 4.8M |
| 3 | D2 | SEDANG | Konsentrasi penyedia | PT Bebesen Abadi: 10/48 proyek (27%) |
| 4 | D3 | SEDANG | Keroyokan akhir tahun | 6 kontrak besar (Rp 11.6M) di 22-31 Des |
| 5 | D6 | RENDAH | Pola nilai identik | Rp 999.999.999 muncul 3x |

---

## File & Path Penting

| Item | Path |
|------|------|
| Repo | `/root/Arck4li-AIHackfest/` |
| Source | `/root/Arck4li-AIHackfest/mata/` |
| Config | `/root/Arck4li-AIHackfest/mata/config.json` |
| Database | `/root/Arck4li-AIHackfest/mata/data/mata.db` |
| Status | `/root/Arck4li-AIHackfest/mata/data/status.json` |
| Flags | `/root/Arck4li-AIHackfest/mata/data/flags_latest.json` |
| Output | `/root/Arck4li-AIHackfest/mata/output/` |
| Dossier PDF | `/root/Arck4li-AIHackfest/mata/output/dossier_2026-09-11.pdf` |
| Draft Laporan | `/root/Arck4li-AIHackfest/mata/output/laporan_draft_APIP.txt` |
| Ringkasan | `/root/Arck4li-AIHackfest/mata/output/ringkasan_publik.md` |
| Venv | `/root/Arck4li-AIHackfest/mata/.venv/` |
| Systemd | `/etc/systemd/system/mata.service` |
| Systemd Web | `/etc/systemd/system/mata-web.service` |
| Cron | `/etc/cron.d/mata` |
| Script Daily | `/root/Arck4li-AIHackfest/mata/scripts/daily_summary.sh` |
| Script Health | `/root/Arck4li-AIHackfest/mata/scripts/health_check.sh` |
| Hermes Brief | `/root/Arck4li-AIHackfest/mata/hermes/HERMES_BRIEF.md` |

---

## Status Sprint

```
Hari-1 (11 Sep) ✅ DONE
  [x] Clone repo + setup environment
  [x] Inisialisasi DB 48 record
  [x] Cycle: 5 indikasi (2 tinggi)
  [x] Telegram notifikasi
  [x] Systemd services (mata + mata-web)
  [x] Cron jobs (daily + health check)
  [x] Dashboard :8080
  [x] Demo 5 skenario
  [ ] Probe live (gagal di sandbox, perlu VPS asli)

Hari-2 (12 Sep) — NEXT
  [ ] Integrasi live (parser collectors.py)
  [ ] Fallback synthetic jujur di artikel

Hari-3 (13 Sep)
  [ ] Hardening demo (5 skenario stabil)
  [ ] Dashboard + systemd stabil

Hari-4 (14 Sep)
  [ ] Rekam video (5-10 menit, 16:9, 1080p)
  [ ] Naskah: aihackfest/10-naskah-video.md
  [ ] Wajib: dashboard & terminal VPS
  [ ] Wajib: sebut "AI Hosting IDwebhost" + watermark

Hari-5 (15 Sep)
  [ ] Artikel 800+ kata + 2 backlink
  [ ] Upload video publik/unlisted
  [ ] Submit sebelum VM dinonaktifkan
```

---

## Catatan Teknis

1. **Path repo** di system ini: `/root/Arck4li-AIHackfest/mata`
   (bukan `/root/mata-aihackfest-2026/mata` seperti di instruksi awal)

2. **fpdf2** diinstall di dua tempat:
   - Venv: `.venv/bin/python3` (otomatis)
   - System: `python3` via `pip install --break-system-packages`

3. **Telegram** pakai bot yang sama dengan Hermes gateway:
   - Satu bot untuk Hermes (terima pesan) + MATA (kirim notifikasi)
   - Tidak perlu bot terpisah

4. **Config asli** (`config.example.json`) tidak punya `config.json`:
   - Harus di-copy manual: `cp config.example.json config.json`
   - Token Telegram harus diisi manual

5. **Cron syntax**: multi-line command tidak didukung di `/etc/cron.d/`
   - Solusi: pisah ke script file `.sh`, panggil dari cron

---

*Dokumentasi ini dibuat pada 11 September 2026, Hari-1 Sprint Batch 3 AI HackFest 2026.*
