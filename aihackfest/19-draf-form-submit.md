# DRAF FORM SUBMIT — MATA (AI HackFest 2026)
> **Deadline resmi (dari form): 30 Sep 2026, 23.59 WIB · target kirim 16–17 Sep.**
> ⚠️ **Peta form aktual (16 halaman, diekstrak 14 Sep) + status tiap item: lihat `20-checklist-submit.md`.** File ini = bahan isi (ringkasan, poin pembeda).
> Format: salin per bagian; [ISI] = menunggu hasil eksekusi.

## 2a. Deskripsi Singkat (hal. 15 form — WAJIB ≤150 karakter, terukur 143)
> AI agent 24/7 pembaca data pengadaan publik Kab. Aceh Tengah yang menghasilkan indikasi anomali terverifikasi per paket. Indikasi, bukan vonis.

## 2b. Pesan untuk Dewan Juri (hal. 16 — opsional)
> Terima kasih, Dewan Juri. MATA tidak mengklaim menangkap koruptor — ia hanya membuat data yang sudah dibuka benar-benar dibaca: 662 paket pengadaan TA2026 satu kabupaten, 14 indikasi yang lahir otomatis, dan setiap angka bisa ditelusuri hingga record ID + CSV publik. Alat ini open source, berjalan di VPS 4GB, dan bisa direplikasi untuk daerah mana pun dengan satu perintah. Semoga MATA tidak pernah dipuji — karena itu artinya tidak ada yang perlu diawasi.

## 2c. Identitas (hal. 3, 7–10 — WAJIB persis sesuai registrasi)
- Solo ✅ · Nama lengkap / Email / WA / Instansi / Kota domisili → 👤 salin persis dari data registrasi.

---

## 1. Identitas
- **Nama produk:** MATA — Watchdog Akuntabilitas Pengadaan
- **Kategori:** Productivity & Personal AI
- **Tim/Peserta:** Afrizal Munthe
- **Tagline:** "Arsip yang dibaca, uang yang dijaga — indikasi berbasis data, bukan vonis."

## 2. Tautan wajib
| Item | Nilai | Status |
|---|---|---|
| Dashboard live | **https://mata.niumination.web.id** | ✅ LIVE (MODE: LIVE, 14 indikasi, HTTPS) |
| Repositori (public) | **https://github.com/niumination/mata-aihackfest-2026** | ✅ public — sinkronkan ke commit terakhir sebelum submit |
| Artikel (≥800 kata, 2 backlink) | [ISI setelah publish — URL LinkedIn/blog] | ⏳ publish 13 Sep |
| Video (5–10 mnt) | [ISI setelah rekam — URL YouTube unlisted/publik] | ⏳ rekam 14–15 Sep |

## 3. Ringkasan proyek (salin ke form)
> MATA adalah AI agent (Hermes Agent) yang berjalan 24/7 di VPS murah,
> membaca data pengadaan publik Kabupaten Aceh Tengah — 662 paket realisasi
> TA2026 beserta nama penyedia, 599 paket TA2025, dan 15.105 baris RUP
> rencana — dari tiga sumber live: INAPROC, SPSE LKPP, dan SAPA (portal data
> terbuka daerah). Dengan rule engine deterministik yang transparan (lima
> aturan, rumus & ambang dipublikasikan), MATA menghasilkan **14 indikasi
> anomali (3 tingkat tinggi)** — misalnya penyedia ber-riwayat satu proyek
> Rp229 juta yang menang kontrak Rp3,12 miliar, dan dua penyedia yang
> menyerap 8,4% & 7,5% dari seluruh nilai pengadaan kabupaten. Setiap
> indikasi menyimpan bukti, ID record, dan langkah lanjut; 1.250 paket bisa
> diunduh sebagai CSV untuk diverifikasi siapa pun. MATA juga membandingkan
> rencana (RUP) vs realisasi per 55 SKPD, menerbitkan dossier PDF + draft
> laporan resmi ke APIP, dan menjawab pertanyaan warga lewat chatbot
> terisolasi yang hanya menjawab dari data yang ia pegang. MATA tidak
> menghakimi: ia menyebut "indikasi, bukan vonis" — verifikasi dan pelaporan
> dilakukan manusia lewat kanal resmi (LAPOR!, Ombudsman, KPK, APIP).
> Infrastruktur: VPS 4 core/4GB ([Cloud VPS](https://cloudbaik.com/) via
> [AI Hosting](https://idwebhost.com/ai-hosting/)), domain
> `mata.niumination.web.id` (program .web.id IDwebhost) + HTTPS (Cloudflare).

## 4. Poin pembeda (jika form ada kolom "keunikan/kenapa menang")
1. **Data riil, bukan demo** — seluruh dashboard, indikasi, dan chatbot
   berjalan pada data publik sungguhan satu kabupaten (bukan mock).
2. **Transparansi total** — rumus & ambang aturan dipublikasikan di repo
   (`config.example.json` + `rules.py`); LLM tidak memutuskan, hanya
   menjelaskan.
3. **Verifikabel per paket** — setiap angka punya record ID + CSV 1.250 baris
   + tautan sumber.
4. **Jujur tentang batas** — aturan yang kekurangan data (D1 tanpa ref
   harga, D3 tanpa tanggal) tidak berjalan dan hal itu DITULIS di dashboard.
5. **Etika tertanam di arsitektur** — chatbot terisolasi (jail, audit,
   rate-limit), human-in-the-loop, red-line anti-bypass, "indikasi bukan vonis".
6. **Murah & reproducible** — 4GB RAM, deterministik, offline-capable (data
   ikut repo), 1 perintah untuk menjalankan ulang.
7. **Ekosistem kompetisi** — VPS via AI Hosting IDwebhost + domain .web.id
   dari program IDwebhost (Instagram official).

## 5. Check final submit (siang 16 Sep)
- [ ] Repo publik sinkron commit terakhir (konfirmasi ke Hermes)
- [ ] `https://mata.niumination.web.id` LIVE (MODE: LIVE, 14 indikasi)
- [ ] Artikel tayang + 2 backlink hidup (tes klik)
- [ ] Video tayang (publik/unlisted) + tautan tersimpan
- [ ] 4 screenshot (hero, kartu D4, RUP-vs-Realisasi, Tanya MATA) tersimpan
- [ ] Form terisi + terkirim ≤30 Sep (target: 16–17 Sep, aman dari edge)

## 6. Jika form meminta "dampak"
- 14 indikasi riil terdokumentasi (3 tinggi) dengan jalur verifikasi & kanal
  pelaporan resmi — alat yang bisa di-replikasi daerah lain (repo + 1 perintah).
- Narasi: dari "data dibuka" ke "data dibaca untuk rakyat".
