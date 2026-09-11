# AI HackFest 2026 — RONDE BOLD (Ronde 6): "Agent Yang Kamu Tidak Bisa Lakukan Sendiri"
**Afrizal Munthe** · Batch 3 (11–15 Sep 2026) · Productivity & Personal AI · Hermes Agent

> **Pergeseran total.** 24 ide sebelumnya = "agent membantu kamu". Ronde ini = **"agent melakukan yang mustahil kamu lakukan sendiri"**:
> melawan sistem, mengejar hasil sampai tuntas, memperjuangkan hak, memberi suara pada yang tak bersuara, atau **menggantikan dirimu** saat kamu tidak ada.
> **Boldness statement:** nilai tertinggi bukan "berguna", tapi **"agent itu bertindak, bukan sekadar menyarankan."**
>
> **Boldness scorecard (1–10, total 90):**
> **B1** Keberanian (radikal, "tak terfikirkan") · **B2** Masalah masif · **B3** Momen holy-crap (agent *bertindak*) · **B4** Frontiers agentic (otonom/jangka-panjang/adversarial/memory) · **B5** Emosional · **B6** Why now · **B7** Bisnis · **B8** Open source/public good (Onno) · **B9** Jujur & feasible 5 hari (Eko).

---

## 🔥 BOLD #1 — **ADVOKAT**: Personal AI yang **MELAWAN** untukmu, sampai beres ⚖️

### Boldness statement
> Semua agent lain *menyarankan*. Advokat **bertindak**: ia mengumpulkan bukti, menyusun dalil, mengirim surat keberatan, melacak status, **mencecar 3 instansi**, mengeskalasi ke regulator — **semata-mata, ber-memory, tidak berhenti sampai ada hasil.** Kamu tidur; kasusnya maju.

### Masalah (masif + universal + menyakit)
Hampir semua orang Indonesia pernah: **klaim asuransi ditolak tanpa penjelasan**, **uang lembur tidak dibayar**, **refund/klaim garansi diabaikan**, **izin/kartu diproses "nanti-nanti"** selamanya, **kontrak dipermainkan pihak kuat**.
- OJK: **ratusan ribu laporan** sengketa/penipuan jasa keuangan; klaim asuransi ditolak = complaint #1.
- Disnaker: sengketa hubungan industrial ribuan kasus/tahun (UPHR).
- Konsumen: BPSK/Kanmen — sengketa barang/jasa tak pernah habis.
**Inti:** kamu vs **sistem/pihak kuat** yang punya time, uang, dan lawyer — kamu cuma punya HP & waktu kerja. **Ketimpangan daya yang struktural.**

### Solusi
**Advokat = personal AI "pengacara & pengajar" yang mengambil alih urusanmu melawan sistem.** Ia memegang **CASE** (kasus) sebagai **tugas otonom jangka-panjang ber-memory**:
1. **Intake & bukti:** kamu serahkan dokumen (surat penolakan klaim, slip gaji, chat, kontrak) → Advokat **menganalisis**, mengekstrak dalil, menemukan **kelemahan pihak lawan** & **dasar hukum/aturan** (RAG atas regulasi: POJK, UU Ketenagakerjaan, UUPK, terms polis).
2. **Bertindak (otonom):** menyusun **surat keberatan/klaim yang benar** (format & bahasa formal), **mengisi & mengirim form** resmi (atau menyiapkan 1-klik siap kirim), **melacak status** (cron), dan **mencecar** jika diam — dengan nada yang makin tegas tiap eskalasi.
3. **Eskalasi cerdas:** kalau macet → otomatis susun surat ke **OJK/Disnaker/BPSK/YLKI** + **dossier bukti** terstruktur siap seret.
4. **Memory kasus:** ingat semua timeline, bukti, janji pihak lawan → tidak ada yang "terlupakan", tidak ada yang bisa menyangkal.
5. **Laporan ke kamu:** tiap langkah: *"Hari 12: saya sudah kirim keberatan ke cabang. Hari 19: mereka diam → saya eskalasi ke OJK. Status: diproses."*

### 🎬 Momen "holy-crap" (demo 90 detik, kasus ter-bounded)
> **Kasus: klaim asuransi kesehatan ditolak** ("penyakit pre-existing").
> Kamu melempar 3 dokumen (surat penolakan, polis, rekam medis) ke Advokat.
> **Tanpa disuruh lagi**, agent: (1) menemukan klausul polis yang **kabur** + dasar **POJK** bahwa penolakan wajib disertai alasan tertulis, (2) **menulis & "mengirim" surat keberatan** (ditampilkan tersusun lengkap), (3) **membuat timeline & dossier bukti** (PDF), (4) menjadwalkan **2 kali mencecar** (cron) + **draft eskalasi OJK**, (5) melapor ke kamu: *"Keberatan terkirim hari ini. Jika 7 hari tidak ada jawaban, saya siap draft laporan OJK."*
> **Juri baru saja melihat seorang "pengacara" bekerja 8 jam — dalam 90 detik — untuk kasus yang biasanya menyeret orang berbulan-bulan & berbiaya juta.**

### Boldness scorecard
| B | Nilai | Catatan |
|---|-------|---------|
| B1 Keberanian | **10** | Agent *melawan* & *bertindak* — belum ada peserta |
| B2 Masif | 9 | Ketimpangan daya; klaim/sengketa = universal |
| B3 Holy-crap | **10** | "Pengacara 8 jam dalam 90 detik" |
| B4 Frontiers agentic | **10** | Otonom, jangka-panjang, adversarial, memory, tool |
| B5 Emosional | 9 | Vindication; "hakmu diambil, agent mengambilkan balik" |
| B6 Why now | 8 | Agentic AI = topik 2025–26; sengketa finansial naik |
| B7 Bisnis | 9 | Legal-tech; B2C + B2B (advokasi nasabah/HR) |
| B8 Public good | 8 | Melawan pihak kuat = pemberdayaan |
| B9 Feasible 5 hari | 7 | 1 kasus end-to-end (lihat scope) |
| **Total** | **88/90** | **Paling "frontiers" + paling berani** |

### Scope 5 hari (biar tetap feasible & jujur)
- **Satu kasus ter-bounded** (klaim asuransi) di-demo **end-to-end nyata**: intake → analisis dalil → surat keberatan (PDF nyata) → timeline/dossier (PDF) → 2 cron "mencecar" (nyata terjadwal) → draft eskalasi OJK.
- "Kirim" = **menyiapkan + meng-simulasi pengiriman** (atau kirim ke inbox demo) — **jujur**, tidak klaim sudah masuk server OJK.
- **RAG regulasi**: kumpulkan 10–15 dokumen resmi (POJK, UU Ketenagakerjaan, UUPK) → basis dalil yang bisa disitasi (poin Eko + Onno).

### Teknologi & integrasi OSS
- Hermes (memory = **CASE** sebagai state jangka-panjang, cron untuk mencecar, subagent untuk riset dalil paralel, gateway WA).
- **RAG** (pgvector) atas regulasi + dokumen kasus; **OCR** (PaddleOCR) untuk scan polis/surat; **WeasyPrint** (PDF surat & dossier); **Grafana** (timeline kasus).
- Integrasi OSS: pgvector, PaddleOCR, LibreOffice; (roadmap: integrasi form resmi via API yang tersedia).

### Risiko & mitigasi
- **"Mengirim ke OJK" tidak bisa di-demo nyata** → posisi jujur: *"siap kirim, 1-klik"* + tampilkan form terisi; tidak klaim sudah masuk.
- **Liability hukum** (memberi "nasihat hukum") → posisi: **advokasi & pendampingan dokumen**, bukan hukum; disclaimer; dalil disitasi sumber resmi.
- **Autonomi terlalu "liar"** → **human-in-the-loop untuk langkah eksternal** (agent menyiapkan, kamu approve kirim) — justru poin etis di depan juri.
- **5 hari** → 1 kasus, 3 dokumen, 2 eskalasi. Cukup untuk menunjukkan **pola** (yang bisa direplikasi ke klaim lain).

### Bisnis
B2C (langganan "pengacara saku" Rp99rb/bln); B2B: bank/asuransi (advokasi nasabah), HR (sengketa ketenagakerjaan), komunitas konsumen. TAM = setiap orang yang pernah "kalah" pada sistem.

### Kenapa ini juara
- **Paling frontiers agentic** (B4=10) — Eko akan langsung mengenali "ini agent sungguhan, bukan chatbot".
- **Paling berani** (agent *melawan*) — B1=10, "tak terfikirkan".
- **Emosi vindication** + **bisnis jelas** + **pemberdayaan melawan pihak kuat** (Onno) + **dampak nyata** (Ogi).
- **Sesuai Aturan #7** (deteksi + **lapor kanal resmi**, tidak main hakim).

---

## 🔥 BOLD #2 — **MATA**: Watchdog yang **Membongkar** dari Data yang Diberikan Rakyat Sendiri 🕵️

### Boldness statement
> Pemerintah punya data terbuka (anggaran, pengadaan, proyek, izin). **Tidak ada yang membacanya untuk rakyat.** MATA membacanya 24/7, **mendeteksi anomali** (proyek fiktif, mark-up, anggaran ganda), **menyusun bukti**, dan **melaporkan ke kanal resmi** — **menjadikan data rakyat menjadi senjata akuntabilitas rakyat.**

### Masalah (masif + Onno-core)
- **Korupsi & anggaran yang tak transparan** = luka nasional; dana desa, pengadaan, proyek infrastruktur miliaran tak terawasi.
- **Open data ada, tapi jadi "pemandangan"** — tidak ada yang mengubahnya jadi **tindakan**.
- Onno W. Purbo hidup untuk **transparansi, open source, akuntabilitas, internet untuk rakyat** → ini **bahasa ibunda-nya**.

### Solusi
**MATA = watchdog AI yang mengawasi data publik & melindungi kepentingan umum.**
1. **Monitor 24/7** (cron) atas dataset publik (SPBE/pengadaan, laporan realisasi anggaran desa/kab, izin, proyek).
2. **Deteksi anomali transparan** (rule-based + reasoning): proyek tanpa pemenang, harga di atas pasar, anggaran ganda, "phantom project" (ada anggaran, tak ada fisik).
3. **Bukti otomatis:** tiap anomali → **dossier** (sumber data, perbandingan, kalkulasi, timeline) → **laporan ke kanal resmi** (APIP/KPK/ombudsman/pemred) + **ringkasan untuk warga**.
4. **Amplifikasi warga:** warga bisa lapor "proyek di desanya tak ada" → MATA mencocokkan dengan data → memperkuat.
5. **Peta akuntabilitas:** dashboard publik "siapa, berapa, di mana, status".

### 🎬 Momen "holy-crap"
> MATA memindai **laporan realisasi anggaran** sebuah kecamatan (data publik). Ia menemukan: **"Pos anggaran 'rehabilitasi jembatan' Rp800 juta — realisasi 100%, tapi koordinat proyek & foto serah-terima tidak ada."** → MATA menyusun **dossier** (sumber, kalkulasi selisih, pembanding proyek serupa) → **draft laporan ke APIP** + **infografis untuk warga**. **Juri melihat "inspektur" bekerja — dari data yang sebenarnya sudah bisa diakses siapa pun, tapi tak pernah dibaca.**

### Boldness scorecard
| B | Nilai | Catatan |
|---|-------|---------|
| B1 Keberanian | 9 | Mengawasi **kekuasaan** — berani secara politik |
| B2 Masif | 9 | Korupsi/anggaran = nasional |
| B3 Holy-crap | 9 | "Inspektur yang membongkar phantom project" |
| B4 Frontiers agentic | 8 | Monitor + deteksi + bukti + lapor |
| B5 Emosional | 8 | Keadilan; uang rakyat |
| B6 Why now | 7 | Akuntabilitas selalu relevan |
| B7 Bisnis | 7 | B2G/NGO/media/grant (B2C lemah) |
| B8 Public good | **10** | Ini jantung Onno |
| B9 Feasible 5 hari | 7 | 1 dataset + 1 jenis anomali |
| **Total** | **84/90** | |

### Scope 5 hari
- **Satu dataset publik nyata** (mis. laporan realisasi anggaran / SPBE yang bisa diunduh) + **satu jenis anomali** (phantom project / harga di atas pasar) + **1 dossier + 1 draft laporan** nyata.
- **Risiko data** (format berubah/tak tersedia) → siapkan 2–3 dataset cadangan; jika tak ada yang cocok, **dataset sintetik yang realistis** + jujur.

### Risiko & mitigasi
- **Aksesi data** (open data Indonesia tidak seragam) → 2–3 sumber cadangan; fallback dataset sintetik realistis.
- **Aksi "korupsi" = sensitif hukum** → posisi: **deteksi anomali + lapor kanal resmi + tidak vonis** ("indikasi, bukan kesimpulan") — sesuai Aturan #7.
- **Klaim berlebihan** → tunjukkan metodologi & batasan di artikel.
- **Bisnis B2C lemah** → fokus B2G/NGO/media/grant (jujur).

### Kenapa kuat
- **Paling "Onno" (B8=10)** — akuntabilitas + open data + open source = filosofi seumur hidupnya.
- Momen "membongkar" sangat kuat. **Bisnis B2C lemah** → menahan di #2.

---

## 🔥 BOLD #3 — **SUARA**: Agent yang **Membesar-besarkan** yang Tak Bersuara 📢

### Boldness statement
> Satu orang mengeluh = diabaikan. **Seribu orang mengeluh yang sama, terverifikasi & terstruktur = didengar.** SUARA mengambil **N keluhan seragam** (tengkulak, telat gaji, harga dipatok, layanan macet), **memverifikasi & mengagregasi** menjadi **dossier kolektif** yang tak bisa diabaikan, lalu **mengajuinya ke pemangku kepentingan** — **memberi kuasa pada yang selama ini tak berdaya.**

### Masalah (masif + sosial)
Nelayan dibayar di bawah pasar, buruh telat gaji, petani dipatok harga, pasien ditolak — **masing-masing kecil, kolektif raksasa.** Ketimpangan daya: **individu tak berdaya, kolektivitas tak terorganisir.**

### Solusi
**SUARA = agent agregasi & advokasi kolektif.**
1. **Kumpulkan** keluhan (WA) dari banyak pihak (nelayan, buruh, petani, pasien).
2. **Verifikasi & pola:** deteksi **pola seragam** (sama tengkulak? sama telat? sama harga?) → **dossier kolektif** (jumlah terdampak, nilai, pola, bukti).
3. **Eskalasi terukur:** draft **laporan/petisi** ke asosiasi/DKP/Disnaker/Dinas + **media** → **"500 nelayan, rugi 2 M, pola: 3 tengkulak"** (bukan "saya kesel").
4. **Follow-up & akuntabilitas:** lacak respons, eskalasi jika diabaikan.
5. **Memory kolektif:** pola historis (tahun lalu juga?).

### 🎬 Momen "holy-crap"
> 50 keluhan nelayan masuk (harga tongkol dipatok). SUARA mendeteksi: **3 tengkulak, 50 KK, selisih Rp2,1 M** → menyusun **dossier** (peta, kalkulasi, testimonial) → **draft laporan ke DKP** + **press release**. **Juri melihat "50 orang kecil" tiba-tiba punya "serikat" yang bekerja dalam hitungan menit.**

### Boldness scorecard
| B | Nilai | Catatan |
|---|-------|---------|
| B1 Keberanian | 9 | Memihak **yang lemah vs kuat** |
| B2 Masif | 9 | Ketimpangan daya kolektif |
| B3 Holy-crap | 8 | "50 orang → 1 serikat dalam 1 menit" |
| B4 Frontiers agentic | 8 | Agregasi + verifikasi + eskalasi |
| B5 Emosional | 9 | Keadilan sosial |
| B6 Why now | 7 | Selalu relevan |
| B7 Bisnis | 7 | NGO/asosiasi/pemerintah (B2C lemah) |
| B8 Public good | 9 | Pemberdayaan kolektif |
| B9 Feasible 5 hari | 7 | Agregasi N keluhan → 1 dossier |
| **Total** | **81/90** | |

### Scope 5 hari
- **N keluhan (50, bisa sintetis realistis)** → deteksi pola → **1 dossier kolektif + 1 draft laporan** nyata.
- **Risiko**: "membuat petisi" sensitif → posisi: **agregasi data & lapor kanal resmi/asosiasi**, bukan mobilisasi.

### Risiko & mitigasi
- **Sensitivitas sosial/politik** → netral, berbasis data, lapor kanal resmi, tidak memprovokasi.
- **Verifikasi** → tunjukkan metode (tidak klaim semua terverifikasi).
- **Bisnis B2C lemah** → fokus NGO/asosiasi/pemerintah.

---

## 🔥 BOLD #4 — **DIRI**: "Diri Kedua" yang **Tetap Hidup** Saat Kamu Tidak Ada 🕊️

### Boldness statement
> Di ekonomi informal, **ketika kepala keluarga wafat/ lumpuh, segalanya runtuh**: tagihan, bisnis, anak, orang tua. DIRI adalah **"diri kedua"** yang belajar caramu berpikir, lalu **melanjutkan**: mengurus tagihan, memelihara bisnis, membesarkan anak, menjaga orang tua — **setelahmu.**

### Masalah (masif + emosional terdalam)
- Ekonomi informal Indonesia: **satu penghasil = satu titik kegagalan.** Kematian/lumpuhnya penopang = **bencana ekonomi keluarga** yang tak ter asuransi.
- **Nas warisan, tagihan, dan "urusannya"** jadi beban tanpa sistem.

### Solusi
**DIRI = personal AI "diri kedua" yang persisten.**
1. **Belajar dirimu** (memory dalam): nilai, prioritas, gaya keputusan, relasi, utang-piutang, tagihan, bisnis.
2. **Mengurus saat kamu ada:** manajemen keuangan/tagihan/bisnis (co-pilot).
3. **Melanjutkan saat kamu tidak ada:** **mode kelangsungan** — teruskan tagihan, jaga bisnis, komunicasi dengan keluarga & kreditor sesuai **nilai & instruksimu**, lindungi anak & orang tua.
4. **Warisan terstruktur:** "surat" & keputusan yang konsisten dengan caramu.

### 🎬 Momen "holy-crap"
> (Emosional, bukan teknikal) Demo: setelah "kematian" (simulasi), **DIRI** tetap membayar 3 tagihan, mengirim pesan konsisten-gaya-keluarga ke kreditor, menjaga jadwal bisnis, dan memberi ringkasan ke anak: *"Apa yang Papa tinggalkan, dan apa yang harus kamu lakukan minggu ini."* **Juri melihat "keluarga tidak runtuh."**

### Boldness scorecard
| B | Nilai | Catatan |
|---|-------|---------|
| B1 Keberanian | **10** | Menghadapi **kematian** — paling berani |
| B2 Masif | 8 | Ekonomi informal = 1 penghasil |
| B3 Holy-crap | 8 | Emosional, unik |
| B4 Frontiers agentic | 9 | Memory dalam + kelangsungan |
| B5 Emosional | **10** | Kematian, keluarga |
| B6 Why now | 6 | Kronis, bukan hot-event |
| B7 Bisnis | 7 | Asuransi/fintech (B2B) |
| B8 Public good | 8 | Melindungi keluarga |
| B9 Feasible 5 hari | 6 | Demo "kelangsungan" ter-bounded |
| **Total** | **82/90** | |

### Scope 5 hari
- **1 skenario kelangsungan ter-bounded**: 3 tagihan + 1 pesan ke kreditor + 1 ringkasan ke anak (semua nyata di-demo).
- **Etika berat** → handling sangat hati-hati, tidak sensasional, hormat.

### Risiko & mitigasi
- **Etika/sensitivitas kematian** → hormat, tidak mengeksploitasi; positioning "kelangsungan keluarga", bukan "pengganti orang mati".
- **Why-now & demo "menang"** lebih abstrak → menahan di #4.
- **Liability** (mengurus keuangan orang) → human-in-loop + instruksi eksplisit pengguna.

---

## 📊 PERBANDINGAN BOLD & REKOMENDASI

| Kandidat | Total | Kekuatan inti | Kelemahan |
|----------|-------|---------------|-----------|
| **ADVOKAT** | **88** | Paling frontiers agentic (otonom+adversarial+memory) + "agent melawan" + bisnis jelas | Liabilitasnya; "kirim ke OJK" disimulasikan |
| **MATA** | **84** | Paling "Onno" (akuntabilitas+open data) | Bisnis B2C lemah; akses data |
| **DIRI** | **82** | Paling emosional & berani (kematian) | Why-now & demo "menang" abstrak |
| **SUARA** | **81** | Paling keadilan-kolektif | Bisnis B2C lemah; sensitivitas |

### Rekomendasi
**Utama: ADVOKAT** — satu-satunya yang memuat **frontiers agentic sejati** (agent otonom, jangka-panjang, adversarial, ber-memory, *bertindak*) yang persis apa yang didefinisikan sebagai AI agent 2026, **plus** emosi vindication, bisnis jelas, pemberdayaan melawan pihak kuat, dan **feasible** dengan 1 kasus ter-bounded. Ini yang bikin Eko (praktisi) bilang *"ini agent beneran"*, Onno bilang *"ini memberdayakan rakyat"*, Ogi bilang *"ini bisa dijual."*

**Runner-up paling "Onno": MATA** (jika kamu ingin misi akuntabilitas & nyaman dengan bisnis B2G/NGO).
**Paling emosional/berani: DIRI** (jika kamu siap handling etika berat & why-now yang pelan).

> **Catatan jujur:** ADVOKAT & MATA punya elemen "menyentuh kekuasaan/sistem" — pastikan positioning **deteksi+lapor kanal resmi, bukan vonis** (sesuai Aturan #7) & **human-in-the-loop** untuk langkah eksternal. Itu justru memperkuat poin etika di depan juri.

**Sekarang kamu pegang kemudi.** Mau saya **bedah ADVOKAT sampai ke paket eksekusi 5 hari** (seperti SireneKampung), atau mau lihat **MATA/DIRI** lebih dalam dulu, atau ada **gaya berani lain** yang kamu bayangkan dan saya yang wujudkan?
