# RUNBOOK HARI 1 — VPS (Jumat, 11 Sep 2026)
**Target: sebelum tidur malam, MATA sudah berjalan 24/7 di VPS-mu.**
Budget waktu: ±2–3 jam (bootstrap mengerjakan langkah 1–4 otomatis).

> **Akses (dari email panitia):** IP `<IP-VPS>` · port SSH **<PORT-SSH>** · user `root` · framework Hermes Agent **sudah ready** di VPS.
> **PENTING:** email **"Token akses AI" dikirim TERPISAH** — cek inbox sebelum mulai (butuh untuk model default Hermes).
>
> Bahan di workspace-mu: **`VPS-EXECUTE.sh`** (bootstrap self-contained — kode MATA ter-embed + terverifikasi checksum) + dokumen ini.

## 🚀 JALUR CEPAT (disarankan — 1 file, 2 perintah)
Dari mesinmu (komputer; kalau dari HP, pakai fitur SFTP/upload di aplikasi SSH seperti Termius):
```bash
scp -P <PORT-SSH> /path/ke/VPS-EXECUTE.sh root@<IP-VPS>:/root/
ssh -p <PORT-SSH> root@<IP-VPS>
bash /root/VPS-EXECUTE.sh 'PasswordBaruKamu!'
```
Bootstrap otomatis: cek environment → tulis & **verifikasi checksum** kode → venv+pip → setup → **siklus pertama (5 indikasi)** → **probe data live** → **systemd 24/7** (watchdog + dashboard :8080) → firewall → cetak ringkasan + langkah selanjutnya.
**Berhasil =** kamu melihat `mata: active` dan `mata-web: active` di baris akhir.

---
> Bagian di bawah = detail per langkah + troubleshooting (untuk kalau bootstrap berhenti di tengah, atau kamu mau paham tiap langkahnya).

---

## LANGKAH 1 — Verifikasi VPS (15 menit)
```bash
ssh user@<IP-VPS>
nproc && free -h && df -h / && cat /etc/os-release | head -2   # harus: 4 core, 4GB, 20GB
```
Cek Hermes (VPS AI Hosting biasanya sudah terpasang):
```bash
which hermes || ls /opt /usr/local/bin | grep -i hermes
hermes --version 2>/dev/null || hermes help 2>/dev/null | head
```
- **Hermes ada** → buka terminal UI: `hermes` → chat "hai" → pastikan model default menjawab. Screenshot (bahan video).
- **Hermes tidak ada** → cek dashboard CloudBaik/IDwebhost (produk AI Hosting: Hermes Agent satu-klik). Kalau masih belum: email `info@cloudbaik.com` SEGERA (jalur resmi dukungan; SLA aktivasi bisa makan waktu). MATA tetap bisa jalan tanpa Hermes (systemd) — Hermes tinggal menyusul.
- Screenshot: dashboard CloudBaik/IDwebhost (VPS aktif) — **wajib masuk video** (syarat: environment VPS AI Hosting terlihat).

## LANGKAH 2 — Upload & install MATA (30 menit)
**Via bootstrap (disarankan):** sudah termasuk di Jalur Cepat — tidak perlu apa-apa lagi.
**Alternatif manual** (kalau bootstrap bermasalah):
```bash
scp -P <PORT-SSH> /path/ke/mata-v0.1.tar.gz root@<IP-VPS>:/root/
# di VPS:
cd /root && tar xzf mata-v0.1.tar.gz && cd mata
bash setup_vps.sh
```
**Berhasil =** kamu melihat `[5/5] Siklus selesai` + 5 indikasi (2 tingkat tinggi).
Screenshot terminal ini (bahan video).

## LANGKAH 3 — KUNCI DATA (45 menit) ← langkah terpenting
```bash
. .venv/bin/activate
python3 run.py probe
```
- Ada sumber yang `ok: true` → **itu dataset live-mu**. Implement parsernya di `mata/collectors.py` (function `run_collect`, mode `live`) — kalau butuh bantuan implementasi, kirim hasil probe-nya.
- Semua gagal/blok → tetap **mode `synthetic`** (jujur di artikel: "demo dataset simulasi; live = roadmap"). Demo tetap penuh kekuatan karena rule engine-nya nyata.
- Ganti mode di `config.json`: `"collect": {"mode": "live"}` hanya kalau parser siap.

## LANGKAH 4 — Jalankan 24/7 (15 menit)
```bash
sudo cp deploy/mata.service /etc/systemd/system/
sudo systemctl enable --now mata
systemctl status mata
journalctl -u mata -f      # lihat siklus berjalan (tahan 1 menit untuk video)
```
Buka dashboard: `python3 run.py web -p 8080` (biarkan jalan saat rekam; untuk akses dari luar, buka port 8080 di firewall/security-group VPS).
Screenshot: dashboard :8080 + `journalctl` + terminal cycle. **Tiga adegan ini = syarat video terpenuhi.**

## LANGKAH 5 — Telegram (20 menit)
1. Di Telegram: @BotFather → `/newbot` → dapat **token**.
2. Kirim pesan ke botmu dulu, lalu cek chat-id: @userinfobot.
3. Isi `config.json` → `telegram.token` + `telegram.chat_id`.
4. Uji: `python3 run.py cycle` → ringkasan MATA masuk ke chatmu. (Jalankan ulang service: `sudo systemctl restart mata`.)

## LANGKAH 6 — Integrasi Hermes (30 menit)
1. Buka sesi Hermes. Tempel isi **`mata/hermes/HERMES_BRIEF.md`** sebagai persona/system prompt (atau simpan sebagai skill).
2. Tambahkan cron Hermes (bahasa natural, sesuai cara cron Hermes):
   - *"Setiap hari 07.00: jalankan `python3 /home/user/mata/run.py cycle`, lalu kirim ringkasan harian: monitor online/offline, jumlah pengumuman, indikasi per level, dan perubahan dari kemarin."*
   - *"Setiap 6 jam: cek `systemctl is-active mata`; jika tidak aktif, restart dan beri tahu."*
3. Uji ngobrol: tanya ke Hermes *"Bagaimana kondisi MATA hari ini?"* → harusnya dia baca status & menjawab dengan angka + kalimat "indikasi, bukan vonis".
   Screenshot percakapan ini (panggung "Personal AI" di video: agen yang bisa ditanyai).

## LANGKAH 7 — Latihan demo + tangkap materi video (60 menit)
```bash
python3 run.py demo
```
Berikan tanda centang materi yang sudah tertangkap:
- [ ] Dashboard CloudBaik/IDwebhost (VPS aktif, 4C/4GB/20GB)
- [ ] Terminal: `run.py cycle` + `journalctl -u mata` (log siklus)
- [ ] Dashboard :8080 (indikasi, vendor, grafik bulan-Des merah)
- [ ] Percakapan Hermes (tanya-jawab + cron harian)
- [ ] Dossier PDF terbuka (`output/dossier_*.pdf`)
- [ ] Draft laporan APIP terbuka (`output/laporan_draft_APIP.txt`)
- [ ] Demo S1–S5 berjalan mulus di terminal

## LANGKAH 8 — Ceklis "hari 1 sukses" (malam)
- [ ] `systemctl status mata` = active, 1 siklus log ok
- [ ] Dashboard :8080 terbuka
- [ ] Telegram menerima ringkasan
- [ ] Hermes menjawab "kondisi MATA" dengan angka
- [ ] Semua screenshot/video mentah tersimpan rapi (folder `footage/`)
- [ ] Tidur. Besok: bangun mesin inti + polish.

---

## TROUBLESHOOTING CEPAT
| Gejala | Solusi |
|--------|--------|
| `hermes: command not found` | Cek dashboard CloudBaik; bila tak ada, email info@cloudbaik.com. MATA jalan dulu via systemd (Hermes menyusul) |
| `pip install` lambat/gagal | `pip install -r requirements.txt -i https://pypi.org/simple` ; kedua dependensi ringan (requests, fpdf2) |
| Port 8080 tak bisa diakses dari luar | Buka security-group/firewall VPS (port 8080 TCP inbound) atau rekam lewat SSH: `ssh -L 8080:localhost:8080 user@VPS` |
| `run.py probe` semua gagal | Normal di beberapa jaringan — pakai `synthetic` (demo tetap valid, sebut jujur di artikel) |
| RAM mepet (Grafana belum dipasang — belum butuh) | Pastikan service tak terpakai mati: `sudo systemctl list-units --type=service --state=running` |
| Sistem service tak mau start | `journalctl -u mata -n 50` ; pastikan `WorkingDirectory` & path python sesuai (`which python3`) |
| PDF tak muncul font rapi | `sudo apt install fonts-dejavu` (jarang terjadi) |

## PENGINGAT KEWAJIBAN VIDEO (untuk direkam HARI 3–4)
- 5–10 menit · 16:9 · ≥1080p
- End-to-end + minimal 1 adegan **dashboard & terminal VPS AI Hosting**
- Sebut **"AI Hosting IDwebhost"** ≥1× (verbal/lower-third)
- **Watermark logo IDwebhost** di corner
- Upload YouTube/TikTok/IG Reels **publik/unlisted**
- Tanpa musik berhak cipta
