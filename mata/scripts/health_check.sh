#!/bin/bash
# MATA Health Check — cron */6 jam. Cek: service, disk, RAM, umur siklus,
# API lokal, backend chat. Gagal → restart (service) + alert Telegram.
# Ponytail: satu file, stdlib/curl/systemctl saja.
LOG="/tmp/mata-health.log"
MATA_DIR="/root/Arck4li-AIHackfest/mata"
ALERT_SENT=0

log() { echo "[MATA HEALTH] $(date '+%F %T'): $1" >> "$LOG"; }

alert() {
  # maks 1 alert per run agar tak berisik
  [ "$ALERT_SENT" = 1 ] && return 0
  ALERT_SENT=1
  TOK=$(python3 -c "import json;print(json.load(open('$MATA_DIR/config.json'))['telegram']['token'])" 2>/dev/null)
  CHAT=$(python3 -c "import json;print(json.load(open('$MATA_DIR/config.json'))['telegram']['chat_id'])" 2>/dev/null)
  [ -n "$TOK" ] && curl -s --max-time 15 -X POST "https://api.telegram.org/bot$TOK/sendMessage" \
    -d "chat_id=$CHAT" --data-urlencode "text=🚨 MATA health: $1" -o /dev/null
  log "ALERT: $1"
}

for s in mata mata-web; do
  if ! systemctl is-active --quiet "$s"; then
    systemctl restart "$s"
    alert "$s down — restarted"
  fi
done

# disk >90% / RAM >90%
DISK=$(df / | awk 'NR==2{sub(/%/,"",$5); print $5}')
[ "$DISK" -ge 90 ] && alert "disk ${DISK}% penuh"
MEM=$(free | awk '/Mem/{printf "%.0f", $3/$2*100}')
[ "$MEM" -ge 90 ] && alert "RAM ${MEM}% penuh"

# siklus basi >3 jam?
AGE=$(python3 -c "
import json, time
s = json.load(open('$MATA_DIR/data/status.json'))
import datetime
t = datetime.datetime.fromisoformat(s.get('last_run','1970-01-01')).timestamp()
print(int(time.time()-t))" 2>/dev/null || echo 999999)
[ "$AGE" -gt 10800 ] && alert "siklus basi ${AGE}s"

# API lokal
for ep in status spse sapa inaproc analisis; do
  CODE=$(curl -s --max-time 10 -o /dev/null -w "%{http_code}" "http://127.0.0.1:80/api/$ep")
  [ "$CODE" != "200" ] && alert "/api/$ep HTTP $CODE"
done

# backend chat (tanpa pakai kuota: cek CLI ada)
command -v hermes >/dev/null || alert "hermes CLI hilang"

log "ok (disk ${DISK}%, ram ${MEM}%, siklus ${AGE}s)"
