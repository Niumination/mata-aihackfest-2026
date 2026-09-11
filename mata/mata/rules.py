"""Rule engine MATA — deteksi anomali PBJ.

PRINSIP: TRANSPARAN & BISA DIAUDIT.
Semua aturan = aturan deterministik dengan ambang yang dipajang (config.json).
LLM hanya menjelaskan, tidak memutuskan. (Rumus & ambang dipublikasikan di artikel.)
"""
import datetime
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict


@dataclass
class Flag:
    rule_id: str
    title: str
    severity: str            # "tinggi" | "sedang" | "rendah"
    record_ids: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)   # baris bukti (manusiawi)
    explanation: str = ""    # narasi (template/LLM)
    recommendation: str = ""

    def to_dict(self):
        return asdict(self)


def _d(value):
    return datetime.datetime.strptime(value, "%Y-%m-%d").date()


# ---------------------------------------------------------------------------
def rule_d1_harga_dipasar(records, t):
    """D1 — Nilai proyek jauh di atas harga referensi (katalog/peer)."""
    flags = []
    for r in records:
        ref = r.get("ref_price")
        if not ref or r["value"] < t["d1_min_value"]:
            continue
        dev = (r["value"] - ref) / ref
        if dev >= t["d1_deviation"]:
            sev = "tinggi" if dev >= 1.0 else "sedang"
            flags.append(Flag(
                rule_id="D1",
                title="Harga di atas referensi pasar",
                severity=sev,
                record_ids=[r["id"]],
                metrics={"nilai": r["value"], "referensi": ref, "deviasi": round(dev, 3)},
                evidence=[
                    f"{r['project']} ({r['agency']}) senilai {r['value']:,.0f} rupiah",
                    f"Referensi harga (katalog/peer): {ref:,.0f} rupiah",
                    f"Deviasi: +{dev*100:.0f}% dari referensi",
                ],
            ))
    return flags


def rule_d2_konsentrasi_vendor(records, t):
    """D2 — Satu penyedia mendominasi (banyak proyek / porsi nilai besar)."""
    with_vendor = [r for r in records if r.get("vendor")]
    if not with_vendor:
        return []
    total = sum(r["value"] for r in with_vendor)
    by_vendor = defaultdict(lambda: {"n": 0, "value": 0.0, "projects": []})
    for r in with_vendor:
        d = by_vendor[r["vendor"]]
        d["n"] += 1
        d["value"] += r["value"]
        d["projects"].append(r)
    flags = []
    for vendor, d in sorted(by_vendor.items(), key=lambda kv: -kv[1]["value"]):
        share = d["value"] / total if total else 0
        if d["n"] >= t["d2_min_projects"] and share >= t["d2_min_share"]:
            top = sorted(d["projects"], key=lambda x: -x["value"])[:5]
            flags.append(Flag(
                rule_id="D2",
                title="Konsentrasi penyedia (satu vendor menang berulang)",
                severity="tinggi" if share >= 0.5 else "sedang",
                record_ids=[r["id"] for r in d["projects"]],
                metrics={
                    "vendor": vendor,
                    "jumlah_proyek": d["n"],
                    "total_nilai": d["value"],
                    "porsi": round(share, 3),
                    "total_pengadaan": total,
                },
                evidence=[
                    f"{vendor} memenangkan {d['n']} dari {len(with_vendor)} proyek",
                    f"Porsi nilai: {round(share,3)*100:.1f}% dari total pengadaan yang terdata",
                    "Proyek terbesar: " + "; ".join(
                        f"{x['project']} ({x['value']:,.0f})" for x in top
                    ),
                ],
            ))
    return flags


def rule_d3_keroyokan_akhir_tahun(records, t, fiscal_year):
    """D3 — Lonjakan kontrak besar di 10 hari terakhir tahun anggaran."""
    if not records:
        return []
    last_day = datetime.date(fiscal_year, 12, 31)
    start = last_day - datetime.timedelta(days=t["d3_window_days"] - 1)
    window = [
        r for r in records
        if r.get("date_signed")
        and start <= _d(r["date_signed"]) <= last_day
        and r["value"] >= t["d3_min_value"]
    ]
    if len(window) < 3:
        return []
    monthly = defaultdict(float)
    for r in records:
        if r.get("date_signed") and r["value"] >= t["d3_min_value"]:
            monthly[r["date_signed"][:7]] += r["value"]
    other = sorted(v for m, v in monthly.items() if not m.endswith("-12"))
    if not other:
        return []
    med = other[len(other) // 2]
    total_window = sum(r["value"] for r in window)
    if med > 0 and total_window >= t["d3_ratio"] * med:
        flags = [Flag(
            rule_id="D3",
            title="Keroyokan akhir tahun (lonjakan kontrak besar Des)",
            severity="sedang",
            record_ids=[r["id"] for r in window],
            metrics={
                "jumlah_kontrak": len(window),
                "total_jendela": total_window,
                "median_bulan_lain": med,
                "rasio": round(total_window / med, 2),
                "jendela": f"{start.isoformat()} s.d. {last_day.isoformat()}",
            },
            evidence=[
                f"{len(window)} kontrak >= {t['d3_min_value']/1e9:.0f} M ditandatangani {start.day}–{last_day.day} Des",
                f"Total jendela: {total_window:,.0f} vs median bulan lain {med:,.0f}",
                f"Rasio: {total_window/med:.1f}x (ambang {t['d3_ratio']}x)",
            ],
        )]
        return flags
    return []


def rule_d4_vendor_kecil_menang_besar(records, t):
    """D4 — Penyedia dengan track record kecil/pendek menang kontrak besar."""
    flags = []
    by_vendor = defaultdict(list)
    for r in records:
        if r.get("vendor"):
            by_vendor[r["vendor"]].append(r)
    for r in records:
        if not r.get("vendor") or r["value"] < t["d4_big_contract"]:
            continue
        hist = [x for x in by_vendor[r["vendor"]] if x["id"] != r["id"]]
        if not hist:
            continue
        if (
            len(hist) <= t["d4_max_history_projects"]
            and max(x["value"] for x in hist) < t["d4_max_history_value"]
        ):
            flags.append(Flag(
                rule_id="D4",
                title="Vendor track-record kecil menang kontrak besar",
                severity="tinggi",
                record_ids=[r["id"]] + [x["id"] for x in hist],
                metrics={
                    "vendor": r["vendor"],
                    "kontrak_besar": r["value"],
                    "riwayat": [(x["project"], x["value"]) for x in hist],
                },
                evidence=[
                    f"{r['vendor']} memenangkan {r['project']} senilai {r['value']:,.0f}",
                    f"Riwayat sebelumnya hanya {len(hist)} proyek, terbesar "
                    f"{max(x['value'] for x in hist):,.0f}",
                ],
            ))
    return flags


def rule_d6_pola_nilai(records, t):
    """D6 — Nilai identik berulang antar proyek (indikasi copy-paste anggaran)."""
    vals = Counter(r["value"] for r in records)
    repeats = [(v, c) for v, c in vals.items() if c >= t["d6_repeat_amounts"]]
    near_round = {v for v in vals if v % 1000 == 999}
    targets = [v for v, _ in repeats if v in near_round or v % 1_000_000_000 == 0] or \
              [v for v, _ in repeats]
    flags = []
    for v in targets:
        rs = [r for r in records if r["value"] == v]
        flags.append(Flag(
            rule_id="D6",
            title="Pola nilai identik antar proyek",
            severity="rendah",
            record_ids=[r["id"] for r in rs],
            metrics={"nilai": v, "jumlah": len(rs)},
            evidence=[
                f"Nilai {v:,.0f} muncul {len(rs)}x pada proyek berbeda:",
                * [f"- {r['project']} ({r['agency']})" for r in rs],
            ],
        ))
    return flags


def run_rules(records, thresholds, fiscal_year):
    """Jalankan semua aturan; kembalikan daftar Flag (diurutkan severity)."""
    flags = []
    flags += rule_d1_harga_dipasar(records, thresholds)
    flags += rule_d2_konsentrasi_vendor(records, thresholds)
    flags += rule_d3_keroyokan_akhir_tahun(records, thresholds, fiscal_year)
    flags += rule_d4_vendor_kecil_menang_besar(records, thresholds)
    flags += rule_d6_pola_nilai(records, thresholds)
    order = {"tinggi": 0, "sedang": 1, "rendah": 2}
    flags.sort(key=lambda f: (order.get(f.severity, 9), f.rule_id))
    return flags
