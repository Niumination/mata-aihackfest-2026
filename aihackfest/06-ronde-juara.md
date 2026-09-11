# AI HackFest 2026 — RONDE JUARA (Ronde 5)
**Afrizal Munthe** · Batch 3 (11–15 Sep 2026) · Productivity & Personal AI · Hermes Agent

> **Perubahan strategi.** 21 ide sebelumnya = "alat yang berguna". Ronde ini = **produk yang bikin juri condong ke depan**.
> Kriteria juara yang kita kejar (juara scorecard, nilai 1–10):
> **J1** Masalah masif nasional · **J2** Momen "holy-crap" di demo · **J3** Kedalaman agentic (reasoning/memory/action = bintang) · **J4** Inti emosional · **J5** "Why now" (topikal & terbaru) · **J6** Bisnis jelas (ada yang bayar) · **J7** Muat di kategori Personal AI · **J8** Open source / public good (Onno) · **J9** Jujur & feasible 5 hari di 4GB (Eko).
> **Total 90.** Di bawah 80 = tidak masuk ronde ini.

---

## 🥇 KANDIDAT UTAMA — **Pancing**: "Tang Kapal" Keluarga dari Scam 🎣

### Masalah (masif + topikal + terverifikasi)
Penipuan digital adalah **krisis nasional #1 tahun 2025**:
- **1,2 juta laporan** penipuan digital hingga pertengahan 2025 (Komdigi).
- **Rp476 miliar** kerugian finansial hanya Nov 2024–Jan 2025; ~**Rp18 triliun** di 2024 (task scamming).
- Indonesia masuk **negara paling rentan penipuan** di dunia.
- Modus naik kelas: **deepfake suara/wajah AI** — scammers pakai AI, korban cuma punya HP.
- **Korban terberat: lansia** (dana pensiun//tabungan) & masyarakat non-digital.

**Satu kalimat masalah:** *"Setiap hari, 3.000+ keluarga Indonesia kehilangan uang mereka karena satu pesan atau satu panggilan — dan tidak ada 'penjaga' di HP orang tua mereka."*

### Solusi
**Pancing = personal AI yang menjadi "tang kapal" keluarga dari penipuan digital.** Agent tinggal di WhatsApp keluarga (Hermes), dan:
1. **Deteksi real-time (forward-to-protect):** Anggota keluarga (terutama lansia) meneruskan pesan/link/APK/panggilan mencurigakan ke agent → agent **menganalisis dalam <60 detik**: transkrip suara, reputasi link/domain, metadata APK, cross-check DB modus scam, **reasoning LLM** → **verdict + penjelasan bahasa manusia** + level kepercayaan + **draft blokir & lapor** ke kanal resmi (aduannomor.id/Polisi).
2. **Deteksi deepfake:** *"Suara 'Pak Bos' di rekaman ini menunjukkan ciri manipulasi AI (artefak pitch/latency). Jangan transfer — konfirmasi lewat jalur kedua."* → **narasi "lawan api dengan api"**: AI penjaga melawan AI scammer.
3. **Family Shield (intinya):** Kamu (anak) mendaftarkan HP orang tuamu. Setiap kali mereka hampir kena scam, **kamu yang dapat notifikasi** + bisa intervensi. *"Ibu hampir transfer 5 juta ke 'admin bank'. Agent sudah blokir. Ini buktinya."*
4. **Memory rumah tangga:** Agent belajar profil risiko keluargamu (orang tua rawan task scam, adik rawan investasi bodong) → proteksi adaptif.
5. **Laporan & edukasi:** ringkasan bulanan "nyaris kena berapa kali, modus apa" + konten anti-scam yang bisa dibagikan.

### 🎬 Momen "holy-crap" (naskah demo 60 detik)
> HP lansia masuk pesan: *"Kakak, aku terjebak di bandara, kirim 5 juta sekarang"* (suara mirip, pakai deepfake).
> Lansia meneruskan ke **Pancing** → 30 detik: agent memutar transkrip, menandai **artefak deepfake**, mencocokkan modus "emergency transfer", memverifikasi nomor bukan nomor keluarga → **VERDICT: PENIPUAN (kepercayaan 91%)** + penjelasan + **notifikasi ke anaknya** + draft lapor. Anaknya masuk, telepon, nyelametin uang 5 juta.
> **Juri baru saja melihat uang 5 juta diselamatkan dalam 30 detik.**

### Juara scorecard
| J | Aspek | Nilai | Catatan |
|---|-------|-------|---------|
| J1 | Masif nasional | **10** | 1,2 jt laporan; Rp18 T; krisis nasional |
| J2 | Holy-crap | **9** | Intersepsi real-time; deepfake = 10 |
| J3 | Agentic depth | **9** | Multimodal + reasoning + memory + action |
| J4 | Emosional | **9** | "Tabungan nyawa orang tuamu" |
| J5 | Why now | **10** | 2025 = puncak; Komdigi cari solusi AI |
| J6 | Bisnis | **9** | B2C freemium + family plan + B2B bank/telco |
| J7 | Muat Personal AI | **7** | Frame "penjaga dompet digital keluarga" (lihat baw.) |
| J8 | Open source/public good | **8** | DB modus terbuka; melindungi yang rentan |
| J9 | Jujur & feasible 5 hari | **8** | "Forward = protect" feasible; in-call live = jangankan |
| **Total** | | **88/90** | **Paling tinggi dari semua 24 ide** |

### Fit kategori (penting — mitigasi)
- Didaftarkan di **Productivity & Personal AI** → frame sebagai **personal AI "penjaga dompet digital & keselamatan keluarga"** (personal + family, punya memory, adaptif). Bukan "security tool korporat".
- Secara substansi juga menyentuh subkategori *Cyber Security & Anti Scam* (Digital Safety & Public Good) — **juri akan menghargai jangkauan**, tapi positioning utama tetap Personal AI.
- **Sesuai Aturan #7:** deteksi + **pelaporan lewat kanal resmi** (aduannomor.id, Bareskrim) — tidak "main hakim". Ini justru poin kepatuhan.

### Teknologi & integrasi OSS
- Hermes Agent (gateway WA, memory, skill, subagent untuk analisis paralel, cron untuk laporan bulanan).
- **ASR** (transkrip) + **multimodal LLM** (reasoning) + **deteksi anomali suara** (fitur deepfake: analisis spectral/keberaturan — heuristik transparan, bukan klaim "detektor pasti").
- **DB modus scam** (open, bisa di-fed dari data publik Komdigi/OJK) + **reputasi domain** (open dataset URLhaus/categorically).
- Integrasi OSS: **URLhaus** (abuse.ch), DB publik modus, **Grafana** (dashboard "tebak-nteban keluarga"), **WeasyPrint** (PDF bukti/laporan).
- Semua self-host di VPS 4GB (Hermes + Python + SQLite + Grafana ≈ aman).

### Risiko & mitigasi
- **False positive** (blok yang legitimate) → verdict = *"kemungkinan besar penipuan, verifikasi dulu"* (bukan vonis mutlak); tunjukkan alasan & bukti; user selalu bisa override.
- **Privasi** (agent baca pesan) → self-hosted, data minimal, only-analyze-what's-forwarded, consent, demo data sintetis.
- **Akurasi deepfake** → position "indikasi ciri manipulasi", bukan "pasti deepfake"; selalu sarankan konfirmasi jalur kedua.
- **Akses pesan/ToS** → model "forward-to-protect" (user aktif meneruskan) = tidak melanggar akses pihak ketiga.
- **5 hari** → core = forward→analisis→verdict→notifikasi→draft lapor. In-call live intercept = **di luar scope 5 hari** (sebutkan sebagai roadmap).

### Bisnis
B2C freemium (1 nomor gratis, family plan Rp29rb/bln); B2B: bank (proteksi nasabah lansia), telco, asuransi; pemerintah/NGO (literasi). TAM = seluruh keluarga Indonesia dengan lansia.

### Kenapa ini juara (bukan sekadar bagus)
- **Why now = 10/10** — satu-satunya ide yang jurnalis & juri baru saja baca di berita minggu ini.
- **Dua arah AI (AI lawan AI)** = narasi yang belum ada di kompetisi ini.
- **Emosi paling tajam** (melindungi orang tua) + **bisnis paling jelas** + **kepatuhan aturan** (deteksi+lapor resmi) + **feasible**.
- **Pukul 3 juri sekaligus:** Ogi (bisnis + dampak nyata), Eko (agent multimodal yang jujur), Onno (public good + melindungi yang rentan + DB terbuka).

---

## 🥈 KANDIDAT 2 — **Jembatan**: Penerjemah Real-Time 718 Bahasa + Penyelamat Bahasa Daerah 🌉

### Masalah (masif + budaya + equity)
- **718 bahasa daerah, 778 dialek** (Badan Bahasa) — dan **11 bahasa sudah punah**, puluhan lagi terancam.
- Dampak harian: pasien di puskesmas tak paham dokter, warga tak paham surat pemerintah, UMKM tak bisa jualan ke luar daerah, wisata kehilangan makna.
- Bahasa = identitas + akses. Ini **kesenjangan yang tak terlihat** di tiap interaksi.

### Solusi
**Jembatan = personal AI penerjemah real-time dua arah untuk bahasa Indonesia & bahasa daerah.**
1. **Konversi suara-ke-suara live:** bicara dalam **Gayo/Aceh** → dibalas dalam **Bahasa Indonesia** (dan sebaliknya), dengan transkrip.
2. **Mode kontekstual:** puskesmas (medis), kantor kelurahan (admin), pasar (transaksi) → kosakata & nada adaptif.
3. **Twist juara (Onno magnet):** Jembatan bukan cuma menerjemahkan — dia **merekam & melestarikan**. Percakapan (dengan izin) menjadi **korpus bahasa daerah yang hidup**, terbuka, komunitas-berbasis → **AI yang menyelamatkan bahasa dari kepunahan**.
4. **Memory personal:** inget istilah keluarga, nama, kebiasaan bicara → makin "paham" penggunanya.

### 🎬 Momen "holy-crap"
> Demo 2 arah: peserta bicara **Gayo** ke agent, agent balas **Bahasa Indonesia** real-time — lalu dibalik. Juri (yang tidak bisa Gayo) **baru saja berkomunikasi** dalam bahasa yang tidak mereka kenal.
> Skenario medis: dokter (ID) ↔ pasien (Gayo), agent terjemahkan 2 arah + **otomatis membuat rekam medis terstruktur**.

### Juara scorecard
| J | Nilai | Catatan |
|---|-------|---------|
| J1 Masif | 9 | 718 bahasa; equity nasional |
| J2 Holy-crap | 9 | Live 2 arah + rekam medis |
| J3 Agentic | 8 | Speech + RAG kamus + memory |
| J4 Emosional | 8 | Pelestarian identitas |
| J5 Why now | 7 | Kronis, bukan hot-news |
| J6 Bisnis | 7 | Faskes/pemerintah/wisata/NGO |
| J7 Personal AI | 8 | Komunikasi personal + public good |
| J8 Open source | **10** | Korpus terbuka = mimpi Onno |
| J9 Feasible | 7 | Kualitas bahasa low-resource = risiko |
| **Total** | **83/90** | |

### Risiko & mitigasi
- **Kualitas ASR/TTS bahasa low-resource** (Gayo data minim) → pilih bahasa yang modelnya lebih kuat untuk demo (Aceh punya data lebih); jujur "langkah pertama menuju 718"; kalibrasi + umpan komunitas.
- **Konteks medis/legal** → disclaimers "untuk bantu komunikasi, keputusan krusial diverifikasi manusia".
- **5 hari** → core = terjemahan suara 2 arah + 1 mode kontekstual; korpus = fitur bonus (bisa di-show sebagai "rekam" tanpa full-pipeline).

### Kenapa kuat
- **Paling unik & paling "Onno"** (pelestarian bahasa = public good + edukasi + open source).
- Momen demo sangat visual & personal. **Kurang "hot-news"** dibanding Pancing (why-now 7 vs 10) & bisnis lebih samar → jadi #2.

---

## 🥉 KANDIDAT 3 — **KlinikKampung**: Triage Kesehatan Bahasa Lokal untuk Wilayah Terpencil 🩺

### Masalah (masif + nyawa)
- Rasio dokter Indonesia ~**1:2.000–2.800** (bawah standar WHO 1:1.000), menumpuk di Jawa.
- **514 kabupaten/kota**, kepulauan; puskesmas sering tanpa dokter; penyakit kronis (DM/hipertensi) tak terkelola.
- Warga terpencil (dataran tinggi Gayo, pedalaman) = **jam-jam pertama gejala krusial tanpa akses**.

### Solusi
**KlinikKampung = personal AI triage & pendamping kesehatan, bicara bahasa lokal.**
1. **Intake suara:** lansia bicara gejala dalam **Aceh/Gayo** → agent tanyakan terstruktur (simptom, durasi, riwayat, obat).
2. **Triage + edukasi:** klasifikasi (red/yellow/green) bahasa manusia; **red flag → "segera ke puskesmas/rumah sakit sekarang"** (bukan diagnosis).
3. **Pendamping kronis:** pengingat minum obat (cron), jadwal kontrol, log tekanan gula/darah (input sederhana) → tren untuk keluarga & faskes.
4. **Notifikasi keluarga (sandwich generation):** anak di kota dapat ringkasan kondisi orang tua + alarm jika red flag.
5. **Rekam keluarga:** riwayat kesehatan keluarga di memory agent.

### 🎬 Momen "holy-crap"
> Lansia (aksen Aceh) bicara gejala → agent triage, deteksi red flag → **"Ini bisa darurat. Bawa Ibu ke Puskesmas sekarang, bawa KTP & kartu BPJS."** + **notifikasi ke anaknya** di kota + resep obat lama di-remind. Juri melihat **nyawa** dalam 60 detik.

### Juara scorecard
| J | Nilai | Catatan |
|---|-------|---------|
| J1 Masif | 9 | Kekurangan dokter; 514 kab |
| J2 Holy-crap | 8 | Triage lansia bahasa lokal |
| J3 Agentic | 8 | Reasoning medis + voice + memory |
| J4 Emosional | **10** | Nyawa + lansia |
| J5 Why now | 6 | Kronis, bukan hot-event |
| J6 Bisnis | 8 | Pemerintah/telemed/BPJS/CSR |
| J7 Personal AI | 7 | Health companion (bridge Healthcare) |
| J8 Open source | 9 | Health equity, public good |
| J9 Feasible | **6** | **Liability/akurasi medis = scrutiny Eko** |
| **Total** | **79/90** | |

### Risiko & mitigasi (ini kelemahan utamanya)
- **Liability/akurasi medis** → positioning tegas **triage & edukasi BUKAN diagnosis**; red flag selalu rujuk; tidak meresepkan; disclaimers; human-in-loop. **Ini yang bikin Eko bisa mengurangi poin** → jadi #3.
- **Why-now** lemah (kronis, bukan berita panas).
- **5 hari** → core = intake + triage + notifikasi; chronic companion = roadmap.

### Kenapa tetap masuk
- **Emosi tertinggi (10/10)** + public good kuat. Tapi **risiko medis + why-now** menahan di #3.

---

## 📊 PERBANDINGAN & REKOMENDASI JUARA

| Kandidat | Total | Kenapa di atas 21 ide sebelumnya |
|----------|-------|----------------------------------|
| **Pancing** | **88** | Why-now 10/10 (krisis 2025), holy-crap real-time, bisnis jelas, kepatuhan aturan, AI-lawan-AI |
| **Jembatan** | **83** | Paling unik + Onno-magnet (pelestarian 718 bahasa), demo visual kuat |
| **KlinikKampung** | **79** | Emosi tertinggi, tapi liability medis + why-now menahan |

### Rekomendasi
**Utama: Pancing** — satu-satunya yang memenuhi SEMUA syarat juara sekaligus: masalah paling topikal (juri baru baca di berita), demo yang "menyelamatkan uang dalam 30 detik", narasi AI-lawan-AI yang belum ada, bisnis jelas, patuh aturan, dan feasible 5 hari dengan frame Personal AI yang rapi.

**Jika kamu ingin lebih "aman" secara kategori (Personal AI murni, zero tension):** **Jembatan** — fit kategori lebih bersih, Onno-magnet, tapi why-now & bisnis lebih pelan.

**Jika kamu mau emosi maksimal & siap defending risiko medis:** **KlinikKampung**.

> Catatan jujur: Pancing punya **tezi kategori** (ia juga sangat cocok di Digital Safety & Anti Scam). Solusinya = positioning kuat "personal AI penjaga keluarga" + tunjukkan juga dimensi public good-nya. Kalau kamu tidak nyaman dengan tezi itu, **Jembatan** adalah juara paling bersih.

**Sebelum eksekusi, satu keputusan:** kamu mau **Pancing** (juara paling agresif) atau **Jembatan** (juara paling bersih/aman)? Atau mau saya gabungkan kekuatan keduanya?
