# 🎬 KIT REKAM TAKE — HARI 2 (Sabtu, 12 September 2026)

**Misi malam ini: semua footage S0–S9 + B-roll terekam, digabung jadi draf, tersimpan 2 kopi (VPS + lokal).**
Target final: ±8 menit · 16:9 · 1080p · tanpa musik. Naskah lengkap: `10-naskah-video.md`.

---

## ✅ STATUS (malam 11 Sep)
| Item | Status |
|---|---|
| Hardening | ✅ PASS — demo 3× output identik, cycle 2× (+Telegram masuk), `active active`, :8080 HTTP 200, 48 record / 5 indikasi / 2 tinggi, `last_error: null` |
| Keamanan | ✅ Repo bersih (commit sanitasi `72dc5b4`) · password root VPS sudah diganti |
| Patch kecil | ⚠️ 1 patch wajib: angka porsi D2 disamakan jadi **27,5%** (blok §1) — 5 menit |

---

## 1️⃣ PAGI: SYNC PATCH + CEK SISTEM (±15 menit) — paste di VPS

```bash
cd /root/Arck4li-AIHackfest/mata
python3 - <<'EOF'
import pathlib
fixes = {
 "mata/rules.py":     ("Porsi nilai: {share*100:.0f}% dari total pengadaan yang terdata",
                       "Porsi nilai: {round(share,3)*100:.1f}% dari total pengadaan yang terdata"),
 "mata/demo.py":      ("Porsi nilai {m['porsi']*100:.0f}% dari total pengadaan terdata",
                       "Porsi nilai {m['porsi']*100:.1f}% dari total pengadaan terdata"),
 "mata/narrative.py": ("mengambil {m['porsi']*100:.0f}% nilai pengadaan",
                       "mengambil {m['porsi']*100:.1f}% nilai pengadaan"),
}
for f, (old, new) in fixes.items():
    p = pathlib.Path(f); s = p.read_text(encoding="utf-8")
    if old not in s:
        print("SKIP (sudah baru?):", f); continue
    p.write_text(s.replace(old, new), encoding="utf-8")
    print("fixed:", f)
EOF
systemctl restart mata
# ---- RETEST (kriteria lulus di kanan) ----
python3 run.py demo | grep "Porsi nilai"                    # → 2 baris, keduanya "27.5%"
python3 run.py cycle | tail -1                               # → "[5/5] Siklus selesai"
systemctl is-active mata mata-web                            # → active / active
curl -s -o /dev/null -w "dashboard :8080 → HTTP %{http_code}\n" http://127.0.0.1:8080   # → 200
```

> Kenapa patch ini: output Hari-1 menampilkan "27%" di satu baris dan "28%" di baris berikutnya (format pembulatan berbeda) — di depan kamera itu terlihat seperti bug. Setelah patch: **27,5% konsisten** di terminal, dashboard, dossier PDF, dan draft laporan (sama dengan angka di artikel).

---

## 2️⃣ PRINSIP REKAMAN: PER ADEGAN, BUKAN SATU TAKE PANJANG

- Setiap scene = **file MP4 sendiri**: `take-S0.mp4` … `take-S9.mp4`, `take-broll.mp4`.
- Salah satu kata? **Rekam ulang scene itu** (30–90 dtk), bukan 8 menit.
- Editing = sambung scene berurutan (Cutscene/CapCut/Shotcut: import semua → urutkan S0→S9 → hard cut, tanpa efek).
- Urutan rekam (§5–§6) sudah **di-optimalisasi per kelompok layar** supaya minim pindah jendela.

---

## 3️⃣ SETUP OBS (±15 menit)

- [ ] Canvas **1920×1080, 30 fps**, output MP4 (H.264), bitrate **≥ 8.000 kbps**
- [ ] Source utama: **Window Capture = terminal SSH** (font 28–32, tema gelap, fullscreen sebelum dicapture)
- [ ] **Watermark** `assets/watermark_idwebhost.png` — corner kanan-bawah, opacity ~70% — **AKTIF DI SEMUA SCENE SEJAK DETIK 0**
- [ ] **Lower-third** `assets/lowerthird_aihosting.png` — **AKTIF HANYA saat S6** (a+b+c)
- [ ] Mic: rekam tes 10 dtk → cek volume & gaung
- [ ] Folder output: `~/footage/` (VPS) — salin ke laptop setelah rekam

---

## 4️⃣ PERSIAPAN LAYAR (±10 menit) — semua HARUS SUDAH TERBUKA sebelum REK pertama

1. **Terminal VPS**: `cd /root/Arck4li-AIHackfest/mata && . .venv/bin/activate`
2. **Browser**: tab dashboard `http://<IP-VPS>:8080` (atau lewat tunnel `ssh -L 8080:localhost:8080 -p <PORT-SSH> root@<IP-VPS>` → `http://127.0.0.1:8080`)
3. **Browser tab 2**: `file://` ke folder `output/` (untuk buka dossier PDF)
4. **Chat Telegram**: layar chat MATA (notifikasi hari ini sudah ada di situ — bukti live)
5. **Sesi Hermes** (TUI/gateway)
6. **Terminal 2 (opsional, B-roll)**: `journalctl -u mata -f`
7. **Sebelum rekam S2**: `rm -f output/dossier_*.pdf` — biar PDF "terlahir" di depan kamera

---

## 5️⃣ NASKAH REKAM PER ADEGAN

> VO = baca natural, jangan kaku. [TEKS] = overlay di OBS (Text source).

### ── KELOMPOK A — TERMINAL ──────────────────────────────

#### S2 — PINDAI & DETEKSI (±90 dtk)
- **Sebelum REK:** `rm -f output/dossier_*.pdf`
- **Jalankan (ketik pelan, biarkan "hidup"):** `python3 run.py cycle`
- **VO:** *"Coba kita jalankan satu siklus. MATA mengumpulkan data, menjalankannya lewat rule engine, dan — lihat — lima indikasi terdeteksi. Dua di antaranya tingkat tinggi. Semuanya dari data yang sudah bisa diakses siapa pun — hanya tidak pernah dibaca secara sistematis."*
- [TEKS kecil]: `48 pengumuman → 5 indikasi · rule engine transparan`
- Catatan: jangan mempercepat; salah ketik = ketik ulang (manusiawi, sah).

#### S3 — "HARGA DI PASAR" (±45 dtk)
- **Jalankan:** `python3 run.py analyze` → biarkan selesai → **zoom/scroll ke blok `[D1 · TINGGI]`** (baris: Rp 2.700.000.000 vs Rp 800.000.000 · +238%)
- **VO:** *"Indikasi pertama: sebuah proyek rehabilitasi jalan senilai 2,7 miliar. Harga referensinya dari katalog: 800 juta. Deviasinya: 238 persen — dan ini bukan tebakan: rumusnya (nilai minus referensi) dibagi referensi, dengan ambang 30 persen yang bisa kamu ubah di config. Setiap angkanya punya ID record dan tautan sumbernya."*
- [TEKS]: `Rp2,7 M vs referensi Rp800 jt → +238% · rumus & ambang dipublikasikan`

#### S6a — IDENTITAS VPS (±20 dtk)
- **Jalankan:** `hostname && nproc && free -h | head -2 && df -h / | tail -1`
- **VO:** *"Dan ini panggungnya. MATA berjalan 24 jam nonstop di **AI Hosting IDwebhost** — VPS Hermes: empat core, empat gigabyte, dua puluh gigabyte SSD — dan lihat di hostname-nya: `ubuntu24-hermes-...` instance AI Hosting yang disediakan panitia."*
- ⚠️ Sebutan verbal **"AI Hosting IDwebhost" = di scene ini** (syarat kompetisi).

#### S6b — SERVICE 24/7 (±40 dtk)
- **Jalankan:** `systemctl status mata | head -12` lalu `journalctl -u mata --since "2026-09-11 10:18" | head -15`
- **VO:** *"Bukan laptop yang matinya tergantung tidurku. Ini service: kalau mati, dia restart sendiri — baris itu barusan terjadi di depan kalian. Kalau data sumber bermasalah, dia melapor jujur — 'monitor offline, coba lagi' — bukan pura-pura bekerja. Keandalan yang jujur."*
- Catatan: biarkan baris **auto-restart** (10:18:22) terlihat — itu bukti keandalan.

#### B-ROLL — JOURNALCTL "BERNAPAS" (±20 dtk)
- `journalctl -u mata -f` — untuk cut transisi antar scene.

### ── KELOMPOK B — DASHBOARD :8080 ───────────────────────

#### S1 — APA INI (±40 dtk)
- **Layar:** dashboard penuh, **slow zoom** (transform OBS perlahan)
- **VO:** *"MATA adalah AI agent yang berjalan 24/7 di VPS. Ia memantau data pengadaan publik — pengumuman LPSE, e-katalog, e-kontrak — lalu menjalankan aturan deteksi yang **transparan dan bisa diaudit**. Bukan black-box: setiap rumus dan ambangnya bisa kamu baca. Hasilnya bukan vonis — tapi **indikasi, lengkap dengan bukti dan angkanya**."*
- [TEKS]: `Data publik · Aturan transparan · Indikasi, bukan vonis`

#### S4 — "SATU VENDOR, BANYAK KONTRAK" (±40 dtk)
- **Layar:** bagian tabel vendor (Konsentrasi penyedia) — PT Bebesen Abadi: 10 proyek
- **VO:** *"Indikasi kedua lebih visual. Satu penyedia — PT Bebesen Abadi — memenangkan 10 dari 48 proyek, dengan porsi nilai 27,5 persen dari total pengadaan. Dalam pengadaan yang sehat, tidak seharusnya ada satu nama yang sedominan itu. Prinsipnya sederhana: terbuka, transparan, **kompetitif**."*
- [TEKS]: `1 vendor = 10/48 proyek · ≥10 proyek & ≥25% nilai = flag`

#### S6c — MONITOR & GRAFIK (±20 dtk)
- **Layar:** badge **MONITOR ONLINE** + grafik nilai per bulan (jendela Desember menonjol)
- Visual tanpa VO (sambung langsung ke S5).
- 📌 **Lower-third `lowerthird_aihosting.png` aktif di seluruh grup S6** → syarat sebut nama terpenuhi 2× (verbal + lower-third).

### ── KELOMPOK C — DOKUMEN ───────────────────────────────

#### S5 — DOSSIER + DRAFT LAPORAN (±60 dtk)
- **Layar:** buka `output/dossier_2026-09-12.pdf` (yang lahir di S2) → scroll perlahan: halaman indikasi → lampiran record → lalu `laporan_draft_APIP.txt`
- **VO:** *"Yang MATA buat bukan sekadar notifikasi. Ini dossier: per indikasi ada buktinya, kalkulasinya, penjelasan, dan langkah lanjutnya. Dan ini — draft laporan resmi ke APIP. Perhatikan: MATA **menyiapkan**, tapi **kamu** yang memutuskan dan mengirim. Tidak ada yang auto-kirim ke siapa pun. Karena akuntabilitas yang serius berjalan lewat **kanal resmi** — bukan vonis dari satu aplikasi."*
- [TEKS]: `Dossier PDF · Draft laporan APIP · Human-in-the-loop`

### ── KELOMPOK D — AGEN ──────────────────────────────────

#### S7 — HERMES: BISA DITANYA (±40 dtk)
- **Layar:** sesi Hermes. Ketik di depan kamera: `Bagaimana kondisi MATA hari ini?` → biarkan menjawab (angka + penutup etika). Kalau sempat: tunjukkan juga baris cron 07.00.
- **VO:** *"Karena MATA dibangun di atas Hermes Agent, ia tidak diam di balik dashboard. Kamu bisa bertanya langsung: 'Bagaimana kondisi hari ini?' — dan dia menjawab dengan angka, bukan basa-basi. Tiap pagi jam tujuh, dia mengirim ringkasan harian sendiri: berapa yang dipindai, apa yang baru terdeteksi, apa yang berubah."*
- **PLAN B** (Hermes lambat/gagal): layar = **screenshot percakapan** + VO: *"Ini jawaban MATA saat ditanya kondisi hari ini…"* — tetap sah.
- [TEKS]: `Hermes Agent · cron 07.00 · ringkasan harian otomatis`

### ── KELOMPOK E — KARTU TEKS (OBS: Text source, background HITAM) ──

#### S0 — HOOK (±40 dtk)
Teks muncul satu-satu (jeda 1 dtk antar baris), baca pelan:
1. "Pengadaan pemerintah: **triliunan rupiah** per tahun."
2. "BPKP: modus manipulasi penganggaran & pengadaan = **Rp141 triliun**."
3. "KPK (Des 2025): 'pemenang sudah dikondisikan' — HPS bocor, fee 15–20%."
4. "Datanya? **Sudah dibuka untuk publik.**"
5. (jeda) — "**Tapi tidak ada yang membacanya untuk rakyat.**"
- **VO:** *"Setiap tahun, negara mengeluarkan triliunan rupiah lewat pengadaan. Dan pemerintah sudah membuka datanya untuk publik. Masalahnya bukan data tidak ada. Masalahnya: tidak ada yang membacanya untuk kita. Ini MATA — yang membacanya, 24 jam, tanpa lelah."*
- [TEKS besar penutup scene]: **MATA — Watchdog Akuntabilitas Pengadaan**

#### S8 — ETIKA (±30 dtk)
Kartu satu per satu:
1. "Hanya data **publik** — setiap klaim punya tautan sumber."
2. "**Indikasi, bukan vonis.** Tidak ada yang divonis satu aplikasi."
3. "**Human-in-the-loop** — MATA menyiapkan, manusia yang mengirim."
4. "Pelaporan via **kanal resmi**: LAPOR!, Ombudsman, KPK, APIP/BPKP."
- **VO:** *"Ada satu hal yang lebih penting daripada fitur: batas. MATA hanya membaca data publik. Ia menyebut 'indikasi', bukan 'bersalah'. Dan ia tidak pernah mengirim apa pun tanpa manusia yang memutuskan. Akuntabilitas publik tidak boleh berubah jadi alat menghakimi."*

#### S9 — PENUTUP (±30 dtk)
- Teks: *"Semoga tidak pernah dipuji. Semoga cukup diawasi."*
- **VO:** *"MATA — AI agent yang mengawasi agar uang kita diawasi. Dibangun dengan AI Hosting IDwebhost di AI HackFest 2026. Semoga ia tidak pernah dipuji — karena artinya tidak ada yang perlu diawasi. Semoga cukup... diawasi."*
- [TEKS akhir]: `MATA · AI HackFest 2026 · Productivity & Personal AI · Hermes Agent`

---

## 6️⃣ URUTAN REKAM (±45–60 menit total)

| # | File | Scene | Layar | Durasi |
|---|------|-------|-------|--------|
| 1 | take-S2.mp4 | Pindai & deteksi | terminal | 90 dtk |
| 2 | take-S3.mp4 | Harga di pasar | terminal | 45 dtk |
| 3 | take-S6a.mp4 | Identitas VPS | terminal | 20 dtk |
| 4 | take-S6b.mp4 | Service 24/7 | terminal | 40 dtk |
| 5 | take-broll.mp4 | journalctl -f | terminal | 20 dtk |
| 6 | take-S1.mp4 | Apa ini | dashboard | 40 dtk |
| 7 | take-S4.mp4 | Satu vendor | dashboard | 40 dtk |
| 8 | take-S6c.mp4 | Monitor & grafik | dashboard | 20 dtk |
| 9 | take-S5.mp4 | Dossier | dokumen | 60 dtk |
| 10 | take-S7.mp4 | Hermes | chat | 40 dtk |
| 11 | take-S0.mp4 | Hook | kartu teks | 40 dtk |
| 12 | take-S8.mp4 | Etika | kartu teks | 30 dtk |
| 13 | take-S9.mp4 | Penutup | kartu teks | 30 dtk |

Antara scene: hentikan REK → atur layar scene berikutnya → REK lagi. (Kartu teks S0/S8/S9 boleh direkam terakhir — paling tidak berisiko.)

---

## 7️⃣ GATE KEWAJIBAN — cek satu-satu SEBELUM upload

- [ ] Durasi final **5–10 menit**
- [ ] Landscape **16:9, ≥1080p**
- [ ] Proses agent **end-to-end** terlihat (bukan slide-only)
- [ ] ≥1 adegan **environment VPS AI Hosting**: terminal + dashboard (S6a/b/c) ✓
- [ ] Sebut **"AI Hosting IDwebhost" ≥1×** — verbal (S6a) + lower-third (S6) — pengaman ganda
- [ ] **Watermark** logo IDwebhost di SEMUA scene sejak detik 0
- [ ] **Tanpa musik berhak cipta** (naskah tanpa musik; kalau mau, YouTube Audio Library saja)
- [ ] Upload YouTube/TikTok/IG **PUBLIK atau UNLISTED** (bukan private)
- [ ] Tidak ada footage orang/pihak lain

---

## 8️⃣ POST-REKAM MALAM INI (±30 menit)

1. **Review tiap scene** (putar sekali): suara jernih? angka terbaca? scene gagal? → catat yang perlu **re-take Hari 3**
2. **Gabungkan** S0→S9 (Cutscene/CapCut/Shotcut): import → urutkan → hard cut antar scene → export **1080p H.264**
3. **Simpan 2 kopi**: `~/footage/` di VPS + laptop
4. Screenshot tambahan (bahan artikel + form submit): dashboard :8080 + `systemctl status mata`

---

## 9️⃣ TIMELINE SISA SPRINT

| Hari | Pekerjaan |
|---|---|
| **2 — Sabtu (malam ini)** | Patch §1 → rekam 13 file → draf gabungan → 2 kopi |
| **3 — Minggu** | Re-take scene gagal (jika ada) → export final → **upload YouTube** → **publish artikel** (`11-draf-artikel.md`) |
| **4 — Senin** | Polish (jika perlu) → TikTok/IG Reels 60–90 dtk (opsional: S0 + potongan S2 + S5 + S9) |
| **5 — Selasa** | Buffer + **SUBMIT**: link video + link artikel |
| ⚠️ **Setelah 15 Sep** | VM/VPS dimatikan — **semua adegan VPS harus sudah terekam** |

---

## 🔟 PLAN B CEPAT

| Masalah | Solusi |
|---|---|
| `cycle` gagal di depan kamera | `python3 run.py demo` (deterministik) — narasi S2–S5 tetap valid |
| Dashboard tak terbuka dari browser | Tunnel: `ssh -L 8080:localhost:8080 -p <PORT-SSH> root@<IP-VPS>` → buka `http://127.0.0.1:8080` |
| Hermes lambat/tak menjawab | Screenshot percakapan + VO (tetap sah) |
| Salah ucap / salah ketik | Rekam ulang **scene itu saja** — bukan seluruh video |
| Mic gaung | Pakai headphone / dekatkan mic; rekam ulang scene |
| PDF tak muncul di S2 | `rm -f output/dossier_*.pdf` dulu, pastikan `cycle` sampai `[5/5]` |
