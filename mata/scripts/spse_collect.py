#!/usr/bin/env python3
"""MATA — Kolektor SPSE (Jalur B, jalan di LAPTOP — koneksi ISP lolos Cloudflare).

Mengambil data penuh LPSE Kab. Aceh Tengah dari spse.inaproc.id (perlu cookie
sesi browser — Cloudflare memblokir curl polos dari datacenter, temuan 12 Sep)
lalu push ke dashboard MATA di VPS.

Langkah sekali (menyiapkan cookie):
  1. Buka https://spse.inaproc.id/acehtengahkab di browser (selesaikan verifikasi
     jika muncul).
  2. DevTools (F12) → tab Network → klik ulang halaman → request utama →
     Headers → copy nilai header "cookie" (cukup 2 nilai ini: cf_clearance,
     __cf_bm) → simpan ke file, mis. cookies.txt (satu baris:
     cf_clearance=...; __cf_bm=...)

Jalankan:
  python3 scripts/spse_collect.py --cookie-file cookies.txt \
      [--tahun 2026] [--out spse_full.json] \
      [--push https://HOST:PORT --token TOKEN_PUSH]

Zero-dependency (stdlib saja). Token push = nilai config.json VPS: spse.push_token.
"""
import argparse
import html as _html
import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mata import spse_pub  # noqa: E402

BASE = "https://spse.inaproc.id/" + spse_pub.DEFAULT_SLUG
UA = spse_pub.UA


def _req(url, cookie="", referer=None, timeout=30):
    h = dict(UA)
    if cookie:
        h["Cookie"] = cookie
    if referer:
        h["Referer"] = referer
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def html2cells(h):
    h = re.sub(r"<(script|style).*?</\1>", " ", h, flags=re.S)
    h = re.sub(r"</t[dh]>", " \u00a7 ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = _html.unescape(h)
    return re.sub(r"[ \t]+", " ", h)


def field(cells, label):
    m = re.search(re.escape(label) + r"\s*\u00a7\s*(.+?)\s*\u00a7", cells)
    return m.group(1).strip() if m else None


def detail(pkg, cookie):
    """Perkaya satu paket dengan data halaman detail (satker, metode, tahap…)."""
    try:
        cells = html2cells(_req(pkg["url"], cookie, referer=BASE))
    except Exception as e:
        pkg["detail_error"] = str(e)[:120]
        return pkg
    pkg["satker"] = field(cells, "Satuan Kerja")
    pkg["metode"] = field(cells, "Metode Pengadaan")
    pkg["tahap"] = field(cells, "Tahap Tender Saat Ini")
    pkg["ta"] = field(cells, "Tahun Anggaran")
    pkg["sumber_dana"] = field(cells, "Sumber Dana")
    pkg["rup_kode"] = field(cells, "Kode RUP")
    pkg["pagu"] = field(cells, "Nilai Pagu Paket")
    p = field(cells, "Peserta Tender")
    if p:
        m = re.search(r"\d+", p)
        pkg["n_peserta"] = int(m.group(0)) if m else None
    return pkg


def dt_lelang(cookie, tahun):
    """Endpoint DataTables /dt/lelang — mungkin tetap terblokir CF; tangkap apa adanya."""
    try:
        raw = _req(BASE + "/dt/lelang?tahun=" + tahun, cookie,
                   referer=BASE + "/lelang")
        if raw.lstrip().startswith("{"):
            j = json.loads(raw)
            return j if isinstance(j, dict) else {"rows": raw[:4000]}
        return {"error": "bukan JSON", "snippet": raw[:300]}
    except Exception as e:
        return {"error": str(e)[:160]}


def main():
    ap = argparse.ArgumentParser(description="Kolektor SPSE Kab. Aceh Tengah (Jalur B)")
    ap.add_argument("--cookie-file", help="file berisi header cookie (cf_clearance; __cf_bm)")
    ap.add_argument("--cookie", help="string cookie langsung (alternatif --cookie-file)")
    ap.add_argument("--tahun", default="2026", help="tahun anggaran untuk /dt/lelang")
    ap.add_argument("--out", default="spse_full.json")
    ap.add_argument("--no-detail", action="store_true", help="lewati halaman detail (cepat)")
    ap.add_argument("--push", help="URL VPS, mis. https://HOST:8080")
    ap.add_argument("--token", help="token push (config.json VPS: spse.push_token)")
    a = ap.parse_args()

    cookie = a.cookie or ""
    if not cookie and a.cookie_file:
        cookie = open(a.cookie_file, encoding="utf-8").read().strip()
    if not cookie:
        sys.exit("Butuh cookie: --cookie 'cf_clearance=...; __cf_bm=...' "
                 "atau --cookie-file cookies.txt (lihat docstring).")

    home = _req(BASE, cookie)
    pkgs = spse_pub.parse_packages(home, spse_pub.DEFAULT_SLUG)
    print("Halaman utama: %d paket" % len(pkgs))
    if not a.no_detail:
        for i, p in enumerate(pkgs, 1):
            print("  detail %d/%d: %s" % (i, len(pkgs), p["nama"][:48]))
            p = detail(p, cookie)
            time.sleep(1.0)  # sopan: jangan hantam server publik
    dt = dt_lelang(cookie, a.tahun)
    n_rows = len(dt.get("data") or dt.get("rows") or [])
    print("DataTables /dt/lelang: %s" % (str(n_rows) + " baris" if n_rows else dt.get("error", "kosong")))

    out = {
        "slug": spse_pub.DEFAULT_SLUG,
        "source": BASE,
        "scope": "kolektor laptop (Jalur B): halaman utama + detail + /dt/lelang "
                 "sesuai jangkauan sesi",
        "tahun": a.tahun,
        "packages": pkgs,
        "tender": [p for p in pkgs if p["jenis"] == "tender"],
        "nontender": [p for p in pkgs if p["jenis"] == "nontender"],
        "count": len(pkgs),
        "dt_lelang": dt,
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("Tersimpan: " + a.out)

    if a.push:
        body = json.dumps({"token": a.token, "data": out}).encode("utf-8")
        req = urllib.request.Request(a.push.rstrip("/") + "/api/spse-push",
                                     data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            print("Push → " + r.read().decode("utf-8")[:200])


if __name__ == "__main__":
    main()
