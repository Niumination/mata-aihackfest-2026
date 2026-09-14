"""Notifikasi MATA ke Telegram (Bot API). No-op aman jika token kosong."""
import requests


def send_telegram(cfg, text):
    tg = cfg.get("telegram", {})
    token, chat_id = tg.get("token"), tg.get("chat_id")
    if not token or not chat_id:
        return {"sent": False, "reason": "token/chat_id kosong (no-op)"}
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text[:4000], "parse_mode": "HTML"},
            timeout=15,
        )
        return {"sent": r.status_code == 200, "status": r.status_code}
    except Exception as e:  # noqa: BLE001
        return {"sent": False, "error": str(e)}


def _on(cfg, key):
    """Toggle per-jenis notifikasi (default ON bila blok tak ada)."""
    return cfg.get("notify", {}).get(key, True)


def format_tinggi_baru(flags):
    lines = ["🚨 <b>MATA — indikasi TINGGI baru</b>", ""]
    for f in flags:
        d = f if isinstance(f, dict) else f.to_dict()
        lines.append(f"[{d['rule_id']} · TINGGI] {d['title']}")
        if d.get("evidence"):
            lines.append(f"   {d['evidence'][0]}")
    lines += ["", "Verifikasi + laporkan via kanal resmi. INDIKASI, BUKAN VONIS."]
    return "\n".join(lines)


def format_dossier(pdf, letter, summary, n_flags):
    import os
    return "\n".join([
        "📁 <b>MATA — dossier jadi</b>",
        f"Indikasi: <b>{n_flags}</b>",
        f"PDF: <code>{os.path.basename(pdf)}</code>",
        f"APIP: <code>{os.path.basename(letter)}</code>",
        f"Publik: <code>{os.path.basename(summary)}</code>",
        "Siap ditinjau manusia sebelum dikirim.",
    ])


def format_data_baru(delta, total):
    return "\n".join([
        "📥 <b>MATA — data baru masuk</b>",
        f"Record baru: <b>+{delta}</b> (total {total})",
        "Analisis + dossier diperbarui siklus ini.",
    ])


def format_harian(status, flags):
    lv = {}
    for f in flags:
        s = f.get("severity") if isinstance(f, dict) else f.severity
        lv[s] = lv.get(s, 0) + 1
    lines = [
        f"🗓 <b>MATA harian — {status.get('last_run', '-')[:10]}</b>",
        f"Monitor: {'ONLINE' if status.get('ok') else 'OFFLINE'} · "
        f"{status.get('n_records', '?')} pengumuman · "
        f"{status.get('n_flags', '?')} indikasi ({status.get('n_flags_tinggi', '?')} tinggi)",
    ]
    for s in ("tinggi", "sedang", "rendah"):
        if s in lv:
            lines.append(f"  {s.upper()}: {lv[s]}")
    lines.append("Ini indikasi berbasis data, bukan vonis.")
    return "\n".join(lines)


def format_report_text(region, fiscal_year, n_records, flags):
    n_tinggi = sum(1 for f in flags if f.severity == "tinggi")
    lines = [
        f"<b>MATA — Rekap Pengadaan {region} TA {fiscal_year}</b>",
        f"Pengumuman dipindai: <b>{n_records}</b>",
        f"Indikasi: <b>{len(flags)}</b> ({n_tinggi} tingkat tinggi)",
        "",
    ]
    for f in flags:
        lines.append(f"[{f.rule_id} · {f.severity.upper()}] {f.title}")
        lines.append(f"   {f.evidence[0] if f.evidence else ''}")
    lines.append("")
    lines.append("Dossier PDF & draft laporan: siap (lihat output/).")
    lines.append("INDIKASI, BUKAN VONIS — laporkan via kanal resmi.")
    return "\n".join(lines)
