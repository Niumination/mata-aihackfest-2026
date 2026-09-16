# SNAPSHOT STATIS + DEPLOY CADANGAN (Netlify/Vercel) · 14 Sep 2026
> Konteks: VM Batch 3 mati **15 Sep 23.59 WIB** → domain `mata.niumination.web.id` ikut mati.
> Solusi 2 lapis: (1) **snapshot statis** self-commit ke repo (bukti utk juri), (2) **deploy cadangan**
> ke Netlify/Vercel + re-point DNS (opsional, kalau mau domain tetap hidup).

## 1. Snapshot statis — SUDAH DIBUAT & DIVERIFIKASI

File: **`snapshot/dashboard-live-2026-09-14.html`** (single-file, ±1.8 MB, self-contained).

Cara kerja:
- Halaman live `https://mata.niumination.web.id/` di-capture utuh (server-rendered).
- 9 endpoint `/api/*` + `records.csv` (296 KB) di-capture dan disuntik sebagai **stub `fetch`**
  → seluruh seksi interaktif tetap jalan tanpa backend: analisis top-10, simulator, peta iklim,
  kartu INAPROC/RUP/SPSE, SAPA, health, pengunjung.
- Tombol **UNDUH CSV** & link JSON flags → `data:` URI (bisa diunduh dari file statis).
- Banner sticky di atas: "▣ STATIC SNAPSHOT — ditangkap {ts} … data beku …".
- `<title>` diberi prefix `[SNAPSHOT]`.
- Script tracking Cloudflare di buang (tidak relevan di hosting lain).
- Chat & locate → respons jujur "static mode".

Diverifikasi (chromium headless, 14 Sep): banner ✅, 14 flag ✅, D4 ANANDA ✅,
analisis ter-render ✅, link CSV data-URI (395 KB) ✅, **0 JS runtime error** ✅.

**Buat ulang** (mis. utk capture data final malam 15 Sep):
```bash
python3 scripts/make_snapshot.py --out snapshot/dashboard-live-2026-09-15.html
# default base = https://mata.niumination.web.id ; --base http://127.0.0.1:80 utk dari VPS
```
Python 3 stdlib saja (urllib/json/base64) — bisa jalan di VPS, laptop, atau sandbox.

**Commit ke repo** (agar juri bisa buka langsung dari GitHub walau domain mati):
```bash
git add snapshot/dashboard-live-2026-09-14.html
git commit -m "feat(snapshot): arsip statis dashboard live (self-contained, utk pasca-VM)"
git push
```

## 3. Status pasca-VM mati (16 Sep 2026)

VM Batch 3 **dinonaktifkan 15 Sep 23.59 WIB** per instruksi panitia. Status setelah shutdown:

| Item | Status | Catatan |
|------|--------|---------|
| Dashboard live `mata.niumination.web.id` | ❌ DOWN | Domain mati bersamaan VM (A record VPS lama, tidak diubah) |
| GitHub Pages `watchdog-mata.niumination.web.id` | ✅ LIVE 16 Sep | CNAME → `niumination.github.io`, branch `gh-pages`, `built`, HTTP 200 verifikasi 16 Sep |
| VPS SSH | ❌ OFFLINE | Akses Kitty tidak mungkin |
| Video demo YouTube | ✅ PUBLIK | https://youtu.be/dbw5KVA75q8 (16 Sep, QC PASS) |
| Artikel LinkedIn | ✅ TAYANG | 14 Sep, akses publik |
| Repo GitHub | ✅ PUBLIC | `main` commit `f8aa1fe` (dokumentasi final) |
| Form Google Form | ✅ SUBMIT | 16 Sep 00:19 WIB, konfirmasi tersimpan |
| Snapshot statis | ✅ Di repo | `snapshot/dashboard-live-2026-09-14.html` |
| Backup VPS | ✅ Di submodule media | `mata-final-backup-20260915.tgz` (36 MB) |
| Sesi percakapan VPS | ✅ Di repo | `aihackfest/00-VPShermes-semua-sesi.md` |

**Untuk juri**: Seluruh bukti kompetisi tersimpan permanen di GitHub + YouTube + LinkedIn. Domain mati tidak memengaruhi validitas submission. Snapshot statis dan backup VPS tersedia sebagai jaring pengaman jika diperlukan verifikasi teknis.

## 2. Deploy cadangan ke Netlify ATAU Vercel (opsional, kalau mau domain tetap hidup)

Kedua platform menerima **folder berisi 1 file HTML** tanpa konfigurasi apa pun.

### Netlify (paling cepat)
1. Buka https://app.netlify.com/drop
2. Drag-drop **folder `snapshot/`** (bukan file-nya, agar URL-nya `/dashboard-live-...`).
   - Opsional: buat file `snapshot/index.html` = salinan snapshot, supaya root domain langsung
     menampilkan dashboard.
3. Netlify kasih URL `https://<random>.netlify.app`.
4. (Opsional) claim custom domain → arahkan `mata.niumination.web.id` (via CNAME di panel DNS).

### Vercel
```bash
cd snapshot && npx vercel --prod
```
- Framework preset: **Other** (static). Build command: kosong. Output dir: `.`.
- Dapat URL `https://<random>.vercel.app`.
- Custom domain: `vercel domains add mata.niumination.web.id` → ikuti CNAME yang diberikan.

### Catatan teknis
- Snapshot memakai **font Google (CDN)** + **Leaflet (unpkg CDN)** → tetap butuh internet saat
  dibuka (sama seperti situs aslinya). Offline total: font fallback ke system, peta tak muat,
  tapi konten teks/angka/CSV tetap tampil.
- Tidak ada backend → chat "Tanya MATA" akan menampilkan pesan static mode (jujur, bukan error).
- Setelah deploy, **tes**: buka URL deploy tanpa login, pastikan banner SNAPSHOT + angka muncul.

## 3. Re-point DNS (HANYA setelah VM benar-benar mati, 16 Sep)

> ⚠️ Jangan re-point sebelum 15 Sep 23:59 — dashboard live masih dibutuhkan utk video &
> screenshot. Setelah VM mati, domain akan error (origin down) → baru di-switch.

1. Di panel DNS (Cloudflare / IDwebhost, record `mata`):
   - Ganti record A → **CNAME** ke hostname Netlify/Vercel (mis. `mata-aihackfest-2026.netlify.app`).
   - Proxy (Cloudflare) boleh ON.
2. Tunggu propagasi (±5–15 mnt) → `https://mata.niumination.web.id` kini menyajikan snapshot statis.
3. (Opsional) di snapshot, banner sudah menjelaskan "sistem live berakhir" → juri paham konteks.

## 4. Urutan final (14–16 Sep)

| Waktu | Aksi |
|---|---|
| 14 Sep (sekarang) | Snapshot dibuat ✅. Commit snapshot ke repo (VPS/laptop) — bukti permanen. |
| 14–15 Sep | Rekam video (aquadan VPS wajib sebelum VM mati) → YouTube PUBLIK. |
| 15 Sep pre-23:59 | 4 screenshot produksi → submodule media. **Submit form.** |
| 15 Sep 23.59 | VM mati. |
| **16 Sep 00:00+** | **VM OFFLINE — domain `mata.niumination.web.id` DOWN.** ✅ Semua yang abadi sudah tersimpan: video (YouTube PUBLIK), artikel (LinkedIn), repo (GitHub), form (Google Form submit). Snapshot statis + backup VPS `mata-final-backup-20260915.tgz` (36 MB, submodule media) sebagai jaring pengaman. Dokumentasi sesi percakapan Hermes VPS: `aihackfest/00-VPShermes-semua-sesi.md` (360 KB, 10.481 baris, 28 sesi 11–15 Sep 2026). |
| 16 Sep (opsional) | Deploy snapshot ke Netlify/Vercel + re-point DNS → domain tetap hidup (menyajikan snapshot). |

## 5. GitHub Pages AKTIF (16 Sep 2026, ~02:00 WIB) — EKSEKUSI

Dipilih GitHub Pages (bukan Netlify/Vercel) — gratis, tanpa deploy manual, branch `gh-pages` sebagai source.

- Branch `gh-pages`: hanya `snapshot/` + `index.html` (redirect root → snapshot final) + `CNAME`.
- Custom domain: `watchdog-mata.niumination.web.id` (subdomain baru, A record lama `mata.*` tidak disentuh).
- DNS Cloudflare: `watchdog-mata` CNAME → `niumination.github.io`, Proxied ON.
- Pages status: `built`, cname terdaftar, `https_enforced: false` (via Cloudflare proxy).
- Verifikasi 16 Sep (curl): `/` → 200 (322 B redirect), `/snapshot/dashboard-live-2026-09-15-final.html` → 200 (1.816.083 B).
- URL live:
  - https://watchdog-mata.niumination.web.id/ → redirect ke snapshot
  - https://watchdog-mata.niumination.web.id/snapshot/dashboard-live-2026-09-15-final.html → dashboard statis langsung
- Fallback tetap: https://niumination.github.io/mata-aihackfest-2026/snapshot/dashboard-live-2026-09-15-final.html

## 6. Snapshot dari branch `dev` (16 Sep 2026, ~11:30 WIB) — EKSEKUSI

Diminta owner: snapshot statis versi **branch dev** (UI lebih baru, `web.py` +961 baris vs `main`).

Metode (VPS mati → dashboard dev dijalankan lokal):
1. `git worktree add /tmp/mata-dev-wt origin/dev` (main tak terganggu).
2. Data produksi final dipulihkan dari backup VPS: `assets/media/mata-final-backup-20260915.tgz`
   = **nested tar 2 lapis** (ekstrak 2×) → `root/Arck4li-AIHackfest/mata/data/`.
   Disalin: `mata.db` (1,73 MB), `status.json`, `flags_latest.json`, `kutipan.json`,
   `realisasi_20{25,26}_full.json`, `rup_20{25,26}_full.json`, cache iklim/inaproc/sapa/spse.
3. `python3 mata/run.py web -p 8181` → 10/10 endpoint HTTP 200
   (`/api/status|flags|analisis|health|iklim|inaproc|sapa|spse|visitors|records.csv`).
4. `python3 scripts/make_snapshot.py --base http://127.0.0.1:8181 --out snapshot/dashboard-dev-2026-09-16.html`.
5. Label banner dipatch: `http://127.0.0.1:8181` → `dashboard branch dev (build lokal, b20d0b8)`.

Hasil: **`snapshot/dashboard-dev-2026-09-16.html`** — 3.069.971 B (2.140 baris ter-commit).

QC (Playwright Chromium headless, DOM penuh):
stub `fetch /api/status` → ok, `n_records` 662, `n_flags` 14, `n_flags_tinggi` 3;
`/api/flags` 14 item (3 tinggi, vendor pertama CV. FIKRI BROTHER'S); `/api/analisis` ok;
ANANDA ada di DOM; 8 tabel; 35 seksi; **0 JS error / 0 console error** → PASS.

Live: https://watchdog-mata.niumination.web.id/snapshot/dashboard-dev-2026-09-16.html
(HTTP 200, 3.069.971 B, verifikasi headless ulang PASS).

Commit: `main` `03cdefd` · `gh-pages` `e4aadd3`.
