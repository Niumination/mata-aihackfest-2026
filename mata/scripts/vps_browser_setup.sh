#!/usr/bin/env bash
# MATA — Setup stack browser di VPS (untuk Hermes).
# Kegunaan: (1) situs yang blokurnya FINGERPRINT/JS (bukan IP) — mis. SPSE
# bila test B' gagal, portal OPD; (2) basis untuk Jalur G2 bila nanti dipilih
# varian egress. Situs yang blokirnya IP-reputation (data.inaproc.id,
# isb.lkpp.go.id) TIDAK bisa diatasi dari VPS — lihat docs/15 ★5b.
#
# Jalankan di VPS (root):  bash scripts/vps_browser_setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── pasang playwright + chromium (butuh apt; ~200 MB)..."
python3 -m pip install -U playwright
python3 -m playwright install --with-deps chromium

echo "── verifikasi headless..."
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page()
    pg.goto("https://example.com", timeout=30000)
    print("✅ Chromium headless OK:", pg.title())
    b.close()
EOF
echo "Selesai. Pakai via: python3 -c 'from playwright.sync_api import sync_playwright' ..."
