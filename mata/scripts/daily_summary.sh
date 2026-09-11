#!/bin/bash
# MATA Daily Summary — dipanggil cron setiap 07.00
set -e

MATA_DIR="/root/Arck4li-AIHackfest/mata"
VENV="$MATA_DIR/.venv/bin/python3"

cd "$MATA_DIR"

# Jalankan cycle
$VENV run.py cycle > /tmp/mata-cycle.log 2>&1

# Generate ringkasan
$VENV -c "
import json, os
from datetime import datetime

base = '$MATA_DIR/data'
status = json.load(open(os.path.join(base, 'status.json')))
flags = json.load(open(os.path.join(base, 'flags_latest.json')))

levels = {}
for f in flags:
    s = f['severity']
    levels[s] = levels.get(s, 0) + 1

print(f'[MATA Laporan Harian {datetime.now().strftime(\"%Y-%m-%d %H:%M\")}]')
print(f'Monitor: {\"ONLINE\" if status[\"ok\"] else \"OFFLINE\"} | Data: {status[\"n_records\"]} pengumuman')
print(f'Indikasi: {status[\"n_flags\"]} total ({status[\"n_flags_tinggi\"]} tinggi)')
for lvl in ['tinggi','sedang','rendah']:
    if lvl in levels:
        print(f'  {lvl.upper()}: {levels[lvl]}')
print()
for f in flags:
    print(f'[{f[\"rule_id\"]} {f[\"severity\"].upper()}] {f[\"title\"]}')
print()
print('Ini indikasi berbasis data, bukan vonis.')
" > /tmp/mata-daily-summary.txt 2>&1

cat /tmp/mata-daily-summary.txt
