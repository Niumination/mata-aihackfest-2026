#!/usr/bin/env python3
"""MATA — Edge Collector (Jalur G): tarik data dari browser ASLI user di laptop.

Konteks (12 Sep): data.inaproc.id memblokir IP datacenter di WAF (layanan di
baliknya "Akses Ditolak" + Ray ID) — keputusan WAF terjadi di EDGE berdasarkan
reputasi IP, SEBELUM aplikasi; dari IP yang sama, tak ada kombinasi
UA/header/TLS yang akan lolos. Browser HP/laptop (IP ISP + sidik jari browser
asli) lolos normal. Maka: JANGAN bypass — pindahkan PENARIKNYA ke perangkat
yang memang diizinkan, yaitu browser user sendiri.

Metode: CDP PASSIVE TAP (Chrome DevTools Protocol, port 9222). Skrip ini
TIDAK mengemudi browser, TIDAK memalsukan request, TIDAK membuka URL. Ia hanya
MENGAMATI respons jaringan dari tab yang user buka sendiri (situs yang
dikonfigurasi), menyimpan payload JSON yang halaman itu sendiri minta — persis
yang terlihat manusia — lalu (opsional) push ke MATA VPS via /api/edge-push
(token; pola sama dengan spse_collect.py).

Legal: data mengalir persis seperti browsing manusia di perangkat & sesi user
sendiri; tidak ada pemblokiran yang dilompati, tidak ada autentikasi yang
dilawan, volume = satu halaman manusia.

Dependensi: websocket-client  (pip install websocket-client — sekali saja)
Sisanya stdlib. Token push = config.json VPS: edge.push_token.

Cara pakai (di laptop):
  1. Tutup semua tab Chrome, lalu buka Chrome dengan flag debug:
       macOS: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \
                --remote-debugging-port=9222
       Linux: google-chrome --remote-debugging-port=9222
       Win:   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" \
                --remote-debugging-port=9222
  2. Jalankan skrip:  python3 scripts/edge_collect.py --host data.inaproc.id
     (skrip menunggu & siap mendengar)
  3. DI CHROME: buka URL data.inaproc.id yang menampilkan data RUP, login bila
     perlu, klik sampai tabel data muncul. Skrip menangkap respons JSON-nya.
  4. Setelah selesai (skrip berhenti saat --wait habis, atau Ctrl+C):
     - tanpa --push : capture tersimpan di data/edge_capture.jsonl
     - --push       : juga dikirim ke VPS (butuh --url dan --token)
"""
import argparse
import json
import os
import platform
import re
import socket
import sys
import time
import urllib.request

CDP_HTTP = "http://127.0.0.1:9222"


def _now():
    return time.time()


def cdp_targets():
    req = urllib.request.Request(CDP_HTTP + "/json/list")
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


class Tap:
    """Pengamat pasif satu tab CDP: kumpulkan respons host yang dicocokkan."""

    def __init__(self, ws, host):
        self.ws = ws
        self.host = host
        self.pending = {}     # requestId -> {url, status, mime}
        self.queued = []      # requestId siap diambil body-nya
        self.inflight = {}    # msg_id -> requestId
        self.next_id = 50
        self.captures = []
        self._send("Network.enable")

    def _send(self, method, params=None):
        self.next_id += 1
        self.ws.send(json.dumps({"id": self.next_id, "method": method,
                                 "params": params or {}}))
        return self.next_id

    def _send_body(self, rid):
        mid = self._send("Network.getResponseBody", {"requestId": rid})
        self.inflight[mid] = rid

    def handle(self, m):
        method = m.get("method")
        if method == "Network.responseReceived":
            p = m.get("params") or {}
            resp = p.get("response") or {}
            url = resp.get("url", "")
            if self.host in url and p.get("requestId"):
                self.pending[p["requestId"]] = {
                    "url": url,
                    "status": resp.get("status"),
                    "mime": resp.get("mimeType", ""),
                }
        elif method == "Network.loadingFinished":
            rid = (m.get("params") or {}).get("requestId")
            if rid in self.pending:
                self.queued.append(rid)
        elif "id" in m:
            rid = self.inflight.pop(m["id"], None)
            if rid is None:
                return
            result = m.get("result") or {}
            info = self.pending.pop(rid, {})
            if result.get("base64Encoded"):
                import base64
                raw = base64.b64decode(result.get("body", ""))
            else:
                raw = (result.get("body") or "").encode("utf-8", "replace")
            if not raw:
                return  # body belum tersedia / dibersihkan Chrome
            body_txt = raw.decode("utf-8", "replace")
            # simpan JSON apa adanya (API data.inaproc.id) + teks kecil lain
            keep = (info.get("mime") or "").startswith("application/json") \
                or "/api/" in info.get("url", "") \
                or body_txt.lstrip()[:1] in "{["
            if not keep and len(raw) > 200_000:
                return
            body = None
            try:
                body = json.loads(body_txt)
            except Exception:
                body = body_txt[:200_000]
            self.captures.append({
                "captured_at": _now(),
                "url": info.get("url"),
                "status": info.get("status"),
                "bytes": len(raw),
                "body": body,
            })
            print("  + %-8s %6dB  %s" % (str(info.get("status")), len(raw),
                                         info.get("url", "")[:110]))

    def step(self, timeout=2.0):
        """Proses satu pesan WS; kirim getBody bila ada antrean & slot kosong."""
        if self.queued and not self.inflight:
            self._send_body(self.queued.pop(0))
        while True:
            try:
                m = json.loads(self.ws.recv())
            except Exception:
                return  # timeout / socket tertutup — loop utama yang memutuskan
            self.handle(m)
            if "id" not in m:
                # pesan event: lanjut dengar (maks 5 event per step)
                continue
            return


def main():
    ap = argparse.ArgumentParser(description="MATA Edge Collector (CDP tap)")
    ap.add_argument("--host", default="data.inaproc.id",
                    help="host yang diamati (default: data.inaproc.id)")
    ap.add_argument("--wait", type=int, default=300,
                    help="detik mengamati (default 300)")
    ap.add_argument("--out", default=None,
                    help="file JSONL capture (default data/edge_capture.jsonl)")
    ap.add_argument("--push", action="store_true",
                    help="push capture ke MATA VPS setelah selesai")
    ap.add_argument("--url", default=os.environ.get("MATA_URL", ""),
                    help="base URL MATA VPS, mis. https://HOST:8080")
    ap.add_argument("--token", default=os.environ.get("MATA_EDGE_PUSH_TOKEN", ""),
                    help="edge.push_token dari config.json VPS")
    a = ap.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = a.out or os.path.join(base_dir, "data", "edge_capture.jsonl")

    try:
        import websocket  # websocket-client
    except ImportError:
        sys.exit("Kebutuhan: pip install websocket-client  (satu kali saja)")

    try:
        targets = cdp_targets()
    except Exception as e:
        sys.exit("Gagal menghubungi Chrome di 127.0.0.1:9222 (%s).\n"
                 "Buka Chrome dengan --remote-debugging-port=9222 (tab baru, "
                 "profil yang sudah login)." % e)
    pages = [t for t in targets if t.get("type") == "page"
             and t.get("webSocketDebuggerUrl")]
    if not pages:
        sys.exit("Tidak ada tab page di Chrome debug — buka satu tab dulu.")
    ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"],
                                     timeout=3)
    tap = Tap(ws, a.host)
    print("MATA Edge Collector — mengamati host: %s" % a.host)
    print("Tab: %s" % pages[0].get("url", "")[:100])
    print("KINI buka halaman-nya di Chrome & klik sampai data muncul. "
          "Berhenti setelah %d dtk (atau Ctrl+C).\n" % a.wait)
    deadline = _now() + a.wait
    try:
        while _now() < deadline:
            tap.step(timeout=2.0)
            if _now() + 2.0 >= deadline:
                break
    except KeyboardInterrupt:
        print("\n(dihentikan Ctrl+C)")
    finally:
        try:
            ws.close()
        except Exception:
            pass

    n = len(tap.captures)
    print("\nTercatat: %d respons dari %s" % (n, a.host))
    if n == 0:
        print("Tips: pastikan halaman yang dibuka benar-benar host %s dan "
              "data tampil dari XHR/fetch (bukan dari cache — buka ulang "
              "halaman dengan Ctrl+Shift+R saat skrip berjalan)." % a.host)
        return
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        for c in tap.captures:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print("Tersimpan: %s" % out_path)
    urls = sorted({c["url"].split("?")[0] for c in tap.captures})
    print("Endpoint unik (%d):" % len(urls))
    for u in urls[:15]:
        print("  - " + u)

    if a.push:
        if not (a.url and a.token):
            print("SKIP push: butuh --url dan --token")
            return
        payload = {"token": a.token, "source": "edge-collector",
                   "device": "%s/%s" % (platform.node(), sys.platform),
                   "items": tap.captures}
        req = urllib.request.Request(
            a.url.rstrip("/") + "/api/edge-push",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print("PUSH: %s" % r.read().decode("utf-8", "replace")[:200])
        except Exception as e:
            print("PUSH GAGAL: %s (capture tetap aman di %s)" % (e, out_path))


if __name__ == "__main__":
    main()
