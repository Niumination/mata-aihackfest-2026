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
  python3 run.py live-test             # uji koneksi INAPROC API (butuh jwt_token)
  python3 run.py live-collect          # kumpulkan data LIVE (pengumuman+kontrak) → DB
  python3 run.py live-collect --mbg    # hanya paket MBG (atau --keyword SPPG ...)
  python3 run.py live-open             # LIVE v1: open data LKPP (TANPA registrasi)
  python3 run.py open-data             # open data v2: SIRUP + katalog per daerah (XLSX LKPP)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mata import db, collectors, engine  # noqa: E402


def main():
    p = argparse.ArgumentParser(prog="mata", description="MATA — Watchdog Akuntabilitas Pengadaan")
    p.add_argument("cmd", choices=["setup", "collect", "analyze", "report", "cycle",
                                   "loop", "web", "demo", "probe",
                                   "live-test", "live-collect", "live-open", "open-data"])
    p.add_argument("-i", "--interval", type=int, default=3600, help="interval loop (detik)")
    p.add_argument("-p", "--port", type=int, default=8080, help="port dashboard web")
    p.add_argument("-q", "--quiet", action="store_true")
    p.add_argument("--keyword", action="append", default=[],
                   help="filter nama paket (boleh diulang). Cth: --keyword SPPG --keyword dapur")
    p.add_argument("--mbg", action="store_true",
                   help="pintasan: filter paket MBG (Makan Bergizi Gratis) via kata kunci bawaan")
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

    elif a.cmd == "live-test":
        cfg = engine.load_cfg()
        from mata import live_api
        icfg = cfg.get("inaproc") or {}
        params = {"limit": 5}
        if icfg.get("kode_klpd"):
            params.update({"tahun": icfg.get("tahun", cfg.get("fiscal_year", 2025)),
                           "kode_klpd": icfg["kode_klpd"]})
        try:
            data, meta = live_api.get_page(cfg, "tender/pengumuman", params)
            print(f"OK — API LIVE aktif. {len(data)} baris pengumuman:")
            for r in data[:5]:
                pagu = r.get("pagu") or 0
                print(f"  · {r.get('nama_paket')} | {r.get('nama_klpd')} | pagu {pagu:,.0f}")
            print("SIAP: jalankan `python3 run.py live-collect` untuk data penuh.")
        except live_api.LiveError as e:
            print(f"GAGAL: {e}")
        except Exception as e:
            print(f"GAGAL (jaringan?): {type(e).__name__}: {e}")

    elif a.cmd == "live-collect":
        cfg = engine.load_cfg()
        from mata import live_api
        icfg = cfg.get("inaproc") or {}
        tahun = icfg.get("tahun", cfg.get("fiscal_year", 2025))
        klpd = icfg.get("kode_klpd", "")
        if not klpd:
            print("GAGAL: config.json → inaproc.kode_klpd wajib diisi (kode KLPD daerah).")
            return
        keywords = list(a.keyword or [])
        if a.mbg:
            from mata import mbg as _mbg
            keywords += [k for k in _mbg.MBG_KEYWORDS if k not in keywords]
        if keywords:
            print(f"[live] Filter kata kunci aktif: {', '.join(keywords)}")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        raw_dir = os.path.join(base_dir, "output", "live_raw")
        params = {"tahun": tahun, "kode_klpd": klpd}
        region = cfg.get("region", "")
        print(f"[live] Mengumpulkan data {tahun} · kode_klpd={klpd} dari INAPROC API ...")
        recs = {}
        hps_map = {}  # kd_tender → HPS (dari pengumuman) — referensi resmi untuk D1

        def _keep(r):
            if not keywords:
                return True
            from mata import mbg as _mbg
            name = r.get("nama_paket", "") or ""
            return any(_mbg.match_keyword(name, k) for k in keywords)

        n_raw = 0
        for r in live_api.iter_all(cfg, "tender/pengumuman", params, raw_dir):
            n_raw += 1
            if not _keep(r):
                continue
            recs[r["id"]] = live_api.norm_pengumuman(r, region)
            if r.get("hps") is not None and r.get("kd_tender"):
                hps_map[str(r["kd_tender"])] = r["hps"]
        for r in live_api.iter_all(cfg, "tender/tender-ekontrak", params, raw_dir):
            n_raw += 1
            if not _keep(r):
                continue
            recs[r["id"]] = live_api.norm_kontrak(r, hps_map, region)
        for r in live_api.iter_all(cfg, "tender/non-tender-ekontrak-kontrak", params, raw_dir):
            n_raw += 1
            if not _keep(r):
                continue
            recs[r["id"]] = live_api.norm_kontrak(r, hps_map, region)
        n = db.upsert_records(list(recs.values()))
        nv = sum(1 for x in recs.values() if x["vendor"])
        print(f"[live] {len(recs)} record ternormalisasi ({nv} dgn pemenang) → DB total {n} record.", end="")
        if keywords:
            print(f" (dari {n_raw} record mentah, filter: {len(recs)} cocok)")
        else:
            print()
        print(f"[live] Raw snapshot tersimpan di output/live_raw/ (audit).")
        print("Selanjutnya: python3 run.py cycle  (rule engine D1-D6 membaca data LIVE ini)")

    elif a.cmd == "open-data":
        cfg = engine.load_cfg()
        from mata import open_data
        base_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            print(open_data.run_collect(cfg, os.path.join(base_dir, "output")))
        except open_data.OpenDataError as e:
            print(f"GAGAL: {e}")
        except Exception as e:
            print(f"GAGAL (jaringan?): {type(e).__name__}: {e}")

    elif a.cmd == "live-open":
        cfg = engine.load_cfg()
        from mata import live_lkpp
        base_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            print(live_lkpp.run_report(cfg, os.path.join(base_dir, "output")))
        except live_lkpp.LkppOpenError as e:
            print(f"GAGAL: {e}")
        except Exception as e:
            print(f"GAGAL (jaringan?): {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
