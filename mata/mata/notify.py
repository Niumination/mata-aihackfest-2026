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
