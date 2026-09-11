"""MATA — Iklim Gayo: advis kopi & siaga hidrometeorologi.

Port logika dari niu-gayo-agroclimate (milik pemilik, React) ke Python stdlib:
- 15 sentra agro-ekologi Aceh Tengah (koordinat sama persis).
- Ambang sama: suhu optimal 15–24°C, karat daun RH>85% + hangat,
  penjemuran via radiasi + hujan, longsor ≥25/50 mm, danau Lut Tawar/Peusangan,
  angin ≥20/35 km/jam.
- Data: Open-Meteo (gratis, tanpa key), diambil SERVER-SIDE + cache 30 menit,
  sehingga IP pengunjung tidak tersebar ke pihak ketiga (selaras UU PDP).
"""
import json
import os
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(BASE_DIR, "data", "iklim_cache.json")
TTL = 1800
UA = {"User-Agent": "MATA/0.3 (AI HackFest 2026; watchdog akuntabilitas pengadaan)"}

LOCATIONS = [
    {"id": "bebesan", "name": "Bebesan (Kemili)", "elev": 1250, "lat": 4.6275, "lon": 96.8491},
    {"id": "takengon", "name": "Takengon Kota", "elev": 1200, "lat": 4.6300, "lon": 96.8450},
    {"id": "pegasing", "name": "Pegasing", "elev": 1300, "lat": 4.5800, "lon": 96.8200},
    {"id": "kutepanang", "name": "Kute Panang", "elev": 1450, "lat": 4.6800, "lon": 96.7900},
    {"id": "atulintang", "name": "Atu Lintang", "elev": 1400, "lat": 4.4500, "lon": 96.8200},
    {"id": "jagongjeget", "name": "Jagong Jeget", "elev": 1450, "lat": 4.3800, "lon": 96.8000},
    {"id": "luttawar", "name": "Lut Tawar", "elev": 1200, "lat": 4.6100, "lon": 96.8800},
    {"id": "bintang", "name": "Bintang", "elev": 1210, "lat": 4.5800, "lon": 96.9500},
    {"id": "kebayakan", "name": "Kebayakan", "elev": 1220, "lat": 4.6500, "lon": 96.8500},
    {"id": "bies", "name": "Bies", "elev": 1350, "lat": 4.5900, "lon": 96.7800},
    {"id": "silihnara", "name": "Silih Nara (Angkup)", "elev": 1100, "lat": 4.6100, "lon": 96.7200},
    {"id": "ketol", "name": "Ketol", "elev": 950, "lat": 4.7500, "lon": 96.7500},
    {"id": "celala", "name": "Celala", "elev": 1200, "lat": 4.5000, "lon": 96.6500},
    {"id": "rusipantara", "name": "Rusip Antara", "elev": 1050, "lat": 4.4000, "lon": 96.5500},
    {"id": "linge", "name": "Linge (Isaq)", "elev": 900, "lat": 4.4200, "lon": 97.0200},
]
BY_ID = {loc["id"]: loc for loc in LOCATIONS}
LAKE_WATCH = {"luttawar", "bintang", "kebayakan", "takengon"}


def locations():
    return [{"id": loc["id"], "name": loc["name"]} for loc in LOCATIONS]


def _fetch(loc):
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={loc['lat']}&longitude={loc['lon']}"
           "&current=temperature_2m,relative_humidity_2m,precipitation,"
           "weather_code,wind_speed_10m"
           "&hourly=temperature_2m,precipitation,direct_normal_irradiance"
           "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
           "precipitation_probability_max"
           "&timezone=Asia%2FJakarta&forecast_days=1")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        if r.status != 200:
            raise RuntimeError(f"Open-Meteo HTTP {r.status}")
        return json.loads(r.read().decode("utf-8"))


def _advise(loc, data):
    cur = data["current"]
    daily = data["daily"]
    temp = cur["temperature_2m"]
    rh = cur["relative_humidity_2m"]
    rain = cur["precipitation"]
    wind = cur["wind_speed_10m"]
    solar = (data["hourly"].get("direct_normal_irradiance") or [0])[0]
    rain_sum = (daily.get("precipitation_sum") or [0])[0] or 0

    temp_s = "Optimal (15–24°C)" if 15 <= temp <= 24 else (
        "Dingin (vegetatif melambat)" if temp < 15
        else "Panas (waspada ceri prematur & PBKo)")
    if rh >= 85 and 18 <= temp <= 25:
        rust, rust_d = ("Tinggi",
            "RH >85% + hangat: kondusif spora karat daun. Periksa naungan & sanitasi.")
    elif rh >= 75:
        rust, rust_d = "Sedang", "Lembap tinggi; pantau tanaman di cekungan."
    else:
        rust, rust_d = "Rendah", "Kelembapan aman."
    if rain > 0.1:
        dry, dry_d = ("Tutup terpal", "Hujan turun; amankan kopi ke solar dryer.")
    elif solar < 150 or rh > 80:
        dry, dry_d = ("Kurang optimal", "Mendung/lembap; balik gabah lebih sering.")
    else:
        dry, dry_d = ("Sangat baik", "Radiasi kuat; penjemuran optimal.")
    if rain_sum >= 50 or rain >= 15:
        slide = "Bahaya tinggi"
    elif rain_sum >= 25 or rain >= 5:
        slide = "Waspada"
    else:
        slide = "Rendah"
    lake = ("Waspada luapan DAS Peusangan" if loc["id"] in LAKE_WATCH and rain_sum >= 40
            else "Normal")
    wind_s = ("Bahaya (peneduh roboh)" if wind >= 35
              else "Waspada angin kencang" if wind >= 20 else "Normal")

    return {
        "loc": {"id": loc["id"], "name": loc["name"], "elev": loc["elev"]},
        "current": {"temp": temp, "rh": rh, "rain": rain, "wind": wind,
                    "solar": round(solar or 0)},
        "daily": {"min": (daily.get("temperature_2m_min") or [None])[0],
                  "max": (daily.get("temperature_2m_max") or [None])[0],
                  "rain_prob": (daily.get("precipitation_probability_max") or [None])[0],
                  "rain_sum": rain_sum},
        "kopi": {"suhu": temp_s, "karat": rust, "karat_desc": rust_d,
                 "jemur": dry, "jemur_desc": dry_d},
        "siaga": {"longsor": slide, "danau": lake, "angin": wind_s},
    }


def get(loc_id):
    loc = BY_ID.get(loc_id or "takengon") or BY_ID["takengon"]
    now = time.time()
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            cache = json.load(f)
        hit = cache.get(loc["id"])
        if hit and now - hit["ts"] < TTL:
            out = dict(hit["data"])
            out["cached"] = True
            return out
    except Exception:
        cache = {}
    data = _fetch(loc)
    out = _advise(loc, data)
    out["cached"] = False
    cache[loc["id"]] = {"ts": now, "data": out}
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception:
        pass
    return out
