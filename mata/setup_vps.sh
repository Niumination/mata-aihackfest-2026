#!/usr/bin/env bash
# MATA — instalasi cepat di VPS (AI Hosting IDwebhost x CloudBaik)
# Jalankan: bash setup_vps.sh
set -e
cd "$(dirname "$0")"

echo "==> 1/5 Dependensi (venv + pip)..."
python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt

echo "==> 2/5 Inisialisasi DB + dataset demo..."
python3 run.py setup

echo "==> 3/5 Siklus pertama (collect -> analyze -> dossier -> status)..."
python3 run.py cycle

echo "==> 4/5 Uji akses sumber data live (opsional, info saja)..."
python3 run.py probe || echo "   (beberapa sumber tidak terjangkau dari sini — normal; pakai mode synthetic untuk demo)"

echo "==> 5/5 Selesai."
echo ""
echo "Selanjutnya:"
echo "  python3 run.py web -p 8080     # dashboard status (bind 0.0.0.0)"
echo "  python3 run.py demo            # 5 skenario demo (latihan video)"
echo "  sudo cp deploy/mata.service /etc/systemd/system/ && sudo systemctl enable --now mata   # 24/7"
echo ""
echo "Lengkapi config.json: telegram.token + telegram.chat_id (lihat runbook Hari 1)."
