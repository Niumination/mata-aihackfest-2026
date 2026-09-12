#!/usr/bin/env python3
"""MATA — RUP Browser Collector (Jalur G2): browser dioperasikan HERMES, mesin di laptop.

Arsitektur (12 Sep): WAF data.inaproc.id menolak IP datacenter di lapisan
jaringan (reputasi ASN) — browser sedetail apa pun di VPS tetap ditolak.
Maka: browser headless dipasang di LAPTOP (IP ISP = profil yang sah bagi WAF),
sedangkan OTAK-nya tetap Hermes di VPS yang menjalankan script ini lewat SSH:

    ssh LAPTOP "cd /path/repo && python3 scripts/rup_browser_collect.py \
        --url 'https://data.inaproc.id/...' --push --url https://VPS:8080 \
        --token <edge.push_token>"

Setup SEKALI di laptop:
    pip install playwright
    python3 -m playwright install chromium
    # bila halaman butuh login: jalankan sekali dengan --headed, login manual,
    # sesi tersimpan di data/browser_profile/ → eksekusi berikutnya headless.

Capture: respons JSON (XHR/fetch) dari host yang ditarget — bentuk file sama
dengan CDP tap (Jalur G1) sehingga VPS menerima lewat /api/edge-push yang
sudah ada. Etika: 1 halaman manusia, volume rendah, tanpa manipulasi sesi
operator; profil browser dipakai apa adanya.
"""
import argparse
import json
import os
import platform
import sys
import time
import urllib.parse
import urllib.request


def push_to_vps(base_url, token, captures, device):
    payload = {"token": token, "source": "rup-browser-collector",
               "device": "%s/%s" % (platform.node(), sys.platform),
               "items": captures}
    req = urllib.request.Request(
        base_url.rstrip("/") + "/api/edge-push",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")[:200]


def main():
    ap = argparse.ArgumentParser(description="MATA RUP Browser Collector (Jalur G2)")
    ap.add_argument("--url", required=True,
                    help="URL halaman yang menampilkan data (mis. halaman RUP)")
    ap.add_argument("--host", default=None,
                    help="host yang dicapture (default: host dari --url)")
    ap.add_argument("--wait", type=int, default=25,
                    help="detik tunggu setelah load agar XHR sempat masuk (default 25)")
    ap.add_argument("--headed", action="store_true",
                    help="tampilkan window browser (untuk login manual sekali)")
    ap.add_argument("--screenshot", action="store_true", help="simpan bukti visual")
    ap.add_argument("--out", default=None,
                    help="file JSONL (default data/edge_capture.jsonl)")
    ap.add_argument("--push", action="store_true", help="push ke MATA VPS")
    ap.add_argument("--url-vps", dest="vps_url", default=os.environ.get("MATA_URL", ""),
                    help="base URL MATA VPS (mis. https://HOST:8080)")
    ap.add_argument("--token", default=os.environ.get("MATA_EDGE_PUSH_TOKEN", ""),
                    help="edge.push_token dari config.json VPS")
    a = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Kebutuhan laptop: pip install playwright && "
                "python3 -m playwright install chromium")

    host = a.host or urllib.parse.urlparse(a.url).netloc
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile = os.path.join(base_dir, "data", "browser_profile")
    out_path = a.out or os.path.join(base_dir, "data", "edge_capture.jsonl")
    os.makedirs(profile, exist_ok=True)

    print("G2: buka %s (capture host: %s, tunggu %ds, headed=%s)"
          % (a.url, host, a.wait, a.headed))
    collected = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            profile,
            headless=not a.headed,
            viewport={"width": 1440, "height": 900},
            locale="id-ID",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        def on_response(resp):
            try:
                u = resp.url
            except Exception:
                return
            if host in u and resp.status < 400:
                ct = (resp.headers or {}).get("content-type", "")
                if "json" in ct or "/api/" in u:
                    collected.append(resp)
                    print("  ~ %s %s" % (resp.status, u[:110]))

        page.on("response", on_response)
        page.goto(a.url, wait_until="load", timeout=90_000)
        if a.headed:
            print("Mode HEADED: selesaikan login (jika ada), lalu tutup tab "
                  "ini setelah data tampil — atau biarkan %ds untuk capture."
                  % a.wait)
        # beri waktu XHR; gulir pelan agar tabel lazy-load terpicu
        for _ in range(a.wait):
            try:
                page.mouse.wheel(0, 400)
            except Exception:
                pass
            page.wait_for_timeout(1000)
        if a.screenshot:
            shot = os.path.join(base_dir, "data",
                                "edge_screenshot_%s.png" % int(time.time()))
            try:
                page.screenshot(path=shot, full_page=False)
                print("  screenshot: %s" % shot)
            except Exception as e:
                print("  screenshot gagal: %s" % e)
        # ambil body setelah semua XHR masuk
        captures = []
        for resp in collected:
            try:
                body = resp.json()
            except Exception:
                try:
                    body = resp.text()[:200_000]
                except Exception:
                    continue
            captures.append({
                "captured_at": time.time(),
                "url": resp.url,
                "status": resp.status,
                "bytes": None,
                "body": body,
            })
        ctx.close()

    n = len(captures)
    print("Tercatat: %d respons JSON dari %s" % (n, host))
    if n == 0:
        print("Tips: jalankan sekali dengan --headed --screenshot, pastikan data "
              "benar-benar tampil di halaman, lalu ulangi tanpa --headed. "
              "Bila halaman butuh login, login manual dulu saat --headed.")
        return
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        for c in captures:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print("Tersimpan: %s" % out_path)
    for u in sorted({c["url"].split("?")[0] for c in captures})[:15]:
        print("  - " + u)
    if a.push:
        if not (a.vps_url and a.token):
            print("SKIP push: butuh --url-vps dan --token")
            return
        try:
            print("PUSH: %s" % push_to_vps(a.vps_url, a.token, captures,
                                           platform.node()))
        except Exception as e:
            print("PUSH GAGAL: %s (capture aman di %s)" % (e, out_path))


if __name__ == "__main__":
    main()
