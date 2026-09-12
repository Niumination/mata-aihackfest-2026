# 14 — Audit UI/UX + Refactor Dashboard MATA (12 Sep 2026)

Role: Lead UI/UX & Frontend. Target: `mata/web.py` (single-file, zero-dependency).
Status: **SELESAI — teruji di sandbox**. Deliverable: `web.py` baru (drop-in swap) + `DESIGN.md` v3.
Sifat perubahan: **100% presentasi + 1 konstanta warna Python**. Tidak ada perubahan API, data, logika konsensus, atau flow consent.

## 1. Analisis singkat (audit kode lama, 1240 baris)

**Yang sudah bagus (dipertahankan):** token warna "living codex" di `:root`, hierarki tipografi
serif/mono yang jelas, boot sinematik, panel bisa collapse/zoom (localStorage), consent-first
UU PDP, `focus-visible`, `prefers-reduced-motion` (parsial).

**Temuan utama:**

| # | Masalah | Dampak |
|---|---------|--------|
| 1 | **3 set warna severity** — Python `SEV_STYLE` `#c0392b/#d97c1e/#4a7c3a`, CSS `--red/--amber/--green` `#b3261e/#96690a/#35703c`, titik legend hex ketiga | Graph & label & legenda tidak konsisten; desain DESIGN.md sendiri dilanggar |
| 2 | **Kontras gagal WCAG AA** — `--ink-soft #5c5347` @12px ≈4.0:1, `.dim` opacity .55, `.ghint` .35, `.t-l` .5 | Teks kecil sulit dibaca (kriteria a11y + profesionalitas) |
| 3 | **Tidak ada skala** — spasi 6/8/10/12/14/16/18/24/26/34/40px ad hoc; radius 8–22px bebas; bayangan hanya 4 elemen | Ritme visual tidak konsisten, terasa "tempelan" |
| 4 | **6 varian tombol** tanpa sistem transisi/`active` | Interaksi terasa mati |
| 5 | **Nol feedback dinamis** — tanpa toast (error = innerHTML ke panel), tanpa loading state (box iklim melompat ke teks error), tanpa hover di kartu/ubin/baris tabel, tanpa transisi ganti isi pembaca, ticker tidak bisa di-pause | "Kaku dan statis" — inti keluhan |
| 6 | **Mobile** — `#locbanner` tumpang tindih `#chatfab` (<640px), tanpa breakpoint tablet (640→1100 = 1 kolom), tap target 30px, tanpa safe-area iOS | Rusak di HP & tablet |

## 2. Refactor per modul (sudah diimplementasikan di `web.py` baru)

Semua modul **independen** — bisa di-cherry-pick bertahap sesuai peta lokasi baris.
CSS/JS ada di dalam f-string Python → semua `{` ditulis `{{` (sudah benar di file akhir).

| Modul | Isi | Lokasi |
|-------|-----|--------|
| **M0 — Design tokens** | Skala spasi `--s1…7` (4–40px), radius `--r-sm…xxl`, bayangan `--sh-1/2/3`, durasi `--dur-1…4` + easing tunggal `cubic-bezier(.16,1,.3,1)`, `--sev-*` satu-sumber | CSS `:root` (baris ~426–452); Python `SEV_STYLE` baris 75 |
| **M1 — Kontras & tipografi** | `--ink-soft #5c5347→#4a4238`, `--amber #96690a→#7d5708` (AA untuk teks kecil), semua teks tipis di gelap ≥opacity .68, `.t-l` 9→9.5px, `.leg`/`.dim` dinaikkan | Seluruh CSS |
| **M2 — Spasi/radius/bayangan** | Semua elemen pindah ke token; `.flag` jadi kartu (border+radius+shadow saat open); bayangan konsisten sh-1/sh-2/sh-3; `.leg` border transparan anti layout-shift | Seluruh CSS |
| **M3 — Mikro-interaksi** | Sistem tombol tunggal (transisi 140ms + `active` scale .985) untuk `.btn/.ptbtn/.pill/.chip/.leg/.csug`; hover-lift `translateY(-2px)+shadow` di kartu/ubin/`.idx`; hover baris tabel; ticker **pause saat hover** | CSS `M3 — SISTEM TOMBOL` (baris 475–488), `M3 — KARTU` (489–496) |
| **M4 — Toast + loading** | `#toasts` (aria-live) + CSS in/out; JS wrapper `fetch` → toast error per-endpoint (throttle 60 dtk); toast sukses "Iklim termuat"; kelas `.skeleton` shimmer siap pakai; LIVE badge pulse | HTML baris 781; CSS 454–474; JS `M4` (baris 1227–1255, 1327–1335) |
| **M5 — Komponen dinamis** | Scroll-reveal (h2/ticker/grid4, `IntersectionObserver`, flag head `rv-init` anti-flash); count-up angka hero/kartu (restore nilai asli di akhir); bar vendor animasi 0→nilai (bar bulanan: markup-nya adalah dead code di template — tak pernah ter-render, jadi JS/CSS-nya standby); isi panel pembaca fade saat ganti (MutationObserver); badge LIVE pulse | JS `M5` (baris 1257–1319); CSS `flag-in`, `reader-in`, `decpulse`, `livepulse` |
| **M6 — Mobile** | Breakpoint tengah **768px** (2 kolom tablet), tap target ≥40px (ptbtn/prb), `body.loc-open` → chatfab naik 118px saat banner lokasi tampil (MutationObserver), safe-area `env(safe-area-inset-bottom)` di wrap/hero/banner/chatfab/toast, toast full-width di ≤640px | CSS `M6 — MOBILE` (baris 742–762) + `body.loc-open` (baris ~640); JS `M6` (1320–1326) |
| **A11Y** | `prefers-reduced-motion: reduce` mematikan **semua** animasi/transisi (marquee, orb, pulse, bar, reveal, toast, shimmer); `:focus-visible` dipertahankan | CSS 763–777 |

**Inti arsitektur JS:** modul baru = satu IIFE terpisah (baris 1224–1335) yang **append-only** —
tidak satu pun baris JS lama disentuh; nama-namanya lokal, tidak bentrok; semuanya
no-op aman jika elemen tidak ada. JS lama (boot, reader, filter, OSM, chat, consent) utuh.

## 3. Bukti uji (sandbox, 12 Sep 2026)

| Uji | Hasil |
|-----|-------|
| `ast.parse(web.py)` | ✓ syntax Python valid |
| Render halaman (48 record demo) | ✓ HTTP 200, 115.000 B |
| F-string bocor `{{` di output | ✓ 0 |
| Warna lama `c0392b/d97c1e/4a7c3a` | ✓ 0 (lenyap total) |
| `node --check` 3 blok JS | ✓ 3/3 valid (27.366 B modul utama) |
| Cakupan selector lama vs baru | ✓ 0 selector hilang (`[open]` via attribute) |
| API: status / flags / visitors / iklim / records.csv | ✓ 200 — iklim bahkan **live** Open-Meteo (Takengon 20°C, RH 9x%) |
| Node graph | ✓ 2 node `fill="#b3261e"` = token `--sev-tinggi` |

Batas uji: sandbox **tanpa headless browser** → verifikasi struktural + render, bukan screenshot.
**Wajib cek visual sekali** setelah di-VPS: boot → hover kartu → ganti node graph → buka chat →
resize ke 390px (banner lokasi + chatfab) → mode reduced-motion (OS).

## 4. Instalasi (VPS, <2 menit)

```bash
# di VPS
cd /root/Arck4li-AIHackfest/mata
sudo cp mata/web.py mata/web.py.bak.$(date +%F)      # backup
# salin file web.py baru (dari workspace ini) ke: mata/web.py
# salin DESIGN.md baru ke: DESIGN.md
sudo systemctl restart mata-web.service
curl -s localhost:8080 | grep -c 'rv-init'           # harus ≥1
curl -s localhost:8080/api/status                    # harus JSON 200
```

Rollback: `sudo cp mata/web.py.bak.* mata/web.py && sudo systemctl restart mata-web.service`.

## 5. Re-audit (12 Sep 2026, setelah ronde pertama)

Permintaan user: "periksa lagi dan perbaiki jika masih ada kesalahan." Hasil:

| Temuan | Status |
|--------|--------|
| **BUG — transisi bar bulanan salah target**: selector `.months .bar div` (anak) padahal elemen dengan tinggi adalah `.mcol > .bar` langsung → animasi tak pernah jalan | **DIKOREKSI** → `.months .bar,.bar-dec{transition:height var(--dur-4)}` (juga di daftar reduced-motion) |
| **BUG (kecil) — offset `body.loc-open` 118px**: tinggi banner lokasi maks ≈170px → masih bisa tumpang 5–10px di layar sempit | **DIKOREKSI** → 138px |
| Dead code **sejak asli** (bukan regresi, dibiarkan): `month_bars` dibangun tapi tak pernah dipakai di template (bar bulanan tak pernah ter-render) | Didokumentasikan; JS/CSS bar bulanan M5 jadi *standby* bila markup nanti diaktifkan |
| Dead CSS **sejak asli**: `#minimap` tak punya elemen (peta memakai `#osm`; SVG noscript tak ber-id) | Didokumentasikan; aturan dipertahankan |
| `idx`/INDEKS NASIONAL LKPP = blok kondisional (hanya ada bila data nasional termuat) | Sesuai rancangan, bukan bug |
| JS lama baris "angka panjang mengecil" (`.long`) vs count-up baru | **Aman** — kelas `.long` dipasang sekali saat load, count-up tak menyentuh kelas |
| Hover baris `#pkgs` (`.pkg`) | Ter-cover `tbody tr:hover td` (browser auto-wrap `<tbody>`) |
| Fetch pertama (iklim/visitors saat load) tak kena wrapper toast (IIFE lama jalan duluan) | Diterima — error tetap tampil inline (perilaku lama); fetch berikutnya semua ter-wrapping |

Verifikasi tambahan ronde re-audit: balance brace CSS ✓ · 0 aturan kosong ✓ · semua
deklarasi valid ✓ · `node --check` 3/3 blok JS ✓ · cross-check semua selector kelas & id
CSS vs HTML render ✓ · render 115.984 B, 0 brace f-string bocor ✓.

## 6. Catatan keputusan

- `--amber` dipermudah `#96690a → #7d5708` demi WCAG AA (DESIGN.md lama menyebut `#96690a`
  untuk *label* severity; label itu bold 10–11px — tetap diubah agar aman di semua konteks).
- Reveal hanya di `h2/.ticker/.grid4` — **bukan** di `.panel` (akan bentrok dengan
  transisi hover-lift).
- Count-up dilewati untuk angka majemuk ("48 / 30") agar tidak menipu (suffix diam).
- Fetch wrapper hanya men-toast path `/api/*` — tidak menyentuh fetch Leaflet (OSM tiles).
- Tidak ditambahkan dependensi apa pun (tetap vanilla; Leaflet CDN tetap satu-satunya).
- Bar porsi vendor: track kini memenuhi lebar kolom (asli: 120px tengah-tengah akibat
  aturan `.bar` global) — perubahan visual kecil, sengaja dipertahankan (lebih responsif).
