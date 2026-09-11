# SIRENEKAMPUNG × ACEH TENGAH — Bedah Lengkap & Paket Eksekusi
**Afrizal Munthe** · AI HackFest 2026 · Batch 3 (11–15 Sep 2026) · Productivity & Personal AI · Hermes Agent

> Posisi satu kalimat: **"Agen kesiapsiagaan bencana keluarga & gampong — 24/7 di VPS, alert <30 detik, ceklis keluarga, dan log insiden yang rapi."**
> Tagline demo: *"Ketika listrik mati dan internet putus, keluargamu sudah tahu harus di mana."*

---

## 1. MENGAPA ACEH TENGAH (locus) — data yang bisa dikutip

### Profil wilayah
- Kabupaten Aceh Tengah: ibu kota **Takengon**, Dataran Tinggi Gayo (±1.300 mdpl), **14 kecamatan, 295 gampong**, luas 4.454 km², populasi **232.606 jiwa** (BPS, 31 Des 2024 — via Wikipedia/BPS; verifikasi di artikel).
- Geografis rawan: pegunungan Bukit Barisan + sistem sungai (Agusan, Sesa, Kekecutan) + zona patahan aktif Sumatra + sejarah tsunami 2004 (episenter dekat pesisir utara Aceh).
- Musim hujan puncak Oktober–Desember → **relevansi waktu kompetisi: kita membangun tepat sebelum musim hujan kembali.**

### Peristiwa baru-baru ini (ini "why now" yang tidak dimiliki peserta lain)
| Waktu | Peristiwa | Angka (sumber — verifikasi di artikel) |
|-------|-----------|------------------------------------------|
| Nov–Des 2025 | **Banjir bandang + longsor** (Badai Siklon 04B Selat Malaka) | **295 gampong di 14 kecamatan** terdampak; **14.899 jiwa di 30 gampong terisolasi** (Posko Hidrometeorologi Kab. Aceh Tengah, 31 Des 2025, via Antara) |
| 1 Des 2025 | **PN Takengon terisolasi total**; akses, listrik, komunikasi putus | 5 SUTET Arun–Bireuen roboh → gelap total; **fiber optik putus** → internet lumpuh; hanya Starlink terbatas di kompleks bupati (MARINews MA, 1 Des 2025) |
| 2 Des 2025 | Korban se-Aceh | **173 meninggal, 204 hilang, 443.001 jiwa mengungsi (828 titik), 77.049 rumah rusak** (Posko Pemprov Aceh, via CNN Indonesia) |
| 8–11 Apr 2026 | **Banjir & longsor susulan** | Hujan deras sejak 8 Apr → akses jalan lumpuh (Waspada.id, 11 Apr 2026) |
| 70% bangunan Takengon | Kerusakan terparah | Terutama pinggiran **Danau Lut Tawar** (saksi warga, Kompas, 2 Des 2025) |

### Pola kegagalan yang kita selesaikan (problem statement — 5 baris untuk brief & artikel)
Dari berita di atas, pola yang berulang dan **bukan** soal "tidak ada sirene":
1. **Komunikasi keluarga putus** saat infrastruktur jatuh (elektrifikasi & fiber) — anggota keluarga tidak saling tahu kondisi.
2. **Info vacuum → panik & hoaks** — tidak ada sumber satu kalimat "apa yang terjadi, apa yang harus dilakukan".
3. **Daftar darurat keluarga tidak ada / tersebar** — obat, kontak, titik kumpul, dokumen.
4. **Tidak ada log insiden gampong** yang rapi untuk laporan & bantuan.
5. **Kesiapsiagaan harian tidak ada** — tidak ada ritme drill, cek logistik, pemutakhiran kontak.

> **Insight kunci (untuk juri):** masalah terbesar bukan mendeteksi gempa (BMKG sudah bagus) — masalahnya **apa yang terjadi setelah alarm**: koordinasi keluarga, aksi, dan pencatatan. SireneKampung membangun **lapis koordinasi keluarga & gampong** di atas data BMKG.

---

## 2. BRIEF 1 HALAMAN (siap jadi halaman pembuka artikel)

- **Masalah:** Di Aceh Tengah, satu siklon (Nov 2025) mengisolasi 295 gampong & 14.899 jiwa; listrik dan internet putus. Saat itu, keluarga tidak punya cara cepat untuk (a) tahu ada apa, (b) saling memastikan selamat, (c) mengingat apa yang harus dibawa/dilakukan, (d) membuat laporan untuk bantuan.
- **Target user:** (1) Keluarga di dataran tinggi Gayo (utama), (2) Pengurus gampong/RT (sekunder — log & laporan).
- **Solusi:** SireneKampung = AI agent (Hermes) di VPS 24/7 yang: memonitor **data BMKG terbuka** (gempa + cuaca/hujan) via cron → menghitung estimasi guncangan/hujan untuk lokasi gampong → **alert <30 detik** ke grup keluarga (Telegram/WA) dengan instruksi spesifik → **check-in keselamatan** (siapa sudah konfirmasi "aman") → **daftar darurat keluarga** yang dirawat agent → **log insiden + draft laporan gampong** (PDF).
- **Bukan apa:** bukan pengganti sirene resmi/INATEWS — **pelengkap di level keluarga & gampong**. (Disclaimer ini wajib & justru poin etika.)
- **Metrik dampak (demo):** alert tersampaikan <30 dtk dari data uji; 100% checklist keluarga terisi; 5/5 check-in terlacak (termasuk 1 reminder otomatis); 1 laporan gampong PDF otomatis; 1 reminder drill bulanan terjadwal.
- **Ciri khas (1 kalimat):** *"Agent yang tidak cuma memberi tahu, tapi memastikan — siapa yang sudah aman, siapa yang belum, dan apa yang belum ditindak."*

---

## 3. CARA KERJA PRODUK

### 3.1 Monitor (cron, tiap 60 detik)
- **Sumber data (semua terbuka & legal):**
  - **Gempa:** `https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json` (BMKG Open Data — **wajib cantumkan BMKG sebagai sumber** di UI & artikel = kepatuhan sekaligus nilai plus).
  - **Tsunami (flag):** field `tsunami` (ya/tidak) di dataset BMKG + (opsional) status INATEWS.
  - **Hujan/cuaca (opsional, hari 3+):** prakiraan/warning hujan BMKG untuk wilayah Takengon/Aceh Tengah (data.bmkg.go.id) → deteksi potensi banjir/longsor (hidrometeorologi — penyebab utama bencana di locus ini).
- **Rule engine (transparan, bisa diaudit di artikel):**
  - Input: magnitude, koordinat episenter, kedalaman + koordinat lokasi terdaftar (Takengon ≈ 4.63°N, 96.82°E — bisa diset per gampong).
  - Jarak hiposenter (haversine) → **estimasi intensitas (skala MMI)** dengan rumus heuristik sederhana & terbuka (mis. `I ≈ M − 2.5·log10(max(jarak,10)) − 0.002·jarak + 4.0`) → **bukan black-box**: artikel memajang rumusnya.
  - Threshold (bisa diset user):
    - **LEVEL SIAGA** (I≥V terestimasikan) → alert keluarga dengan instruksi gempa.
    - **LEVEL DARURAT** (field tsunami=ya, atau I≥VI) → alert darurat + instruksi evakuasi ke titik tinggi (posisi jujur: *ikuti juga arahan BMKG/INATEWS*).
    - **Hujan lebat** (jika modul cuaca aktif) → peringatan potensi longsor/banjir + checklist.
  - **Validasi:** dataset "Gempa Dirasakan" BMKG bisa dipakai untuk mengkalibrasi/menguji rumus di artikel (transparansi ilmiah → Eko & Onno suka).

### 3.2 Respons (<30 detik)
- Pesan alert (template per skenario, bahasa Indonesia + opsi Gayo/Inggris) berisi: apa (M, lokasi, kedalaman, waktu) → estimasi guncangan di lokasimu → **3 langkah pertama** (gempa: jauh dari kaca/struktur rawan, siap evakuasi; longsor: jalur evakuasi; banjir: titik tinggi) → **titik kumpul keluargamu** → "balas **AMAN** jika selamat".
- **Check-in engine:** agent melacak siapa yang sudah konfirmasi; yang belum → reminder 5 menit kemudian; status board sederhana ("4/5 aman, 1 belum: Budi — reminder terkirim 13:05").
- **Daftar darurat keluarga** (di-memory agent): anggota (kondisi medis, obat), titik kumpul, nomor kontak penting (BPBD, puskesmas, keluarga jauh), dokumen penting & lokasi, logistik (air, baterai, P3K). Bisa dipertanyakan kapan pun: *"Obat Ibu apa?"*, *"Titik kumpul kita di mana?"*

### 3.3 Pasca-peristiwa & Kesiapsiagaan harian
- **Log insiden** (SQLite): tiap event (walaupun kecil) tercatat: waktu, magnitude, level, respons, check-in.
- **Draft laporan gampong (PDF):** 1-klik setelah event: ringkasan event + status check-in + aksi yang diambil + kebutuhan (template) — siap dikirim ke kecamatan/BPBD.
- **Mode kesiapsiagaan:** cron bulanan → reminder **drill** (gladi); cek daftar (kontak usang? logistik?); status monitor jujur (*"monitor online, cek terakhir 13:59:42, 4.2 dtk lalu"*).
- **Mode jujur saat gagal:** jika API tidak terjangkau (mis. jaringan VPS bermasalah) → agent mengirim status: *"monitor offline, coba lagi 1 menit lagi"* — **reliability yang jujur** = poin Eko.

### 3.4 Arsitektur (di VPS 4 Core/4GB/20GB — AI Hosting IDwebhost x CloudBaik)
```
        ┌────────────────────────────  VPS (24/7)  ────────────────────────────┐
        │                                                                      │
  BMKG API ──► [monitor.py] (cron 60 dtk) ──► [rule engine] ──► keputusan level
   (autogempa,        │  (Python ringan, log ke file)      │
    cuaca)            │                                    ▼
                      │                          ┌─────────────────────┐
                      │                          │  SQLite             │
                      │                          │  - registry keluarga │
                      │                          │  - insiden & checkin │
                      │                          │  - logistik/kontak   │
                      │                          └──────────┬──────────┘
                      │                                     │
                      ▼                                     ▼
        [Hermes Agent]  ◄──── trigger (event/reminder/user)
         - gateway: Telegram + WhatsApp
         - cron: cek-in reminder, drill bulanan, laporan mingguan
         - memory: profil keluarga, skill (belajar pola pengguna)
         - subagent: draft laporan gampong (paralel, zero-context)
                      │
                      ▼
        [Grafana]  (grafik guncangan riwayat, status check-in, uptime)
        [WeasyPrint] (PDF laporan gampong)
        └──────────────────────────────────────────────────────────────────────┘
```
- Semua containerized (Docker) atau systemd + auto-restart; RAM aman: Hermes + Python + SQLite + Grafana ≈ <2.5GB.
- **Narasi AI Hosting:** VPS inilah panggungnya — uptime 24/7, dashboard CloudBaik/IDwebhost, terminal, cron terlihat berjalan. (Wajib tampil di video.)

---

## 4. LIMA SKENARIO DEMO (ini naskah inti video)

| # | Skenario | Aksi di demo | Yang dilihat juri | Bobot yang dipukul |
|---|----------|--------------|-------------------|--------------------|
| 1 | **Gempa terestimasikan kuat** | Injeksi data uji (M6.5, episenter 40 km dari Takengon) → alert <30 dtk ke grup Telegram → 3 anggota balas "AMAN", 1 belum → reminder otomatis → status board | Pipeline data→rumus→alert→check-in **berjalan nyata** (bukan script) | Efektivitas 30% + Teknis 20% |
| 2 | **Skenario tsunami (flag BMKG)** | Data uji `tsunami=ya` M8.0 offshore → pesan DARURAT + instruksi evakuasi + disclaimer "ikuti BMKG/INATEWS" | Batas etis dijaga; pesan yang benar | Relevansi 20% + Teknis (desain aman) |
| 3 | **Kesiapsiagaan harian** | Tanya agent: *"Obat Ibu apa?"* / *"Titik kumpul?"* → jawab dari memory; tampilkan cron drill bulanan; tampilkan status monitor (jam terakhir cek) | Agent sebagai **personal AI** (bukan sekadar alarm) | Kreativitas 15% + Relevansi |
| 4 | **Pasca-peristiwa** | 1-klik: PDF laporan gampong ter-generate (ringkasan + check-in + kebutuhan) + log insiden di Grafana | Output **dunia nyata** (bisa dikirim ke BPBD) | Efektivitas + Storytelling |
| 5 | **Keandalan jujur** | Matikan akses API (simulasi) → agent: *"monitor offline, retry 60 dtk"* → pulih → *"monitor online kembali"* + dashboard & terminal VPS ditampilkan | **Reliability** yang jujur + adegan VPS wajib | Teknis 20% (kriteria "reliability" eksplisit!) |

> Catatan: injeksi data uji = **sinyal etika** (tidak kita klaim memicu alarm palsu ke warga nyata; demo dilakukan di grup uji privat). Sebutkan ini 1 kalimat di video & artikel.

---

## 5. SETUP DI VPS — URUTAN PERINTAH (rangka; detail saat eksekusi)

**HARI 1 (hari ini) — fondasi**
1. Verifikasi VPS aktif (dashboard CloudBaik/IDwebhost; kendala → `info@cloudbaik.com`).
2. Install **Hermes Agent** (pakai jalur resmi AI Hosting IDwebhost/CloudBaik — screenshot dashboard untuk video).
3. Setup gateway: **Telegram bot** (token) sebagai kanal utama demo; (WA opsional hari 2).
4. Uji dari VPS: `curl https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json` → pastikan JSON masuk + catat field-nya.
5. Buat `db.sqlite` (registry keluarga demo: 5 anggota sintetis, titik kumpul, obat, kontak; 1 gampong demo).
6. Tulis brief + catat 5 skenario demo (di atas) + 6 statistik artikel (bagian 7).

**HARI 2 — mesin inti**
7. `monitor.py`: poll 60 dtk → parse → simpan ke SQLite → log (JSON lines).
8. Rule engine + threshold per lokasi (Takengon + 2 gampong contoh); fungsi `estimasi_intensitas()`.
9. Trigger ke Hermes (event → pesan alert template per level).
10. Check-in engine: parse balasan "AMAN" per anggota, reminder 5 menit, status board.
11. Uji: injeksi 3 data uji (kecil/siaga/darurat) → verifikasi alert & check-in.

**HARI 3 — output dunia nyata + REKAM VIDEO v1**
12. Generator **PDF laporan gampong** (weasyprint) + draft via subagent.
13. **Grafana** (opsional tapi sangat disarankan): grafik riwayat, status check-in, uptime.
14. Mode jujur: simulasi API down → pesan status monitor.
15. Jalankan 5 skenario beruntun tanpa error (3× ulangan) → **rekam video v1** (5–10 mnt, 16:9, 1080p).

**HARI 4 — polish & narasi**
16. Reliability: auto-restart (systemd/docker `restart: unless-stopped`), log terpusat, handling error API.
17. Rehearsal demo (siapkan alur "live" + fallback rekaman layar). Re-take video jika perlu.
18. **Artikel draft** (800+ kata; struktur di bagian 8) + diagram arsitektur (dari bagian 3.4).

**HARI 5 — submit**
19. Final video (watermark IDwebhost, sebut "AI Hosting IDwebhost", adegan dashboard+terminal) → upload YouTube/TikTok **publik/unlisted**.
20. Artikel terbit (blog/LinkedIn) + **2 backlink**: "AI Hosting"→idwebhost.com/ai-hosting, "Cloud VPS"→cloudbaik.com.
21. Isi form submit (link video + artikel). **Selesai sebelum VM dimatikan.**

---

## 6. RISIKO & MITIGASI (spesifik build ini)

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| **False alarm** (rumus over-estimasi) | Kepercayaan hancur; etik buruk | Threshold konservatif; mode "konfirmasi dulu"; label jelas "estimasi, bukan pengumuman resmi"; kalibrasi vs dataset Gempa Dirasakan BMKG |
| **Posisi legal/etis** (bukan EW resmi) | Klaim berlebihan = minus | Positioning tetap: *pelengkap keluarga & gampong*; disclaimer di UI, video, artikel; kredit BMKG di setiap sumber data |
| **API BMKG berubah/turun** | Monitor mati | Wrapper terpisah + cache + pesan status jujur + retry; (daya tahan justru jadi fitur demo skenario 5) |
| **PDP** (kontak, lokasi, kondisi medis) | Pelanggaran UU PDP | Self-hosted; data minimal; consent saat onboarding; **demo 100% data sintetis** (sebutkan di artikel = best practice) |
| **RAM 4GB** | Grafana + Hermes + monitor berebut | Drop Grafana jika perlu (dashboard = terminal + PDF); SQLite; matikan service tak terpakai; tes beban hari 1–2 |
| **Kanal WA tidak stabil** | Demo gagal | **Telegram = kanal utama demo** (stabil, resmi); WA sebagai bonus |
| **Demo "terlalu mudah" menurut juri** | Nilai teknis diragukan | Tunjukkan rumus + kalibrasi + log + mode jujur; artikel memuat trade-off (Eko menghargai kejujuran teknis) |

---

## 7. DATA & STATISTIK UNTUK ARTIKEL (verifikasi sumber saat menulis)
1. Populasi Aceh Tengah: **232.606 jiwa**; 14 kecamatan, 295 gampong (BPS 2024).
2. **295 gampong terdampak, 14.899 jiwa terisolasi** — Posko Hidrometeorologi Kab. Aceh Tengah, 31 Des 2025 (Antara).
3. Se-Aceh Des 2025: **173 meninggal, 204 hilang, 443.001 jiwa mengungsi, 77.049 rumah rusak** (Posko Pemprov Aceh, 2 Des 2025).
4. **PN Takengon terisolasi; 5 SUTET roboh; fiber putus** (1 Des 2025).
5. **Banjir-longsor susulan 8–11 Apr 2026** (Waspada.id).
6. Musim hujan puncak **Okt–Des** → "waktu membangun adalah sekarang".
7. Indonesia: salah satu negara dengan frekuensi bencana tertinggi dunia (±2.000+ peristiwa/tahun, BNPB — ambil angka tahunan terbaru).
8. **Kredit BMKG** di setiap kutipan data (kepatuhan lisensi data terbuka + poin etika).

---

## 8. SUDUT CERITA (storytelling 15%)

**Naskah pembuka video (±30 dtk, contoh):**
> "November 2025, di dataran tinggi Gayo — 295 gampong terdampak banjir bandang dan longsor. Listrik mati. Fiber putus. Internet tidak ada. Pertanyaannya bukan 'kapan gempa berikutnya', tapi: *siapa yang tahu keluargamu aman?* SireneKampung dibangun untuk 30 detik pertama itu — dan untuk semuanya setelahnya."

**Struktur artikel (800+ kata):**
1. **Buka:** 2 paragraf kejadian Aceh Tengah (data di atas) + pertanyaan "siapa yang tahu keluargamu aman?"
2. **Masalah:** 5 pola kegagalan (bagian 1) — masalahnya koordinasi, bukan deteksi.
3. **Solusi:** arsitektur (diagram) + 5 skenario + rumus intensitas (dipajang — transparan).
4. **Mengapa AI agent (Hermes):** cron, multi-kanal, memory, subagent; self-hosted 24/7 di [AI Hosting](https://idwebhost.com/ai-hosting/) → [Cloud VPS](https://cloudbaik.com/) 24/7. *(2 backlink wajib, natural)*
5. **Dampak terukur:** metrik demo.
6. **Kejujuran teknis:** trade-off (heuristik vs resmi, batas PDP, mode jujur) — paragraf yang Eko & Onno cari.
7. **Open source & replikasi:** semua komponen terbuka; rumus bisa diaudit; roadmap (gampong→kecamatan).
8. **Bisnis & keberlanjutan:** Rp10rb/bln per keluarga; pilot B2G kecamatan; grant/CSR; open-core.
9. **Penutup:** "Semoga tidak pernah dipuji. Semoga cukup siap."

---

## 9. PETA SKOR PER JURI

| Juri | Yang mereka lihat di SireneKampung |
|------|-------------------------------------|
| **Onno W. Purbo** | Public good murni; open data + rumus terbuka (bisa diaudit); komunitas gampong; spirit "teknologi untuk rakyat" (RT/RW-Net 2.0); data BMKG dikreditkan dengan benar |
| **Ogi S. Pornawan** | TAM 232.606 jiwa (1 locus) → replikasi ke 14 kecamatan/732 kab-sekun; SaaS keluarga + pilot B2G; AI Hosting IDwebhost benar-benar jadi infrastruktur (24/7, dashboard, uptime) |
| **Eko Novianto** | Pipeline nyata (API→rule engine→alert→check-in→PDF), reliability yang **jujur** (skenario 5), arsitektur bersih di VPS, kalibrasi vs data BMKG — bukan demo palsu |

**Bobot:** Efektivitas 30% (5 skenario nyata) · Teknis 20% (arsitektur + mode jujur) · Relevansi 20% (data bencana yang menganga) · Kreativitas 15% (check-in "siapa yang aman" + laporan gampong) · Storytelling 15% (cerita Gayo — milikmu).

---

## 10. CHECKLIST HARI INI (Jumat, 11 Sep — sisa hari)

- [ ] 15 mnt — Cek VPS aktif (dashboard CloudBaik/IDwebhost). Jika belum: email `info@cloudbaik.com` SEKARANG (SLA aktivasi bisa makan waktu).
- [ ] 30 mnt — Install Hermes Agent + setup gateway Telegram (bot token) + test chat bolak-balik.
- [ ] 15 mnt — Uji `autogempa.json` dari VPS; simpan contoh respons; catat field (magnitudo, koordinat, kedalaman, waktu, tsunami).
- [ ] 30 mnt — Buat `db.sqlite` + registry keluarga demo (5 anggota sintetis, titik kumpul, obat, kontak, 1 gampong).
- [ ] 30 mnt — Tulis file `monitor.py` versi 0 (poll → log ke console) + jalankan.
- [ ] 20 mnt — Catat 6–8 statistik artikel + daftar sumber (bagian 7) ke file `sumber.md`.
- [ ] Sisa — Rehearse alur 5 skenario di kepala; screenshot dashboard VPS (bahan video).

**Target akhir hari ini:** Hermes hidup di VPS + data BMKG mengalir + brief terkunci. Kalau ini tercapai, kita on-track untuk 5 hari.
