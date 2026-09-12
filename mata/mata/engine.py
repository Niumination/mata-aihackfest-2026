"""Engine MATA: satu siklus = collect → analyze → dossier → notify → status.

Dijalankan oleh:
  - `run.py cycle` (manual/cron)
  - `run.py loop` (24/7, systemd — deploy/mata.service)
  - Hermes Agent: cron Hermes bisa memanggil `run.py cycle` dan
    `hermes_hook.py` untuk menyampaikan ringkasan ke Telegram.
"""
import os
import json
import time
import traceback
import datetime

from . import db, collectors, rules, narrative, dossier, notify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")


def load_cfg(path=CONFIG_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


NOTIFY_EVERY = 3 * 3600  # rekap Telegram maks tiap 3 jam (deteksi tetap tiap siklus)


def _prev_status():
    try:
        with open(db.STATUS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _notify_due(prev, sig):
    """Kirim bila >=3 jam sejak notif terakhir, atau indikasi berubah."""
    if prev.get("flags_sig") != sig:
        return True
    try:
        last = datetime.datetime.fromisoformat(prev.get("last_notify") or "1970-01-01")
        return (datetime.datetime.now() - last).total_seconds() >= NOTIFY_EVERY
    except Exception:
        return True


def cycle(cfg_path=CONFIG_PATH, quiet=False):
    cfg = load_cfg(cfg_path)
    out_dir = os.path.join(BASE_DIR, cfg.get("output_dir", "output"))
    log = []

    def say(msg):
        if not quiet:
            print(msg)

    try:
        # 1) KOLEKSI
        records = collectors.run_collect(cfg)
        n = db.upsert_records(records)
        say(f"[1/5] Koleksi: {len(records)} record diproses → {n} record di database.")

        # 2) ANALISIS (rule engine transparan)
        all_recs = db.load_records(cfg.get("fiscal_year"))
        flags = rules.run_rules(all_recs, cfg["thresholds"], cfg.get("fiscal_year"))
        for f in flags:
            narrative.explain(f, cfg)
        n_tinggi = sum(1 for f in flags if f.severity == "tinggi")
        say(f"[2/5] Analisis: {len(flags)} indikasi dari {len(all_recs)} pengumuman "
            f"({n_tinggi} tingkat tinggi).")
        for f in flags:
            say(f"      [{f.rule_id} · {f.severity.upper()}] {f.title}")

        # 3) DOSSIER + LAPORAN
        report = {
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "region": cfg.get("region"),
            "fiscal_year": cfg.get("fiscal_year"),
            "n_records": len(all_recs),
            "n_flags": len(flags),
            "n_flags_tinggi": n_tinggi,
            "summary": f"{len(flags)} indikasi dari {len(all_recs)} pengumuman",
        }
        pdf = dossier.generate_pdf(report, flags, all_recs, cfg, out_dir)
        letter = dossier.generate_letter(report, flags, cfg, out_dir)
        summary = dossier.generate_public_summary(report, flags, cfg, out_dir)
        say(f"[3/5] Output: {os.path.basename(pdf)} · {os.path.basename(letter)} · "
            f"{os.path.basename(summary)}")

        # 4) NOTIFIKASI (throttle 3 jam; deteksi tiap siklus tetap jalan)
        sig = f"{len(flags)}:{n_tinggi}:{','.join(sorted(f.rule_id for f in flags))}"
        prev = _prev_status()
        last_notify = prev.get("last_notify")
        if _notify_due(prev, sig):
            text = notify.format_report_text(
                cfg.get("region"), cfg.get("fiscal_year"), len(all_recs), flags)
            res = notify.send_telegram(cfg, text)
            if res.get("sent"):
                last_notify = report["ts"]
            say(f"[4/5] Notifikasi: {'terkirim ke Telegram' if res.get('sent') else 'no-op (token belum diset)'}")
        else:
            say("[4/5] Notifikasi: dilewati (rekap terakhir <3 jam, indikasi tetap).")

        # 5) STATUS (untuk web dashboard & Hermes hook)
        db.write_flags([f.to_dict() for f in flags])
        db.write_status({
            "ok": True,
            "last_run": report["ts"],
            "n_records": len(all_recs),
            "n_flags": len(flags),
            "n_flags_tinggi": n_tinggi,
            "last_error": None,
            "last_notify": last_notify,
            "flags_sig": sig,
        })
        db.log_run(len(all_recs), len(flags), "ok")
        say("[5/5] Siklus selesai — status & flags tersimpan (data/status.json, data/flags_latest.json).")
        return {"ok": True, "report": report, "pdf": pdf, "letter": letter, "summary": summary}
    except Exception as e:  # noqa: BLE001 — kegagalan dicatat & dilaporkan, tidak diam
        err = f"{type(e).__name__}: {e}"
        prev = _prev_status()
        db.write_status({"ok": False, "last_error": err,
                         "last_run": datetime.datetime.now().isoformat(timespec="seconds"),
                         "last_notify": prev.get("last_notify"),
                         "flags_sig": prev.get("flags_sig")})
        db.log_run(0, 0, "error")
        say(f"[GAGAL] {err}")
        notify.send_telegram(cfg, f"MATA monitor: siklus GAGAL — {err}")
        traceback.print_exc()
        return {"ok": False, "error": err}


def loop(cfg_path=CONFIG_PATH, interval=3600):
    print(f"MATA loop dimulai (interval {interval}s). Ctrl-C untuk berhenti.")
    while True:
        cycle(cfg_path)
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit("jalankan via: python3 run.py cycle")
