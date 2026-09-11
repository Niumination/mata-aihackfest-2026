# DESIGN.md — MATA live web

Dunia visual committed ("living codex"): terang, arsip, tenang. Mode: **Operate**.
Bahasa UI: Indonesia. Etik: indikasi, bukan vonis.

## Token

- `--cream:#f6f1e7` latar · `--ink:#241d17` teks · `--ink-2:#171310` panel gelap
- `--ember:#c8501a` aksi/aksen · `--ember-soft:#f0a35e` sorot di gelap
- Severity: tinggi `#b3261e` · sedang `#96690a` · rendah `#35703c`
- Live `#0b6bcb` · radius panel 20px · kartu 16px · pil penuh (kontrol kecil saja)
- Font: Instrument Serif (display) · Inter (tubuh) · JetBrains Mono (angka/data saja)

## Pola

Hero ink (headline + 3 ubin + pil) → ticker → grid arsip|peta|pembaca →
indikasi → konsentrasi → paket + konteks → pengunjung + peta → kaki.
Kicker mono + nomor seksi adalah identitas template — dipertahankan.

## Aturan

- Angka klikabel wajib ke sumber real; demo = tag abu-abu + tooltip.
- Batas data tertulis di samping data (agregat vs per paket).
- IP tak disimpan (hash 8 char); lokasi hanya via izin eksplisit (UU PDP).
- Motion: satu momen (boot); sisanya statis. Fokus keyboard terlihat.
