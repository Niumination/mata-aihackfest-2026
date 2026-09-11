# AI HackFest 2026 — Ronde 4: Ide dari Top Issue Paling Masif
**Untuk:** Afrizal Munthe · Batch 3 (11–15 Sep 2026) · Productivity & Personal AI · Hermes Agent

> Ini ronde BARU — 5 ide yang belum pernah muncul di ronde 1–3, masing-masing diikat mati ke satu masalah masif nasional.
> **Keunggulan tersembutumu:** kamu dari **Banda Aceh** — kota tsunami 2004, kota pelabuhan, kota nelayan. Cerita lokal + masalah nasional = storytelling 15% yang tidak bisa ditiru peserta lain. Dua ide di bawah sengaja memanfaatkan ini.

## 1. Lima Top Issue Paling Masif (yang belum tersentuh 15 ide sebelumnya)

| # | Top issue | Skala (verifikasi sumber terbaru di artikel) | Kenapa masih "ruang kosong" |
|---|-----------|-----------------------------------------------|------------------------------|
| 1 | **Bencana alam** — ribuan peristiwa/tahun (gempa, tsunami, banjir, longsor; data BNPB) | Nasional; Aceh = wilayah rawan ganda (gempa+tsunami) | Semua hackathon fokus "produktivitas kantor"; hampir tidak ada yang bikin **agen kesiapsiagaan keluarga** |
| 2 | **Nelayan & perbudakan ekonomi "sistem lung"** — jutaan KK nelayan (BPS ±4,5–5 juta), harga tangkapan dikuasai tengkulak, utang berbunga | Nasional; sangat kental di pesisir Aceh | Data & ketimpangan tangkapan hampir tidak pernah disentuh AI agent |
| 3 | **Stunting** — ±1 dari 5 anak (SSGI 2024, ±19%), program prioritas negara | Nasional | Posyandu = jaringan kader yang belum ter-digitalkan dengan AI |
| 4 | **BPJS Kesehatan** — 270+ juta peserta; bingung FKTP, faskes, penolakan klaim | Nasional | Navigasi hak & prosedur = personal AI yang sangat dibutuhkan |
| 5 | **Transparansi uang bersama komunitas** (kas RT/RW, masjid) — 1+ juta RT, 800.000+ masjid | Nasional | Uang publik mikro = sumber konflik & ketidakpercayaan; Onno W. Purbo hidup di dunia ini (RT/RW-Net!) |

---

## 2. LIMA IDE BARU

### IDE 1 — **SireneKampung**: Agen kesiapsiagaan bencana keluarga & RT 🌊 (top issue: BENCANA)
**Pitch:** Agent 24/7 di VPS yang **memonitor data gempa BMKG (open API publik)** via cron → estimasi kekuatan guncangan untuk lokasimu (rumus empiris magnitude + jarak episenter — transparan, bukan black-box) → **alert < 30 detik** ke grup keluarga (WA/Telegram) dengan instruksi otomatis (meeting point, siapa pegang obat, dokumen penting) → **daftar darurat keluarga** yang dirawat agent (medis, kontak, lokasi aman) → pasca-peristiwa: **log insiden + draft laporan ke RT**. Posisi jujur: *"pelengkap, bukan pengganti sirene resmi."*
- **Dampak nyata:** Indonesia = negara dengan ribuan bencana/tahun; respons 30 detik pertama menentukan. Metrik demo: injeksi data uji gempa → alert terkirim <30 dtk, checklist keluarga lengkap 100%, log insiden + draft laporan RT ter-generate.
- **Teknologi:** Hermes (cron, gateway multi-kanal, memory, subagent) + API BMKG/BNPB (publik) + rumus intensitas (Python, bisa diaudit) + SQLite + Grafana (grafik riwayat guncangan — adegan video).
- **Integrasi OSS:** Grafana, SQLite; data BMKG/BNPB (open data).
- **Risiko & syarat khusus:** false alarm → kalibrasi threshold + mode "pastikan dulu"; jangan klaim sebagai sistem resmi; data lokasi keluarga = PDP → self-hosted, minimalkan; uji API BMKG **hari 1**.
- **Feasibility 5 hari:** TINGGI (semua internal + 1 open API publik).
- **Nilai jual:** SaaS keluarga Rp10rb/bln; B2B2C: pemerintah daerah/BNPB (pilot komunitas); donasi/grant untuk wilayah rawan.
- **Kenapa juri suka:** **Onno** = public good + komunitas + open data (DNA-nya, dan semangat RT/RW-Net); **Ogi** = SaaS keluarga + pilot pemda; **Eko** = pipeline data → rule engine → alert nyata.
- **Kenapa menang untukmu:** kamu dari **Aceh**. 2004 bukan sekadar statistik bagimu — itu cerita yang membuat 3 juri diam di kursi. Demo "alert tsunami" di kota kelahiranmu = storytelling yang tidak bisa disaingi.

### IDE 2 — **LautPintar**: Buku kas nelayan yang membebaskan dari "sistem lung" ⚓ (top issue: KELAUTAN & KEMAKMURAN NELAYAN)
**Pitch:** Nelayan kecil terjebak: tangkapan dibeli tengkulak ("lung") di bawah harga pasar + utang berbunga. LautPintar = agen via WA/voice: (1) **buku kas tangkapan** — *"Tadi dapat 40kg tongkol, jual ke lung 45 ribu"* → tercatat otomatis (voice-friendly, Whisper), (2) **rekap transparan** mingguan: total tangkapan, harga rata-rata vs harga pasar (input mingguan dari kelompok nelayan / data publik), (3) **pelacak utang lung** + angsuran → **"progress kebebasan"** (grafik utang menipis), (4) rekap settlement bulanan per lung (PDF), (5) pengingat: BBM subsidi, iuran, jadwal serah terima.
- **Dampak nyata:** jutaan KK nelayan; praktik "lung" mengunci nelayan di kemiskinan (terdocument di banyak riset). Metrik demo: 30 entri tangkapan (voice), 1 rekap minggu vs harga pasar (menunjukkan selisih yang hilang), 1 grafik pelunasan utang, 1 PDF settlement.
- **Teknologi:** Hermes (gateway, cron, memory, skill) + **Whisper** (OSS) + rule engine settlement (Python, transparan) + SQLite + PDF + Grafana (grafik "progress kebebasan" — visual yang emosional).
- **Integrasi OSS:** Whisper, Grafana, SQLite; harga pasar: input kelompok nelayan / data DKP daerah (jujur soal sumber).
- **Risiko & syarat khusus:** suara di laut → mode kalimat pendek + konfirmasi baca-balik; literasi digital rendah → desain ultra-sederhana (WA + suara); data harga tangkapan tidak ada API resmi → posisi jujur "input komunitas, analisis agent"; demo pakai data sintetis 1 kelompok nelayan.
- **Feasibility 5 hari:** SEDANG-TINGGI (Whisper + rule engine; tanpa OCR).
- **Nilai jual:** SaaS per kelompok nelayan (KUD/kelompok usaha) — bukan per individu; B2B: KUD, cold storage, DKP, program CSR perikanan.
- **Kenapa juri suka:** **Onno** = pemberdayaan komunitas pesisir + open source (spirit "internet untuk rakyat" versi laut); **Ogi** = B2B KUD + CSR; **Eko** = voice pipeline + rule engine settlement yang transparan.
- **Kenapa menang untukmu:** Banda Aceh = kota pelabuhan. Kamu bisa narasi ini dengan otoritas personal. "Agen yang membebaskan nelayan dari utang" = judul yang akan diingat juri sampai hari voting.

### IDE 3 — **TumbuhSiaga**: Penjaga stunting untuk ibu & kader posyandu 🍼 (top issue: STUNTING)
**Pitch:** Agent untuk kader posyandu & ibu: (1) input berat/tinggi (manual, 10 detik) → **hitung Z-score WHO** (rule-based, bisa diaudit) → grafik tumbuh + **flag dini** dengan saran konkret (bukan diagnosa medis — "segera ke puskesmas"), (2) **cron imunisasi** (jadwal KIA standar, data publik) → reminder otomatis ke ibu via WA, (3) **RAG resep gizi lokal** — menu anti-stunting dari bahan lokal & murah (teriyang, singkong, kangkung, ikan lokal → sentuhan Aceh: *ikan teri, kepal, singkong rebus*), (4) **laporan bulanan posyandu** (PDF) — 30 ibu = 1 laporan 1-klik, (5) pelacakan "tindak lanjut" ibu yang flag.
- **Dampak nyata:** stunting = program prioritas negara (target nasional terus ditekan); posyandu = 200.000+ titik layanan yang masih manual. Metrik demo: 30 ibu sintetis, 12 grafik tumbuh, 5 flag + 5 referral text, 12 reminder imunisasi terjadwal, 1 laporan bulanan.
- **Teknologi:** Hermes (cron, memory, gateway) + kurva WHO (standar publik, Python) + RAG resep gizi (pgvector) + PDF.
- **Integrasi OSS:** pgvector/Qdrant, WeasyPrint, Grafana (dashboard posyandu).
- **Risiko & syarat khusus:** **bukan alat medis** — positioning screening & rujukan + disclaimer jelas; data anak = PDP sensitif → demo 100% data sintetis; input manual = kunci akurasi (jangan klaim ukur otomatis).
- **Feasibility 5 hari:** SEDANG-TINGGI.
- **Nilai jual:** B2G (dinkes/puskesmas — pilot), B2C komunitas ibu (free/sumbangan), grant CSR.
- **Kenapa juri suka:** **Onno** = pendidikan kesehatan + public good + open data (WHO); **Ogi** = B2G pilot; **Eko** = rule engine Z-score + RAG yang rapi.
- **Kenapa unik:** semua peserta bikin "chatbot kesehatan"; yang bikin **agen kerja untuk kader posyandu** (siapa yang benar-benar sibuk) = jarang sekali.

### IDE 4 — **JKNavigator**: Navigator BPJS untuk keluarga Indonesia 🏥 (top issue: AKSES KES & BENEFIT BPJS)
**Pitch:** 270+ juta peserta BPJS, tapi mayoritas bingung: FKTP-nya di mana, rujukan harus lewat mana, kenapa klaim ditolak. JKNavigator = agent RAG di atas **dokumen resmi publik BPJS** (Perpres, alur layanan, ketentuan faskes) → jawab dalam bahasa manusia + **sitasi sumber** → (1) playbook "jika X maka Y" (rawat inap, darurat, resep lanjutan, pindah FKTP), (2) **cron pengingat pribadi** (periksa rutin, perpanjang, jadwal poli orang tua), (3) **checklist dokumen klaim** per jenis kasus, (4) **draft surat pengaduan** (kecall center BPJS/Ombudsman) dengan bahasa formal yang benar. Posisi jujur: *navigator & pendamping dokumen — bukan akses rekening.*
- **Dampak nyata:** salah prosedur = penolakan klaim = biaya out-of-pocket bagi kelas menengah ke bawah. Metrik demo: 20 pertanyaan dijawab dengan sitasi, 5 playbook, 5 pengingat terjadwal, 2 draft pengaduan.
- **Teknologi:** Hermes (memory, cron, gateway) + **RAG atas dokumen publik BPJS** (kumpulkan 5–10 PDF resmi — ini konten uniknya) + pgvector + PDF.
- **Integrasi OSS:** pgvector/Qdrant, Paperless-ngx (arsip dokumen klaim), WeasyPrint.
- **Risiko & syarat khusus:** tidak ada API resmi → posisi jujur "navigator" (jangan klaim cek status akun); akurasi aturan → RAG hanya dari dokumen resmi + sitasi + "cek ke call center 165"; batas nasihat medis.
- **Feasibility 5 hari:** TINGGI (inti = kurasi dokumen + RAG + cron — cocok untuk vibecoding).
- **Nilai jual:** SaaS Rp15–25rb/bln (keluarga); B2B2C: perusahaan (fitur benefit karyawan), fintech asuransi; **knowledge base-nya bisa di-open-source** (poin Onno).
- **Kenapa juri suka:** **Eko** = showcase RAG berkualitas (sitasi = diferensiasi teknis); **Ogi** = B2B perusahaan; **Onno** = literasi publik + open knowledge base.
- **Kenapa unik:** "chatbot BPJS" ada, tapi **navigator + dokumen pengaduan + cron pengingat keluarga** sebagai satu agen = belum.

### IDE 5 — **KasRT**: Bendarahsuna digital RT/RW yang transparan ke warga 🏘️ (top issue: TRANSPARANSI UANG BERSAMA)
**Pitch:** Kas RT/RW = sumber konflik (uang masuk-keluar tidak jelas, laporan musyawarah menghilang). KasRT: (1) bendahara foto kwitansi/resi → **Vision LLM** ekstraksi (tanggal, nominal, keterangan) → tercatat, (2) **cron: laporan mingguan otomatis** ke grup warga (format rapi, bisa diaudit semua warga), (3) **pelacak rencana anggaran** musyawarah (realisasi vs rencana per pos), (4) **notulen musyawarah** otomatis dari rekaman/catatan, (5) **komplain warga → work order** (jalan berlubang → tercatat, ada status, ada tenggat), (6) arsip semua bukti di **Paperless-ngx**.
- **Dampak nyata:** 1+ juta RT di Indonesia; kepercayaan warga = fondasi kohesi sosial. Metrik demo: 30 bukti keuangan (20 foto + 10 manual), 1 laporan mingguan terkirim ke grup, 1 dashboard realisasi anggaran, 3 work order warga dengan status.
- **Teknologi:** Hermes (cron, gateway WA grup, memory) + **Vision LLM** (kwitansi) + SQLite/Postgres + **Grafana** (dashboard realisasi — adegan video) + **Paperless-ngx** (arsip).
- **Risiko & syarat khusus:** OCR tulisan tangan → fallback input manual + konfirmasi 1-tap; **posisi: pencatat & transparansi, BUKAN pengelola uang** (tidak pernah menyentuh transfer); kepercayaan → semua data terbuka untuk warga (desain = kepercayaan).
- **Feasibility 5 hari:** SEDANG-TINGGI (Vision LLM = satu-satunya risiko; fallback manual aman).
- **Nilai jual:** B2G (kelurahan — pilot), SaaS ringan per RT (Rp10–20rb/bln, diluar niscaya), grant/fasilitasi kelurahan.
- **Kenapa juri suka:** **Onno** — ini **surat cinta untuk RT/RW-Net**, karya seumur hidupnya (jaringan komunitas swadaya). Ide yang bicara bahasa dia; dia akan langsung paham. **Ogi** = B2G pilot. **Eko** = Vision pipeline + audit trail.
- **Kenapa unik:** "transparansi kas RT dengan AI" — saya yakin tidak ada peserta lain yang berpikir ke arah ini.

---

## 3. Ranking Ronde 4 + Finalis Seluruh Ronde

| Rank Ronde 4 | Ide | Top issue | Bisnis | Teknis | Dampak | Unik | Feasible |
|---|-----|-----------|--------|--------|--------|------|----------|
| 🥇 | **SireneKampung** | Bencana | 8.5 | 9 | 9.5 | 9.5 | 9 |
| 🥈 | **LautPintar** | Nelayan/lung | 8 | 8.5 | 9.5 | 9.5 | 8 |
| 🥉 | **KasRT** | Transparansi komunitas | 7.5 | 8.5 | 9 | 9.5 | 8 |
| 4 | **TumbuhSiaga** | Stunting | 8 | 8.5 | 9 | 8 | 8 |
| 5 | **JKNavigator** | BPJS | 8.5 | 9 | 8.5 | 8 | 8.5 |

### Finalis SELURUH 21 ide (ronde 1–4) — 5 yang saya anjurkan untuk dipertimbangkan terakhir:
1. **SireneKampung** — dampak + cerita Aceh = storytelling tertinggi; public good = Onno; SaaS+pemda = Ogi; pipeline data nyata = Eko. **Risiko terkecil secara teknis** (1 open API + rule engine).
2. **GajiTepat** (ronde 3) — bisnis + inklusi keuangan; TAM 64 juta pekerja.
3. **KasPintar** (ronde 1) — paling "standard" tapi sangat kuat dan feasible.
4. **LautPintar** — cerita paling personal & emosional (pelabuhan Aceh); sedikit lebih berisiko (voice di lapangan, data harga).
5. **Klienin** (ronde 1) — pilihan paling "komersial/developer-first" kalau kamu mau bermain aman di sisi teknis-bisnis.

### Saran strategis akhir
- **Mau menang lewat cerita & dampak** → **SireneKampung** (cerita tsunami Aceh + public good + teknis aman).
- **Mau menang lewat bisnis & skala ekonomi** → **GajiTepat**.
- **Mau kombinasi keduanya dalam satu narasi** → tidak bisa (pilih satu), tapi SireneKampung punya jalur B2B pemda yang juga jelas.

**Dengan waktu batch 5 hari dan kamu berasal dari Aceh, saya menaruh 1 jempol di SireneKampung** — bukan cuma karena masalahnya masif, tapi karena *hanya kamu* yang bisa menceritakan ide ini dengan bobot emosional seperti itu.
