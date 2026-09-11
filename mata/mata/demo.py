#!/usr/bin/env python3
"""MATA — DEMO 5 SKENARIO (untuk video 5–10 menit).

Jalankan:  python3 run.py demo
Urutan sesuai naskah video:
  S1  Pindai & deteksi (pipeline nyata)
  S2  "Harga di pasar" (D1, kalkulasi terbuka)
  S3  "Satu vendor, banyak kontrak" (D2, konsentrasi)
  S4  Dossier + draft laporan (output dunia nyata)
  S5  Keandalan & etika (status monitor, human-in-the-loop, sumber)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mata import db, engine, rules, narrative, dossier  # noqa: E402

LINE = "=" * 78


def s1_pindai(cfg):
    print(LINE)
    print("SKENARIO 1 — PINDAI & DETEKSI (pipeline data → analisis, berjalan nyata)")
    print(LINE)
    recs = db.load_records(cfg.get("fiscal_year"))
    print(f"MATA memindai {len(recs)} pengumuman PBJ publik — {cfg.get('region')} "
          f"TA {cfg.get('fiscal_year')}.")
    print(f"Total nilai pengadaan terdata: {dossier.rupiah(sum(r['value'] for r in recs))}")
    print(f"Penyedia terdata: {len({r['vendor'] for r in recs if r.get('vendor')})} · "
          f"Instansi: {len({r['agency'] for r in recs})}")
    flags = rules.run_rules(recs, cfg["thresholds"], cfg.get("fiscal_year"))
    for f in flags:
        narrative.explain(f, cfg)
    n_t = sum(1 for f in flags if f.severity == "tinggi")
    print(f"\nRESULT: {len(flags)} indikasi terdeteksi ({n_t} tingkat tinggi) — "
          f"oleh rule engine TRANSPARAN (ambang dipajang di config & artikel).")
    return recs, flags


def s2_harga(cfg, recs, flags):
    print("\n" + LINE)
    print('SKENARIO 2 — "HARGA DI PASAR" (D1: kalkulasi terbuka)')
    print(LINE)
    f = next((x for x in flags if x.rule_id == "D1"), None)
    if not f:
        print("(D1 tidak terpicu pada dataset ini)")
        return
    r = next((x for x in recs if x["id"] == f.record_ids[0]), None)
    print(f"Proyek   : {r['project']} ({r['agency']})")
    print(f"Nilai    : {dossier.rupiah(r['value'])}")
    print(f"Referensi: {dossier.rupiah(r['ref_price'])} (harga katalog/peer)")
    dev = (r["value"] - r["ref_price"]) / r["ref_price"]
    print(f"Deviasi  : +{dev*100:.0f}%  →  RUMUS: (nilai − referensi) / referensi "
          f"≥ ambang {cfg['thresholds']['d1_deviation']*100:.0f}%")
    print(f"Bukti    : {r['id']} · {r['date_signed']} · {r['url']}")


def s3_vendor(cfg, recs, flags):
    print("\n" + LINE)
    print('SKENARIO 3 — "SATU VENDOR, BANYAK KONTRAK" (D2: konsentrasi)')
    print(LINE)
    f = next((x for x in flags if x.rule_id == "D2"), None)
    if not f:
        print("(D2 tidak terpicu pada dataset ini)")
        return
    m = f.metrics
    for e in f.evidence:
        print(" ", e)
    print(f"  → Porsi nilai {m['porsi']*100:.1f}% dari total pengadaan terdata. "
          f"Aturan: ≥{cfg['thresholds']['d2_min_projects']} proyek DAN "
          f"≥{cfg['thresholds']['d2_min_share']*100:.0f}% nilai.")


def s4_dossier(cfg, recs, flags):
    print("\n" + LINE)
    print("SKENARIO 4 — DOSSIER + DRAFT LAPORAN (output dunia nyata)")
    print(LINE)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, cfg.get("output_dir", "output"))
    pdf = dossier.generate_pdf({"n_records": len(recs)}, flags, recs, cfg, out_dir)
    letter = dossier.generate_letter({"n_records": len(recs)}, flags, cfg, out_dir)
    summary = dossier.generate_public_summary({"n_records": len(recs)}, flags, cfg, out_dir)
    print(f"Dossier PDF      : {pdf}")
    print(f"  - per indikasi: bukti + penjelasan + langkah lanjut + lampiran record")
    print(f"  - pernyataan   : 'INDIKASI, BUKAN VONIS' + kredit sumber data")
    print(f"Draft laporan    : {letter}  (ke APIP — DRAFT, kirim = keputusan manusia)")
    print(f"Ringkasan publik : {summary}")


def s5_etika(cfg):
    print("\n" + LINE)
    print("SKENARIO 5 — KEANDALAN & ETIKA")
    print(LINE)
    st = {}
    if os.path.exists(db.STATUS_PATH):
        import json as _json
        with open(db.STATUS_PATH, encoding="utf-8") as fh:
            st = _json.load(fh)
    print(f"Status monitor   : {st}")
    print("Keandalan        : auto-restart (systemd), log siklus, mode jujur saat gagal")
    print("Etika            : (1) hanya data PUBLIK + kredit sumber")
    print("                   (2) INDIKASI, bukan vonis — semua angka bisa ditelusuri")
    print("                   (3) HUMAN-IN-THE-LOOP: MATA menyiapkan, manusia yang mengirim")
    print("                   (4) pelaporan lewat KANAL RESMI (APIP/BPKP/KPK/Ombudsman)")
    print("                   (5) data demo = sintetis; demo tidak menyasar pihak nyata")
    print("\n" + LINE)
    print("DEMO SIAP DIREKAM — output tersimpan di output/")
    print(LINE)


def run():
    cfg = engine.load_cfg()
    # pastikan data ada
    if not db.load_records():
        import collectors
        db.upsert_records(collectors.generate_synthetic())
        print("(dataset demo dibuat otomatis)")
    recs, flags = s1_pindai(cfg)
    s2_harga(cfg, recs, flags)
    s3_vendor(cfg, recs, flags)
    s4_dossier(cfg, recs, flags)
    s5_etika(cfg)


if __name__ == "__main__":
    run()
