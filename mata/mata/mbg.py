"""MATA — Filter paket MBG (Makan Bergizi Gratis) dari data LIVE.

MBG dijalankan BGN (Badan Gizi Nasional) via SPPG/dapur satuan pelayanan.
Paket terkait muncul di INAPROC/SIRUP dengan kata kunci pada `nama_paket`
(mis. "makan bergizi", "SPPG", "dapur", "bahan pangan").

Fungsi: filter client-side atas record mentah INAPROC (dict API) ATAU
record ternormalisasi MATA (punya key `project`). Pencocokan case-insensitive,
substring — sengaja longgar (recall > precision); hasil filter TETAP melewati
rule engine D1–D6 seperti record lain, bukan vonis.
"""

MBG_KEYWORDS = [
    "makan bergizi",
    "makan gratis",
    "mbg",
    "sppg",
    "satuan pelayanan pemenuhan gizi",
    "pemenuhan gizi",
    "dapur",
    "bahan pangan",
    "paket makanan",
    "jasa boga",
    "katering",
    "catering",
    "gizi nasional",
    "bgn",
]


def is_mbg_text(text):
    """True jika teks mengandung salah satu kata kunci MBG."""
    t = (text or "").lower()
    return any(k in t for k in MBG_KEYWORDS)


def match_keyword(text, keyword):
    """True jika teks mengandung keyword (case-insensitive)."""
    return (keyword or "").lower() in (text or "").lower()


def filter_records(raw_records, keywords=None):
    """Filter iterable dict mentah INAPROC (`nama_paket`) atau
    record MATA (`project`). Return (matched, total)."""
    keys = [k.lower() for k in (keywords or MBG_KEYWORDS)]
    matched = []
    total = 0
    for r in raw_records:
        total += 1
        name = r.get("nama_paket", r.get("project", "") or "")
        if any(k in (name or "").lower() for k in keys):
            matched.append(r)
    return matched, total
