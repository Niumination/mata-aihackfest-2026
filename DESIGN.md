# DESIGN.md — MATA live web

Dunia visual committed ("living codex"): terang, arsip, tenang. Mode: **Operate**.
Bahasa UI: Indonesia. Etik: indikasi, bukan vonis.

## Token

- `--cream:#f6f1e7` latar · `--ink:#241d17` teks · `--ink-2:#171310` panel gelap
- `--ember:#c8501a` aksi/aksen · `--ember-soft:#f0a35e` sorot di gelap
- Severity: tinggi `#b3261e` · sedang `#96690a` · rendah `#35703c`
  (satu-sumber: CSS `--sev-*` = Python `SEV_STYLE` — graph, label, titik legend sama)
- Live `#0b6bcb` · radius panel 20px · kartu 16px · pil penuh (kontrol kecil saja)
- Font: Instrument Serif (display) · Inter (tubuh) · JetBrains Mono (angka/data saja)

### Skala (tambah v3, 12 Sep 2026)

- Spasi: `--s1…--s7` = 4/8/12/16/24/32/40px — pakai token, jangan angka ad hoc.
- Radius: `--r-sm 10` · `--r-md 12` · `--r-lg 16` · `--r-xl 20` · `--r-xxl 22`px.
- Bayangan: `--sh-1` halus (kartu) · `--sh-2` angkat (hover) · `--sh-3` hero/toast.
- Durasi: `--dur-1 140ms` mikro · `--dur-2 220ms` transisi · `--dur-3 420ms` muncul ·
  `--dur-4 900ms` bar. Easing: `cubic-bezier(.16,1,.3,1)`.
- Kontras: teks kecil `--ink-soft #4a4238` (≥4.5:1 di cream); teks tipis di gelap
  tidak boleh di bawah opacity 0.65.

## Pola

Hero ink (headline + 3 ubin + pil) → ticker → grid arsip|peta|pembaca →
indikasi → konsentrasi → paket + konteks → pengunjung + peta → kaki.
Kicker mono + nomor seksi adalah identitas template — dipertahankan.

## Aturan

- Angka klikabel wajib ke sumber real; demo = tag abu-abu + tooltip.
- Batas data tertulis di samping data (agregat vs per paket).
- IP tak disimpan (hash 8 char); lokasi hanya via izin eksplisit (UU PDP).
- Motion: tenang. Satu momen besar (boot); sisanya mikro-interaksi
  (hover-lift, transisi 140–420ms, count-up, reveal saat scroll, pulse LIVE).
  `prefers-reduced-motion` wajib dimatikan semua.
- Feedback: sukses/gagal selalu via toast `#toasts` (jangan innerHTML ke panel).
- Loading: `.skeleton` shimmer (max 2,5 dtk) — bukan teks "memuat" yang melompat.
- Mobile: target tap ≥40px · breakpoint 640/768/1100 · safe-area iOS ·
  chatfab naik otomatis saat banner lokasi tampil (`body.loc-open`).
- Fokus keyboard terlihat.
