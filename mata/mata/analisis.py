"""MATA — Analisis realisasi pengadaan (D2: konsentrasi & pola).

Sumber: `data/realisasi_2026_full.json` + `data/realisasi_2025_full.json`
(koleksi penuh dari BFF INAPROC — 662 + 599 paket, commit 2e74e78).

Prinsip: **INDIKASI, BUKAN VONIS.** Setiap temuan adalah sinyal statistik
yang perlu verifikasi manual di SPSE/e-kontrak; modul ini tidak menuduh
siapa pun. Atribusi sumber + tanggal koleksi wajib tampil di panel.

Metode deterministik (tanpa AI): agregat per penyedia/SKPD, share %,
repetisi antar-tahun, dan 4 jenis flag pola:
  - repetisi_tinggi   : penyedia ≥ 5 paket dalam satu tahun
  - pengadaan_langsung_besar : Pengadaan Langsung ≥ Rp 100 jt
  - duplikat_kode     : kode_paket muncul >1× (kualitas data)
  - konsentrasi       : share top-10 penyedia
"""
import json
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE_DIR, "data")
FILES = {2026: os.path.join(DATA, "realisasi_2026_full.json"),
         2025: os.path.join(DATA, "realisasi_2025_full.json")}
RUP_FILES = {2026: os.path.join(DATA, "rup_2026_full.json"),
             2025: os.path.join(DATA, "rup_2025_full.json")}
TTL = 1800  # file statis antar-koleksi; cache 30 mnt cukup
_CACHE = {"at": 0, "out": None}

PL_BESAR = 100_000_000  # Rp 100 jt
REPETISI_MIN = 5


def _load_rows(tahun):
    try:
        with open(FILES[tahun], encoding="utf-8") as f:
            rows = json.load(f)
        return [r for r in rows if isinstance(r, dict)]
    except Exception:
        return []


def _penyedia(r):
    p = (r.get("nama_penyedia") or "").strip()
    return p if p and p != "-" else None


def _skpd(r):
    s = (r.get("nama_satuan_kerja") or "").strip()
    return s.split(" - ")[0] if s else None


def _tahun(rows):
    tot = sum(r.get("total_nilai") or 0 for r in rows)
    by_val, by_cnt = {}, {}
    for r in rows:
        p = _penyedia(r)
        if not p:
            continue
        v = r.get("total_nilai") or 0
        by_val[p] = by_val.get(p, 0) + v
        by_cnt[p] = by_cnt.get(p, 0) + 1
    top_val = sorted(by_val.items(), key=lambda kv: -kv[1])[:10]
    top_cnt = sorted(by_cnt.items(), key=lambda kv: -kv[1])[:5]
    skpd = {}
    for r in rows:
        k = _skpd(r)
        if not k:
            continue
        s = skpd.setdefault(k, {"n": 0, "nilai": 0})
        s["n"] += 1
        s["nilai"] += r.get("total_nilai") or 0
    status, metode = {}, {}
    for r in rows:
        for d, key in ((status, "status_paket"), (metode, "metode_pengadaan")):
            k = r.get(key) or "-"
            d[k] = d.get(k, 0) + 1
    return {
        "n_paket": len(rows),
        "total_nilai": tot,
        "n_penyedia": len(by_val),
        "top10_nilai": [{"nama": n, "nilai": v,
                         "paket": by_cnt.get(n, 0),
                         "share": round(v * 100.0 / tot, 1) if tot else 0}
                        for n, v in top_val],
        "top5_paket": [{"nama": n, "paket": c} for n, c in top_cnt],
        "top5_skpd": sorted(
            ({"nama": k, "n": s["n"], "nilai": s["nilai"]} for k, s in skpd.items()),
            key=lambda x: -x["nilai"])[:5],
        "status": status,
        "metode": metode,
        "top10_share": round(sum(v for _, v in top_val) * 100.0 / tot, 1) if tot else 0,
    }


def _flags(rows, tahun):
    out = []
    by_cnt = {}
    for r in rows:
        p = _penyedia(r)
        if p:
            by_cnt[p] = by_cnt.get(p, 0) + 1
    rep = sorted(((n, c) for n, c in by_cnt.items() if c >= REPETISI_MIN),
                 key=lambda x: -x[1])
    if rep:
        out.append({"jenis": "repetisi_tinggi",
                    "label": "Penyedia ≥ %d paket (TA%d)" % (REPETISI_MIN, tahun),
                    "n": len(rep),
                    "contoh": ["%s (%d paket)" % (n, c) for n, c in rep[:3]]})
    pl = [r for r in rows
          if (r.get("metode_pengadaan") or "") == "Pengadaan Langsung"
          and (r.get("total_nilai") or 0) >= PL_BESAR]
    if pl:
        pl.sort(key=lambda r: -(r.get("total_nilai") or 0))
        out.append({"jenis": "pengadaan_langsung_besar",
                    "label": "Pengadaan Langsung ≥ Rp 100 jt (TA%d)" % tahun,
                    "n": len(pl),
                    "contoh": ["%s — Rp %s jt" % (
                        (r.get("nama_paket") or "?")[:60],
                        format((r.get("total_nilai") or 0) / 1e6, ",.0f").replace(",", "."))
                        for r in pl[:3]]})
    seen, dup = {}, []
    for r in rows:
        k = r.get("kode_paket")
        if k is None:
            continue
        if k in seen:
            dup.append(k)
        seen[k] = 1
    if dup:
        out.append({"jenis": "duplikat_kode",
                    "label": "Kode paket duplikat (TA%d) — cek kualitas data" % tahun,
                    "n": len(dup), "contoh": dup[:5]})
    return out


def _repeat_cross(t25, t26):
    a, b = {}, {}
    for r in t25:
        p = _penyedia(r)
        if p:
            a[p] = a.get(p, 0) + (r.get("total_nilai") or 0)
    for r in t26:
        p = _penyedia(r)
        if p:
            b[p] = b.get(p, 0) + (r.get("total_nilai") or 0)
    both = []
    for p in set(a) & set(b):
        both.append({"nama": p, "nilai_2025": a[p], "nilai_2026": b[p],
                     "delta": b[p] - a[p]})
    both.sort(key=lambda x: -x["nilai_2026"])
    return both[:15]


def _rup_vs_realisasi(rup_rows, rel_rows):
    """Rencana (RUP per-paket) vs realisasi, per SKPD + keseluruhan (TA2026).

    `total_nilai` di RUP = rencana; di realisasi = nilai kontrak/realisasi.
    Rate < 0 = belum ada realisasi tercatat utk SKPD tsb.
    """
    renc, real = {}, {}
    for r in rup_rows:
        k = _skpd(r)
        if k:
            renc[k] = renc.get(k, 0) + (r.get("total_nilai") or 0)
    for r in rel_rows:
        k = _skpd(r)
        if k:
            real[k] = real.get(k, 0) + (r.get("total_nilai") or 0)
    keys = set(renc) | set(real)
    per = []
    for k in keys:
        rn, rl = renc.get(k, 0), real.get(k, 0)
        per.append({"nama": k, "rencana": rn, "realisasi": rl,
                    "rate": round(rl * 100.0 / rn, 1) if rn else None,
                    "selisih": rn - rl})
    per.sort(key=lambda x: -x["rencana"])
    TR, TL = sum(renc.values()), sum(real.values())
    return {"skpd": per,
            "keseluruhan": {"rencana": TR, "realisasi": TL,
                            "rate": round(TL * 100.0 / TR, 1) if TR else None}}


def compute():
    r26, r25 = _load_rows(2026), _load_rows(2025)
    if not r26 and not r25:
        return {"ok": False, "error": "file koleksi belum ada (data/realisasi_*_full.json)"}
    y26, y25 = _tahun(r26), _tahun(r25)
    out = {
        "ok": True,
        "source": "INAPROC realisasi (data.inaproc.id) — koleksi penuh 12 Sep 2026",
        "tahun": {"2026": y26, "2025": y25},
        "repeat": _repeat_cross(r25, r26),
        "flags": _flags(r26, 2026) + _flags(r25, 2025),
    }
    # RUP vs Realisasi — tampil hanya bila koleksi RUP penuh sudah ada
    try:
        with open(RUP_FILES[2026], encoding="utf-8") as f:
            u26 = [r for r in json.load(f) if isinstance(r, dict)]
    except Exception:
        u26 = []
    if u26 and r26:
        out["rup_vs_realisasi"] = _rup_vs_realisasi(u26, r26)
    return out


def load(max_age=TTL):
    if _CACHE["out"] and time.time() - _CACHE["at"] < max_age:
        return _CACHE["out"]
    out = compute()
    _CACHE.update({"at": time.time(), "out": out})
    return out
