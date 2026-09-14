# AI HackFest 2026 — Strategi & 10 Ide Juara
**Peserta:** Afrizal Munthe · **Batch 3 (11–15 September 2026)** · **Kategori:** Productivity & Personal AI · **Platform:** Hermes Agent

> ⚠️ **Fakta paling penting: hari ini (Jumat, 11 Sep 2026) adalah HARI PERTAMA batch 3-mu.**
> Periode development batch = **5 hari (11–15 Sep)**. Setelah periode batch berakhir, **VM dinonaktifkan mulai 15 Sep 23:59 WIB** (aturan umum #5 + info panitia).
> Artinya: **video demo (yang wajib menampilkan VPS dashboard & terminal) WAJIB direkam paling telat 14–15 Sep.** Artikel masih bisa dipublikasikan sampai 30 Sep, tapi karyanya harus jadi dulu.

---

## 1. Peta Bobot Penilaian (target skor)

| # | Kriteria | Bobot | Artinya untuk kita |
|---|----------|-------|--------------------|
| 1 | **Efektivitas solusi** (agent benar-benar bekerja & solve problem) | **30%** | MVP harus jalan end-to-end, demo harus bisa diulang tanpa gagal |
| 2 | **Kualitas eksekusi teknis** (arsitektur, reliability, penggunaan fitur AI hosting) | **20%** | Arsitektur bersih, reliability nyata (retry/log/cron), dan VPS AI Hosting IDwebhost benar-benar jadi "panggung" |
| 3 | **Relevansi & kejelasan masalah** | **20%** | Masalah spesifik Indonesia + data pendukung + siapa yang untung jelas |
| 4 | **Kreativitas & orisinalitas** | **15%** | Ciri khas yang tidak dibayangkan peserta lain (disain di HARI 1, bukan belakangan) |
| 5 | **Storytelling video & artikel** | **15%** | Video 5–10 menit + artikel 800+ kata dengan 2 backlink wajib |

Tema resmi: *"AI Agent paling berharga adalah yang benar-benar dipakai dan menyelesaikan masalah — bukan yang paling rumit."* → **Kesederhanaan yang bekerja = senjata utama kita.**

---

## 2. Membaca 3 Dewan Juri (apa yang membuat mereka memberi skor tinggi)

### 🔴 Ogi S. Pornawan — CEO IDwebhost
- Latar: programmer (UGM, S2 IT), co-founder JogjaCamp & STORE.co.id, founder Kledo (media bisnis UKM), CEO web hosting tertua di Indonesia (22 thn).
- **Yang dia nilai:** nilai bisnis riil, masalah UKM/UMKM Indonesia, apakah produk ini "dibeli/dipakai orang", dan apakah peserta benar-benar memakai produk AI Hosting-nya (fitur deploy cepat, uptime 24/7, dsb.).
- **Cara memikatnya:** business model yang bisa diucapkan dalam 1 kalimat (harga, siapa yang bayar), dampak ke UKM, adegan di video yang menunjukkan VPS AI Hosting bekerja 24/7.

### 🟠 Eko Novianto, S.T. — President aiclub.id & Founder konova.id
- Latar: praktisi & builder komunitas AI Indonesia (aiclub.id), pendiri konova.id — orang yang setiap hari melihat karya AI agent.
- **Yang dia nilai:** agent-nya ASLI (bukan demo skenario palsu): memory, RAG, tool-calling, cron, reliability. Dia akan mencium "keajaiban yang dipaksakan" dari jauh.
- **Cara mempeknya:** tunjukkan arsitektur nyata (diagram + terminal), satu mekanisme teknis yang elegan (mis. learning loop Hermes, RAG untuk katalog), dan jangan takut menjelaskan trade-off di artikel.

### 🔵 Ir. Onno W. Purbo, M.Eng., PhD. — Rektor ITTS, "Bapak Internet & Open Source Indonesia"
- Latar: PhD Universitas Waterloo, 50+ buku, Wajanbolic, RT/RW-Net, Open BTS, penerima John Postel Service Award (Internet Society, 2020), komite WEF "AI for Humanity", pegiat copyleft.
- **Yang dia nilai:** open source & open standard, public good, teknologi murah yang memberdayakan komunitas/umat, ketulusan teknis (dia jago sekali melihat kepalsuan), dan nilai edukasi.
- **Cara memikatnya:** bangun di atas stack open source (Hermes = open source, plus komponen OSS lain), cerita pemberdayaan (UMKM/nelayan/guru/ibu rumah tangga), dan satu paragraf di artikel tentang "semua komponen ini open source, siapa pun bisa replikasi."

**Rumus skor maksimal:** masalah Indonesia yang nyata (Ogi + Onno) × pipeline teknis yang jujur & modern (Eko) × stack open source yang memberdayakan (Onno) × bisnis yang jelas (Ogi) × cerita yang manusiawi (ketiganya).

---

## 3. Ciri Kekuatan Hermes Agent (senjata yang harus kita manfaatkan)

Hermes Agent (Nous Research, open source) punya fitur yang **jarang dieksplorasi peserta lain** — ini celah orisinalitas kita:

1. **Learning loop / self-improving** — agent membuat *skill* dari pengalaman, memperbaiki skill saat dipakai, dan membangun model tentang penggunanya lintas sesi. → *Belum tentu peserta lain berani "menampilkan" fitur ini.*
2. **Multi-channel gateway** — Telegram, WhatsApp, Discord, Slack, Signal, Email dari satu proses. → Demo paling Indonesia = **WhatsApp/Telegram**.
3. **Cron scheduler bawaan** — automasi terjadwal dalam bahasa natural. → Agent **proaktif** (bukan cuma reaktif).
4. **Subagents** — pekerjaan paralel terisolasi.
5. **Model-agnostic** (OpenRouter, API apa pun, endpoint lokal) + **agentskills.io** (standar open) + ekosistem 647+ skill.
6. **Trajectory export / research-ready** → nilai edukasi (makanan Onno).

> **Keputusan strategis:** setiap ide di bawah saya desain supaya minimal 1 fitur khas Hermes jadi *panggung utama* demo.

---

## 4. 10 IDE + DAMPAK NYATA + RISIKO

> Format tiap ide: pitch → dampak & metrik → teknologi & integrasi OSS → risiko & syarat khusus → kelayakan 5 hari → nilai jual → kenapa unik.
> Catatan RAM: VPS hanya **4GB RAM** — maks. 2–3 service open source, pakai SQLite kalau bisa, matikan service yang tidak dipakai.

---

### IDE 1 — **KasPintar**: "Bilang Saja, Kas Tercatat" 🎙️ (REKOMENDASI #1)
**Pitch:** Agen pembukuan suara untuk UMKM via WhatsApp/Telegram. Warung/pedagang bicara: *"Dua indomie, satu aqua 600, dua belas ribu tunai"* → STT (Whisper) → LLM menerjemahkan jadi entri terstruktur (produk, qty, harga, metode bayar) → dicocokkan ke katalog produk (RAG vector) → otomatis masuk ledger **Firefly III** (OSS) → cron 20.00: "Laporan hari ini: omzet X, perkiraan laba Y" → PDF laporan laba-rugi mingguan.
- **Ciri khas:** *voice-first* (tangan pedagang penuh barang) + **katalog yang belajar sendiri** (skill Hermes: makin sering dipakai, makin paham bahasa warung — "bikin dua teh manis" → 2× teh manis @5rb).
- **Dampak nyata:** ±70 juta UMKM (Kemenkop UKM, verifikasilah angka terbaru di artikel); mayoritas usaha mikro tidak pernah pembukuan → tidak bisa hitung laba, tidak siap pajak/SPT, tidak bisa ajukan KUR. Metrik demo: 100+ transaksi tercatat dalam 1 minggu, 1 transaksi: ±2 menit manual → ±30 detik bicara.
- **Teknologi:** Hermes (gateway, cron, memory, skill) + **Whisper** (OSS, model base/small jalan di CPU 4GB) + pgvector/Qdrant + **Firefly III** (ledger OSS) + Telegram/WhatsApp.
- **Integrasi OSS:** Firefly III (akuntansi), opsional ERPNext (jika mau versi "berat"), Grafana (dashboard omzet untuk adegan video).
- **Risiko & syarat khusus:**
  - Kebisingan pasar → mode kalimat pendek + konfirmasi baca-balik ("Tercatat 2 indomie 1 aqua, benar?") — 1 tap konfirmasi.
  - Kesalahan angka → semua entri bisa "batalkan" via chat; human-in-the-loop untuk koreksi.
  - **UU PDP:** audio = data pribadi → hapus file audio setelah transkripsi, simpan hanya teks; self-hosted di VPS sendiri.
  - Cold start katalog → onboarding 10 produk pertama (bagus untuk demo: tunjukkan agent "belajar" produk baru di live demo).
- **Kelayakan 5 hari:** TINGGI. Semua komponen standar; demo-nya paling meyakinkan (bicara di HP → dashboard berubah).
- **Nilai jual:** SaaS Rp19–29rb/bln per UMKM; nilai jual tersembunyi yang GEMBIRAKAN: data keuangan rapi = **siap skor KUR perbankan/fintech** (B2B2C).
- **Kenapa unik:** hampir semua peserta membuat "chatbot asistens"; yang voice-first + ledger riil + angle KUR — sangat jarang.

---

### IDE 2 — **UangPulang**: Agen tagih utang yang tidak merusak hubungan 🤝 (REKOMENDASI #3)
**Pitch:** Agen pribadi untuk orang yang pernah pinjam-meminjam (keluarga, rekan usaha, kontraktor). Daftar pinjaman: *"Budi, 5 juta, janji bayar 25 bulan depan"* → agen mengirim pengingat lewat WhatsApp **dengan etika Indonesia** (tidak memojokkan, memberi jalan keluar, hanya di jam wajar), mencatat janji bayar baru, eskalasi sopan maks 3×/minggu, lalu merapikan **bukti chat + PDF rekap** sebagai arsip sengketa.
- **Ciri khas:** *etiquette engine* — tahu "seni" menagih di Indonesia. Dan ini showcase sempurna fitur **"user modeling lintas sesi"** milik Hermes: agen membangun profil relasi per-debitur (dekat/sahabat/bisnis, nada bicara yang aman).
- **Dampak nyata:** pinjam-meminjam informal adalah budaya & praktik bisnis harian (data informal lending bisa dikutip dari BPS/Kajian; verifikasi di artikel); konflik rumah tangga & bisnis karena utang tidak ditagih. Metrik: 10 tagihan aktif di demo, 100% pengirim terjadwal, 0 pengingat di luar jam wajar, rekap sengketa PDF 1-klik.
- **Teknologi:** Hermes (cron, memory, user modeling) + LLM (tone) + PDF (weasyprint/reportlab) + vektor untuk riwayat.
- **Integrasi OSS:** bisa dikawinkan Firefly III (ledger piutang) → narasi "ekosistem" (bagus untuk Ogi).
- **Risiko & syarat khusus:**
  - **UU ITE:** dilarang keras nada ancaman, mempermalukan, spam → aturan keras di sistem: max 3×/minggu, jam 08.00–20.00, tanpa group chat, tanpa kata ancaman; **fase 1: semua pesan butuh approval user** (human-in-the-loop) — ini justru nilai plus di mata juri (ethical by design).
  - Data utang = sensitif → enkripsi at-rest, hanya di VPS sendiri.
- **Kelayakan 5 hari:** SANGAT TINGGI (tanpa OCR/STT; intinya LLM + cron + memory).
- **Nilai jual:** freemium (3 tagihan gratis), Rp20rb/bln; pasar: kontraktor kecil, toko kredit, keluarga besar yang "berbisnis".
- **Kenapa unik:** emosional & relatable (juri pasti tersenyum melihat demo "pengingat sopan"); fitur memory Hermes yang jarang ditunjukkan orang.

---

### IDE 3 — **BiroSurat**: Kantor surat resmi pribadi dengan gaya tulisanmu ✉️ (risiko bangun TERENDAH)
**Pitch:** Agen pembuat surat resmi Indonesia (izin, pengantar, mutasi, SK, undangan, notulen, laporan, permohonan) dengan format yang benar (kop, nomor, tanggal, perihal, penutup) sesuai konteks (sekolah/perusahaan/kecamatan/organisasi). Twist-nya: (a) **style memory** — RAG atas surat-surat lamamu → "tulis seperti gaya suratku", (b) **pengingat proses** — cron: *"SK yang kamu ajukan 5 hari lalu belum keluar, mau saya draft follow-up?"* — agen tidak cuma nulis, tapi **mengejar prosesnya**. Output .docx rapi (python-docx/LibreOffice).
- **Ciri khas:** "biro" — personal secretariat. Twist pengejaran proses (bukan sekadar generator) adalah bagian yang tidak dipikirkan peserta lain.
- **Dampak nyata:** semua orang Indonesia pernah tersangkut administrasi (SK, izin, surat pindah, proposal OSIS, laporan RT/RW). Metrik: 1 jam bikin surat → ±1 menit; 10+ surat dihasilkan di demo dengan 0 revisi format.
- **Teknologi:** Hermes (cron, memory) + LLM + python-docx + RAG (vector atas arsip surat) + template engine.
- **Integrasi OSS:** **LibreOffice** (render docx), **BookStack/Wiki.js** (gudang template), **Paperless-ngx** (arsip final → bisa dinarasikan "berkembang jadi Arsipin").
- **Risiko & syarat khusus:**
  - Format tiap instansi berbeda → user wajib preview sebelum dipakai; sertakan disclaimer "cek dulu dengan instansi".
  - Surat memuat data pribadi (alamat, NIK, dsb.) → **UU PDP**: self-hosted; di demo **jangan** tunjukkan data pribadi asli, gunakan data sintetis (ini juga sinyal "best practice" ke juri).
- **Kelayakan 5 hari:** SANGAT TINGGI (docx generation mudah; demo cepat jadi).
- **Nilai jual:** SaaS Rp15rb/bln; B2B: sekretariat perusahaan, sekolah, OSIS/kepanitiaan; pasar template premium.
- **Kenapa unik:** niche budaya yang dilewatkan hampir semua peserta; sentuhan budaya Indonesia = poin cerita; Onno (generasi surat-menyurat) akan menghargai.

---

### IDE 4 — **RadarHarga**: Agen yang jagain pasar buat orang biasa 📡
**Pitch:** Agen pemantau **harga komoditas pangan/agri dari data publik resmi** (BPS, Kemendag/SP2KP, portal harga daerah — semua data terbuka, TIDAK ada scraping yang melanggar ToS). Cron harian: tarik data → deteksi anomali/tren (7/30 hari) → alert ke Telegram/WhatsApp: *"Cabai di X +15% vs minggu lalu — panenmu minggu depan, pertimbangkan simpan dulu"* → rekomendasi berbasis **aturan transparan** ("jual/simpan" + alasan), plus dashboard **Grafana** yang tumbuh sendiri di VPS.
- **Ciri khas:** **agen proaktif** (cron + alert) — bukan chatbot tanya-jawab; rekomendasi aturan-basis yang bisa diaudit (bukan black-box) — jati diri Onno.
- **Dampak nyata:** fluktuasi harga menggerus margin petani/nelayan/pedagang kecil. **Aksentu lokal Aceh (storytelling emas):** gamit, kakao, udang, kopi — kalau ada keluarga/lingkaranmu yang berhubungan dengan salah satu komoditas ini, cerita personalnya langsung hidup. Metrik: N alert selama minggu demo, waktu tanggap pedagang dari "harga berubah" → "tahu" (manual cek 30menit/hari → 0).
- **Teknologi:** Hermes (cron, subagent paralel untuk multi-sumber) + Python (pandas) + **Grafana** (OSS) + Telegram.
- **Integrasi OSS:** Grafana, open-data BPS/Kemendag.
- **Risiko & syarat khusus:**
  - Kualitas/kesegaran data publik → multi-sumber + label "data per" di setiap alert; siap fallback jika sumber berubah (risiko waktu di 5 hari — **uji sumber data HARI 1** sebelum komitmen ide ini).
  - Rekomendasi salah → positioning "alat bantu, bukan jaminan"; aturan transparan + user bisa set threshold.
  - Data pribadi minimal (risiko PDP rendah).
- **Kelayakan 5 hari:** SEDANG (risiko utamanya hunting & uji sumber data).
- **Nilai jual:** alert premium Rp10rb/bln untuk pedagang; B2B: gapoktan, koperasi, distributor, pemda (monitoring harga daerah).
- **Kenapa unik:** agen proaktif + data publik + cerita lokal = kombinasi yang hampir pasti tidak dibuat peserta lain; spirit "teknologi murah untuk komunitas" = DNA Onno.

---

### IDE 5 — **WaliKelas**: Digital admin guru yang ngumpulin PR via foto 📚
**Pitch:** Agen untuk guru: (a) generate PR/quiz diferensiasi dari materi + level siswa (RAG atas bahan ajar), (b) siswa/fotokopinya kirim **foto jawaban via WhatsApp** → OCR + LLM **menilai & memberi feedback lembut**, (c) cron: **laporan progres per siswa ke orang tua** mingguan yang sopan & personal, (d) menjawab pertanyaan siswa di luar jam dengan **guardrail** (hanya dari RAG materi; selain itu: "konfirmasi ke Pak/Bu Guru ya").
- **Ciri khas:** "menilai dari foto" (pain riil: guru mengoreksi sampai malam) + laporan orang tua tanpa pagelaran; guardrail = AI yang jujur.
- **Dampak nyata:** 1 guru = 30–40 siswa × beberapa mapel; koreksi 40 lembar hitungan ±2 jam → ±10 menit review. Metrik demo: 40 PR dinilai, akurasi % vs koreksi ulang guru, 40 laporan orang tua terkirim.
- **Teknologi:** Hermes (WhatsApp, cron) + **PaddleOCR/Tesseract** (OSS, support Indonesia) + LLM penilaian + RAG + generator laporan (docx/PDF).
- **Integrasi OSS:** **Moodle** (LMS — nilai bisa diposting ke gradebook), PaddleOCR.
- **Risiko & syarat khusus:**
  - **Data siswa (anak di bawah umur) = PDP paling sensitif** → demo wajib pakai **siswa sintetis** + narasi "consent orang tua" di artikel; tidak boleh ada data asli.
  - Akurasi nilai → AI memberi *draft nilai + alasan*, guru approve 1-klik (human-in-the-loop = nilai plus).
  - OCR tulisan tangan → mulai dari jawaban terstruktur/typed + foto jelas; jujur di artikel tentang batasnya.
  - Etika: tidak boleh mengontak siswa di luar jam wajar; selalu label "AI membantu guru".
- **Kelayakan 5 hari:** SEDANG-TINGGI.
- **Nilai jual:** B2B2C sekolah swasta/pesantren (Rp25rb/siswa/semester); SaaS tool guru.
- **Kenapa unik:** "pendidikan" umum, tapi twist pipeline foto-OCR-nilai + laporan orang tua jarang; demo-nya paling emosional → storytelling 15% mudah dimenangkan.
- **Catatan kategori:** aman masuk "Productivity & Personal AI" dengan framing "produktivitas pribadi guru" (subkategori Education juga tersedia di daftar).

---

### IDE 6 — **Rekapin**: Agen konsinyasi untuk reseller social commerce 📦
**Pitch:** Reseller (jualan IG/TikTok/WA) memegang stok **konsinyasi** dari banyak supplier. Setiap jualan, tinggal kirim **foto struk/chat order** ke WhatsApp agen → Vision LLM ekstraksi (produk, qty, supplier) → stok & piutang per supplier terawat → **cron Jumat: rekap settlement** otomatis dikirim ke supplier: *"Supplier A: terjual 12, biaya 1,8jt, margin kamu 600rb"* → konfirmasi 1-tap.
- **Ciri khas:** "settlement dari foto" + **menghilangkan konflik hitungan** reseller–supplier (pain yang sangat spesifik & nyata).
- **Dampak nyata:** social commerce adalah mesin UMKM Indonesia (Kemenkop UKM — verifikasi angka di artikel); rekap manual = 15–30 menit/malam + potensi salah hitung. Metrik demo: 100+ jualan dari foto, settlement 15menit → 15detik, akurasi ekstraksi %.
- **Teknologi:** Hermes (WhatsApp, cron) + **Vision LLM** (cek model default apakah support vision; kalau tidak, pakai API vision murah — biaya di tanggung peserta) + RAG (katalog & perjanjian supplier) + PDF rekap.
- **Integrasi OSS:** **ERPNext** (punya modul konsinyasi sungguhan!) atau Postgres+Grafana versi ringkas.
- **Risiko & syarat khusus:**
  - Akurasi vision pada foto berantakan → step konfirmasi "Ini benar? (1-2)" sebelum tercatat.
  - Aturan supplier beragam → onboarding: daftarkan supplier + persentase bagi hasil (ini juga konten demo yang bagus).
  - Biaya API vision → hitung budget (±berapa juta cukup untuk 5 hari).
- **Kelayakan 5 hari:** SEDANG-TINGGI.
- **Nilai jual:** SaaS Rp30rb/bln; sisi B2B: **brand supplier konsinyasi** (mereka butuh rekap yang jujur juga!) — dua sisi yang mau bayar.
- **Kenapa unik:** bentuk bisnis "social commerce + konsinyasi" itu sangat Indonesia — peserta yang tidak merasakannya tidak akan memikirkan ide ini.

---

### IDE 7 — **AjaBisa**: Butler pribadi yang tumbuh & bisa "buktiin" dia belajar 🧠
**Pitch:** Agen butler hidup: pengingat tagihan (PLN, BPJS, sewa, langganan, **SPT tahunan**, pajak kendaraan) dengan cron, brief pagi/malam, perencanaan perjalanan (data resmi KAI/berangkat), dan showcase-nya: **"Skill Report mingguan"** — tiap Jumat agen mengirim: *"Minggu ini saya belajar 3 kebiasaanmu: (1) kamu selalu rencana belanja Sabtu pagi → saya siapkan list otomatis, (2) ..."* — **visualisasi learning loop Hermes** yang tidak bisa ditiru framework lain.
- **Ciri khas:** "agen yang **bisa menunjukkan** dia bertumbuh" — bukti konkret self-improvement, bukan klaim.
- **Dampak nyata:** beban mental personal admin (deadline, reminder) ±2 jam/minggu → 0. Metrik: 100% deadline tertangani, 3+ skill terbentuk & terlihat di minggu demo.
- **Teknologi:** Hermes 100% (cron, memory, skill, user modeling) + vektor + subagent.
- **Integrasi OSS:** Taskwarrior/Todo.txt (task), Grafana (dashboard penggunaan).
- **Risiko & syarat khusus:**
  - **Ini ide yang PALING umum di hackathon** ("personal assistant") — hanya "skill report + bukti pertumbuhan" yang membuatnya berbeda; eksekusi cerita wajib kuat, kalau tidak tenggelam.
  - Data sangat sensitif (tagihan, jadwal) → self-hosted, narasi kedaulatan data.
  - Notifikasi kelelahan → desain: 2 brief + hanya pengecualian penting.
  - Nilai jual ke konsumen Indonesia masih lemah (komersialisasi paling lemah dari 10 ide) → Ogi mungkin mengganjal di sini.
- **Kelayakan 5 hari:** TINGGI.
- **Nilai jual:** langganan personal premium (pasar konsumen sulit); lebih kuat sebagai **showcase teknis**.
- **Kenapa unik:** kalau "skill report" dieksekusi rapi, ini ide yang membuat Eko (praktisi agent) mengangguk: satu-satunya peserta yang benar-benar memakai fitur khas Hermes.

---

### IDE 8 — **Klienin**: Ubah chat klien WhatsApp jadi pipeline studio 🔧 (REKOMENDASI #2)
**Pitch:** Untuk freelancer/studio kecil: pesan klien datang berantakan (*"bang tolong tombolnya ya, urgent"*) → agen **mengkategorikan** (request baru/bug/tanya/urgent) → draft pertanyaan klarifikasi (approval user) → **buat task di Plane** (OSS project management) → **estimasikan effort & deadline** dari memori proyek-proyek sebelumnya ("perbaikan tombol kemarin cuma 1 jam, ini kira-kira 2 jam") → draft balasan profesional dengan gaya user → cron pantau deadline → **invoice otomatis di InvoiceNinja** (OSS) → **follow-up tagihan yang telat** dengan nada sopan (spirit UangPulang).
- **Ciri khas:** "WhatsApp = pintu depan studio" + estimasi berbasis pengalaman + dunning sopan; loop-nya penuh: chat → pipeline → invoice → tagihan.
- **Dampak nyata:** pekerja lepas Indonesia ±16 juta (BPS, verifikasi angka terbaru); admin proyek memakan 1–3 jam/hari. Metrik demo: 10 pesan klien → 100% terkategorikan benar, 3 invoice terbit, 0 deadline lolos.
- **Teknologi:** Hermes (WhatsApp, cron, memory) + LLM klasifikasi + **REST API Plane & InvoiceNinja** (keduanya self-host di VPS yang sama = reliability terkontrol) + PDF.
- **Integrasi OSS:** **Plane** (OSS PM modern), **InvoiceNinja** (OSS invoicing), opsional **n8n** sebagai glue → **bonus poin "penggunaan fitur AI hosting"**: n8n adalah salah satu produk AI Hosting IDwebhost!
- **Risiko & syarat khusus:**
  - Miss-kategorisasi hal urgent klien → **semua pesan keluar = draft + approval user** (aturan emas).
  - Dua OSS tambahan membebani RAM 4GB → pakai versi ringan, SQLite di mana bisa; tes beban HARI 1–2.
  - Akurasi estimasi → positioning "rekomendasi", user tetap atur.
- **Kelayakan 5 hari:** SEDANG-TINGGI (setup 2 OSS + agent;Plane & InvoiceNinja punya install yang documented).
- **Nilai jual:** SaaS Rp50rb/bln — **willingness-to-pay paling jelas** dari 10 ide (menghemat jam yang bisa difakturkan).
- **Kenapa unik:** "agent sebagai ops studio" jarang; demo-nya paling end-to-end (memukul bobot 30% langsung); arsitektur multi-integrasi = makanan Eko; semua self-hosted = makanan Onno; n8n = makanan Ogi.

---

### IDE 9 — **DapurSiaga**: Agen PO (pre-order) & restock dapur rumah 🍱
**Pitch:** Bisnis kuliner rumahan yang jualan **sistem PO** (kue/meal box/nasi kotak) via WA/IG: agen membuka PO per cron (*"PO buka Senin 09.00, tutup Rabu 17.00"*) → terima order + catat → **rekonsiliasi pembayaran** (owner teruskan screenshot transfer → Vision LLM cocokkan nominal → status "lunas") → daftar final per item → **hitung bahan baku dari BOM/ resep** (*"40 nasi kotak → 8kg beras, 4kg ayam, ..."*) → laporan laba per batch di hari kirim.
- **Ciri khas:** *BOM-driven* — agen yang tahu resep, jadi tahu belanjaan. Ini twist yang tidak dimiliki aplikasi kasir mana pun.
- **Dampak nyata:** pelaku UMKM rumahan (terutama ibu rumah tangga) = mesin ekonomi besar pasca-pandemi; metrik demo: 1 batch PO 50 item: 2 jam kerja manual → 10 menit; akurasi list belanja 100%; laba per batch terlihat jelas (sebelumnya "perkiraan").
- **Teknologi:** Hermes (WhatsApp, cron, memory) + Vision LLM (screenshot transfer) + SQL (BOM & hitung) + laporan.
- **Integrasi OSS:** **ERPNext** (modul BOM/manufaktur sungguhan) atau Postgres+Grafana ringan.
- **Risiko & syarat khusus:**
  - Rekonsiliasi pembayaran → Vision + step konfirmasi "OK, dicatat lunas?" (tidak pernah auto-banking; tidak pernah menyimpan data rekening).
  - Resep bervariasi → BOM editable via chat.
  - Biaya API vision → hitung budget.
- **Kelayakan 5 hari:** SEDANG-TINGGI.
- **Nilai jual:** SaaS Rp25rb/bln; komunitas ibu-ibu bisnis = kanal distribusi organik yang kuat & sticky (komunitas = bahasa Onno).
- **Kenapa unik:** budaya "PO" itu spesifik Indonesia; demo siklus lengkap (order→bayar→produksi→kirim→laba) sangat memuaskan; cerita ibu-ibu = storytelling yang hangat.

---

### IDE 10 — **Arsipin**: Otak untuk dokumen hidupmu 🗄️
**Pitch:** User meneruskan foto/PDF (struk, kontrak, rapor, STNK, sertifikat, tagihan) via WhatsApp/Email → **OCR + ekstraksi field kunci** (tanggal, nominal, pihak, jatuh tempo) → disimpan ke **Paperless-ngx** (OSS document management) + vector DB → bisa ditanya: *"Pajak mobilku jatuh tempo kapan?"*, *"Tampilkan tagihan listrik 2025"* → **cron: pengingat H-30 jatuh tempo** (*"STNK H-30, mau saya draft surat perpanjangan?"*).
- **Ciri khas:** "radar jatuh tempo" — dokumen yang **menghubungi balik** pemiliknya, bukan cuma bisa dicari.
- **Dampak nyata:** orang Indonesia masih menumpuk dokumen fisik; kehilangan dokumen = masalah riil (urusan bank, sekolah, pajak). Metrik demo: 200 dokumen terindeks, waktu jawaban rata-rata ±3 dtk, 5+ pengingat jatuh tempo terpicu.
- **Teknologi:** Hermes (gateway, cron, memory) + **PaddleOCR/Tesseract** + LLM ekstraksi + **Paperless-ngx** + pgvector (RAG).
- **Integrasi OSS:** Paperless-ngx (sangat cocok & aktif), LibreOffice.
- **Risiko & syarat khusus:**
  - **PDP terberat dari 10 ide** (KTP, bank, medis) → narasi wajib: *"self-hosted di VPS milikmu; data tidak pernah keluar"* — ini justru **pitch sempurna produk AI Hosting** (data privat → VPS privat). Di demo **pakai dokumen sintetis 100%** — jangan pakai KTP asli.
  - OCR foto miring/kotor → orientasi + threshold + konfirmasi.
- **Kelayakan 5 hari:** SEDANG (Paperless-ngx setup cepat; tuning prompt ekstraksi butuh waktu).
- **Nilai jual:** Rp30rb/bln personal, Rp150rb/UMK kecil; pitch "kedaulatan data" sangat kuat di era UU PDP.
- **Kenapa unik:** document management ada (Paperless), tapi twist-nya agen yang **menjaga & mengingatkan & mendraf surat** — "dokumen yang hidup".

---

## 5. Ranking Rekomendasi (dipetakan ke 3 juri & 5 bobot)

| Rank | Ide | Efektif 30% | Teknis 20% | Relevan 20% | Kreatif 15% | Cerita 15% | Total rasa |
|------|-----|----|----|----|----|----|----|
| 🥇 | **KasPintar** (1) | 9.5 | 8.5 | 9.5 | 8.5 | 9 | **Juara umum** — memukul semua juri |
| 🥈 | **Klienin** (8) | 9 | 9.5 | 8.5 | 8 | 8.5 | **Paling kuat teknis & bisnis** |
| 🥉 | **UangPulang** (2) | 8.5 | 8 | 8.5 | 9.5 | 9 | **Paling unik & tercepat dibangun**; showcase memory Hermes |
| 4 | **BiroSurat** (3) | 8.5 | 8 | 8.5 | 8.5 | 8.5 | **Risiko bangun terendah**; budaya lokal kuat |
| 5 | **Arsipin** (10) | 8.5 | 8.5 | 8.5 | 8 | 8 | Pitch "kedaulatan data" terbaik |
| 6 | **WaliKelas** (5) | 8 | 8 | 9 | 8 | 9 | Emosional, tapi risiko PDP anak |
| 7 | **DapurSiaga** (9) | 8.5 | 8 | 8.5 | 8 | 8.5 | Sangat lokal, butuh budget vision |
| 8 | **Rekapin** (6) | 8 | 8.5 | 8.5 | 8.5 | 8 | Unik bisnis, butuh budget vision |
| 9 | **RadarHarga** (4) | 7.5 | 8 | 9 | 9 | 9 | Story lokal kuat; risiko sumber data |
| 10 | **AjaBisa** (7) | 8 | 9 | 7 | 7 | 7.5 | Showcase teknis, tapi ide paling umum & komersial lemah |

**Saran taktis (opsional tapi kuat):** pilih 1 ide utama, lalu sebutkan 1 ide lain sebagai "jalur pengembangan berikutnya" di akhir artikel — menunjukkan visi ekosistem (Ogi & Onno suka ekosistem; contoh: KasPintar → Arsipin → Klienin = "satu agen, semua urusan UMKM").

---

## 6. Urutan Pekerjaan Selama Kompetisi (sesuai bobot penilaian)

### Prinsip: kerjakan dari bobot terbesar, dan kunci kreativitas di awal.

**Fase A — BOBOT 30%: Efektivitas (HARI 1–3) → prioritas #1**
1. [Hari 1] Kunci IDE + tulis **1-halaman brief**: masalah (1 paragraf), target user, metrik dampak, daftar 5 skenario demo, dan "ciri khas" (1 kalimat).
2. [Hari 1] Pastikan VPS aktif (cek email/WA panitia; kalau belum: email **info@cloudbaik.com** — ini jalur resmi dukungan teknis).
3. [Hari 1–2] Setup Hermes Agent di VPS + gateway (Telegram/WhatsApp) + 1 service OSS inti.
4. [Hari 2–3] Bangun pipeline inti (alur utama end-to-end) dengan data uji 30–50 item.
5. [Hari 3] **Ceklis "benar-benar bekerja":** jalankan 5 skenario demo beruntun tanpa error; tambahkan retry/log; human-in-the-loop untuk hal sensitif.
   *Ini fase yang menentukan 30% skor. Jangan lanjut ke dekorasi sebelum ini solid.*

**Fase B — BOBOT 20%: Eksekusi Teknis (HARI 2–4) → prioritas #2**
1. Arsitektur bersih: Hermes = orkestrator; service OSS di container terpisah; diagram arsitektur sederhana (untuk artikel & video).
2. Reliability: log terpusat, auto-restart (systemd/docker restart), cron yang benar-benar jalan, penanganan gagal (jaringan, API limit).
3. **Panggung AI Hosting:** pastikan yang terlihat di VPS: dashboard CloudBaik/IDwebhost, terminal aktif, cron berjalan 24/7, resource (4C/4GB/20GB) terpakai sehat → **ini wajib muncul di video**.
4. [Opsional tapi bernilai] Sisipkan **n8n** (produk AI Hosting IDwebhost) sebagai glue → poin "penggunaan fitur AI hosting" makin tebal.

**Fase C — BOBOT 20%: Relevansi Masalah (HARI 1 + HARI 4–5) → prioritas #3**
1. [Hari 1] Data pendukung: 2–3 statistik (BPS/Kemenkop UKM/BI) untuk masalah yang diangkat — catat sumbernya untuk artikel.
2. [Hari 4–5] Tulis bagian "masalah & dampak" artikel dari data + testimoni/skenario nyata (jika bisa: satu mitra warung/guru/ibu rumah tangga = kredibilitas melonjak).
3. Definisi "siapa yang untung & apa yang berubah" harus bisa diucapkan dalam 1 kalimat.

**Fase D — BOBOT 15%: Storytelling (HARI 3–5) → prioritas #4**
1. [Hari 3] **Rekam video v1** (5–10 menit, 16:9, 1080p):
   - pembuka: masalah manusiawi (15 dtk) → demo end-to-end dari HP (WhatsApp/Telegram) → adegan **dashboard & terminal VPS** (wajib) → arsitektur singkat → metrik dampak → penutup bisnis model.
   - sebut **"AI Hosting IDwebhost"** minimal 1× (verbal/lower-third) + **watermark logo IDwebhost** di corner.
   - musik: royalty-free atau tanpa musik (aturan: dilarang musik berhak cipta).
   - upload YouTube/TikTok/IG **publik atau unlisted** (bukan private).
2. [Hari 4–5] **Artikel 800+ kata** (original, belum pernah dipublikasikan), platform publik terindeks (blog pribadi/LinkedIn Articles), WAJIB 2 backlink:
   - anchor **"AI Hosting"** → https://idwebhost.com/ai-hosting/
   - anchor **"Cloud VPS"** → https://cloudbaik.com/
   - Struktur yang disarankan: Masalah (data) → Solusi & demo → Arsitektur (sederhana, jujur trade-off) → Dampak terukur → Open source & replikasi (poin Onno) → Model bisnis (poin Ogi) → Pengembangan berikutnya.
3. [Hari 5] Re-take video jika perlu (buffer 1 hari), publikasi artikel, isi **form submit** (link video + link artikel).

**Fase E — BOBOT 15%: Kreativitas/Orisinalitas (HARI 1, terus dijaga) → prioritas #5**
1. [Hari 1] Tentukan "satu hal yang tidak dimiliki peserta lain" (1 kalimat) — contoh: KasPintar = "buku kas suara yang belajar bahasa warung"; Klienin = "WhatsApp sebagai pintu depan studio".
2. Jangan ganti ide di tengah (hari 2–4) — orisinalitas yang setengah jadi kalah dari eksekusi utuh.
3. Biarkan ciri khas itu tampil di: judul, demo, dan penutup artikel.

### Sprint 5 Hari — Batch 3 (jadwal konkretnya)
| Hari | Tanggal | Fokus (bobot) | Deliverable |
|------|---------|--------------|-------------|
| 1 | **Jumat, 11 Sep** (hari ini) | Ide + relevansi + teknis awal | VPS aktif, brief 1-halaman, data statistik, Hermes jalan, sumber data/API diuji |
| 2 | Sabtu, 12 Sep | Efektivitas | Pipeline inti jalan dengan data uji, service OSS terpasang |
| 3 | Minggu, 13 Sep | Efektivitas + teknis + cerita | End-to-end solid (5 skenario OK), log/retry, **video v1 terekam** |
| 4 | Senin, 14 Sep | Cerita + relevan | Video final (atau re-take), artikel draft selesai, diagram arsitektur |
| 5 | Selasa, 15 Sep | Submit + buffer | Video ter-upload, artikel terpublikasi + 2 backlink, form submit terisi, **selesai SEBELUM VM dimatikan 23:59 WIB** |

---

## 7. Checklist Kepatuhan (jangan sampai diskualifikasi)

**Umum**
- [ ] Patuhi UU ITE & UU PDP (data pribadi: minimalkan, self-hosted, hapus audio, demo pakai data sintetis).
- [ ] Tidak ada scraping yang melanggar ToS (pakai data publik resmi/API resmi — terutama untuk RadarHarga).
- [ ] Tidak ada konten menyerang individu; tagihan/ingatkan hanya lewat kanal resmi & sopan.
- [ ] AI model/API di luar default = tanggung jawab biaya sendiri → **hitung budget API HARI 1**.

**Video (5–10 menit)**
- [ ] 16:9, ≥1080p, landscape.
- [ ] End-to-end + minimal 1 adegan VPS AI Hosting (dashboard & terminal).
- [ ] Sebut "AI Hosting" + "IDwebhost" ≥1× (verbal/lower-third).
- [ ] Watermark logo IDwebhost di corner.
- [ ] Publik/unlisted di YouTube/TikTok/IG Reels.
- [ ] Tanpa musik/footage berhak cipta.

**Artikel (≥800 kata)**
- [ ] Original, belum pernah dipublikasikan.
- [ ] Platform publik terindeks (bukan private/paywall).
- [ ] Backlink 1: anchor "AI Hosting" → idwebhost.com/ai-hosting.
- [ ] Backlink 2: anchor "Cloud VPS" → cloudbaik.com.
- [ ] Hak cipta milikmu; panitia dapat izin non-eksklusif untuk repost.

**Timeline**
- [ ] Technical meeting 1 Sep 2026 (selesai) — pastikan sudah join grup WA panitia.
- [ ] Development batch 3: 11–15 Sep 2026 (VM mati 15 Sep 23:59 WIB!).
- [ ] Submit (link video + artikel): **paling lambat 30 Sep 2026**.
- [ ] Penilaian 1–31 Okt; pengumuman **6 Nov 2026** (webinar).

---

## 8. Langkah Berikutnya (sekarang)
1. Pilih 1 ide utama dari 10 (saran: **KasPintar**, atau **Klienin** kalau kamu lebih kuat di integrasi, atau **UangPulang** kalau ingin tercepat & paling beda).
2. Saya bantu: brief 1-halaman + skenario demo 5 poin + diagram arsitektur + daftar perintah setup di VPS + draft artikel + naskah video.
