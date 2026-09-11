"""Web dashboard MATA — susunan "living codex": hero gelap + grid arsip|graf|pembaca.

Rute:
  /                 dashboard (hero, graf indikasi, arsip, konteks, pengunjung)
  /api/status       status monitor (JSON)
  /api/flags        indikasi terkini (JSON)
  /api/visitors     statistik pengunjung (JSON)
  /api/records.csv  seluruh record (CSV, untuk verifikasi publik)

Pembuka (boot): overlay fullscreen + backsound sintesis WebAudio (klik MASUK).
"""
import csv
import html
import io
import json
import math
import os
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import db
from . import visitors

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _status():
    if os.path.exists(db.STATUS_PATH):
        with open(db.STATUS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"ok": False, "last_error": "belum ada siklus"}


def _rupiah(v):
    try:
        return f"Rp {int(v or 0):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "-"


def _esc(s):
    return html.escape(str(s or ""), quote=True)


def _mode(recs):
    """LIVE jika ada record dari INAPROC, selain itu SYNTHETIC (demo)."""
    for r in recs:
        rid = str(r.get("id", ""))
        src = str(r.get("source", ""))
        if rid.startswith("INP-") or "INAPROC" in src.upper():
            return "LIVE"
    return "SYNTHETIC"


def _open_ctx():
    p = os.path.join(BASE_DIR, "data", "open_context.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


SEV_STYLE = {"tinggi": ("#c0392b", 26), "sedang": ("#d97c1e", 20), "rendah": ("#4a7c3a", 15)}


def _graph_svg(flags, vendors):
    """SVG konstelasi: MATA di inti, indikasi di orbit dalam, vendor di orbit luar."""
    cx, cy = 320, 230
    parts = [f'<circle cx="{cx}" cy="{cy}" r="34" fill="#221e19" stroke="#e05a1e" stroke-width="3"/>',
             f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" fill="#f5efe6" font-size="16" '
             f'font-family="Georgia,serif" font-style="italic">M</text>']
    nf = max(len(flags), 1)
    for i, f in enumerate(flags):
        a = -math.pi / 2 + 2 * math.pi * i / nf
        x, y = cx + 120 * math.cos(a), cy + 120 * math.sin(a)
        color, r = SEV_STYLE.get(f["severity"], ("#888", 15))
        rid = _esc(f["rule_id"])
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="#e05a1e" stroke-opacity=".35"/>')
        parts.append(
            f'<g class="gnode" data-rule="{rid}" data-sev="{_esc(f["severity"])}">'
            f'<title>[{rid}] {_esc(f["title"])}</title>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{color}" fill-opacity=".88"/>'
            f'<text x="{x:.0f}" y="{y - r - 7:.0f}" text-anchor="middle" fill="#f5efe6" '
            f'font-size="13" font-family="monospace" font-weight="bold">{rid}</text></g>')
    nv = max(len(vendors), 1)
    for i, (name, d) in enumerate(vendors[:6]):
        a = -math.pi / 2 + 2 * math.pi * i / nv + math.pi / nv
        x, y = cx + 200 * math.cos(a), cy + 200 * math.sin(a)
        if abs(x - cx) > 305:
            x = cx + 305 * (1 if x > cx else -1)
        if y < 20:
            y = 20
        if y > 440:
            y = 440
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="#f5efe6" stroke-opacity=".15"/>')
        parts.append(
            f'<g class="gnode" data-vendor="{_esc(name)}">'
            f'<title>{_esc(name)} — {d["n"]} proyek</title>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="#f5efe6" fill-opacity=".8"/>'
            f'<text x="{x:.0f}" y="{y + 22:.0f}" text-anchor="middle" fill="#f5efe6" '
            f'fill-opacity=".65" font-size="10" font-family="monospace">'
            f'{_esc(name.split(" ")[0] + " " + (name.split(" ")[1][:4] + "." if len(name.split(" ")) > 1 else ""))}</text></g>')
    return "".join(parts)


def _minimap(locations):
    """Peta sketsa Indonesia (SVG mandiri) + pin kota/GPS hari ini."""
    def xy(lat, lon):
        x = 20 + (lon - 94.3) / 46.7 * 600
        y = 20 + (6 - lat) / 17 * 320
        return (round(x), round(y))
    isles = (
        # Sumatera (gemuk utara-tengah, meruncing ke selatan)
        "M22,28 C48,52 72,86 94,122 C114,156 136,192 162,238 L140,250 "
        "C118,214 96,178 74,140 C60,116 44,100 30,84 C18,68 10,48 6,38 Z "
        # Jawa (ramping, ujung meruncing) + Madura
        "M158,254 C190,248 232,248 272,256 L276,263 C238,263 194,262 156,261 Z "
        "M292,250 L314,248 L311,259 L290,260 Z "
        # Kalimantan (bahu barat lebar, ekor tenggara)
        "M222,84 C258,60 302,64 322,96 C332,118 330,150 322,175 "
        "C330,195 334,215 328,232 C310,238 292,228 282,210 "
        "C260,224 232,214 222,190 C212,165 210,112 222,84 Z "
        # Sulawesi (tulang + 3 lengan ke timur)
        "M348,108 C356,140 354,175 346,205 C352,225 365,240 382,248 "
        "L374,260 C352,250 340,228 336,200 C331,170 334,135 340,110 Z "
        "M348,122 L408,104 L410,116 L350,134 Z "
        "M346,160 L400,158 L398,172 L346,174 Z "
        # Papua + kepala burung
        "M483,168 C522,152 576,158 616,180 C626,198 614,232 584,258 "
        "C550,278 502,270 480,240 C466,216 468,184 483,168 Z "
        "M481,172 C468,162 458,148 461,136 C473,138 483,153 487,168 Z "
        # Nusa Tenggara
        "M333,290 L385,287 L383,297 L335,299 Z "
        "M325,306 L350,304 L348,314 L327,314 Z "
        "M392,315 L432,312 L430,323 L394,324 Z "
        # Maluku
        "M478,100 L498,95 L502,140 L488,165 L476,140 Z "
        "M478,186 L508,184 L506,196 L480,196 Z")
    dots = [(55, 110, 4), (282, 282, 4), (296, 290, 3), (175, 225, 4),
            (150, 210, 3), (70, 178, 4), (430, 108, 3), (540, 250, 3), (560, 235, 3)]
    parts = [
        f'<path d="{isles}" fill="#6b573d" stroke="#f0a35e" stroke-width="1.5"/>',
        "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#6b573d" '
                 f'stroke="#f0a35e" stroke-width="1"/>' for x, y, r in dots),
        ('<text x="24" y="346" font-size="11" font-family="monospace" '
         'letter-spacing="3" fill="rgba(245,239,230,.5)">SKETSA NUSANTARA · SEBARAN HARI INI</text>'),
        ('<g transform="translate(606,36)" stroke="rgba(245,239,230,.6)" fill="none">'
         '<circle r="12"/><path d="M0,7 L0,-7 M-4,-2 L0,-7 L4,-2"/>'
         '<text y="-18" text-anchor="middle" font-size="10" font-family="monospace" '
         'fill="rgba(245,239,230,.6)" stroke="none">U</text></g>'),
    ]
    for g in range(96, 142, 5):
        x, _ = xy(0, g)
        parts.append(f'<line x1="{x}" y1="10" x2="{x}" y2="350" stroke="rgba(245,239,230,.06)"/>')
    for la in range(5, -12, -4):
        _, y = xy(la, 95)
        parts.append(f'<line x1="10" y1="{y}" x2="630" y2="{y}" stroke="rgba(245,239,230,.06)"/>')
    coords = visitors.city_coords()
    plotted, outside, placed = 0, 0, []
    for loc in locations:
        key = (loc.get("city") or "").lower()
        lat, lon = loc.get("lat"), loc.get("lon")
        if lat is None or lon is None:
            if key in coords:
                lat, lon = coords[key]
            else:
                outside += loc.get("count", 0)
                continue
        try:
            x, y = xy(float(lat), float(lon))
        except (TypeError, ValueError):
            outside += loc.get("count", 0)
            continue
        n = loc.get("count", 1)
        r = 6 + min(n, 9)
        ly = y + r + 17 if y < 80 else y - r - 6
        lx = min(max(x, 78), 562)
        while any(abs(lx - px) < 72 and abs(ly - py) < 18 for px, py in placed):
            ly += 20
        placed.append((lx, ly))
        parts.append(
            f'<g class="pin"><title>{_esc(loc.get("city"))} — {n} kunjungan</title>'
            f'<circle cx="{x}" cy="{y}" r="{r + 8}" fill="#e05a1e" fill-opacity=".18">'
            f'<animate attributeName="r" values="{r + 4};{r + 11};{r + 4}" dur="2.4s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e05a1e" stroke="#ffd9ad" stroke-width="1.5"/>'
            f'<circle cx="{x}" cy="{y}" r="2.2" fill="#fff7ea"/>'
            f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="11.5" font-weight="bold" '
            f'font-family="monospace" fill="none" stroke="#14100c" stroke-width="5">'
            f'{_esc(loc.get("city"))} · {n}</text>'
            f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="11.5" font-weight="bold" '
            f'font-family="monospace" fill="#f5efe6">'
            f'{_esc(loc.get("city"))} · {n}</text></g>')
        plotted += 1
    note = f"{outside} kunjungan di luar peta. " if outside else ""
    return ("".join(parts),
            f"Sketsa — {plotted} titik hari ini. {note}Titik GPS dibulatkan ~1 km; "
            f"titik kota = perkiraan wilayah.")


def render():
    st = _status()
    flags = db.read_flags()
    recs = db.load_records()
    mode = _mode(recs)
    by_vendor = {}
    by_month = {}
    for r in recs:
        if r.get("vendor"):
            d = by_vendor.setdefault(r["vendor"], {"n": 0, "value": 0.0})
            d["n"] += 1
            d["value"] += r["value"] or 0
        if r.get("date_signed"):
            by_month[r["date_signed"][:7]] = by_month.get(r["date_signed"][:7], 0) + (r["value"] or 0)
    vendors = sorted(by_vendor.items(), key=lambda kv: -kv[1]["value"])[:8]
    months = sorted(by_month.items())
    max_m = max((v for _, v in months), default=1)
    max_v = max((d["value"] for _, d in vendors), default=1)

    ok = st.get("ok")
    n_flags = st.get("n_flags", len(flags))
    n_records = st.get("n_records", len(recs))
    badge = ('<span class="badge ok">● ONLINE</span>' if ok
             else '<span class="badge err">● ERROR</span>')
    mode_badge = ('<span class="badge live">MODE: LIVE</span>' if mode == "LIVE"
                  else '<span class="badge syn">MODE: SYNTHETIC</span>')

    ticker_items = "".join(
        f'<span class="tk-item"><b>[{_esc(f["rule_id"])} · {_esc(f["severity"].upper())}]</b> '
        f'{_esc(f["title"])}</span><span class="tk-sep">◆</span>' for f in flags)

    sev_class = {"tinggi": "sev-tinggi", "sedang": "sev-sedang", "rendah": "sev-rendah"}
    flag_cards = ""
    for f in flags:
        sev = sev_class.get(f["severity"], "")
        ev = "".join(f"<li>{_esc(e)}</li>" for e in (f.get("evidence") or []))
        rids = ", ".join(_esc(x) for x in (f.get("record_ids") or []))
        flag_cards += (
            f'<details class="flag" id="flag-{_esc(f["rule_id"])}" data-sev="{_esc(f["severity"])}">'
            f'<summary><span class="rule">[{_esc(f["rule_id"])}]</span> '
            f'<span class="{sev}">{_esc(f["severity"].upper())}</span>'
            f'<span class="flag-title">{_esc(f["title"])}</span></summary>'
            f'<ul class="ev">{ev}</ul>'
            f'<div class="meta">Record: <b>{rids or "-"}</b></div>'
            f'<div class="meta">Penjelasan: {_esc(f.get("explanation", ""))}</div>'
            f'<div class="meta">Langkah lanjut: {_esc(f.get("recommendation", ""))}</div>'
            f'</details>')

    chips = "".join(
        f'<button class="chip" data-v="{_esc(name)}">{_esc(name)} <b>{d["n"]}</b></button>'
        for name, d in vendors)

    vendor_rows = ""
    for name, d in vendors:
        pct = d["value"] / max_v * 100 if max_v else 0
        vendor_rows += (f'<tr><td>{_esc(name)}</td><td class="num">{d["n"]}</td>'
                        f'<td class="num mono">{_rupiah(d["value"])}</td>'
                        f'<td><div class="bar"><div style="width:{pct:.0f}%"></div></div></td></tr>')
    month_bars = ""
    for m, v in months:
        h = max(4, int(v / max_m * 120)) if max_m else 4
        cls = "bar-dec" if m.endswith("-12") else "bar"
        month_bars += (f'<div class="mcol"><div class="{cls}" style="height:{h}px"></div>'
                       f'<div class="mlabel">{_esc(m[5:])}/{_esc(m[2:4])}</div>'
                       f'<div class="mval mono">{v / 1e9:.1f}M</div></div>')

    pkg_rows = ""
    for r in sorted(recs, key=lambda x: str(x.get("id"))):
        url = r.get("url")
        live = url and "synthetic" not in str(r.get("source", "")).lower()
        if live:
            src = f'<a href="{_esc(url)}" target="_blank" rel="noopener">sumber ↗</a>'
        elif url:
            src = ('<span class="demo-tag" title="Data demo — tautan ilustrasi. '
                   'Tautan live aktif setelah data INAPROC masuk.">demo</span>')
        else:
            src = _esc(r.get("source", "-"))
        pkg_rows += (
            f'<tr class="pkg" data-q="{_esc((r.get("project") or "") + " " + (r.get("agency") or "") + " " + (r.get("vendor") or "") + " " + str(r.get("id")))}">'
            f'<td class="small mono">{_esc(r.get("id"))}</td><td>{_esc(r.get("project"))}</td>'
            f'<td class="small">{_esc(r.get("agency"))}</td>'
            f'<td class="num mono">{_rupiah(r.get("value"))}</td>'
            f'<td class="small">{_esc(r.get("vendor") or "—")}</td>'
            f'<td class="small mono">{_esc(r.get("date_signed") or "—")}</td>'
            f'<td class="small">{src}</td></tr>')

    ctx = _open_ctx()
    aceh = ((ctx.get("sirup") or {}).get("aceh")) or {}
    kat = ctx.get("katalog") or {}
    ctx_html = ""
    if aceh:
        topkat = ", ".join(f"{_esc(k)} ({v})" for k, v in (kat.get("top_categories") or [])[:5])
        ctx_html = (
            f'<div class="orow"><span>RUP SIRUP</span><b class="mono">{_rupiah(aceh.get("rup_total"))}</b></div>'
            f'<div class="orow"><span>Paket RUP</span><b class="mono">{_esc(aceh.get("paket_total", "-"))}</b></div>'
            f'<div class="orow"><span>Produk katalog</span><b class="mono">{_esc(kat.get("produk_total", "-"))} '
            f'({_esc(kat.get("komoditas_count", "-"))} komoditas)</b></div>'
            f'<p class="dim">Teratas: {topkat or "-"}.</p>'
            f'<p class="dim">Diambil {_esc(ctx.get("fetched_at", "-"))} · LKPP data.lkpp.go.id '
            f'(agregat per daerah, bukan per paket).</p>')

    vs = visitors.stats()
    vtop = ", ".join(f"{_esc(t['path'])} ({t['hits']})" for t in vs["top_today"][:3]) or "-"
    vrows = "".join(
        f'<tr><td class="small mono">{_esc(v["ts"] or "")}</td><td class="small">{_esc(v["path"])}</td>'
        f'<td class="small">{_esc(v["browser"])} · {_esc(v["os"])}</td>'
        f'<td class="small">{_esc(v["city"])} <b>{_esc(v["tag"])}</b></td></tr>' for v in vs["recent"])
    map_svg, map_note = _minimap(vs["locations"])
    widget = (
        f'<div class="grid4">'
        f'<div class="card"><div class="n mono" id="v-online">{vs["online"]}</div>'
        f'<div class="l">online (5 mnt)</div></div>'
        f'<div class="card"><div class="n mono" id="v-today">{vs["today_hits"]} / {vs["today_unique"]}</div>'
        f'<div class="l">kunjungan / unik hari ini</div></div>'
        f'<div class="card"><div class="n mono" id="v-total">{vs["total_hits"]} / {vs["total_unique"]}</div>'
        f'<div class="l">kunjungan / unik total</div></div>'
        f'<div class="card"><div class="n small-n" id="v-top">{vtop}</div>'
        f'<div class="l">halaman teratas hari ini</div></div></div>'
        f'<div class="cols2">'
        f'<div><div class="table-scroll"><table class="light"><tr><td>Waktu (UTC)</td><td>Halaman</td><td>Perangkat</td><td>Lokasi</td></tr>'
        f'<tbody id="v-recent">{vrows or "<tr><td colspan=4 class=small>Belum ada kunjungan tercatat.</td></tr>"}</tbody></table></div>'
        f'<p class="note">Segar otomatis tiap 30 detik · privasi minimal: IP asli tidak disimpan.</p></div>'
        f'<div class="panel light"><div class="kicker">◈ SEBARAN HARI INI</div>'
        f'<svg id="minimap" viewBox="0 0 640 360" style="width:100%;height:auto;display:block;margin-top:8px">'
        f'<defs><radialGradient id="seagrad" cx="50%" cy="38%" r="80%">'
        f'<stop offset="0%" stop-color="#4a3b29"/><stop offset="100%" stop-color="#221a12"/>'
        f'</radialGradient></defs>'
        f'<rect x="0" y="0" width="640" height="360" rx="16" fill="url(#seagrad)"/>'
        f'<g id="pins">{map_svg}</g></svg>'
        f'<p class="note" id="map-note">{_esc(map_note)}</p></div>'
        f'</div>')

    flags_json = json.dumps(flags, ensure_ascii=False).replace("</", "<\\/")
    city_json = json.dumps(visitors.city_coords(), ensure_ascii=False)
    graph = _graph_svg(flags, vendors)

    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MATA — penjaga uang publik</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{{
 --ink:#241d17; --ink-2:#171310; --ink-soft:#5c5347; --cream:#f6f1e7; --surface:#efe8d8;
 --border:#ddd2bd; --ember:#c8501a; --ember-deep:#93350e; --ember-soft:#f0a35e;
 --red:#b3261e; --amber:#96690a; --green:#35703c;
}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ink);background:var(--cream);
 background-image:radial-gradient(900px 600px at 100% 0%, rgba(200,80,26,.14), transparent 60%),
  radial-gradient(700px 500px at 0% 100%, rgba(36,29,23,.08), transparent 60%);
 background-attachment:fixed;min-height:100vh}}
body::before{{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
 background-image:radial-gradient(rgba(36,29,23,.07) 1px, transparent 1px);background-size:20px 20px;
 -webkit-mask-image:radial-gradient(ellipse at center, black 30%, transparent 80%);
 mask-image:radial-gradient(ellipse at center, black 30%, transparent 80%)}}
#app{{position:relative;z-index:1}}
.wrap{{max-width:1600px;margin:0 auto;padding:16px 16px 60px}}
@media(min-width:900px){{.wrap{{padding:24px 32px 60px}}}}
.mono{{font-family:'JetBrains Mono',monospace}}
/* HERO */
.hero{{background:var(--ink-2);color:var(--cream);border-radius:28px;padding:26px;position:relative;overflow:hidden;animation:rise .7s cubic-bezier(.16,1,.3,1) both}}
@media(min-width:900px){{.hero{{padding:36px}}}}
.hero .orb{{position:absolute;top:-96px;right:-64px;width:320px;height:320px;border-radius:50%;
 background:rgba(200,80,26,.28);filter:blur(90px);pointer-events:none;animation:float-orb 14s ease-in-out infinite}}
@keyframes float-orb{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-40px,30px)}}}}
.hero-grid{{position:relative;display:grid;gap:24px;grid-template-columns:1fr}}
@media(min-width:1000px){{.hero-grid{{grid-template-columns:7fr 5fr}}}}
.eyebrow{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.24em;color:#b8ab98}}
.hero h1{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(36px,5.4vw,60px);line-height:.98;margin:12px 0}}
.hero h1 em{{color:var(--ember-soft)}}
.hero p.desc{{color:rgba(245,239,230,.7);font-size:14px;line-height:1.7;max-width:34rem}}
.tiles{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0 14px}}
.tile{{background:rgba(245,239,230,.05);border:1px solid rgba(245,239,230,.12);border-radius:16px;padding:14px}}
.tile .t-n{{font-family:'Instrument Serif',Georgia,serif;font-size:clamp(24px,3.4vw,32px);line-height:1;font-variant-numeric:tabular-nums}}
.tile .t-n.long{{font-size:19px}}
.tile .t-l{{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.18em;color:rgba(245,239,230,.5);margin-top:6px}}
.pills{{display:flex;flex-wrap:wrap;gap:8px}}
.pill{{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 18px;border-radius:999px;
 font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.08em;text-decoration:none;cursor:pointer;border:1px solid rgba(245,239,230,.2);
 background:rgba(245,239,230,.05);color:var(--cream)}}
.pill.hot{{background:var(--ember);border-color:var(--ember);color:#fff}}
.pill:hover{{background:rgba(245,239,230,.14)}}
.pill.hot:hover{{background:var(--ember-soft);color:var(--ink-2)}}
.badges{{margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.badge{{display:inline-block;padding:3px 12px;border-radius:999px;font-size:11px;font-weight:600;border:1px solid rgba(245,239,230,.25);white-space:nowrap}}
.badge.ok{{color:#7ddba0;border-color:#7ddba0}} .badge.err{{color:#ff9d9d;border-color:#ff9d9d}}
.badge.live{{color:#7fd4ff;border-color:#7fd4ff}} .badge.syn{{color:#f0c46c;border-color:#f0c46c}}
.badge .mono{{font-size:11px}}
/* ticker */
.ticker{{overflow:hidden;white-space:nowrap;border-radius:16px;background:var(--ink);color:var(--cream);margin:16px 0 0;padding:10px 0;font-size:12.5px;letter-spacing:.01em}}
.ticker-inner{{display:inline-block;animation:marquee 55s linear infinite}}
@keyframes marquee{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tk-item b{{color:var(--ember-soft)}} .tk-sep{{color:var(--ember-soft);margin:0 18px}}
/* 12-col */
.cols{{display:grid;gap:16px;grid-template-columns:1fr;margin-top:16px}}
@media(min-width:1100px){{.cols{{grid-template-columns:3fr 6fr 3fr}}}}
.panel{{border-radius:28px;padding:20px;min-width:0}}
.panel.light{{background:var(--cream);border:1px solid var(--border)}}
.panel.dark{{background:var(--ink-2);color:var(--cream)}}
.kicker{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--ember);display:flex;align-items:center;gap:8px}}
.panel.dark .kicker{{color:var(--ember-soft)}}
.count{{margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:10px;opacity:.6}}
.chip{{display:flex;justify-content:space-between;align-items:center;width:100%;text-align:left;margin-top:8px;
 background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:9px 12px;font-size:12px;cursor:pointer;font-family:inherit;color:var(--ink)}}
.chip:hover{{border-color:var(--ember)}} .chip b{{font-family:'JetBrains Mono',monospace}}
.chip.on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}
.schema{{margin-top:16px;background:var(--ink-2);color:var(--cream);border-radius:16px;padding:16px;font-size:12px;line-height:1.8}}
.schema .kicker{{color:var(--ember-soft)}}
.schema ol{{margin:8px 0 0;padding-left:18px;color:rgba(245,239,230,.75)}}
/* graph */
#gsvg{{width:100%;height:auto;display:block}}
.gnode{{cursor:pointer}} .gnode circle{{transition:r .2s}}
.gnode:hover circle{{stroke:#fff;stroke-width:2}}
.gnode.sel circle{{stroke:#fff;stroke-width:3}}
.ghint{{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.2em;color:rgba(245,239,230,.35);margin-top:6px}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;border-top:1px solid rgba(245,239,230,.12);margin-top:10px;padding-top:12px}}
.leg{{display:flex;align-items:center;gap:7px;font-size:11px;color:rgba(245,239,230,.75);background:none;border:none;cursor:pointer;font-family:inherit;padding:2px 4px}}
.dot{{width:10px;height:10px;border-radius:50%}}
/* reader */
#reader .r-rule{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--ember)}}
#reader h3{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(19px,2.4vw,22px);margin:6px 0;line-height:1.25}}
#reader ul{{font-size:12.5px;color:#3d352b;padding-left:18px;line-height:1.7}}
#reader .meta{{font-size:12px;color:var(--ink-soft);margin-top:6px;line-height:1.7}}
#reader .rec{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 12px;font-size:12px;margin-top:10px}}
/* sections */
h2{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(22px,2.8vw,28px);margin:34px 0 6px;line-height:1.2}}
.h-num{{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ember);vertical-align:super;margin-right:8px}}
.note{{color:var(--ink-soft);font-size:12px}}
.grid4{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:16px 0}}
@media(min-width:900px){{.grid4{{grid-template-columns:repeat(4,1fr)}}}}
.card{{background:#fffdf7;border:1px solid var(--border);border-radius:20px;padding:16px;animation:rise .7s cubic-bezier(.16,1,.3,1) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(12px);filter:blur(6px)}}to{{opacity:1;transform:none;filter:none}}}}
.card .n{{font-size:clamp(19px,2.2vw,24px);font-weight:600;word-break:break-word;font-variant-numeric:tabular-nums;line-height:1.25}}
.card .n.long{{font-size:15px;line-height:1.55;word-break:break-all}}
.card .l{{color:var(--ink-soft);font-size:12px;margin-top:4px}}
.card .small-n{{font-size:13px;line-height:1.6}}
.flag{{background:#fffdf7;border:1px solid var(--border);border-radius:16px;padding:12px 16px;margin:10px 0}}
.flag.open{{border-color:var(--ember)}}
.flag summary{{cursor:pointer;font-size:14px;line-height:1.65;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}}
.flag .rule{{font-family:'JetBrains Mono',monospace;color:var(--ember);font-size:12px}}
.flag-title{{font-weight:600}}
.sev-tinggi{{color:var(--red);font-weight:800}} .sev-sedang{{color:var(--amber);font-weight:700}} .sev-rendah{{color:var(--green);font-weight:600}}
.flag .ev{{font-size:13px;color:#3d352b}} .flag .meta{{font-size:12px;color:var(--ink-soft);margin-top:4px}}
table{{width:100%;border-collapse:collapse;font-size:12.5px;line-height:1.55}}
table.light{{background:#fffdf7;border:1px solid var(--border);border-radius:16px;overflow:hidden}}
td{{padding:7px 9px;border-bottom:1px solid var(--border);vertical-align:top}}
.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.small{{color:var(--ink-soft)}}
a{{color:var(--ember-deep)}}
.bar{{background:var(--surface);border-radius:6px;height:10px;min-width:120px;overflow:hidden}}
.bar div{{background:linear-gradient(90deg,var(--ember),var(--ember-soft));height:10px;border-radius:6px}}
.months{{display:flex;align-items:flex-end;gap:8px;padding:12px 4px;overflow-x:auto}}
.mcol{{text-align:center;min-width:44px}} .bar{{width:34px;margin:0 auto}}
.bar-dec{{width:34px;background:linear-gradient(180deg,#d8483c,#7e1d12);margin:0 auto;border-radius:4px 4px 0 0}}
.mlabel{{font-size:10px;color:var(--ink-soft);margin-top:4px}} .mval{{font-size:10px}}
.demo-tag{{color:var(--ink-soft);border:1px dashed var(--border);border-radius:6px;padding:1px 8px;font-size:11px;cursor:help}}
.toolbar{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;align-items:center}}
.toolbar input[type=search]{{background:#fffdf7;border:1px solid var(--border);color:var(--ink);border-radius:10px;padding:8px 12px;font-size:13px;min-width:230px;font-family:inherit}}
.btn{{background:#fffdf7;border:1px solid var(--border);color:var(--ink);border-radius:10px;padding:8px 14px;font-size:12px;cursor:pointer;text-decoration:none;display:inline-block;font-family:inherit}}
.btn.on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}
.btn:hover{{border-color:var(--ember)}}
/* bottom 7+5 */
.cols2{{display:grid;gap:16px;grid-template-columns:1fr;margin-top:8px}}
@media(min-width:1100px){{.cols2{{grid-template-columns:7fr 5fr}}}}
.orow{{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid rgba(245,239,230,.12);font-size:13px}}
.orow span{{color:rgba(245,239,230,.6);font-size:12.5px}} .orow b{{color:var(--cream);text-align:right;font-size:12.5px;word-break:break-all}}
.dim{{font-size:12px;color:rgba(245,239,230,.55);line-height:1.7}}
.lapor a{{color:var(--ember-soft)}}
#minimap{{border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,.25)}}
#minimap .pin{{cursor:pointer}}
#minimap .pin:hover circle:nth-of-type(2){{stroke:#fff;stroke-width:2.5}}
/* boot */
#boot{{position:fixed;inset:0;z-index:50;background:#171310;color:#f5efe6;display:flex;align-items:center;justify-content:center;transition:opacity .8s ease, visibility .8s}}
#boot.gone{{opacity:0;visibility:hidden;pointer-events:none}}
.boot-inner{{text-align:center;max-width:420px;padding:24px}}
.boot-eye{{width:92px;height:92px;margin:0 auto 18px;position:relative}}
.boot-eye svg{{width:100%;height:100%;animation:breathe 3.2s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{opacity:.6;transform:scale(1)}}50%{{opacity:1;transform:scale(1.07)}}}}
.boot-eye::after{{content:"";position:absolute;inset:-6px;border-radius:50%;border:1px solid #e05a1e;animation:pulse-ring 2.4s ease-out infinite}}
@keyframes pulse-ring{{0%{{transform:scale(.85);opacity:.7}}100%{{transform:scale(1.5);opacity:0}}}}
.boot-title{{font-family:'Instrument Serif',Georgia,serif;font-size:clamp(34px,8vw,46px);margin:0}}
.boot-title em{{color:var(--ember-soft)}}
.boot-sub{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.25em;color:#b8ab98;margin:8px 0 20px}}
.boot-log{{font-family:'JetBrains Mono',monospace;font-size:11px;color:#8f8474;min-height:56px;text-align:left;border:1px solid #3a322a;border-radius:12px;padding:12px 14px;margin-bottom:18px;background:#1e1915}}
.boot-log div{{animation:stream-in .4s both}}
@keyframes stream-in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.boot-bar{{height:3px;background:#3a322a;border-radius:99px;overflow:hidden;margin-bottom:22px}}
.boot-bar i{{display:block;height:100%;width:40%;background:linear-gradient(90deg,#e05a1e,#f0a35e);border-radius:99px;animation:load 1.6s ease-in-out infinite}}
@keyframes load{{0%{{margin-left:-40%}}100%{{margin-left:100%}}}}
.boot-btn{{background:#e05a1e;color:#fff;border:none;border-radius:999px;padding:13px 34px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit}}
.boot-btn:hover{{background:var(--ember-soft);color:#171310}}
.boot-quiet{{display:block;margin:12px auto 0;font-size:12px;color:#8f8474;text-decoration:underline;cursor:pointer;background:none;border:none;font-family:inherit}}
#locbanner{{position:fixed;left:12px;right:12px;bottom:12px;z-index:40;max-width:640px;margin:0 auto;
 background:var(--ink-2);color:var(--cream);border:1px solid rgba(240,163,94,.4);border-radius:18px;padding:16px 18px;
 box-shadow:0 12px 40px rgba(0,0,0,.4);display:none}}
#locbanner.show{{display:block;animation:rise .5s both}}
#locbanner .lb-title{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.22em;color:var(--ember-soft)}}
#locbanner p{{font-size:12px;line-height:1.7;color:rgba(245,239,230,.8)}}
#locbanner .lb-row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}}
#locbanner .pill{{height:36px;font-size:10px}}
#locbanner .lb-forget{{background:none;border:none;color:rgba(245,239,230,.5);text-decoration:underline;
 font-size:11px;cursor:pointer;margin-top:8px;font-family:inherit;padding:0}}
.foot{{margin-top:40px;color:var(--ink-soft);font-size:11px;border-top:1px solid var(--border);padding-top:14px;line-height:2}}
.foot button{{background:none;border:none;color:var(--ember-deep);text-decoration:underline;cursor:pointer;font-size:11px;font-family:inherit;padding:0}}
/* ---- mobile ---- */
.table-scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:16px}}
.table-scroll table{{min-width:560px}}
@media(max-width:640px){{
 .wrap{{padding:12px 10px 48px}}
 .hero{{padding:20px 16px;border-radius:22px}}
 .hero h1{{font-size:clamp(30px,9vw,40px)}}
 .tiles{{gap:8px}} .tile{{padding:10px}}
 .tile .t-l{{font-size:8px;letter-spacing:.12em}}
 .pill{{height:36px;padding:0 14px;font-size:10px}}
 .toolbar input[type=search]{{min-width:0;flex:1}}
 .panel{{padding:14px;border-radius:22px}}
 h2{{margin:26px 0 4px}}
 .boot-inner{{padding:16px}} .boot-log{{font-size:10px}}
 #locbanner{{left:8px;right:8px;bottom:8px;padding:12px 14px}}
 .months{{gap:6px}} .mcol{{min-width:38px}}
 td{{padding:6px 7px}}
}}
::selection{{background:var(--ember);color:var(--cream)}}
html.booted #boot{{display:none}}
</style>
<script>try{{if(sessionStorage.getItem('mata_boot'))document.documentElement.classList.add('booted');}}catch(e){{}}</script></head><body>
<div id="boot"><div class="boot-inner">
 <div class="boot-eye"><svg viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="14" fill="#221e19"/>
  <path d="M32 12l15.6 9v18L32 48l-15.6-9V21z" stroke="#e05a1e" stroke-width="4.5" stroke-linejoin="round"/>
  <circle cx="47" cy="15" r="5" fill="#e05a1e"/></svg></div>
 <p class="boot-title">MATA <em>menyala</em></p>
 <p class="boot-sub">WATCHDOG AKUNTABILITAS PENGADAAN</p>
 <div class="boot-log" id="bootlog"></div>
 <div class="boot-bar"><i></i></div>
 <button class="boot-btn" id="bootgo">MASUK — DENGAN SUARA ⟶</button>
 <button class="boot-quiet" id="bootquiet">masuk senyap</button>
</div></div>
<div id="app"><div class="wrap">
 <section class="hero"><div class="orb"></div><div class="hero-grid">
  <div>
   <div class="eyebrow">◉ WATCHDOG AKUNTABILITAS PENGADAAN · KAB. ACEH TENGAH</div>
   <h1>Arsip yang dibaca,<br><em>uang yang dijaga.</em></h1>
   <p class="desc">MATA memindai pengumuman pengadaan publik dan menandainya dengan aturan
    transparan D1–D6. Setiap angka bisa diklik kembali ke sumbernya. Ini indikasi berbasis data, bukan vonis.</p>
   <div class="badges">{badge} {mode_badge}
    <span class="badge">terakhir <span class="mono">{_esc(st.get("last_run", "-"))}</span></span></div>
  </div>
  <div>
   <div class="tiles">
    <div class="tile"><div class="t-n">{_esc(n_records)}</div><div class="t-l">PENGUMUMAN</div></div>
    <div class="tile"><div class="t-n" style="color:var(--ember-soft)">{_esc(n_flags)}</div><div class="t-l">INDIKASI</div></div>
    <div class="tile"><div class="t-n">{_esc(len(vendors))}</div><div class="t-l">PENYEDIA</div></div>
   </div>
   <div class="pills">
    <a class="pill hot" href="/api/records.csv" download>⇩ UNDUH CSV</a>
    <a class="pill" href="/api/flags" target="_blank">JSON INDIKASI</a>
    <a class="pill" href="https://www.lapor.go.id" target="_blank" rel="noopener">LAPOR! ↗</a>
   </div>
  </div>
 </div></section>
 <div class="ticker"><div class="ticker-inner">{ticker_items}{ticker_items}</div></div>

 <h2><span class="h-num">01</span> Jelajah arsip</h2>
 <div class="cols">
  <aside class="panel light">
   <div class="kicker">▤ ARSIP PENYEDIA <span class="count">{_esc(len(vendors))}</span></div>
   <p class="note">Klik penyedia untuk menyaring tabel paket di bawah.</p>
   <div id="chips">{chips}</div>
   <div class="schema">
    <div class="kicker">⌁ SKEMA ATURAN</div>
    <ol>
     <li><b>D1</b> harga vs referensi</li>
     <li><b>D2</b> konsentrasi vendor</li>
     <li><b>D3</b> keroyokan akhir tahun</li>
     <li><b>D4</b> vendor kecil–menang besar</li>
     <li><b>D6</b> pola nilai identik</li>
    </ol>
   </div>
  </aside>
  <section class="panel dark">
   <div class="kicker">◈ PETA INDIKASI <span class="count">{_esc(n_flags)} SIMPUL</span></div>
   <svg id="gsvg" viewBox="0 0 640 460">{graph}</svg>
   <div class="ghint">KLIK SIMPUL UNTUK MEMBACA · MERAH TINGGI · OREN SEDANG · HIJAU RENDAH</div>
   <div class="legend">
    <button class="leg" data-f="tinggi"><span class="dot" style="background:#c0392b"></span>Tinggi</button>
    <button class="leg" data-f="sedang"><span class="dot" style="background:#d97c1e"></span>Sedang</button>
    <button class="leg" data-f="rendah"><span class="dot" style="background:#4a7c3a"></span>Rendah</button>
    <button class="leg" data-f="semua"><span class="dot" style="background:#f5efe6"></span>Semua</button>
   </div>
  </section>
  <aside class="panel light" id="reader">
   <div class="kicker">☰ PEMBACA</div>
   <div id="reader-body"><p class="note">Klik simpul pada peta untuk membaca bukti, record, dan langkah lanjut di sini.</p></div>
  </aside>
 </div>

 <h2><span class="h-num">02</span> Indikasi — klik untuk bukti &amp; langkah lanjut</h2>
 <div class="toolbar">
  <button class="btn on" data-f="semua">Semua</button>
  <button class="btn" data-f="tinggi">Tinggi</button>
  <button class="btn" data-f="sedang">Sedang</button>
  <button class="btn" data-f="rendah">Rendah</button>
 </div>
 <div id="flags">{flag_cards or "<p class='note'>Belum ada indikasi.</p>"}</div>

 <h2><span class="h-num">03</span> Konsentrasi &amp; musim anggaran</h2>
 <div class="table-scroll"><table class="light"><tr><td>Penyedia</td><td class="num">Proyek</td><td class="num">Total nilai</td><td>Porsi</td></tr>{vendor_rows}</table></div>
 <h2><span class="h-num">04</span> Paket &amp; konteks terbuka</h2>
 <div class="cols2">
  <section class="panel light">
   <div class="kicker">🔎 CARI PAKET <span class="count">{_esc(len(recs))} RECORD</span></div>
   <div class="toolbar"><input type="search" id="q" placeholder="Nama paket / instansi / vendor / ID…"></div>
   <div class="table-scroll"><table><tr><td>ID</td><td>Paket</td><td class="num">Nilai</td><td>Pemenang</td><td>Sumber</td></tr>
   <tbody id="pkgs">{pkg_rows}</tbody></table></div>
  </section>
  <section class="panel dark">
   <div class="kicker">⬣ KONTEKS TERBUKA — {_esc(ctx.get("region", "ACEH TENGAH").upper())}</div>
   {ctx_html or '<p class="dim">Belum ada konteks — jalankan `python3 run.py open-data`.</p>'}
   <div class="lapor" style="margin-top:16px;border-top:1px solid rgba(245,239,230,.12);padding-top:12px">
    <div class="kicker">⚑ LAPOR &amp; VERIFIKASI</div>
    <p class="dim">MATA tidak mengirim laporan otomatis. Verifikasi ke sumber,
     lalu laporkan via <a href="https://www.lapor.go.id" target="_blank" rel="noopener">LAPOR!</a> ·
     <a href="https://www.ombudsman.go.id" target="_blank" rel="noopener">Ombudsman RI</a> ·
     KPK · APIP/BPKP.</p>
   </div>
  </section>
 </div>

 <h2><span class="h-num">05</span> Pengunjung live</h2>
 {widget}
 <div class="foot">MATA · AI HackFest 2026 · indikasi berbasis data, bukan vonis hukum ·
  {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ·
  <button id="reboot">putar ulang pembuka</button></div>
</div></div>
<div id="locbanner">
 <div class="lb-title">◎ IZIN LOKASI PENGUNJUNG</div>
 <p id="locmsg">Agar peta sebaran di bawah bermakna, MATA meminta izin mencatat <b>lokasi kasar</b> Anda
  (kota dari IP, atau GPS ±1 km bila Anda setuju dan koneksi HTTPS). IP asli tidak disimpan,
  koordinat presisi terhapus otomatis &lt;72 jam. Dasar: persetujuan Anda (UU PDP No. 27/2022).</p>
 <div class="lb-row">
  <button class="pill hot" id="loc-gps">IZINKAN GPS PRESISI</button>
  <button class="pill" id="loc-city">HANYA PERKIRAAN KOTA</button>
  <button class="pill" id="loc-no">TOLAK</button>
 </div>
 <button class="lb-forget" id="loc-forget">lupakan seluruh kunjungan saya</button>
</div>
<script>
var CITYC={city_json};
var FLAGS={flags_json};
(function(){{
 var NREC={n_records}, NFLG={n_flags};
 var lines=["▸ menghubungi arsip data publik…","▸ memuat "+NREC+" pengumuman pengadaan…",
  "▸ memeriksa "+NFLG+" indikasi anomali…","▸ siap. selamat datang, pengawas."];
 var log=document.getElementById('bootlog'), li=0;
 var timer=setInterval(function(){{ if(li<lines.length){{ var d=document.createElement('div'); d.textContent=lines[li++]; log.appendChild(d); }} else {{ clearInterval(timer); }} }},450);
 function bootSound(){{
  try{{
   var AC=window.AudioContext||window.webkitAudioContext; if(!AC) return;
   var ac=new AC(), now=ac.currentTime;
   var master=ac.createGain(); master.gain.value=0.9; master.connect(ac.destination);
   [110,164.81,220,277.18].forEach(function(f,i){{
    var o=ac.createOscillator(), g=ac.createGain();
    o.type='sine'; o.frequency.value=f;
    g.gain.setValueAtTime(0.0001,now);
    g.gain.linearRampToValueAtTime(0.10/(i+1),now+1.6);
    g.gain.linearRampToValueAtTime(0.0001,now+6);
    o.connect(g); g.connect(master); o.start(now); o.stop(now+6.2);}});
   var lfo=ac.createOscillator(), lg=ac.createGain();
   lfo.frequency.value=0.25; lg.gain.value=0.12;
   lfo.connect(lg); lg.connect(master.gain); lfo.start(now); lfo.stop(now+6.2);
   setTimeout(function(){{ac.close();}},7000);
  }}catch(e){{}}
 }}
 function enter(withSound){{
  if(withSound) bootSound();
  try{{sessionStorage.setItem('mata_boot','1');}}catch(e){{}}
  document.getElementById('boot').classList.add('gone');
 }}
 document.getElementById('bootgo').onclick=function(){{enter(true);}};
 document.getElementById('bootquiet').onclick=function(){{enter(false);}};
 document.getElementById('reboot').onclick=function(){{try{{sessionStorage.removeItem('mata_boot');}}catch(e){{}} location.reload();}};
 try{{ if(sessionStorage.getItem('mata_boot')){{ document.getElementById('boot').classList.add('gone'); }} }}catch(e){{}}
 /* ---- pembaca ---- */
 function esc(s){{ var d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }}
 function showReader(f){{
  var h='<div class="r-rule">['+esc(f.rule_id)+' · '+esc((f.severity||'').toUpperCase())+']</div>'
   +'<h3>'+esc(f.title)+'</h3><ul>'+ (f.evidence||[]).map(function(e){{return '<li>'+esc(e)+'</li>';}}).join('')
   +'</ul><div class="meta">Record: <b>'+esc((f.record_ids||[]).join(', '))+'</b></div>'
   +'<div class="meta">'+esc(f.explanation||'')+'</div>'
   +'<div class="rec">Langkah lanjut: '+esc(f.recommendation||'')+'</div>';
  document.getElementById('reader-body').innerHTML=h;
 }}
 function focusFlag(rule){{
  var card=document.getElementById('flag-'+rule);
  document.querySelectorAll('.flag').forEach(function(c){{c.classList.remove('open');}});
  document.querySelectorAll('.gnode').forEach(function(g){{g.classList.remove('sel');}});
  var g=document.querySelector('.gnode[data-rule="'+rule+'"]');
  if(g) g.classList.add('sel');
  var f=null;
  FLAGS.forEach(function(x){{ if(x.rule_id===rule) f=x; }});
  if(f) showReader(f);
  if(card){{ card.open=true; card.classList.add('open'); card.scrollIntoView({{behavior:'smooth',block:'center'}}); }}
 }}
 document.querySelectorAll('.gnode[data-rule]').forEach(function(g){{
  g.addEventListener('click',function(){{focusFlag(g.getAttribute('data-rule'));}});
 }});
 document.querySelectorAll('.gnode[data-vendor]').forEach(function(g){{
  g.addEventListener('click',function(){{chipFilter(g.getAttribute('data-vendor'));}});
 }});
 if(FLAGS.length) showReader(FLAGS[0]);
 /* ---- filter level (tombol + legenda) ---- */
 function sevFilter(f, btn){{
  document.querySelectorAll('[data-f]').forEach(function(x){{x.classList.remove('on');}});
  if(btn) btn.classList.add('on');
  document.querySelectorAll('#flags .flag').forEach(function(c){{
   c.style.display=(f==='semua'||c.getAttribute('data-sev')===f)?'':'none';}});
  document.querySelectorAll('.gnode[data-rule]').forEach(function(g){{
   g.style.display=(f==='semua'||g.getAttribute('data-sev')===f)?'':'none';}});
 }}
 document.querySelectorAll('[data-f]').forEach(function(b){{
  b.onclick=function(){{sevFilter(b.getAttribute('data-f'), b);}};
 }});
 /* ---- cari paket + chip vendor ---- */
 var q=document.getElementById('q');
 function pkgFilter(s){{
  s=(s||'').toLowerCase();
  document.querySelectorAll('#pkgs .pkg').forEach(function(r){{
   r.style.display=r.getAttribute('data-q').toLowerCase().indexOf(s)>=0?'':'none';}});
 }}
 q.oninput=function(){{pkgFilter(q.value);}};
 function chipFilter(name){{
  q.value=name; pkgFilter(name);
  document.querySelectorAll('.chip').forEach(function(c){{
   c.classList.toggle('on',c.getAttribute('data-v')===name);}});
  document.getElementById('pkgs').scrollIntoView({{behavior:'smooth',block:'start'}});
 }}
 document.querySelectorAll('.chip').forEach(function(c){{
  c.onclick=function(){{chipFilter(c.getAttribute('data-v'));}};
 }});
 /* ---- angka panjang mengecil otomatis mengikuti konten ---- */
 document.querySelectorAll('.card .n, .tile .t-n').forEach(function(el){{
  if(el.textContent.trim().length>14) el.classList.add('long');
 }});
 /* ---- izin lokasi + peta (consent-first, UU PDP) ---- */
 function locMsg(t){{document.getElementById('locmsg').innerHTML=t;}}
 function locPost(body, done){{
  fetch('/api/locate',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}})
   .then(function(r){{return r.json();}}).then(done).catch(function(){{locMsg('Gagal menyimpan — coba lagi.');}});
 }}
 function locHide(v){{try{{localStorage.setItem('mata_loc',v);}}catch(e){{}}
  document.getElementById('locbanner').classList.remove('show');}}
 try{{ if(!localStorage.getItem('mata_loc')){{
  setTimeout(function(){{document.getElementById('locbanner').classList.add('show');}},7500);
 }} }}catch(e){{ document.getElementById('locbanner').classList.add('show'); }}
 document.getElementById('loc-gps').onclick=function(){{
  if(!window.isSecureContext){{ locMsg('Browser menolak GPS pada koneksi HTTP (wajib HTTPS). Merekam <b>perkiraan kota</b> saja.'); locPost({{consent:'city'}},function(){{locHide('city');vrefresh();}}); return; }}
  if(!navigator.geolocation){{ locMsg('Perangkat tidak mendukung GPS. Merekam <b>perkiraan kota</b> saja.'); locPost({{consent:'city'}},function(){{locHide('city');vrefresh();}}); return; }}
  locMsg('Menunggu izin GPS dari browser…');
  navigator.geolocation.getCurrentPosition(function(p){{
   locPost({{consent:'precise',lat:Math.round(p.coords.latitude*100)/100,lon:Math.round(p.coords.longitude*100)/100}},
    function(){{locMsg('Tersimpan (±1 km). Terima kasih.');locHide('precise');vrefresh();}});
  }},function(){{ locMsg('Izin GPS ditolak — merekam <b>perkiraan kota</b> saja.');
   locPost({{consent:'city'}},function(){{locHide('city');vrefresh();}}); }},{{timeout:10000}});
 }};
 document.getElementById('loc-city').onclick=function(){{
  locPost({{consent:'city'}},function(){{locHide('city');vrefresh();}});}};
 document.getElementById('loc-no').onclick=function(){{locHide('no');}};
 document.getElementById('loc-forget').onclick=function(){{
  fetch('/api/forget',{{method:'POST'}}).then(function(r){{return r.json();}}).then(function(d){{
   locMsg('Dihapus '+d.deleted+' baris kunjungan Anda.');locHide('forgot');vrefresh();}});
 }};
 function mapXY(lat,lon){{return [20+(lon-95)/46*600, 20+(6-lat)/17*320];}}
 function drawPins(locs){{
  var g=document.getElementById('pins'); if(!g) return;
  var keep=g.querySelectorAll('path,line'); var html='';
  (locs||[]).forEach(function(L){{
   var la=L.lat, lo=L.lon, key=(L.city||'').toLowerCase();
   if((la===null||la===undefined)&&(CITYC[key]!==undefined)){{la=CITYC[key][0];lo=CITYC[key][1];}}
   if(la===null||la===undefined) return;
   var p=mapXY(la,lo), n=L.count||1, r=6+Math.min(n,9);
   html+='<g class="pin"><circle cx="'+p[0].toFixed(0)+'" cy="'+p[1].toFixed(0)+'" r="'+(r+8)+'" fill="#e05a1e" fill-opacity=".18"/>'
    +'<circle cx="'+p[0].toFixed(0)+'" cy="'+p[1].toFixed(0)+'" r="'+r+'" fill="#e05a1e" stroke="#ffd9ad" stroke-width="1.5"/>'
    +'<circle cx="'+p[0].toFixed(0)+'" cy="'+p[1].toFixed(0)+'" r="2.2" fill="#fff7ea"/>'
    +'<text x="'+p[0].toFixed(0)+'" y="'+(p[1]-r-6).toFixed(0)+'" text-anchor="middle" font-size="11.5" font-weight="bold" font-family="monospace" fill="none" stroke="#14100c" stroke-width="5">'
    +esc(L.city)+' · '+n+'</text>'
    +'<text x="'+p[0].toFixed(0)+'" y="'+(p[1]-r-6).toFixed(0)+'" text-anchor="middle" font-size="11.5" font-weight="bold" font-family="monospace" fill="#f5efe6">'
    +esc(L.city)+' · '+n+'</text></g>';
  }});
  g.querySelectorAll('g').forEach(function(x){{x.remove();}});
  g.insertAdjacentHTML('beforeend',html);
 }}
 /* ---- pengunjung live: refresh 30 dtk ---- */
 function vrefresh(){{
  fetch('/api/visitors').then(function(r){{return r.json();}}).then(function(v){{
   document.getElementById('v-online').textContent=v.online;
   document.getElementById('v-today').textContent=v.today_hits+' / '+v.today_unique;
   document.getElementById('v-total').textContent=v.total_hits+' / '+v.total_unique;
   document.getElementById('v-top').textContent=v.top_today.map(function(t){{return t.path+' ('+t.hits+')';}}).join(', ')||'-';
   var tb=document.getElementById('v-recent'); tb.innerHTML='';
   v.recent.forEach(function(x){{
    var tr=document.createElement('tr');
    tr.innerHTML='<td class="small mono"></td><td class="small"></td><td class="small"></td>';
    tr.children[0].textContent=x.ts||''; tr.children[1].textContent=x.path||'';
    tr.children[2].textContent=(x.browser||'')+' · '+(x.os||'');
    tb.appendChild(tr);}});
  }}).catch(function(){{}});
 }}
 setInterval(vrefresh,30000);
}})();
</script>
</body></html>"""


def records_csv():
    recs = db.load_records()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "project", "agency", "value", "vendor", "date_signed", "source", "url"])
    for r in recs:
        w.writerow([r.get("id"), r.get("project"), r.get("agency"), r.get("value"),
                    r.get("vendor"), r.get("date_signed"), r.get("source"), r.get("url")])
    return buf.getvalue()


class H(BaseHTTPRequestHandler):
    def _send(self, body, ctype):
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):  # noqa: N802
        path = urlparse(self.path).path
        try:
            visitors.log_visit(self.client_address[0], self.headers.get("User-Agent", ""), path)
        except Exception:
            pass
        if path == "/api/status":
            self._send(json.dumps(_status(), ensure_ascii=False), "application/json")
        elif path == "/api/flags":
            self._send(json.dumps(db.read_flags(), ensure_ascii=False), "application/json")
        elif path == "/api/visitors":
            self._send(json.dumps(visitors.stats(), ensure_ascii=False), "application/json")
        elif path == "/api/records.csv":
            self._send(records_csv(), "text/csv; charset=utf-8")
        else:
            self._send(render(), "text/html; charset=utf-8")

    def do_POST(self):  # noqa: N802
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            n = 0
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            body = {}
        path = urlparse(self.path).path
        ip = self.client_address[0]
        if path == "/api/locate":
            consent = body.get("consent")
            if consent == "precise":
                try:
                    lat = round(float(body.get("lat")), 2)
                    lon = round(float(body.get("lon")), 2)
                except (TypeError, ValueError):
                    self._send(json.dumps({"ok": False}), "application/json")
                    return
                visitors.set_location(ip, city="GPS", lat=lat, lon=lon, precise=True)
                self._send(json.dumps({"ok": True, "mode": "precise"}), "application/json")
            elif consent == "city":
                geo = visitors.geocode_ip(ip)
                if geo:
                    visitors.set_location(ip, city=geo[0], lat=geo[1], lon=geo[2])
                    self._send(json.dumps({"ok": True, "mode": "city",
                                           "city": geo[0]}), "application/json")
                else:
                    self._send(json.dumps({"ok": False}), "application/json")
            else:
                self._send(json.dumps({"ok": False}), "application/json")
        elif path == "/api/forget":
            self._send(json.dumps({"ok": True,
                                   "deleted": visitors.forget(ip)}), "application/json")
        else:
            self._send(json.dumps({"ok": False}), "application/json")

    def log_message(self, *a):  # sunyi
        pass


def serve(port=8080, host="0.0.0.0"):
    srv = ThreadingHTTPServer((host, port), H)
    print(f"MATA dashboard: http://{host}:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    serve()
