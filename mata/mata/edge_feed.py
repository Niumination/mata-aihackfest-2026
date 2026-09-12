"""MATA — Edge Feed (Jalur G): penerima capture dari Edge Collector laptop.

Data.inaproc.id (dan situs ber-WAF IP-reputation serupa) memblokir IP
datacenter; penarikannya dilakukan oleh browser ASLI user di laptop/HP
(IP ISP) via scripts/edge_collect.py (CDP passive tap — bukan bypass).
Modul ini menerima push JSON-nya dan menumpuk di data/edge_feed.jsonl
(agregat mentah per URL; parsing skema dilakukan setelah capture pertama).

Fail-closed: tanpa edge.push_token di config.json (atau env
MATA_EDGE_PUSH_TOKEN) semua push ditolak.
"""
import json
import os
import secrets
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
FEED_PATH = os.path.join(BASE_DIR, "data", "edge_feed.jsonl")
MAX_ITEMS = 500
MAX_BODY = 5_000_000  # 5 MB per item


def _expected_token():
    env = os.environ.get("MATA_EDGE_PUSH_TOKEN")
    if env:
        return env
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return (json.load(f).get("edge") or {}).get("push_token") or None
    except Exception:
        return None


def push(token, payload):
    """Terima batch capture. Fail-closed: token salah/kosong => tolak."""
    want = _expected_token()
    if not want or not token or not secrets.compare_digest(str(token), str(want)):
        return {"ok": False, "error": "token tidak valid (set edge.push_token)"}
    if not isinstance(payload, dict):
        return {"ok": False, "error": "payload harus objek JSON"}
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return {"ok": False, "error": "bentuk payload salah (wajib: {items: [...]})"}
    items = items[:MAX_ITEMS]
    os.makedirs(os.path.dirname(FEED_PATH), exist_ok=True)
    n = 0
    with open(FEED_PATH, "a", encoding="utf-8") as f:
        for it in items:
            if not isinstance(it, dict) or not it.get("url"):
                continue
            body = it.get("body")
            size = len(json.dumps(body, ensure_ascii=False)) if body is not None else 0
            if size > MAX_BODY:
                body = {"_truncated": True, "bytes": it.get("bytes")}
            f.write(json.dumps({
                "received_at": time.time(),
                "device": payload.get("device"),
                "source": payload.get("source"),
                "captured_at": it.get("captured_at"),
                "url": it["url"],
                "status": it.get("status"),
                "bytes": it.get("bytes"),
                "body": body,
            }, ensure_ascii=False) + "\n")
            n += 1
    return {"ok": True, "n": n, "feed": "data/edge_feed.jsonl"}


def summary(limit=100):
    """Ringkasan feed untuk /api/edge (tanpa memuat seluruh isi)."""
    urls = {}
    last = []
    total = 0
    try:
        with open(FEED_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                total += 1
                u = r.get("url", "?").split("?")[0]
                urls[u] = urls.get(u, 0) + 1
                last.append({k: r.get(k) for k in
                             ("received_at", "url", "status", "bytes")})
                if len(last) > limit:
                    last.pop(0)
    except FileNotFoundError:
        pass
    return {"ok": True, "n": total,
            "urls": sorted(urls, key=lambda k: -urls[k])[:30],
            "url_counts": {k: urls[k] for k in sorted(urls, key=lambda k: -urls[k])[:30]},
            "last": last[-min(len(last), 10):]}
