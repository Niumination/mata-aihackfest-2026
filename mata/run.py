#!/usr/bin/env python3
"""MATA — CLI utama.

  python3 run.py setup                 # init DB + generate dataset demo
  python3 run.py collect               # koleksi data (mode di config.json)
  python3 run.py analyze               # jalankan rule engine, tampilkan indikasi
  python3 run.py report                # generate dossier PDF + draft laporan
  python3 run.py cycle                 # siklus penuh (collect→analyze→report→notify)
  python3 run.py loop -i 3600          # 24/7 (untuk systemd)
  python3 run.py web -p 8080           # dashboard status (zero-dependency)
  python3 run.py demo                  # 5 skenario demo untuk video
  python3 run.py probe                 # uji akses sumber data live (HARI 1)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mata import db, collectors, engine  # noqa: E402


def main():
    p = argparse.ArgumentParser(prog="mata", description="MATA — Watchdog Akuntabilitas Pengadaan")
    p.add_argument("cmd", choices=["setup", "collect", "analyze", "report", "cycle",
                                   "loop", "web", "demo", "probe"])
    p.add_argument("-i", "--interval", type=int, default=3600, help="interval loop (detik)")
    p.add_argument("-p", "--port", type=int, default=8080, help="port dashboard web")
    p.add_argument("-q", "--quiet", action="store_true")
    a = p.parse_args()

    if a.cmd == "setup":
        db.init_db()
        recs = collectors.generate_synthetic()
        n = db.upsert_records(recs)
        print(f"DB siap. {n} record demo terisi (mode synthetic).")

    elif a.cmd == "collect":
        cfg = engine.load_cfg()
        recs = collectors.run_collect(cfg)
        n = db.upsert_records(recs)
        print(f"{n} record di database.")

    elif a.cmd == "analyze":
        cfg = engine.load_cfg()
        recs = db.load_records(cfg.get("fiscal_year"))
        from mata import rules, narrative
        flags = rules.run_rules(recs, cfg["thresholds"], cfg.get("fiscal_year"))
        for f in flags:
            narrative.explain(f, cfg)
        print(f"{len(flags)} indikasi dari {len(recs)} pengumuman:\n")
        for f in flags:
            print(f"[{f.rule_id} · {f.severity.upper()}] {f.title}")
            for e in f.evidence:
                print(f"    {e}")
            print()

    elif a.cmd == "report":
        cfg = engine.load_cfg()
        recs = db.load_records(cfg.get("fiscal_year"))
        from mata import rules, narrative, dossier
        flags = rules.run_rules(recs, cfg["thresholds"], cfg.get("fiscal_year"))
        for f in flags:
            narrative.explain(f, cfg)
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg.get("output_dir", "output"))
        pdf = dossier.generate_pdf({"n_records": len(recs)}, flags, recs, cfg, out_dir)
        letter = dossier.generate_letter({"n_records": len(recs)}, flags, cfg, out_dir)
        summary = dossier.generate_public_summary({"n_records": len(recs)}, flags, cfg, out_dir)
        print(f"Dossier : {pdf}\nLaporan : {letter}\nPublik  : {summary}")

    elif a.cmd == "cycle":
        engine.cycle(quiet=a.quiet)

    elif a.cmd == "loop":
        engine.loop(interval=a.interval)

    elif a.cmd == "web":
        from mata import web
        web.serve(port=a.port)

    elif a.cmd == "demo":
        from mata import demo
        demo.run()

    elif a.cmd == "probe":
        import json
        print(json.dumps({
            "panda_lkpp": collectors.probe_panda_lkpp(),
            "inaproc": collectors.probe_inaproc(),
            "lpse_acehtengah": collectors.probe_lpse_region("lpse.acehtengahkab.go.id"),
        }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
