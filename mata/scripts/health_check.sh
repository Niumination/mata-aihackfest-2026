#!/bin/bash
# MATA Health Check — dipanggil cron setiap 6 jam
LOG="/tmp/mata-health.log"

if ! systemctl is-active --quiet mata; then
  systemctl restart mata
  echo "[MATA HEALTH] $(date): mata service down — restarted" >> "$LOG"
elif ! systemctl is-active --quiet mata-web; then
  systemctl restart mata-web
  echo "[MATA HEALTH] $(date): mata-web service down — restarted" >> "$LOG"
else
  echo "[MATA HEALTH] $(date): all services healthy" >> "$LOG"
fi
