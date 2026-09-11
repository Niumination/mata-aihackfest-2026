"""Output dunia nyata MATA: dossier PDF (fpdf2, tanpa dependensi system berat),
draft laporan resmi (txt), dan ringkasan publik (md).
"""
import os
import glob
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/DejaVu Sans.ttf",
    ]
    candidates += glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True)
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def _pdf():
    from fpdf import FPDF

    pdf = FPDF()
    font = _find_font()
    if font:
        pdf.add_font("DejaVu", "", font)
        pdf.set_font("DejaVu", size=10)
        pdf._unicode = True
    else:  # core font (latin-1) — sanitasi text
        pdf.set_font("Helvetica", size=10)
        pdf._unicode = False
    return pdf


def _t(pdf, s):
    if not getattr(pdf, "_unicode", True):
        s = s.encode("latin-1", "replace").decode("latin-1")
    return s


def rupiah(v):
    return f"Rp {int(v):,}".replace(",", ".")


def _hr(pdf):
    y = pdf.get_y()
    pdf.set_draw_color(160, 160, 160)
    pdf.line(10, y, 200, y)
    pdf.ln(3)


def generate_pdf(report, flags, records, cfg, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    pdf = _pdf()
    today = datetime.date.today().isoformat()

    # ---- Halaman 1: sampul & ringkasan ----
    pdf.add_page()
    pdf.set_font_size(18)
    pdf.set_text_color(20, 20, 60)
    pdf.cell(0, 10, _t(pdf, "MATA"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_size(12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 7, _t(pdf, "Dossier Indikasi Anomali Pengadaan Barang/Jasa Pemerintah"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, _t(pdf, "Data publik · Deteksi berbasis aturan · Bukan vonis hukum"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font_size(10)
    pdf.set_text_color(30, 30, 30)
    info = [
        ("Wilayah", cfg.get("region", "-")),
        ("Tahun anggaran", str(cfg.get("fiscal_year", "-"))),
        ("Tanggal laporan", today),
        ("Jumlah pengumuman dipindai", str(report.get("n_records", 0))),
        ("Indikasi terdeteksi", str(len(flags)) +
         f" ({sum(1 for f in flags if f.severity == 'tinggi')} tingkat tinggi)"),
        ("Sumber data", ", ".join(sorted({r.get('source', '-') for r in records}))),
    ]
    for k, v in info:
        pdf.cell(60, 6, _t(pdf, k + ":"))
        pdf.cell(0, 6, _t(pdf, v), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    _hr(pdf)
    pdf.set_text_color(160, 30, 30)
    pdf.set_font_size(10)
    pdf.multi_cell(
        0, 5,
        _t(pdf, "PERNYATAAN: Dokumen ini memuat INDIKASI berbasis data publik, bukan "
               "kesimpulan hukum. Semua angka dapat ditelusuri ke sumber yang dicantumkan. "
               "Pelaporan dilakukan melalui kanal resmi (APIP, BPKP, KPK, Ombudsman)."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # ---- Per flag ----
    sev_color = {"tinggi": (170, 30, 30), "sedang": (200, 120, 0), "rendah": (60, 110, 60)}
    for i, f in enumerate(flags, 1):
        if pdf.get_y() > 200:
            pdf.add_page()
        pdf.set_text_color(*sev_color.get(f.severity, (60, 60, 60)))
        pdf.set_font_size(12)
        pdf.cell(0, 8, _t(pdf, f"{i}. [{f.rule_id} · {f.severity.upper()}] {f.title}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(30, 30, 30)
        pdf.set_font_size(10)
        for line in f.evidence:
            pdf.multi_cell(0, 5, _t(pdf, "   • " + line), new_x="LMARGIN", new_y="NEXT")
        pdf.multi_cell(0, 5, _t(pdf, "   Penjelasan: " + f.explanation), new_x="LMARGIN", new_y="NEXT")
        pdf.multi_cell(0, 5, _t(pdf, "   Langkah lanjut: " + f.recommendation), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        _hr(pdf)

    # ---- Lampiran: tabel record terkait ----
    pdf.add_page()
    pdf.set_text_color(20, 20, 60)
    pdf.set_font_size(12)
    pdf.cell(0, 8, _t(pdf, "Lampiran — Record Terkait"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_size(8)
    pdf.set_text_color(30, 30, 30)
    ids = set()
    for f in flags:
        ids.update(f.record_ids)
    recs = {r["id"]: r for r in records if r["id"] in ids}
    for rid in sorted(recs):
        r = recs[rid]
        pdf.cell(26, 5, _t(pdf, r["id"]))
        pdf.cell(74, 5, _t(pdf, (r["project"] or "")[:52]))
        pdf.cell(30, 5, _t(pdf, rupiah(r["value"])))
        pdf.cell(38, 5, _t(pdf, (r.get("vendor") or "-")[:34]))
        pdf.cell(22, 5, _t(pdf, r.get("date_signed") or "-"), new_x="LMARGIN", new_y="NEXT")

    # ---- Footer tiap halaman ----
    def footer(p):
        p.set_y(-12)
        p.set_font_size(7)
        p.set_text_color(120, 120, 120)
        p.cell(0, 5, _t(p, "MATA — Watchdog Akuntabilitas Pengadaan · data sumber: data publik "
                          "PBJ (LPSE/Panda LKPP, e-Katalog, e-Kontrak) · INDIKASI, BUKAN VONIS · hal. ")
               + str(p.page_no()), align="C")

    for page in pdf.pages if hasattr(pdf, "pages") else []:
        pass  # fpdf2: pakai alias
    pdf.alias_nb_pages()
    try:
        pdf._footer = footer  # fpdf2: override via subclass lebih aman (lihat bawah)
    except Exception:  # noqa: BLE001
        pass

    out = os.path.join(out_dir, f"dossier_{today}.pdf")
    pdf.output(out)
    return out


def generate_letter(report, flags, cfg, out_dir):
    """Draft surat pengaduan/indikasi ke APIP instansi (HUMAN APPROVE sebelum kirim)."""
    os.makedirs(out_dir, exist_ok=True)
    n_tinggi = sum(1 for f in flags if f.severity == "tinggi")
    lines = [
        "Yth. Aparat Pengawasan Intern Pemerintah (APIP)",
        f"{cfg.get('region', '-')}",
        "",
        "Perihal: Penyampaian Indikasi Anomali Pengadaan Barang/Jasa Berbasis Data Publik (TA "
        f"{cfg.get('fiscal_year', '-')})",
        "",
        "Dengan hormat,",
        "",
        f"Melalui surat ini kami menyampaikan {len(flags)} indikasi anomali (termasuk "
        f"{n_tinggi} indikasi tingkat tinggi) yang teridentifikasi secara otomatis dari data "
        "pengadaan publik untuk tahun anggaran "
        f"{cfg.get('fiscal_year', '-')}, wilayah {cfg.get('region', '-')}.",
        "",
        "Ringkasan indikasi:",
    ]
    for i, f in enumerate(flags, 1):
        lines.append(f"{i}. [{f.rule_id} · {f.severity.upper()}] {f.title}")
        for e in f.evidence[:3]:
            lines.append(f"     {e}")
    lines += [
        "",
        "Rincian lengkap beserta sumber data, kalkulasi, dan dasar prinsip pengadaan "
        "terlampir dalam dossier (PDF). Seluruh klaim dapat ditelusuri ke sumber data publik "
        "yang dicantumkan.",
        "",
        "Kami menyampaikan indikasi ini untuk menjadi bahan pengawasan. Dokumen ini adalah "
        "indikasi berbasis data, bukan kesimpulan hukum.",
        "",
        "Hormat kami,",
        "",
        "____________________",
        "(Pelapor — nama & kontak diisi oleh pengguna sebelum dikirim)",
        "",
        "Lampiran: Dossier Indikasi (PDF)",
        "",
        "CATATAN SISTEM: Surat ini DRAFT — MATA tidak mengirim otomatis; pengguna yang "
        "memutuskan dan mengirim melalui kanal resmi.",
    ]
    out = os.path.join(out_dir, "laporan_draft_APIP.txt")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return out


def generate_public_summary(report, flags, cfg, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    n_tinggi = sum(1 for f in flags if f.severity == "tinggi")
    md = [
        f"# MATA — Ringkasan Publik: Pengadaan {cfg.get('region', '')} TA {cfg.get('fiscal_year', '')}",
        "",
        f"MATA memantau **{report.get('n_records', 0)}** pengumuman pengadaan publik dan "
        f"mendeteksi **{len(flags)} indikasi anomali** ({n_tinggi} tingkat tinggi).",
        "",
        "Ini **indikasi berbasis data, bukan vonis**. Setiap angka dapat diverifikasi langsung "
        "dari sumber publik yang dicantumkan di dossier.",
        "",
        "## Indikasi",
    ]
    for f in flags:
        md.append(f"### [{f.rule_id} · {f.severity.upper()}] {f.title}")
        for e in f.evidence:
            md.append(f"- {e}")
        md.append("")
    md += [
        "## Apa yang bisa kamu lakukan",
        "1. Verifikasi sendiri ke sumber data (tautan di dossier).",
        "2. Laporkan melalui kanal resmi: [LAPOR!](https://www.lapor.go.id), Ombudsman RI, "
        "KPK (whistleblower), atau APIP instansi terkait.",
        "3. Bagikan dengan menyebut sumber datanya.",
        "",
        "_Dibuat oleh MATA — open source, self-hosted, data publik._",
    ]
    out = os.path.join(out_dir, "ringkasan_publik.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    return out
