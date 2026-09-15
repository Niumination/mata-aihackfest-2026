# Master Design Prompt — MATA (untuk designarena.ai / AI design tools)

> **Cara pakai:** salin seluruh isi blok di bawah sebagai prompt utama.
> Jika tool meminta follow-up, gunakan instruksi cadangan di bagian akhir.
> Konteks: MATA = dashboard publik watchdog akuntabilitas pengadaan
> Kabupaten Aceh Tengah (live: mata.niumination.web.id). Konten BAHASA INDONESIA.

---

## PROMPT MASTER (salin mulai baris ini)

```
Design a public-facing web dashboard called "MATA" (Indonesian: "penjaga
uang publik" — guardian of public money). MATA is a 24/7 AI-agent watchdog
for government procurement (PBJ) of Kabupaten Aceh Tengah, Indonesia. It
collects real public procurement data, runs transparent deterministic
rules (D1–D6), and publishes verifiable "indikasi" (indicators — NOT
verdicts) with per-package evidence. Audience: journalists, civil society,
oversight institutions (APIP/BPKP), and ordinary citizens.

DESIGN GOAL: make dense procurement data feel calm, credible, and
public-service — like a well-made investigative-news data page, NOT a
crypto/fintech neon dashboard, NOT a generic government portal, NOT a
template. It must feel hand-built by people, for the public.

STYLE & TONE
- Mood: quiet authority, factual, trustworthy. Think "data journalism
  meets civic infrastructure".
- Palette: near-neutral base (warm off-white or deep ink — pick ONE theme,
  default to a dark "ink" theme with a single warm EMBER-red accent
  reserved strictly for risk/signal highlights); muted secondary accent
  (slate/teal) for links and secondary data. No gradients, no glassmorphism,
  no neon.
- Type: a readable grotesque or humanist sans for UI (e.g. Instrument Sans /
  Public Sans family), a monospace (e.g. JetBrains Mono / IBM Plex Mono)
  for ALL numbers, codes, and IDs. Numbers are the hero: large, tabular,
  right-aligned, with compact Indonesian formatting (Rp 134,5 M; 26,6%).
- Density: high but breathing — clear section rhythm, generous whitespace
  between sections, tight rows inside tables. 8-pt spacing grid.
- Iconography: minimal line icons, 1.5px stroke, monochrome + one accent.

MANDATORY UI COMPONENTS (show each in the mockup)
1. Hero header: wordmark "MATA" + one-line mission ("Penjaga uang publik —
   indikasi berbasis data, bukan vonis") + live status badge "● MODE: LIVE"
   (green dot) + a scrolling ticker strip of indicator headlines
   ("[D2 · TINGGI] Konsentrasi penyedia — CV. F. 8,4% nilai total …").
2. Indicator cards (section 03 "Indikasi — klik untuk bukti & langkah
   lanjut"): expandable <details>-style cards; each shows rule tag [D4],
   severity chip (TINGGI = ember-red, SEDANG = amber, RENDAH = neutral),
   title, and on expand: bulleted evidence with real numbers, record IDs
   (monospace), "Penjelasan" and "Langkah lanjut" lines. Filter buttons:
   Semua / Tinggi / Sedang / Rendah.
3. Data table "Top 10 Penyedia — TA2026": columns # | Penyedia | Paket |
   Nilai | Share%, monospace numbers, subtle row hover, top-3 rows
   emphasized.
4. "RENCANA (RUP) vs REALISASI PER SKPD — TA2026" table: SKPD | Rencana |
   Realisasi | Rate | Sisa; rows with rate < 50% highlighted in ember; a
   summary line above: "Rencana Rp 505,4 M · Realisasi Rp 134,5 M ·
   tercapai 26,6%".
5. "Tanya MATA" chatbot: compact conversation panel (visitor question,
   grounded answer), with a note "Hanya menjawab dari data MATA".
6. Footer strip: attribution ("Sumber: INAPROC · SPSE LKPP · SAPA — data
   publik, tanpa login"), "indikasi, bukan vonis hukum", kanal pelaporan
   (LAPOR! · Ombudsman · KPK · APIP), license note.

REAL DATA TO RENDER IN THE MOCKUP (use these exact numbers)
- 662 paket realisasi TA2026 · Rp 134,5 M · 170 penyedia
- 14 indikasi (3 tingkat tinggi)
- Top indicators: "[D2 · TINGGI] CV. FIKRI BROTHER'S — 3 paket, 10,89 M
  rupiah (8,4% dari nilai total)"; "[D4 · TINGGI] ANANDA RAFFAN JAYA —
  riwayat 1 proyek Rp229 jt, menang kontrak Rp3,12 M"
- RUP vs realisasi: Rp 505,4 M rencana → Rp 134,5 M realisasi (26,6%),
  55 SKPD; example low row: "Dinas Pertanian — Rencana Rp 18,2 M ·
  Realisasi Rp 4,1 M · 22,5%"
- Ticker sample: "[D6 · RENDAH] Nilai Rp94.350.000 muncul 3x pada proyek
  berbeda"

LAYOUT
- Desktop 1440px primary (the mockup), mobile 390px secondary.
- Single-column vertical flow of numbered sections (01 Bukti live — data
  nyata · 02 Jelajah arsip · 03 Indikasi · 04 Konsentrasi & musim anggaran ·
  05 Paket & konteks · 06 Pengunjung live); sticky top bar with section
  anchors. No sidebar clutter on mobile.
- Accessible: WCAG AA contrast, visible focus states, ≥16px body text,
  status conveyed by more than color (chips + text labels).

DELIVERABLES
1. One full dashboard page (all 6 components, real numbers above).
2. Three section variants: (a) indicator card collapsed + expanded,
   (b) RUP-vs-realization table close-up, (c) empty/zero state
   ("Belum ada indikasi hari ini" — calm, not celebratory).
3. Design tokens: color hex values, type scale, spacing, border radii,
   shadows (max 1 level), component states.
4. Brief rationale (≤150 words) mapping design decisions to "credible
   public watchdog" and to judge criteria (clarity of data, accessibility,
   originality, civic tone).

DO NOT: dashboard-within-dashboard (no fake browser frames), no
placeholder lorem ipsum (use the real Indonesian text/numbers given), no
dark-mode/light-mode both (pick the ink-dark default), no stock photos,
no emoji as design elements (the dashboard uses a few semantic emoji in
section kickers only: 🎯 📋 🏛  🔎 — keep them small and functional).
```

---

## INSTRUKSI CADANGAN (follow-up)

- **Kalau hasilnya terlalu "korporat/SaaS":** "Remove all SaaS marketing
  patterns (hero CTA buttons, feature cards, testimonial strips). This is a
  public data service, not a product landing page. Increase table density,
  reduce ornament to zero."
- **Kalau terlalu "suram":** "Keep the ink theme but raise surface
  contrast one step and let the ember accent appear slightly more often on
  section kickers. Still no gradients."
- **Kalau angka tidak monospace:** "ALL numeric values, percentages,
  rupiah amounts, and record IDs must use the monospace face, tabular
  figures, right-aligned in tables."
- **Kalau diminta nama font:** UI = Instrument Sans (atau Public Sans);
  mono = JetBrains Mono; Arabic (jika kutipan) = Amiri.
- **Konsistensi dengan produksi:** komponen final harus bisa dipetakan 1:1
  ke panel dashboard live (`mata.niumination.web.id`) — section numbers 01–06,
  badge MODE: LIVE, ticker, kartu [D#] — jangan inventarisasi ulang.
