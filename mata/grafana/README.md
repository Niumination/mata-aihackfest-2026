# Grafana (opsional, untuk adegan dashboard di video)

Grafana bukan syarat wajib — MATA punya dashboard zero-dependency (`python3 run.py web -p 8080`).
Grafana dipilih jika kamu ingin "papan kontrol" yang lebih kaya di depan juri.

## Instalasi di VPS (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install -y grafana
sudo systemctl enable --now grafana-server
```

## Datasource SQLite (plugin)
```bash
sudo grafana-cli plugins install grafana-sqlite-datasource
sudo systemctl restart grafana-server
```
Buat datasource manual (UI → Connections → Data sources → Add → SQLite) dengan:
- Path: `/home/user/mata/data/mata.db`
atau provision otomatis:
```bash
mkdir -p /etc/grafana/provisioning/datasources
cp grafana/provisioning/datasources/mata-sqlite.yaml /etc/grafana/provisioning/datasources/
sudo systemctl restart grafana-server
```

## Dashboard
Import `grafana/dashboards/mata.json` (UI → Dashboards → Import).
Query memakai tabel `announcements` di `data/mata.db`.

## Panel yang disarankan
1. **Stat**: jumlah pengumuman, jumlah indikasi, total nilai pengadaan.
2. **Table** (indikasi): `SELECT rule, title, severity FROM flags` — atau join dari `runs`.
3. **Bar chart** (nilai per bulan): `SELECT substr(date_signed,1,7) m, SUM(value) v FROM announcements GROUP BY m ORDER BY m`
4. **Pie/bar** (konsentrasi vendor): `SELECT vendor, SUM(value) v FROM announcements GROUP BY vendor ORDER BY v DESC LIMIT 10`

> Catatan: tabel `flags` tidak ada di DB (flags disimpan di `data/flags_latest.json`
> agar web dashboard sederhana bisa membacanya). Untuk Grafana, cukup tampilkan
> panel berbasis `announcements` + `runs` — itu sudah cukup untuk video.
