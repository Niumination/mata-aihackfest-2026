#!/usr/bin/env python3
"""MATA — pembuat snapshot statis dashboard (single-file HTML).

Ungkap sistem live menjadi SATU file HTML mandiri (self-contained) yang bisa:
  1. di-commit ke repo (bukti/arsip utk juri setelah VM mati),
  2. di-deploy ke hosting statis (Netlify/Vercel) sebagai pengganti domain pasca-VM.

Cara pakai (Python 3 stdlib saja, tanpa dependensi):
  python3 scripts/make_snapshot.py                      # default: https://mata.niumination.web.id
  python3 scripts/make_snapshot.py --base http://127.0.0.1:80   # dari VPS/laptop lokal
  python3 scripts/make_snapshot.py --out snapshot/dashboard-live.html

Semua endpoint /api/* di-capture dan disuntik sebagai stub fetch, sehingga halaman
snapshot tetap berfungsi penuh (analisis, simulator, peta, unduh CSV) tanpa backend.
Chat & locate dinonaktifkan jujur (respons "static mode").
"""
import argparse
import base64
import datetime as dt
import json
import sys
import urllib.request

UA = {"User-Agent": "MATA-snapshot/1.0"}

GETS = [
    "/api/status", "/api/flags", "/api/analisis", "/api/health",
    "/api/iklim", "/api/inaproc", "/api/sapa", "/api/spse", "/api/visitors",
]


def fetch(base, path, timeout=60):
    req = urllib.request.Request(base + path, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://mata.niumination.web.id")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    base = args.base.rstrip("/")

    print(f"[1/4] Capture halaman + API dari {base}")
    page = fetch(base, "/")
    data = {}
    for p in GETS:
        try:
            raw = fetch(base, p)
            data[p] = json.loads(raw.decode("utf-8"))
            print(f"      {p:18s} {len(raw):>8,} B")
        except Exception as e:
            data[p] = None
            print(f"      {p:18s} GAGAL: {e}")
    try:
        csv_raw = fetch(base, "/api/records.csv")
        print(f"      /api/records.csv   {len(csv_raw):>8,} B")
    except Exception as e:
        csv_raw = b""
        print(f"      /api/records.csv   GAGAL: {e}")

    ts = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
    print("[2/4] Susun snapshot self-contained")
    # buang script tracking Cloudflare (dijamin tidak ada di hosting statis lain)
    import re as _re
    html_page = page.decode("utf-8")
    n_cf = len(_re.findall(r'<script[^>]*cloudflareinsights[^>]*></script>', html_page))
    html_page = _re.sub(r'\s*<script[^>]*cloudflareinsights[^>]*></script>', '', html_page)
    print(f"      {n_cf} script tracking Cloudflare dibuang")
    snap = json.dumps(
        {k: v for k, v in data.items()}, ensure_ascii=False,
    )
    csv_b64 = base64.b64encode(csv_raw).decode("ascii")
    flags_b64 = base64.b64encode(json.dumps(data.get("/api/flags") or [], ensure_ascii=False).encode()).decode("ascii")

    stub = f"""
<script id="mata-snapshot-stub">
(function(){{
  var SNAP = {snap};
  var CSV_B64 = "{csv_b64}";
  var csvText = function(){{
    try{{ return decodeURIComponent(escape(atob(CSV_B64))); }}catch(e){{ return ""; }}
  }};
  function fake(status, body, type){{
    return new Promise(function(res){{
      res(new Response(body, {{status: status, headers: {{"Content-Type": type || "application/json"}}}}));
    }});
  }}
  var realFetch = window.fetch.bind(window);
  window.fetch = function(input, init){{
    var url = (typeof input === "string") ? input : input.url;
    var path = url.split("?")[0].replace(location.origin, "");
    var method = ((init && init.method) || "GET").toUpperCase();
    if (method === "GET") {{
      if (path === "/api/records.csv") return fake(200, csvText(), "text/csv");
      if (SNAP[path] !== undefined) return fake(200, JSON.stringify(SNAP[path]), "application/json");
    }}
    if (path === "/api/chat") return fake(200, JSON.stringify({{ok:false, error:"Static mode — chat hidup hanya selama periode live (hingga 15 Sep 2026)."}}));
    if (path === "/api/locate") return fake(200, JSON.stringify({{ok:false, error:"static"}}));
    if (path === "/api/forget") return fake(200, JSON.stringify({{ok:true}}));
    return realFetch(input, init);
  }};
}})();
</script>
"""
    banner = f"""
<div style="position:sticky;top:0;z-index:99999;background:#1a120b;border-bottom:1px solid #3a2a1c;color:#e8d9c5;font:12px/1.6 'JetBrains Mono',monospace;padding:8px 16px;display:flex;gap:12px;align-items:center">
  <span style="color:#ff6a3d;font-weight:700">▣ STATIC SNAPSHOT</span>
  <span>ditangkap {ts} dari <b>{base}</b> · sistem live berakhir dgn penonaktifan VM Batch 3 (15 Sep 2026 23.59 WIB) · data beku pada saat capture · unduh CSV &amp; API tetap berfungsi</span>
</div>
"""
    html = html_page
    # stub fetch sebelum script halaman (setelah tag <head> utuh)
    m = _re.search(r'<head[^>]*>', html)
    if m:
        html = html[:m.end()] + stub + html[m.end():]
    else:
        html = stub + html
    # banner setelah tag <body> utuh
    m = _re.search(r'<body[^>]*>', html)
    if m:
        html = html[:m.end()] + banner + html[m.end():]
    # link unduh -> data URI
    html = html.replace('href="/api/records.csv"', f'href="data:text/csv;base64,{csv_b64}"')
    html = html.replace('href="/api/flags"', f'href="data:application/json;base64,{flags_b64}"')
    # tandai <title>
    html = html.replace("<title>", "<title>[SNAPSHOT] ", 1)

    out = args.out or f"snapshot/dashboard-live-{dt.date.today().isoformat()}.html"
    import os
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[3/4] Selesai: {out} ({len(html):,} B)")
    print("[4/4] Uji cepat: buka file di browser — semua seksi harus ter-render, 0 error fatal, CSV bisa diunduh.")


if __name__ == "__main__":
    main()
