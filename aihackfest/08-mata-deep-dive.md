# MATA — Watchdog Akuntabilitas Publik: Bedah Lengkap & Paket Eksekusi
**Afrizal Munthe** · AI HackFest 2026 · Batch 3 (11–15 Sep 2026) · Productivity & Personal AI · Hermes Agent

> **Posisi satu kalimat:** *"MATA membaca data pengadaan yang SUDAH dibuka pemerintah, 24/7 — dan mengubah 'pemandangan' jadi 'bukti' sebelum ada yang membongkarnya."*
> Tagline demo: *"Uang itu uangmu. MATA membacanya supaya kamu tidak perlu bisa akuntansi."*
> **Lokus:** pengadaan **Aceh Tengah / Aceh** (kampung halaman) → replikasi ke seluruh Indonesia.

---

## 1. MENGAPA MATA (dan mengapa ini "bahasa Onno")

### Masalah (masif + terverifikasi + "why now")
Pengadaan barang/jasa pemerintah (PBJ) = **saluran uang rakyat terbesar**, dan **juga titik rawan korupsi terbesar**:
| Sumber | Angka (verifikasi di artikel) |
|--------|-------------------------------|
| **BPKP** | Modus manipulasi penganggaran & pengadaan = kerugian **Rp141 triliun** |
| **BPK** | 15.689 masalah pengelolaan keuangan, semester I 2023 = **Rp18,19 triliun** |
| **KPK, Des 2025** | Bongkar **pengaturan lelang DJKA Medan 2021–2024**: "pemenang sudah dikondisikan", HPS bocor, setoran miliaran |
| **KPK, 2025** | **OTT PBJ Lampung Tengah**: **fee proyek 15–20%** + biaya politik |
| **BPA** | Rp26 triliun aset rampasan (2024–2026) — bukti skala kerusakannya |

**"Why now":** KPK sedang **aktif** menggarap kasus PBJ (Des 2025). Ini bukan isu historis — ini **berita minggu ini**.

### Pola kegagalan yang MATA selesaikan
Pemerintah **sudah** membuka datanya (LPSE/Panda, e-Katalog, e-Kontrak). Tapi:
1. **Data terbuka ≠ data dibaca.** Tak ada yang membacanya untuk rakyat.
2. **Anomali tersebar** di ribuan pengumuman → **tak terlihat oleh mata manusia**.
3. **Membongkar = mahal & lambat** (perlu tim, akuntan, waktu) → cuma lembaga besar yang bisa.
4. **Rakyat tak punya "inspektur pribadi."**

> **Insight kunci (untuk juri):** masalahnya bukan "data tidak ada" — **datanya sudah ada & terbuka**. Masalahnya **tak ada yang mengubah data jadi tindakan**. MATA mengisi celah itu: **dari "pemandangan" ke "bukti".**

### Fit kategori (Personal AI)
Didaftarkan di **Productivity & Personal AI** → frame: **"personal AI watchdog — agent pribadimu yang mengawasi uang publik yang menjadi hakmu."**
- Ini **agent personal** yang kamu (individu: warga, jurnalis, aktivis, ASN, peneliti) **jalankan & kendalikan sendiri** di VPS-mu.
- Dampaknya **public good** (juga sangat cocok ke kategori *Public Service / Open Innovation*) — juri akan menghargai jangkauannya, tapi positioning utama tetap **Personal AI**.
- **Patuh Aturan #7:** **deteksi anomali + lapor kanal resmi** (APIP/BPKP/KPK/Ombudsman/media) — **bukan vonis, bukan main hakim.**

---

## 2. BRIEF 1 HALAMAN
- **Masalah:** Uang pengadaan (triliunan) sudah didata & dibuka pemerintah, tapi **tidak ada yang membacanya untuk rakyat**; anomali (harga di pasar, 1 vendor menang banyak, keroyokan akhir tahun) **hanyut** di ribuan pengumuman.
- **Target user:** (1) Warga/aktivis/jurnalis yang ingin mengawasi daerahnya (utama), (2) ASN/APIP & peneliti (sekunder).
- **Solusi:** MATA = personal AI watchdog (Hermes) di VPS 24/7 yang: **memantau data PBJ terbuka** (Panda LKPP + LPSE daerah + e-Katalog + e-Kontrak) via cron → **rule engine transparan** mendeteksi anomali → **LLM menyusun dossier** (sumber, kalkulasi, pembanding, dasar hukum) → **draft laporan ke kanal resmi + ringkasan publik** → **memperbesar suara warga** yang melapor.
- **Bukan apa:** bukan "bukti korupsi" — **indikasi & pelaporan** (posisi hukum yang benar & aman).
- **Metrik dampak (demo):** N pengumuman dipindai → X anomali terdeteksi → 1 dossier lengkap + 1 draft laporan resmi + 1 ringkasan publik; 100% klaim bisa ditelusuri ke sumber.
- **Ciri khas (1 kalimat):** *"Agent yang membuat data yang sudah dibuka pemerintah akhirnya BERTINDAK — untuk rakyat biasa."*

---

## 3. CARA KERJA

### 3.1 Lapis data (semua terbuka & legal — kunci feasibility)
| Sumber | Isi | Peran |
|--------|-----|-------|
| **Panda LKPP** (portal PBJ nasional) + **LPSE daerah** (mis. LPSE Kab. Aceh Tengah / Prov. Aceh) | Pengumuman: nama pekerjaan, instansi/KPA, HPS/pagu, metode (tender/penunjukan/e-katalog), jadwal, pemenang | **Utama** — deteksi D2, D3, D4 |
| **e-Katalog / inaproc** (harga & spesifikasi terbuka) | Harga referensi barang/jasa | **Pembanding** — deteksi D1 (harga di pasar) |
| **e-Kontrak/SPAN** (Kemenkeu) | Kontrak >Rp50 jt: nilai, penyedia, tanggal | **Konteks** — D2, D3, D4 |
| **Fallback:** dataset PBJ sintetis-realistis (kalau akses terbata) | — | Jujur, tetap bisa demo |

> **Langkah pertama HARI 1: uji akses** Panda LKPP / LPSE daerah / inaproc dari VPS. Apa yang bisa di-scrape/diunduh secara legal → itu dataset inti. Siapkan 2–3 cadangan.

### 3.2 Rule engine (transparan, bisa diaudit — poin Eko & Onno)
Model data per pengumuman/kontrak: `{pekerjaan, instansi/KPA, wilayah, nilai/HPS, metode, penyedia/pemenang, tanggal_mulai, tanggal_selesai}`. Aturan:
- **D1 Harga di pasar:** nilai ≫ harga referensi e-Katalog/median proyek serupa (ambang mis. +30%) → flag.
- **D2 Konsentrasi vendor:** 1 penyedia menang **N proyek** / porsi nilai besar dalam periode → flag.
- **D3 Keroyokan akhir tahun:** lonjakan kontrak besar di **Q4/Desember** (jendela klasik) → flag.
- **D4 Vendor kecil menang besar:** track record penyedia sedikit/kecil, menang nilai besar → flag.
- **D6 Pola angka:** nilai identik/round-number di beberapa proyek (copy-paste anggaran) → flag.
- **D5 Phantom / tak ada fisik** & **D7 lelang tunggal** → **roadmap** (butuh data fisik/pembanding luar; disebut jujur, bukan diklaim).

> **Hibrida jujur:** **rule engine** (deterministik, bisa diaudit) men-flag → **LLM** menjelaskan *kenapa* mencurigakan + menulis narasi + menyusun dossier. Rumus & ambang **dipajang di artikel** (bukan black-box).

### 3.3 Dossier & pelaporan (output dunia nyata)
- **Dossier (PDF):** ringkasan anomali + **data mentah + sumber/URL** + **kalkulasi** + **pembanding** + **dasar hukum** (UU Tipikor, PP PBJ) + **level indikasi** + langkah lanjut. **Semua klaim bisa ditelusuri.**
- **Draft laporan ke kanal resmi** (APIP instansi, BPKP, **KPK**, Ombudsman, media) — **human-in-the-loop**: MATA menyiapkan, **kamu approve** kirim (jangan auto-kirim ke lembaga; posisi "siap kirim 1-klik" — jujur & aman).
- **Ringkasan publik** (infografis) — untuk warga/media (bukan vonis, tapi "indikasi yang bisa dicek").
- **Amplifikasi warga:** warga lapor "proyek di desanya tak ada" → MATA mencocokkan dengan data → memperkuat dossier.

### 3.4 Arsitektur (VPS 4 Core/4GB/20GB — AI Hosting IDwebhost x CloudBaik)
```
  [Panda LKPP / LPSE daerah]  [e-Katalog/inaproc]  [e-Kontrak]
          └──────────────►  [collector.py] (cron)  ──► SQLite (pengumuman/kontrak)
                                   │  (parse + normalisasi + log)
                                   ▼
                            [rule engine] (D1–D6, ambang transparan)
                                   │  flag anomali
                                   ▼
                       [Hermes Agent]  ◄─ cron + memory + subagent
                         - menyusun NARASI "kenapa mencurigakan" (LLM)
                         - dossier PDF (WeasyPrint) + draft laporan + ringkasan
                         - cron: pantau harian, rekap mingguan, eskalasi
                                   │
                                   ▼
                        [Grafana] (peta anomali, nilai, vendor, timeline)
```
- Containerized/systemd + auto-restart; RAM aman (Hermes + Python + SQLite + Grafana ≈ <2.5GB).
- **Narasi AI Hosting:** VPS 24/7 inilah panggungnya — dashboard CloudBaik/IDwebhost, terminal, cron terlihat. (Wajib tampil di video.)

---

## 4. LIMA SKENARIO DEMO (naskah inti video)

| # | Skenario | Aksi | Yang dilihat juri | Bobot |
|---|----------|------|-------------------|-------|
| 1 | **Pindai & deteksi** | MATA memindai N pengumuman PBJ (wilayah Aceh Tengah/Aceh) → rule engine flag D1–D3 | **Pipeline data→analisis nyata**, bukan mockup | Efektivitas 30% |
| 2 | **"Harga di pasar"** | 1 proyek: HPS ≫ harga e-Katalog → MATA hitung selisih, tunjukkan pembanding | Deteksi D1 dengan **kalkulasi terbuka** | Teknis 20% |
| 3 | **"Satu vendor, banyak kontrak"** | MATA memetakan 1 penyedia menang N proyek → diagram konsentrasi + porsi nilai | Pola D2 **visual**, sulit disangkal | Kreativitas 15% + Relevansi 20% |
| 4 | **Dossier + laporan** | 1-klik → **PDF dossier** (sumber, kalkulasi, dasar hukum, level indikasi) + **draft laporan ke APIP/KPK** (siap kirim) + ringkasan publik | Output **dunia nyata** yang bisa dikirim | Efektivitas + Storytelling 15% |
| 5 | **Keandalan & etika** | Status monitor (jam terakhir crawl, N record); tunjukkan **human-in-the-loop** (approve kirim) + disclaimer "indikasi, bukan vonis" + kredit sumber data | **Reliability + etika** (poin eksplisit rubrik) | Teknis 20% |

> **Etika demo:** semua data dari sumber **publik**; tampilkan **kredit sumber**; jangan menyebut nama perusahaan/personal dengan nada vonis — gunakan "indikasi" + data. Ini justru **kekuatan** di depan juri (kepatuhan Aturan #7).

---

## 5. SETUP DI VPS — URUTAN (rangka; detail saat eksekusi)

**HARI 1 (hari ini) — KUNCI DATA dulu (ini risiko terbesarnya)**
1. Verifikasi VPS aktif (dashboard CloudBaik/IDwebhost; kendala → `info@cloudbaik.com`).
2. **Uji akses data** dari VPS: Panda LKPP / LPSE Kab. Aceh Tengah / LPSE Prov. Aceh / inaproc / e-kontrak → **apa yang legal & bisa diambil?** Catat 1–3 sumber yang jalan.
3. (Fallback) Siapkan **dataset PBJ sintetis-realistis** (30–50 pengumuman, 3–5 vendor, nilai & tanggal bervariasi) agar demo tetap jalan kalau akses terbatas.
4. Install **Hermes Agent** + gateway **Telegram** (demo utama) + screenshot dashboard VPS.
5. Buat `db.sqlite` (skema pengumuman/kontrak) + simpan contoh data.

**HARI 2 — mesin inti**
6. `collector.py`: tarik/parse data → normalisasi → SQLite (cron harian).
7. **Rule engine** D1–D6 (fungsi + ambang) + output flag.
8. Trigger ke Hermes → LLM menyusun narasi "kenapa mencurigakan" per flag.

**HARI 3 — output dunia nyata + REKAM VIDEO v1**
9. **Generator dossier PDF** (weasyprint) + **draft laporan resmi** + **ringkasan publik**.
10. **Grafana**: peta anomali, konsentrasi vendor, timeline Q4.
11. Jalankan 5 skenario beruntun tanpa error (3×) → **rekam video v1** (5–10 mnt, 16:9, 1080p).

**HARI 4 — polish & narasi**
12. Reliability: auto-restart, log, handling error/crawl gagal (mode jujur).
13. Rehearsal demo (alur live + fallback). Re-take jika perlu.
14. **Artikel draft** (800+ kata) + diagram arsitektur + **daftar sumber & statistik**.

**HARI 5 — submit**
15. Video final (watermark IDwebhost, sebut "AI Hosting IDwebhost", adegan dashboard+terminal) → upload **publik/unlisted**.
16. Artikel terbit (blog/LinkedIn) + **2 backlink**: "AI Hosting"→idwebhost.com/ai-hosting, "Cloud VPS"→cloudbaik.com.
17. Isi form submit. **Selesai sebelum VM dimatikan.**

---

## 6. RISIKO & MITIGASI
| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| **Akses data** (scrape/ToS, format berubah) | Build macet | **HARI 1 kunci sumber**; 2–3 cadangan; **fallback dataset sintetis-realistis** + jujur; hanya ambil data **publik** (patuh ToS & Aturan kompetisi) |
| **"Menuduh korupsi" (sensitif hukum)** | minus besar | Posisi: **indikasi & pelaporan, BUKAN vonis**; tunjukkan metode & batasan; **kredit sumber**; **human-in-the-loop** untuk kirim |
| **False positive** (flag yang sebenarnya wajar) | Kredibilitas turun | Tunjukkan **kalkulasi + konteks** di tiap flag; level indikasi (bukan hitam-putih); user yang menilai |
| **PDP/keamanan** | — | Data pengadaan = publik (low PII); self-hosted; jangan simpan data personal di luar kebutuhan |
| **RAM 4GB** | Grafana+Hermes berebut | Drop Grafana jika perlu (dashboard = terminal+PDF); SQLite; tes beban hari 1–2 |
| **Klaim berlebihan** | Juri Eko mengurangi poin | Artikel memuat **trade-off & batasan** (kejujuran teknis = nilai plus) |

---

## 7. DATA & STATISTIK UNTUK ARTIKEL (verifikasi sumber saat menulis)
1. **BPKP:** modus manipulasi penganggaran & pengadaan = **Rp141 triliun**.
2. **BPK:** 15.689 masalah, semester I 2023 = **Rp18,19 triliun**.
3. **KPK (Des 2025):** pengaturan lelang **DJKA Medan 2021–2024** (pemenang dikondisikan, HPS bocor).
4. **KPK (2025):** OTT PBJ **Lampung Tengah** — fee **15–20%** + biaya politik.
5. **BPA:** Rp26 triliun aset rampasan (2024–2026).
6. **Konteks lokal:** pengadaan **Aceh Tengah/Aceh** (contoh nyata dari LPSE daerah — ambil 2–3 proyek nyata sebagai studi kasus).
7. **Kredit sumber data** di setiap kutipan (kepatuhan data terbuka + poin etika).

---

## 8. SUDUT CERITA (storytelling 15%)
**Naskah pembuka video (±30 dtk):**
> "Pemerintah membuka data pengadaannya. Triliunan rupiah tercatat di situ. Tapi tak ada yang membacanya untuk kita. MATA membacanya — 24 jam, tanpa lelah — sampai ada yang berubah. Ini bukan tentang menuduh. Ini tentang **membuat data yang sudah terbuka, akhirnya bekerja untuk rakyat.**"

**Struktur artikel (800+ kata):**
1. **Buka:** 2 paragraf skala (Rp141 T, Rp18,19 T, KPK Des 2025) + "datanya sudah dibuka — tapi tak dibaca."
2. **Masalah:** 4 pola kegagalan.
3. **Solusi:** arsitektur (diagram) + 5 skenario + **rumus & ambang** (dipajang — transparan).
4. **Mengapa AI agent (Hermes):** cron, memory, subagent, multi-kanal; self-hosted 24/7 di [AI Hosting](https://idwebhost.com/ai-hosting/) → [Cloud VPS](https://cloudbaik.com/). *(2 backlink wajib, natural)*
5. **Dampak terukur:** metrik demo.
6. **Kejujuran & etika:** trade-off, "indikasi bukan vonis", human-in-the-loop, batasan. *(paragraf yang Eko & Onno cari)*
7. **Open source & replikasi:** komponen terbuka, rumus diaudit, roadmap (D5, D7).
8. **Bisnis & keberlanjutan:** tool gratis warga + pilot B2G/NGO/media; open-core.
9. **Penutup:** "Semoga tidak pernah dipuji. Semoga cukup diawasi."

---

## 9. PETA SKOR PER JURI
| Juri | Yang mereka lihat di MATA |
|------|---------------------------|
| **Onno W. Purbo** | **Inti DNA-nya**: open data + akuntabilitas + open source + "internet untuk rakyat". MATA = RT/RW-Net-nya pengawasan publik. Kredit BMKG-style ke sumber data = sopan santun Onno. |
| **Ogi S. Pornawan** | Dampak nyata (uang rakyat terlindungi), pilot B2G/NGO/media, AI Hosting IDwebhost benar-benar infrastruktur 24/7 (dashboard, uptime). |
| **Eko Novianto** | Pipeline nyata (crawl→rule→dossier→lapor), **reliability jujur**, rule engine transparan (bisa diaudit), arsitektur bersih, artikel memuat trade-off. Bukan demo palsu. |

**Bobot:** Efektivitas 30% (5 skenario nyata) · Teknis 20% (arsitektur + mode jujur + rule transparan) · Relevansi 20% (data korupsi yang menganga) · Kreativitas 15% ("data jadi tindakan") · Storytelling 15% (cerita "uangmu" + lokus Aceh).

---

## 10. CHECKLIST HARI INI (Jumat, 11 Sep — sisa hari)
- [ ] 15 mnt — Cek VPS aktif (dashboard CloudBaik/IDwebhost). Jika belum: email `info@cloudbaik.com`.
- [ ] **45 mnt — KUNCI DATA (paling penting):** uji akses Panda LKPP / LPSE Kab. Aceh Tengah / LPSE Prov. Aceh / inaproc / e-kontrak dari VPS. Tandai sumber yang **legal & jalan**. Kalau gagal semua → mulai bangun **dataset sintetis-realistis**.
- [ ] 30 mnt — Install Hermes Agent + gateway Telegram + test chat bolak-balik + screenshot dashboard VPS.
- [ ] 20 mnt — Buat `db.sqlite` (skema pengumuman/kontrak) + isi 10 contoh data.
- [ ] 20 mnt — Tulis `collector.py` v0 (parse 1 sumber → console) + jalankan.
- [ ] 15 mnt — Catat 7 statistik artikel + daftar sumber (bagian 7) ke `sumber.md`.
- [ ] Sisa — Rehearse 5 skenario di kepala; pilih 2–3 proyek nyata Aceh Tengah sebagai **studi kasus** demo.

**Target akhir hari ini:** **sumber data terkunci** + Hermes hidup + data mengalir + brief terkunci. Kalau data terkunci, MATA on-track.
