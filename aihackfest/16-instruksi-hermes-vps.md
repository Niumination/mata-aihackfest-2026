# 16 — Instruksi untuk Hermes VPS (12 Sep 2026)

> **Misi (3 langkah, urut):** (1) terapkan commit baru (kode SAPA sudah ditulis & dites),
> (2) jalankan uji P0 yang menentukan arsitektur inti PBJ, (3) laporkan hasil persis.
> Referensi lengkap: `aihackfest/15-jalur-sumber-data-legal.md`.

## 0. Terapkan (setelah repo di-push)

```bash
cd /root/Arck4li-AIHackfest/mata
git pull
git log --oneline -1   # commit baru (SAPA) harus muncul
git status --short     # harus bersih
```
File baru/ubah: `mata/sapa_pub.py` (baru), `mata/web.py` (route `/api/sapa` + panel),
`_test_sapa.py` (baru), `aihackfest/15-*.md`, `aihackfest/16-*.md`.

## 1. Uji P0 — jalankan PASTE ini (menentukan inti PBJ)

```bash
# ── A) Satu Data eProc: apakah IP VPS lolos? ──
curl -s -o /tmp/ml.json -w "MasterLPSE: HTTP %{http_code} (%{size_download}B)\n" \
  --max-time 20 "https://isb.lkpp.go.id/isb-2/api/satudata/MasterLPSE"
head -c 300 /tmp/ml.json; echo
python3 - <<'EOF'
import json
try:
    d = json.load(open('/tmp/ml.json'))
    rows = d if isinstance(d, list) else d.get('data', d.get('result', []))
    for r in rows:
        if 'aceh tengah' in json.dumps(r, ensure_ascii=False).lower():
            print(json.dumps(r, ensure_ascii=False))
except Exception as e:
    print('parse:', e)
EOF

# ── B) SPSE sesi anonim: apakah /dt/lelang membuka? ──
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
B='https://spse.inaproc.id/acehtengahkab'
curl -s -c /tmp/cj.txt -H "User-Agent: $UA" "$B/lelang" -o /dev/null
echo "cookie: $(grep -o 'SPSE_SESSION[^ ]*' /tmp/cj.txt | head -1 | cut -c1-40)…"
curl -s -b /tmp/cj.txt -X POST "$B/dt/lelang" \
  -H "User-Agent: $UA" -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: $B/lelang" -H "Sec-Fetch-Mode: cors" -H "Sec-Fetch-Site: same-origin" \
  --data "draw=1&start=0&length=5&columns[0][data]=kode_paket&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=nama_paket&columns[1][search][value]=&columns[1][search][regex]=false&tahun=2026" \
  -w "\nPOST /dt/lelang: HTTP %{http_code}\n" | head -c 600
```

## 2. Terapkan SAPA (sumber konteks resmi — kode sudah teruji)

```bash
cd /root/Arck4li-AIHackfest/mata
python3 _test_sapa.py    # harus: ✅ SEMUA LULUS (termasuk bagian LIVE)
# restart servis MATA sesuai cara yang sudah dipakai, lalu:
curl -s localhost:8080/api/sapa | python3 -m json.tool | head -25
```
Ekspektasi: `status: "live"`, `count` ≈ 2067, `n_opd: 38`,
`baseline.apbd_realisasi` ≈ 1.3e12 (Rp 1,32 T). Dashboard: panel baru
**"📊 INDIKATOR RESMI KABUPATEN — API SAPA"** tepat di bawah panel SPSE.

## 3. Laporan — balas dengan format ini, PERSIS (jangan dirangkum)

```
A: HTTP <kode> | <300 char pertama /tmp/ml.json> | baris "aceh tengah": <json / "tidak ada" / "A=403">
B: cookie <…> | POST /dt/lelang: HTTP <kode> | <300 char pertama respons>
S: status <…> | count <…> | n_opd <…> | apbd <…>
```
Jika ada error: kutip **verbatim** (HTTP code + pesan utuh). Maksimal 2× retry per
komando. **Jangan** mendiagnosis, menduga, atau mencoba alternatif lain (proxy, browser,
bypass, login) — cukup laporkan, keputusan arsitektur ada di pihak saya.

## Garis merah
- Hanya ubah/jalankan yang tercantum di atas. **Jangan** sentuh `config.json`.
- Tanpa bypass blokir, tanpa CAPTCHA/login, tanpa volume berlebihan.
- Atribusi sumber di panel SAPA sudah ada di kode — jangan dihapus.
- Urutan: **1 (A dulu, lalu B) → 2 → 3**.
