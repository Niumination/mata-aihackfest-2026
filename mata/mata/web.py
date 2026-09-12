"""Web dashboard MATA — susunan "living codex": hero gelap + grid arsip|graf|pembaca.

Rute:
  /                 dashboard (hero, graf indikasi, arsip, konteks, pengunjung)
  /api/status       status monitor (JSON)
  /api/flags        indikasi terkini (JSON)
  /api/visitors     statistik pengunjung (JSON)
  /api/iklim?id=      agroklimat Gayo per sentra (JSON, Open-Meteo via server)
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
from . import iklim
from . import spse_pub
from . import sapa_pub
from . import edge_feed
from . import inaproc_pub

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CKAN_DS = "https://data.lkpp.go.id/dataset"
OD_SIRUP = f"{CKAN_DS}/data-sirup-sistem-informasi-rencana-umum-pengadaan"
OD_KATALOG = f"{CKAN_DS}/produk-tayang-di-katalog-elektronik"
OD_REALISASI = (f"{CKAN_DS}/nilai-realisasi-pengadaan-barang-jasa-pemerintah-"
                "menurut-instansi-pusat-dan-pemerintah-daerah")
OD_PDN = f"{CKAN_DS}/data-penggunaan-produk-dalam-negeri-pdn-pada-rencana-umum-pengadaan-rup"
OD_IKP = f"{CKAN_DS}/indeks-kinerja-pengadaan"
OD_SAING = f"{CKAN_DS}/persentase-tingkat-persaingan-penyedia-umkk"


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


SEV_STYLE = {"tinggi": ("#b3261e", 26), "sedang": ("#96690a", 20), "rendah": ("#35703c", 15)}  # = CSS --sev-* (satu sumber)


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
            f'<g class="gnode" data-rule="{rid}" data-sev="{_esc(f["severity"])}" '
            f'tabindex="0" role="button" aria-label="Baca indikasi {rid}: {_esc(f["title"])}">'
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
            f'<g class="gnode" data-vendor="{_esc(name)}" tabindex="0" role="button" '
            f'aria-label="Saring paket {_esc(name)}">'
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


def _sparkline(values, w=220, h=44):
    """Kurva mini deret bulanan (abaikan None)."""
    pts = [(i, v) for i, v in enumerate(values or []) if v]
    if len(pts) < 2:
        return ""
    mx = max(v for _, v in pts) or 1
    n = len(values)
    xy = [f"{4 + i / max(n - 1, 1) * (w - 8):.0f},{h - 4 - v / mx * (h - 10):.0f}"
          for i, v in pts]
    return (f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto;display:block;margin:6px 0">'
            f'<polyline points="{" ".join(xy)}" fill="none" stroke="#f0a35e" stroke-width="2"/>'
            f'</svg>')


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
            src = (f'<a href="{OD_SIRUP}" target="_blank" rel="noopener" title="Data demo — '
                   'angka per paket ilustrasi; verifikasi agregat ke dataset SIRUP LKPP.">opendata ↗</a>')
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
        monthly = (ctx.get("realisasi") or {}).get("monthly") or []
        got = [m for m in monthly if m]
        kurva = ""
        if len(got) >= 2:
            naik = (got[-1] - got[0]) / got[0] * 100 if got[0] else 0
            kurva = (f'<div class="orow"><span>Realisasi 2025 (12 bln)</span>'
                     f'<b class="mono">{_rupiah(got[-1])}</b></div>'
                     f'{_sparkline(monthly)}'
                     f'<p class="dim">Jan {_rupiah(got[0])} → Des {_rupiah(got[-1])} '
                     f'(tumbuh {naik:.0f}% setahun).</p>')
        nas = ctx.get("nasional") or {}
        nas_rows = ""
        for key, label in (("ikp", "IKP nasional"), ("saing_umkk", "Saing UMK-K nasional")):
            v = nas.get(key)
            if v:
                nas_rows += (f'<div class="orow"><span>{label} {v.get("tahun", "")}</span>'
                             f'<b class="mono">{_esc(v.get("nilai"))}</b></div>')
        idx_labels = {"digital": "Digitalisasi", "efisiensi": "Efisiensi konsolidasi",
                      "regulasi": "Efektivitas regulasi", "puas": "Kepuasan pengguna",
                      "kelola": "Tata kelola", "probity": "Probity & advokasi",
                      "pdn95": "KLPD belanja PDN ≥95%", "umkk40": "KLPD belanja UMKK ≥40%"}
        idxgrid = ""
        idx_chips = "".join(
            f'<div class="idx"><div class="v">{_esc(nas[k]["nilai"])}</div>'
            f'<div class="k">{lbl} · {nas[k].get("tahun", "")}</div></div>'
            for k, lbl in idx_labels.items() if k in nas)
        if idx_chips:
            idxgrid = (f'<p class="dim" style="margin:12px 0 2px">INDEKS NASIONAL LKPP</p>'
                       f'<div class="idxgrid">{idx_chips}</div>')
        ctx_html = (
            f'<div class="orow"><span>RUP SIRUP</span><b class="mono">{_rupiah(aceh.get("rup_total"))}</b></div>'
            f'<div class="orow"><span>Paket RUP</span><b class="mono">{_esc(aceh.get("paket_total", "-"))}</b></div>'
            f'{kurva}'
            f'<div class="orow"><span>RUP PDN</span><b class="mono">{_rupiah((ctx.get("pdn") or {}).get("rup_pdn")) if (ctx.get("pdn") or {}).get("rup_pdn") else "-"}</b></div>'
            f'<div class="orow"><span>Produk katalog</span><b class="mono">{_esc(kat.get("produk_total", "-"))} '
            f'({_esc(kat.get("komoditas_count", "-"))} komoditas)</b></div>'
            f'{nas_rows}'
            f'{idxgrid}'
            f'<p class="dim">Teratas: {topkat or "-"}.</p>'
            f'<p class="dim">Diambil {_esc(ctx.get("fetched_at", "-"))} · agregat per daerah, '
            f'bukan per paket.</p>'
            f'<p class="dim">Sumber terbuka: '
            f'<a href="{OD_SIRUP}" target="_blank" rel="noopener">SIRUP</a> · '
            f'<a href="{OD_KATALOG}" target="_blank" rel="noopener">Katalog</a> · '
            f'<a href="{OD_REALISASI}" target="_blank" rel="noopener">Realisasi</a> · '
            f'<a href="{OD_PDN}" target="_blank" rel="noopener">PDN</a> · '
            f'<a href="{OD_IKP}" target="_blank" rel="noopener">IKP</a> · '
            f'<a href="{OD_SAING}" target="_blank" rel="noopener">Saing UMK-K</a>.</p>')

    vs = visitors.stats()
    vtop = ", ".join(f"{_esc(t['path'])} ({t['hits']})" for t in vs["top_today"][:3]) or "-"
    vrows = "".join(
        f'<tr><td class="small mono">{_esc(v["ts"] or "")}</td><td class="small">{_esc(v["path"])}</td>'
        f'<td class="small">{_esc(v["browser"])} · {_esc(v["os"])}</td>'
        f'<td class="small">{_esc(v["city"])} <b>{_esc(v["tag"])}</b></td></tr>' for v in vs["recent"])
    map_svg, map_note = _minimap(vs["locations"])
    try:
        ik_opts = "".join(
            f'<option value="{_esc(l["id"])}">{_esc(l["name"])}</option>'
            for l in iklim.locations())
    except Exception:
        ik_opts = '<option value="takengon">Takengon Kota</option>'
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
        f'<div class="table-scroll scrollbox"><table class="light"><tr><td>Waktu (UTC)</td><td>Halaman</td><td>Perangkat</td><td>Lokasi</td></tr>'
        f'<tbody id="v-recent">{vrows or "<tr><td colspan=4 class=small>Belum ada kunjungan tercatat.</td></tr>"}</tbody></table></div>'
        f'<p class="note">Segar otomatis tiap 30 detik · privasi minimal: IP asli tidak disimpan.</p></div>'
        f'<div class="panel light notools"><div class="kicker">◈ SEBARAN HARI INI</div>'
        f'<div id="osm"></div>'
        f'<p class="note" id="osm-fallback" style="display:none">Ubin peta tak termuat '
        f'(CDN terblokir?) — lokasi tetap tercatat di tabel.</p>'
        f'<noscript><svg viewBox="0 0 640 360" style="width:100%;height:auto;display:block">'
        f'<rect x="0" y="0" width="640" height="360" rx="16" fill="#221a12"/>'
        f'<g>{map_svg}</g></svg></noscript>'
        f'<p class="note" id="map-note">{_esc(map_note)}</p>'
        f'<p class="note">Ubin © OpenStreetMap — IP Anda terlihat penyedia ubin saat peta dimuat.</p>'
        f'<div class="kicker" style="margin-top:10px">☕ IKLIM GAYO — KOPI & SIAGA</div>'
        f'<p class="note">Logika niu-gayo-agroclimate · data Open-Meteo diambil server '
        f'(IP Anda tak tersebar) · cache 30 mnt.</p>'
        f'<select id="iklim-sel" aria-label="Pilih sentra agroklimat">{ik_opts}</select>'
        f'<div id="iklim-box"><p class="note">Memuat data iklim…</p></div></div>'
        f'</div>')

    flags_json = json.dumps(flags, ensure_ascii=False).replace("</", "<\\/")
    city_json = json.dumps(visitors.city_coords(), ensure_ascii=False)
    graph = _graph_svg(flags, vendors)

    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="MATA — watchdog akuntabilitas pengadaan Kabupaten Aceh Tengah: indikasi anomali berbasis data publik, dapat diverifikasi per paket.">
<meta name="theme-color" content="#241d17">
<title>MATA — penjaga uang publik</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root{{
 --ink:#241d17; --ink-2:#171310; --ink-soft:#4a4238; --cream:#f6f1e7; --surface:#efe8d8; --surface-2:#fffdf7;
 --border:#ddd2bd; --ember:#c8501a; --ember-deep:#93350e; --ember-soft:#f0a35e;
 --red:#b3261e; --amber:#7d5708; --green:#35703c;
 --sev-tinggi:#b3261e; --sev-sedang:#96690a; --sev-rendah:#35703c;
 --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s5:24px; --s6:32px; --s7:40px;
 --r-sm:10px; --r-md:12px; --r-lg:16px; --r-xl:20px; --r-xxl:22px;
 --sh-1:0 1px 2px rgba(36,29,23,.05);
 --sh-2:0 6px 18px rgba(36,29,23,.09);
 --sh-3:0 18px 44px rgba(36,29,23,.16);
 --dur-1:140ms; --dur-2:220ms; --dur-3:420ms; --dur-4:900ms;
 --ease:cubic-bezier(.16,1,.3,1);
}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
@media (prefers-reduced-motion:no-preference){{ html{{scroll-behavior:smooth}} }}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ink);background:var(--cream);
 background-image:radial-gradient(900px 600px at 100% 0%, rgba(200,80,26,.14), transparent 60%),
  radial-gradient(700px 500px at 0% 100%, rgba(36,29,23,.08), transparent 60%);
 background-attachment:fixed;min-height:100vh}}
body::before{{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
 background-image:radial-gradient(rgba(36,29,23,.07) 1px, transparent 1px);background-size:20px 20px;
 -webkit-mask-image:radial-gradient(ellipse at center, black 30%, transparent 80%);
 mask-image:radial-gradient(ellipse at center, black 30%, transparent 80%)}}
#app{{position:relative;z-index:1}}
.wrap{{max-width:1600px;margin:0 auto;padding:16px 16px calc(60px + env(safe-area-inset-bottom,0px))}}
@media(min-width:900px){{.wrap{{padding:24px 32px calc(60px + env(safe-area-inset-bottom,0px))}}}}
.mono{{font-family:'JetBrains Mono',monospace}}
/* ============ M0 — UTILITAS MOTION (reveal, toast, skeleton) ============ */
.rv-init h2,.rv-init .ticker,.rv-init .grid4{{opacity:0;transform:translateY(10px);
 transition:opacity .55s var(--ease),transform .55s var(--ease)}}
.rv-init .ticker{{transform:none;transition-delay:.15s}}
.rv-init .grid4{{transition-delay:.1s}}
.rv-init .on{{opacity:1;transform:none}}
#toasts{{position:fixed;top:16px;right:16px;z-index:60;display:flex;flex-direction:column;gap:var(--s2);
 max-width:min(360px,calc(100vw - 32px));pointer-events:none}}
.toast{{pointer-events:auto;display:flex;gap:10px;align-items:flex-start;background:var(--ink-2);color:var(--cream);
 border:1px solid rgba(240,163,94,.35);border-radius:var(--r-lg);padding:12px 14px;font-size:12.5px;line-height:1.55;
 box-shadow:var(--sh-3);animation:toast-in var(--dur-2) var(--ease)}}
.toast.out{{animation:toast-out var(--dur-2) var(--ease) forwards}}
.toast .t-ic{{font-size:13px;line-height:1.4;flex:none}}
.toast.info .t-ic{{color:var(--ember-soft)}} .toast.ok .t-ic{{color:#7ddba0}} .toast.err .t-ic{{color:#ff9d9d}}
.toast.ok{{border-color:rgba(125,219,160,.45)}} .toast.err{{border-color:rgba(255,157,157,.45)}}
@keyframes toast-in{{from{{opacity:0;transform:translateX(16px)}}to{{opacity:1;transform:none}}}}
@keyframes toast-out{{to{{opacity:0;transform:translateX(16px)}}}}
.skeleton{{position:relative;overflow:hidden;background:rgba(36,29,23,.06);border-radius:var(--r-md);min-height:14px}}
.skeleton::after{{content:"";position:absolute;inset:0;transform:translateX(-100%);
 background:linear-gradient(90deg,transparent,rgba(246,241,231,.75),transparent);animation:shimmer 1.4s infinite}}
@keyframes shimmer{{to{{transform:translateX(100%)}}}}
/* ============ M3 — SISTEM TOMBOL (transisi + active) ============ */
.btn,.ptbtn,.pill,.chip,.leg,.csug button,#cform button,.boot-btn{{
 transition:background var(--dur-1) var(--ease),border-color var(--dur-1) var(--ease),
 color var(--dur-1) var(--ease),transform var(--dur-1) var(--ease),box-shadow var(--dur-1) var(--ease)}}
.btn:active,.ptbtn:active,.pill:active,.chip:active,.leg:active,.csug button:active,#cform button:active{{transform:translateY(1px) scale(.985)}}
/* ============ M3 — KARTU & UBIN (hover-lift) ============ */
.card,.tile,.idx{{transition:transform var(--dur-2) var(--ease),box-shadow var(--dur-2) var(--ease),
 border-color var(--dur-1) var(--ease),opacity .55s var(--ease)}}
.card:hover{{transform:translateY(-2px);box-shadow:var(--sh-2)}}
.tile:hover{{border-color:rgba(240,163,94,.5);transform:translateY(-2px)}}
.idx:hover{{border-color:rgba(240,163,94,.45)}}
/* ============ HERO ============ */
.hero{{background:var(--ink-2);color:var(--cream);border-radius:var(--r-xxl);padding:26px;position:relative;overflow:hidden;
 box-shadow:var(--sh-3);animation:rise .7s cubic-bezier(.16,1,.3,1) both}}
@media(min-width:900px){{.hero{{padding:36px}}}}
.hero .orb{{position:absolute;top:-96px;right:-64px;width:320px;height:320px;border-radius:50%;
 background:rgba(200,80,26,.28);filter:blur(90px);pointer-events:none;animation:float-orb 14s ease-in-out infinite}}
@keyframes float-orb{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-40px,30px)}}}}
.hero-grid{{position:relative;display:grid;gap:24px;grid-template-columns:1fr}}
@media(min-width:1000px){{.hero-grid{{grid-template-columns:7fr 5fr;align-items:center}}}}
.eyebrow{{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;letter-spacing:.16em;color:var(--ember-soft);margin-bottom:10px}}
.hero h1{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(36px,5.4vw,60px);line-height:.98;margin:12px 0;letter-spacing:-.01em}}
.hero h1 em{{color:var(--ember-soft)}}
.hero p.desc{{color:rgba(245,239,230,.78);font-size:14px;line-height:1.7;max-width:34rem}}
.tiles{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0 14px}}
.tile{{background:rgba(245,239,230,.05);border:1px solid rgba(245,239,230,.14);border-radius:var(--r-lg);padding:14px}}
.tile .t-n{{font-family:'Instrument Serif',Georgia,serif;font-size:clamp(24px,3.4vw,32px);line-height:1;font-variant-numeric:tabular-nums}}
.tile .t-n.long{{font-size:19px}}
.tile .t-l{{font-family:'JetBrains Mono',monospace;font-size:9.5px;letter-spacing:.18em;color:rgba(245,239,230,.68);margin-top:6px}}
.pills{{display:flex;flex-wrap:wrap;gap:8px}}
.pill{{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 18px;border-radius:999px;
 font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.08em;text-decoration:none;cursor:pointer;border:1px solid rgba(245,239,230,.22);
 background:rgba(245,239,230,.05);color:var(--cream)}}
.pill.hot{{background:var(--ember);border-color:var(--ember);color:#fff;box-shadow:0 6px 18px rgba(200,80,26,.35)}}
.pill:hover{{background:rgba(245,239,230,.14);transform:translateY(-1px)}}
.pill.hot:hover{{background:var(--ember-soft);color:var(--ink-2);transform:translateY(-1px)}}
.badges{{margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.badge{{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;font-size:11px;font-weight:600;border:1px solid rgba(245,239,230,.25);white-space:nowrap}}
.badge.ok{{color:#7ddba0;border-color:#7ddba0}} .badge.err{{color:#ff9d9d;border-color:#ff9d9d}}
.badge.live{{color:#7fd4ff;border-color:#7fd4ff}} .badge.syn{{color:#f0c46c;border-color:#f0c46c}}
.badge .mono{{font-size:11px}}
.badge.live::before{{content:"";width:6px;height:6px;border-radius:50%;background:#7fd4ff;animation:livepulse 2s ease-in-out infinite}}
@keyframes livepulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.35;transform:scale(.8)}}}}
/* ============ TICKER (pause on hover) ============ */
.ticker{{overflow:hidden;white-space:nowrap;border-radius:var(--r-lg);background:var(--ink);color:var(--cream);margin:16px 0 0;padding:10px 0;font-size:12.5px;letter-spacing:.01em;box-shadow:var(--sh-1)}}
.ticker-inner{{display:inline-block;animation:marquee 55s linear infinite}}
.ticker:hover .ticker-inner{{animation-play-state:paused}}
@keyframes marquee{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tk-item b{{color:var(--ember-soft)}} .tk-sep{{color:var(--ember-soft);margin:0 18px}}
/* ============ GRID 12-col ============ */
.cols{{display:grid;gap:16px;grid-template-columns:1fr;margin-top:16px;transition:grid-template-columns .45s ease}}
.cols2{{display:grid;gap:16px;grid-template-columns:1fr;margin-top:8px;transition:grid-template-columns .45s ease}}
@media(min-width:768px){{.cols2{{grid-template-columns:1fr 1fr}}}}
@media(min-width:1100px){{.cols2{{grid-template-columns:7fr 5fr}}}}
@media(min-width:1100px){{.cols{{grid-template-columns:3fr 6fr 3fr}}}}
@media(min-width:1100px){{
 .cols.z1{{grid-template-columns:5fr 4fr 3fr}}
 .cols.z2{{grid-template-columns:2fr 8fr 2fr}}
 .cols.z3{{grid-template-columns:3fr 4fr 5fr}}
}}
.panel{{position:relative;border-radius:var(--r-xl);padding:20px;min-width:0}}
.panel.light{{background:var(--cream);border:1px solid var(--border);box-shadow:var(--sh-1);
 transition:box-shadow var(--dur-2) var(--ease),transform var(--dur-2) var(--ease)}}
.panel.light:hover{{box-shadow:var(--sh-2)}}
.panel.dark{{background:var(--ink-2);color:var(--cream);box-shadow:var(--sh-2)}}
.ptools{{margin-left:auto;display:inline-flex;gap:6px}}
.ptbtn{{background:none;border:1px solid var(--border);border-radius:var(--r-sm);min-width:30px;height:30px;
 cursor:pointer;font-size:13px;line-height:1;color:var(--ink-soft);font-family:inherit;padding:0 6px}}
.panel.dark .ptbtn{{border-color:rgba(245,239,230,.25);color:rgba(245,239,230,.75)}}
.ptbtn:hover{{border-color:var(--ember);color:var(--ink);transform:translateY(-1px)}}
.panel.dark .ptbtn:hover{{color:var(--cream)}}
.panel.prailed{{padding:10px 6px}}
.panel.prailed>*{{display:none}}
.panel.prailed>.prail{{display:flex;flex-direction:column;align-items:center;gap:10px}}
.prail{{display:none;cursor:pointer}}
.prl{{writing-mode:vertical-rl;font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.2em;opacity:.7}}
.prb{{background:none;border:1px solid var(--border);border-radius:var(--r-sm);width:30px;height:30px;
 cursor:pointer;font-size:14px;color:inherit;font-family:inherit;transition:border-color var(--dur-1),transform var(--dur-1)}}
.prb:hover{{border-color:var(--ember);transform:translateY(-1px)}}
.panel.dark .prb{{border-color:rgba(245,239,230,.25)}}
.scrollbox{{max-height:430px;overflow-y:auto}}
.idxgrid{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin:10px 0}}
.idx{{background:rgba(245,239,230,.05);border:1px solid rgba(245,239,230,.14);border-radius:var(--r-md);padding:10px 12px}}
.idx .v{{font-family:'JetBrains Mono',monospace;font-size:16px;color:var(--cream);font-variant-numeric:tabular-nums}}
.idx .k{{font-size:10.5px;color:rgba(245,239,230,.72);margin-top:2px;line-height:1.5}}
.panel.light .idx{{background:#fffdf7;border-color:var(--border)}}
.panel.light .idx .v{{color:var(--ink)}}
.panel.light .idx .k{{color:var(--ink-soft)}}
#osm{{height:260px;border-radius:var(--r-lg);z-index:0;box-shadow:inset 0 0 0 1px rgba(36,29,23,.08)}}
@media(max-width:640px){{#osm{{height:220px}}}}
#iklim-sel{{width:100%;background:var(--surface-2);border:1px solid var(--border);color:var(--ink);
 border-radius:var(--r-sm);padding:8px 10px;font-size:13px;font-family:inherit;margin:6px 0 8px;transition:border-color var(--dur-1)}}
#iklim-sel:focus{{border-color:var(--ember)}}
.risk{{display:inline-block;border-radius:999px;padding:2px 10px;font-size:11.5px;font-weight:600}}
.r-ok{{background:rgba(46,125,50,.12);color:#2e7d32}}
.r-mid{{background:rgba(237,108,2,.14);color:#b26a00}}
.r-hi{{background:rgba(198,40,40,.12);color:#b3261e}}
.kicker{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--ember-deep);display:flex;align-items:center;gap:8px}}
.panel.dark .kicker{{color:var(--ember-soft)}}
.count{{margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:10px;opacity:.65}}
.chip{{display:flex;justify-content:space-between;align-items:center;width:100%;text-align:left;margin-top:8px;
 background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:9px 12px;font-size:12px;cursor:pointer;font-family:inherit;color:var(--ink)}}
.chip:hover{{border-color:var(--ember);transform:translateY(-1px);box-shadow:var(--sh-1)}}
.chip b{{font-family:'JetBrains Mono',monospace}}
.chip.on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}
.schema{{margin-top:16px;background:var(--ink-2);color:var(--cream);border-radius:var(--r-lg);padding:16px;font-size:12px;line-height:1.8}}
.schema .kicker{{color:var(--ember-soft)}}
.schema ol{{margin:8px 0 0;padding-left:18px;color:rgba(245,239,230,.78)}}
/* ============ GRAPH ============ */
#gsvg{{width:100%;height:auto;display:block}}
.gnode{{cursor:pointer}} .gnode circle{{transition:r .2s var(--ease),stroke .2s var(--ease)}}
.gnode:hover circle{{stroke:#fff;stroke-width:2}}
.gnode:focus{{outline:none}} .gnode:focus circle{{stroke:#fff;stroke-width:3}}
.gnode.sel circle{{stroke:#fff;stroke-width:3}}
.ghint{{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.2em;color:rgba(245,239,230,.58);margin-top:6px}}
.legend{{display:flex;flex-wrap:wrap;gap:6px;border-top:1px solid rgba(245,239,230,.14);margin-top:10px;padding-top:12px}}
.leg{{display:flex;align-items:center;gap:7px;font-size:11px;color:rgba(245,239,230,.85);background:none;border:1px solid transparent;cursor:pointer;font-family:inherit;padding:8px 10px;border-radius:var(--r-md);min-height:44px}}
.leg:hover{{background:rgba(245,239,230,.07);border-color:rgba(245,239,230,.15)}}
.leg.on{{background:rgba(240,163,94,.14);border-color:rgba(240,163,94,.45)}}
.dot{{width:10px;height:10px;border-radius:50%;flex:none}}
/* ============ READER (swap animation) ============ */
#reader .r-rule{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--ember)}}
#reader h3{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(19px,2.4vw,22px);margin:6px 0;line-height:1.25}}
#reader ul{{font-size:12.5px;color:#3d352b;padding-left:18px;line-height:1.7;margin:8px 0}}
#reader .meta{{font-size:12px;color:var(--ink-soft);margin-top:6px;line-height:1.7}}
#reader .rec{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:10px 12px;font-size:12px;margin-top:10px}}
#reader-body.swap{{animation:reader-in var(--dur-2) var(--ease)}}
@keyframes reader-in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
/* ============ SECTIONS ============ */
h2{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(22px,2.8vw,28px);margin:34px 0 6px;line-height:1.2;letter-spacing:-.005em}}
.h-num{{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ember-deep);vertical-align:super;margin-right:8px}}
.note{{color:var(--ink-soft);font-size:12px}}
.grid4{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:16px 0}}
@media(min-width:900px){{.grid4{{grid-template-columns:repeat(4,1fr)}}}}
.card{{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--r-lg);padding:16px;box-shadow:var(--sh-1)}}
@keyframes rise{{from{{opacity:0;transform:translateY(12px);filter:blur(6px)}}to{{opacity:1;transform:none;filter:none}}}}
.card .n{{font-size:clamp(19px,2.2vw,24px);font-weight:600;word-break:break-word;font-variant-numeric:tabular-nums;line-height:1.25}}
.card .n.long{{font-size:15px}} .card .n.small-n{{font-size:13px}}
.card .l{{font-family:'JetBrains Mono',monospace;font-size:9.5px;letter-spacing:.14em;color:var(--ink-soft);margin-top:6px;text-transform:uppercase}}
/* ============ FLAGS ============ */
.flag{{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--r-lg);margin-top:10px;overflow:hidden;
 transition:border-color var(--dur-1) var(--ease),box-shadow var(--dur-2) var(--ease)}}
.flag[open]{{border-color:var(--ember);box-shadow:var(--sh-2)}}
.flag summary{{display:flex;align-items:center;gap:10px;padding:13px 14px;cursor:pointer;list-style:none;transition:background var(--dur-1)}}
.flag summary:hover{{background:rgba(200,80,26,.05)}}
.flag summary::-webkit-details-marker{{display:none}}
.rule{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;background:var(--ink);color:var(--cream);
 border-radius:6px;padding:3px 7px;flex:none}}
.sev{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.08em;flex:none}}
.sev-tinggi{{color:var(--sev-tinggi);font-weight:700}} .sev-sedang{{color:var(--amber);font-weight:700}} .sev-rendah{{color:var(--sev-rendah);font-weight:600}}
.flag-title{{font-size:13px;font-weight:600;flex:1}}
.flag .ev{{font-size:13px;color:#3d352b;padding:0 14px;line-height:1.7;margin:10px 0}}
.flag .meta{{font-size:12px;color:var(--ink-soft);margin-top:6px;padding:0 14px;line-height:1.7}}
.flag[open] .ev,.flag[open] .meta{{animation:flag-in var(--dur-2) var(--ease)}}
@keyframes flag-in{{from{{opacity:0;transform:translateY(-6px)}}to{{opacity:1;transform:none}}}}
/* ============ TABLES (row hover) ============ */
table{{width:100%;border-collapse:collapse;font-size:12.5px;line-height:1.55}}
table.light{{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--r-lg);overflow:hidden;box-shadow:var(--sh-1)}}
td{{padding:7px 9px;border-bottom:1px solid var(--border);vertical-align:top;transition:background var(--dur-1)}}
tbody tr:hover td{{background:rgba(200,80,26,.055)}}
.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.small{{color:var(--ink-soft)}}
a{{color:var(--ember-deep);text-underline-offset:2px}}
a:hover{{text-decoration-color:var(--ember)}}
.bar{{background:var(--surface);border-radius:6px;height:10px;min-width:120px;overflow:hidden}}
.bar div{{background:linear-gradient(90deg,var(--ember),var(--ember-soft));height:10px;border-radius:6px;transition:width var(--dur-4) var(--ease)}}
.months{{display:flex;align-items:flex-end;gap:8px;padding:12px 4px;overflow-x:auto}}
.mcol{{text-align:center;min-width:44px}} .months .bar{{width:34px;margin:0 auto}}
.months .bar,.bar-dec{{transition:height var(--dur-4) var(--ease)}}
.bar-dec{{width:34px;background:linear-gradient(180deg,#d8483c,#7e1d12);margin:0 auto;border-radius:4px 4px 0 0;box-shadow:0 0 0 0 rgba(216,72,60,0);animation:decpulse 3s ease-in-out infinite}}
@keyframes decpulse{{0%,100%{{box-shadow:0 0 0 0 rgba(216,72,60,0)}}50%{{box-shadow:0 0 12px 1px rgba(216,72,60,.35)}}}}
.mlabel{{font-size:10px;color:var(--ink-soft);margin-top:4px}} .mval{{font-size:10px}}
.toolbar{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;align-items:center}}
.toolbar input[type=search]{{background:var(--surface-2);border:1px solid var(--border);color:var(--ink);border-radius:var(--r-sm);padding:8px 12px;font-size:13px;min-width:230px;font-family:inherit;transition:border-color var(--dur-1),box-shadow var(--dur-1)}}
.toolbar input[type=search]:focus{{border-color:var(--ember);box-shadow:0 0 0 3px rgba(200,80,26,.12);outline:none}}
.btn{{background:var(--surface-2);border:1px solid var(--border);color:var(--ink);border-radius:var(--r-sm);padding:8px 14px;font-size:12px;cursor:pointer;text-decoration:none;display:inline-block;font-family:inherit}}
.btn.on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}
.btn:hover{{border-color:var(--ember);transform:translateY(-1px);box-shadow:var(--sh-1)}}
/* ============ OPEN DATA (orow) ============ */
.orow{{display:flex;justify-content:space-between;gap:12px;padding:var(--s3) 0;border-bottom:1px solid rgba(245,239,230,.14);font-size:13px;transition:opacity .4s var(--ease)}}
.orow span{{color:rgba(245,239,230,.72);font-size:12.5px}} .orow b{{color:var(--cream);text-align:right;font-size:12.5px;word-break:break-all;font-variant-numeric:tabular-nums}}
.dim{{font-size:12px;color:rgba(245,239,230,.74);line-height:1.7}}
.panel.light .orow{{border-bottom-color:var(--border)}}
.panel.light .orow span{{color:var(--ink-soft)}}
.panel.light .orow b{{color:var(--ink)}}
.panel.light .dim{{color:var(--ink-soft)}}
.lapor a{{color:var(--ember-soft)}}
#minimap{{border-radius:var(--r-lg);box-shadow:var(--sh-2)}}
#minimap .pin{{cursor:pointer}}
#minimap .pin:hover circle:nth-of-type(2){{stroke:#fff;stroke-width:2.5}}
/* ============ BOOT ============ */
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
.boot-log{{font-family:'JetBrains Mono',monospace;font-size:11px;color:#a99c8a;min-height:56px;text-align:left;border:1px solid #3a322a;border-radius:var(--r-md);padding:12px 14px;margin-bottom:18px;background:#1e1915}}
.boot-log div{{animation:stream-in .4s both}}
@keyframes stream-in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.boot-bar{{height:3px;background:#3a322a;border-radius:99px;overflow:hidden;margin-bottom:22px}}
.boot-bar i{{display:block;height:100%;width:40%;background:linear-gradient(90deg,#e05a1e,#f0a35e);border-radius:99px;animation:load 1.6s ease-in-out infinite}}
@keyframes load{{0%{{margin-left:-40%}}100%{{margin-left:100%}}}}
.boot-btn{{background:#e05a1e;color:#fff;border:none;border-radius:999px;padding:13px 34px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;box-shadow:0 10px 28px rgba(224,90,30,.4)}}
.boot-btn:hover{{background:var(--ember-soft);color:#171310;transform:translateY(-1px)}}
.boot-quiet{{display:block;margin:12px auto 0;font-size:12px;color:#a99c8a;text-decoration:underline;cursor:pointer;background:none;border:none;font-family:inherit}}
.boot-quiet:hover{{color:var(--ember-soft)}}
/* ============ CHAT (panel transition) ============ */
#chatfab{{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:45;width:56px;height:56px;border-radius:50%;
 background:var(--ember);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;
 box-shadow:0 10px 28px rgba(200,80,26,.45);transition:background var(--dur-1),transform var(--dur-1),box-shadow var(--dur-1),bottom var(--dur-2) var(--ease)}}
#chatfab:hover{{background:var(--ember-soft);transform:translateY(-2px);box-shadow:0 14px 34px rgba(200,80,26,.55)}}
#chatfab:active{{transform:scale(.94)}}
body.loc-open #chatfab{{bottom:calc(138px + env(safe-area-inset-bottom,0px))}}
#chatpanel{{position:fixed;right:16px;bottom:calc(84px + env(safe-area-inset-bottom,0px));z-index:45;width:min(420px,calc(100vw - 32px));
 max-height:min(560px,calc(100vh - 120px));display:flex;flex-direction:column;visibility:hidden;opacity:0;transform:translateY(14px) scale(.98);
 transition:opacity var(--dur-2) var(--ease),transform var(--dur-2) var(--ease),visibility 0s linear var(--dur-2);
 background:var(--surface-2);border:1px solid var(--border);border-radius:20px;overflow:hidden;
 box-shadow:0 24px 60px rgba(0,0,0,.3)}}
#chatpanel.show{{visibility:visible;opacity:1;transform:none;transition:opacity var(--dur-2) var(--ease),transform var(--dur-2) var(--ease)}}
#chatpanel.wide{{width:min(700px,calc(100vw - 32px));max-height:min(72vh,760px)}}
#chatpanel.wide #chatlog{{min-height:300px}}
#chatpanel .chead .w{{float:right;background:none;border:1px solid rgba(245,239,230,.3);color:rgba(245,239,230,.8);
 border-radius:8px;font-size:12px;cursor:pointer;padding:2px 8px;margin-left:6px;font-family:inherit;transition:border-color var(--dur-1),color var(--dur-1)}}
#chatpanel .chead .w:hover{{border-color:var(--ember-soft);color:var(--ember-soft)}}
#chatpanel .chead{{background:var(--ink-2);color:var(--cream);padding:12px 16px;font-size:13px}}
#chatpanel .chead b{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:17px}}
#chatpanel .chead .x{{float:right;background:none;border:none;color:rgba(245,239,230,.65);font-size:16px;cursor:pointer;transition:color var(--dur-1),transform var(--dur-1)}}
#chatpanel .chead .x:hover{{color:#ff9d9d;transform:rotate(90deg)}}
#chatlog{{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px;min-height:220px}}
.cmsg{{font-size:12.5px;line-height:1.65;border-radius:12px;padding:9px 12px;max-width:88%;animation:msg-in var(--dur-2) var(--ease)}}
@keyframes msg-in{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.cmsg.me{{align-self:flex-end;background:var(--ink);color:var(--cream)}}
.cmsg.ai{{align-self:flex-start;background:var(--surface);border:1px solid var(--border)}}
.cmsg .tag{{display:block;font-family:'JetBrains Mono',monospace;font-size:9px;opacity:.65;margin-top:4px}}
.csug{{display:flex;gap:6px;flex-wrap:wrap;padding:0 12px 8px}}
.csug button{{font-size:11px;background:var(--surface);border:1px solid var(--border);border-radius:999px;
 padding:6px 11px;cursor:pointer;font-family:inherit;color:var(--ink)}}
.csug button:hover{{border-color:var(--ember);transform:translateY(-1px)}}
#cform{{display:flex;gap:8px;padding:10px 12px;border-top:1px solid var(--border)}}
#cform input{{flex:1;border:1px solid var(--border);border-radius:var(--r-sm);padding:9px 12px;font-size:13px;font-family:inherit;background:var(--surface-2);transition:border-color var(--dur-1),box-shadow var(--dur-1)}}
#cform input:focus{{border-color:var(--ember);box-shadow:0 0 0 3px rgba(200,80,26,.12);outline:none}}
#cform button{{background:var(--ember);color:#fff;border:none;border-radius:var(--r-sm);padding:0 16px;font-size:13px;cursor:pointer}}
#cform button:hover{{background:var(--ember-soft);color:var(--ink-2)}}
.cdisc{{font-size:10.5px;color:var(--ink-soft);padding:0 14px 10px;line-height:1.6}}
.typing{{display:inline-block}} .typing i{{display:inline-block;width:6px;height:6px;border-radius:50%;
 background:var(--ember);margin-right:3px;animation:tblink 1s infinite}}
.typing i:nth-child(2){{animation-delay:.2s}} .typing i:nth-child(3){{animation-delay:.4s}}
@keyframes tblink{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
/* ============ LOCBANNER ============ */
#locbanner{{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:40;max-width:640px;margin:0 auto;
 background:var(--ink-2);color:var(--cream);border:1px solid rgba(240,163,94,.4);border-radius:18px;padding:16px 18px;
 box-shadow:0 12px 40px rgba(0,0,0,.4);display:none}}
#locbanner.show{{display:block;animation:rise .5s both}}
#locbanner .lb-title{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.22em;color:var(--ember-soft)}}
#locbanner p{{font-size:12px;line-height:1.7;color:rgba(245,239,230,.82)}}
#locbanner .lb-row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}}
#locbanner .pill{{height:36px;font-size:10px}}
#locbanner .lb-forget{{background:none;border:none;color:rgba(245,239,230,.6);text-decoration:underline;
 font-size:11px;cursor:pointer;margin-top:8px;font-family:inherit;padding:0}}
#locbanner .lb-forget:hover{{color:var(--ember-soft)}}
/* ============ FOOTER ============ */
.foot{{margin-top:40px;color:var(--ink-soft);font-size:11px;border-top:1px solid var(--border);padding-top:14px;line-height:2}}
.foot button{{background:none;border:none;color:var(--ember-deep);text-decoration:underline;cursor:pointer;font-size:11px;font-family:inherit;padding:0;transition:color var(--dur-1)}}
.foot button:hover{{color:var(--ember)}}
/* ============ M6 — MOBILE ============ */
.table-scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:var(--r-lg)}}
.table-scroll table{{min-width:560px}}
@media(max-width:640px){{
 .wrap{{padding:12px 10px calc(48px + env(safe-area-inset-bottom,0px))}}
 .hero{{padding:20px 16px;border-radius:var(--r-xxl)}}
 .hero h1{{font-size:clamp(30px,9vw,40px)}}
 .tiles{{gap:8px}} .tile{{padding:10px}}
 .tile .t-l{{font-size:8.5px;letter-spacing:.12em}}
 .pill{{height:38px;padding:0 14px;font-size:10px}}
 .toolbar input[type=search]{{min-width:0;flex:1}}
 .panel{{padding:14px;border-radius:var(--r-xxl)}}
 .panel .ptbtn,.panel .prb{{min-width:40px;height:40px;width:40px}}
 h2{{margin:26px 0 4px}}
 .boot-inner{{padding:16px}} .boot-log{{font-size:10px}}
 #locbanner{{left:8px;right:8px;bottom:calc(8px + env(safe-area-inset-bottom,0px));padding:12px 14px}}
 #chatfab{{right:12px;width:52px;height:52px}}
 .months{{gap:6px}} .mcol{{min-width:38px}}
 td{{padding:6px 7px}}
 #toasts{{top:10px;right:10px;left:10px;max-width:none}}
}}
/* ============ A11Y: reduced motion & focus ============ */
@media (prefers-reduced-motion:reduce){{
 .ticker-inner,.hero .orb,.boot-eye svg,.boot-eye::after,.boot-bar i,.typing i,
 .badge.live::before,.bar-dec,.bar div,.months .bar,.rv-init h2,.rv-init .ticker,.rv-init .grid4{{animation:none;transition:none}}
 .card,.hero,#locbanner.show,.toast,.toast.out,.skeleton::after{{animation:none}}
 .flag[open] .ev,.flag[open] .meta,#reader-body.swap,.cmsg{{animation:none}}
 .card:hover,.tile:hover,.pill:hover,.chip:hover,.btn:hover,.ptbtn:hover{{transform:none}}
}}
::selection{{background:var(--ember);color:var(--cream)}}
:focus-visible{{outline:2px solid var(--ember);outline-offset:2px;border-radius:6px}}
input[type=search]{{caret-color:var(--ember)}}
.scrollbox::-webkit-scrollbar{{width:10px;height:10px}}
.scrollbox::-webkit-scrollbar-thumb{{background:#c9bc9f;border-radius:8px;border:2px solid var(--cream)}}
.scrollbox::-webkit-scrollbar-track{{background:transparent}}
html.booted #boot{{display:none}}
</style>
<script>try{{if(!matchMedia('(prefers-reduced-motion: reduce)').matches){{document.documentElement.classList.add('rv-init');}}}}catch(e){{}}</script>
<script>try{{if(sessionStorage.getItem('mata_boot'))document.documentElement.classList.add('booted');}}catch(e){{}}</script></head><body>
<div id="toasts" role="status" aria-live="polite"></div>
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
    <button class="leg" data-f="tinggi"><span class="dot" style="background:var(--sev-tinggi)"></span>Tinggi</button>
    <button class="leg" data-f="sedang"><span class="dot" style="background:var(--sev-sedang)"></span>Sedang</button>
    <button class="leg" data-f="rendah"><span class="dot" style="background:var(--sev-rendah)"></span>Rendah</button>
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
   <div class="table-scroll scrollbox"><table><tr><td>ID</td><td>Paket</td><td class="num">Nilai</td><td>Pemenang</td><td>Sumber</td></tr>
   <tbody id="pkgs">{pkg_rows or '<tr><td colspan="5" class="small">Belum ada record — jalankan live-collect atau tunggu siklus berikutnya.</td></tr>'}</tbody></table></div>
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
 <section class="panel light" id="spse-panel">
  <div class="kicker">🏛 PBJ KAB. ACEH TENGAH — SPSE PUBLIK <span class="count" id="spse-meta">MEMUAT…</span></div>
  <div class="table-scroll" id="spse-body">
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
  </div>
  <p class="note" style="margin-top:8px">Sumber: spse.inaproc.id/acehtengahkab (portal SPSE LKPP — publik, tanpa login) ·
   cakupan: daftar paket terkini; riwayat &amp; pemenang via jalur terpisah. Indikasi, bukan vonis — verifikasi di SPSE.</p>
 </section>
 <section class="panel light" id="sapa-panel">
  <div class="kicker">📊 INDIKATOR RESMI KABUPATEN — API SAPA <span class="count" id="sapa-meta">MEMUAT…</span></div>
  <p class="note" id="sapa-baseline" style="margin:6px 0"></p>
  <div class="table-scroll" id="sapa-body">
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
  </div>
  <p class="note" style="margin-top:8px">Sumber: API SAPA/SPLP resmi Pemkab Aceh Tengah (api-splp.layanan.go.id — tanpa login) ·
   cakupan: indikator resmi per OPD (baseline anggaran &amp; cross-check sinyal PBJ; bukan daftar per-paket). Indikasi, bukan vonis.</p>
 </section>
 <section class="panel light" id="inaproc-panel">
  <div class="kicker">🧾 REALISASI PENGADAAN — INAPROC <span class="count" id="inaproc-meta">MEMUAT…</span></div>
  <p class="note" id="inaproc-baseline" style="margin:6px 0"></p>
  <div class="table-scroll" id="inaproc-body">
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
  </div>
  <p class="note" style="margin-top:8px">Sumber: data.inaproc.id (INAPROC — API publik, tanpa login) ·
   cakupan: realisasi pengadaan Kab. Aceh Tengah TA2026 (halaman pertama) ·
   diperbarui: <span id="inaproc-upd">—</span>. Indikasi, bukan vonis — verifikasi di SPSE/e-kontrak.</p>
 </section>

 <h2><span class="h-num">05</span> Pengunjung live</h2>
 {widget}
 <div class="foot">MATA · AI HackFest 2026 · indikasi berbasis data, bukan vonis hukum ·
  {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ·
  <button id="reboot">putar ulang pembuka</button></div>
</div></div>
<button id="chatfab" aria-label="Tanya MATA" title="Tanya MATA">
 <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
</button>
<div id="chatpanel" role="dialog" aria-label="Tanya MATA">
 <div class="chead"><b>Tanya MATA</b><button class="x" id="chatx" aria-label="Tutup">✕</button><button class="w" id="chatw" aria-label="Perlebar" title="Perlebar">⤢</button><br>
  <span style="font-size:11px;opacity:.65">Jawaban dari data dashboard ini.</span></div>
 <div id="chatlog"></div>
 <div class="csug">
  <button data-q="Apa indikasi tertinggi saat ini?">Indikasi tertinggi?</button>
  <button data-q="Bagaimana cara melapor?">Cara melapor?</button>
  <button data-q="Berapa total RUP Aceh Tengah?">Total RUP?</button>
 </div>
 <form id="cform"><input id="cinput" maxlength="500" placeholder="Tanya soal data ini…" autocomplete="off">
  <button type="submit" aria-label="Kirim">➤</button></form>
 <p class="cdisc">Isolasi: tanpa akses file/aksi, 5 tanya/jam, tercatat audit. Indikasi, bukan vonis.</p>
</div>
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
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var CITYC={city_json};
var FLAGS={flags_json};
function esc(s){{ var d=document.createElement('div'); d.textContent=(s==null?'':s); return d.innerHTML; }}
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
  g.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();focusFlag(g.getAttribute('data-rule'));}}}});
 }});
 document.querySelectorAll('.gnode[data-vendor]').forEach(function(g){{
  g.addEventListener('click',function(){{chipFilter(g.getAttribute('data-vendor'));}});
  g.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();chipFilter(g.getAttribute('data-vendor'));}}}});
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
 /* ---- peta OSM (Leaflet, open source) ---- */
 var osmMap=null, osmMarks=null;
 function drawMarkers(locs){{
  if(typeof L==='undefined'){{document.getElementById('osm-fallback').style.display='';return;}}
  if(!osmMap){{
   osmMap=L.map('osm',{{scrollWheelZoom:false}}).setView([-2.5,118],5);
   L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
    {{maxZoom:18,attribution:'© OpenStreetMap'}}).addTo(osmMap);
   osmMarks=L.layerGroup().addTo(osmMap);
   setTimeout(function(){{osmMap.invalidateSize();}},600);
  }}
  osmMarks.clearLayers();
  (locs||[]).forEach(function(Lc){{
   var la=Lc.lat, lo=Lc.lon, key=(Lc.city||'').toLowerCase();
   if((la===null||la===undefined)&&(CITYC[key]!==undefined)){{la=CITYC[key][0];lo=CITYC[key][1];}}
   if(la===null||la===undefined) return;
   var n=Lc.count||1;
   L.circleMarker([la,lo],{{radius:6+Math.min(n,9),color:'#c8501a',weight:2,fillColor:'#e05a1e',fillOpacity:.85}})
    .bindTooltip(esc(Lc.city)+' · '+n).addTo(osmMarks);
  }});
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
   drawMarkers(v.locations);
  }}).catch(function(){{}});
 }}
 setInterval(vrefresh,30000); vrefresh();
 /* ---- iklim Gayo (port niu-gayo-agroclimate, via /api/iklim) ---- */
 function riskCls(s){{s=(s||'').toLowerCase();
  if(/bahaya|tinggi|tutup/.test(s))return 'r-hi';
  if(/waspada|sedang|kurang/.test(s))return 'r-mid'; return 'r-ok';}}
 function iklimLoad(){{
  var sel=document.getElementById('iklim-sel'), box=document.getElementById('iklim-box');
  if(!sel||!box) return;
  fetch('/api/iklim?id='+encodeURIComponent(sel.value))
   .then(function(r){{return r.json();}}).then(function(d){{
    if(d.ok===false){{box.innerHTML='<p class="note">Iklim tak termuat: '+esc(d.error||'?')+'</p>';return;}}
    function row(k,v){{return '<div class="orow"><span>'+k+'</span><b>'+esc(v)+'</b></div>';}}
    function rowh(k,h){{return '<div class="orow"><span>'+k+'</span><b>'+h+'</b></div>';}}
    function pill(v){{return '<span class="risk '+riskCls(v)+'">'+esc(v)+'</span>';}}
    box.innerHTML=
     '<p class="dim">'+esc(d.loc.name)+' · '+d.loc.elev+' mdpl · '+d.current.temp+'°C · RH '+d.current.rh+'%</p>'
     +row('Hujan',d.current.rain+' mm/jam · harian '+d.daily.rain_sum+' mm')
     +row('Angin',d.current.wind+' km/jam')
     +row('Suhu kopi',d.kopi.suhu)
     +rowh('Karat daun',pill(d.kopi.karat))
     +'<p class="dim">'+esc(d.kopi.karat_desc)+'</p>'
     +rowh('Penjemuran',pill(d.kopi.jemur))
     +'<p class="dim">'+esc(d.kopi.jemur_desc)+'</p>'
     +rowh('Longsor',pill(d.siaga.longsor))
     +rowh('Danau/Peusangan',pill(d.siaga.danau))
     +rowh('Angin',pill(d.siaga.angin));
   }}).catch(function(){{box.innerHTML='<p class="note">Iklim tak termuat — coba lagi.</p>';}});
 }}
 document.getElementById('iklim-sel').addEventListener('change',iklimLoad); iklimLoad();
 /* ---- rel panel ala template: mati -> rel 56px, ruang dibagi saudara ---- */
 function pstate(){{try{{return JSON.parse(localStorage.getItem('mata_panels')||'{{}}');}}catch(e){{return{{}};}}}}
 function psave(s){{try{{localStorage.setItem('mata_panels',JSON.stringify(s));}}catch(e){{}}}}
 function plabel(p){{var k=p.querySelector('.kicker');
  var t=k?k.textContent.replace(/[–⤢]/g,'').replace(/^[^A-Za-z0-9]+/,'').trim().split(/\\s+/)[0]:'PANEL'; return (t||'PANEL').slice(0,9).toUpperCase();}}
 function praw(p,pid){{var r=p.querySelector(':scope > .prail'); if(r) return r;
  r=document.createElement('div'); r.className='prail'; r.setAttribute('role','button');
  r.setAttribute('tabindex','0'); r.setAttribute('aria-label','Buka panel '+plabel(p));
  r.innerHTML='<span class="prl"></span><button class="prb" tabindex="-1" aria-hidden="true">⤢</button>';
  r.firstChild.textContent=plabel(p);
  r.addEventListener('click',function(){{setPanel(pid,false);}});
  r.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();setPanel(pid,false);}}}});
  p.appendChild(r); return r;}}
 function setPanel(pid,off){{var s=pstate(); if(off)s[pid]=1; else delete s[pid]; psave(s); applyPanels();}}
 function applyPanels(){{document.querySelectorAll('.cols,.cols2').forEach(function(g,gi){{
  g.dataset.gi=gi;
  var ps=Array.prototype.slice.call(g.querySelectorAll(':scope > .panel'));
  var s=pstate(), off=ps.filter(function(p,i){{return s[gi+':'+i];}});
  if(off.length>=ps.length&&ps.length){{var last=ps[ps.length-1];
   delete s[gi+':'+(ps.length-1)]; psave(s); off.pop();}}
  var wide=window.innerWidth>=1100;
  ps.forEach(function(p,i){{
   var pid=gi+':'+i, isoff=!!s[pid];
   p.dataset.pid=pid; praw(p,pid);
   p.classList.toggle('prailed',isoff);
  }});
  if(!wide){{g.style.gridTemplateColumns='';return;}}
  var shares=g.classList.contains('cols2')?[7,5]:[3,6,3];
  var open=shares.filter(function(_,i){{return !s[gi+':'+i];}});
  var tot=open.reduce(function(a,b){{return a+b;}},0)||1;
  var zm=0;
  ['z1','z2','z3'].forEach(function(z,j){{if(g.classList.contains(z))zm=j+1;}});
  var boosted=shares.map(function(sh,i){{
   var k=gi+':'+i;
   if(s[k])return 0;
   if(zm===i+1)return sh*2.4;
   return sh;}});
  var btot=boosted.reduce(function(a,b){{return a+b;}},0)||1;
  g.style.gridTemplateColumns=shares.map(function(sh,i){{
   return s[gi+':'+i]?'56px':'minmax(0,'+(boosted[i]/btot*12).toFixed(2)+'fr)';}}).join(' ');
 }});}}
 window.addEventListener('resize',applyPanels);
 /* ---- perkecil/perbesar panel dalam halaman ---- */
 document.querySelectorAll('.panel:not(.notools)').forEach(function(p){{
  var k=p.querySelector('.kicker'); if(!k) return;
  var t=document.createElement('span'); t.className='ptools';
  t.innerHTML='<button class="ptbtn" data-a="mini" title="Tutup jadi rel">–</button>'
   +'<button class="ptbtn" data-a="zoom" title="Perbesar di halaman">⤢</button>';
  k.appendChild(t);
  t.querySelector('[data-a="mini"]').onclick=function(){{
   var pid=p.dataset.pid||('x:'+Array.prototype.indexOf.call(p.parentNode.children,p));
   setPanel(pid,true);}};
  t.querySelector('[data-a="zoom"]').onclick=function(){{
   var grid=p.closest('.cols'); if(!grid) return;
   var ps2=Array.prototype.slice.call(grid.querySelectorAll(':scope > .panel'));
   var me=ps2.indexOf(p), cls='z'+(me+1);
   var s=pstate(), pid=grid.dataset.gi+':'+me;
   if(s[pid]){{delete s[pid]; psave(s);}}
   var on=!grid.classList.contains(cls);
   grid.classList.remove('z1','z2','z3');
   if(on)grid.classList.add(cls);
   applyPanels();
   if(p.querySelector('#osm')&&osmMap)setTimeout(function(){{osmMap.invalidateSize();}},500);
  }};
 }});
 applyPanels();
 /* ---- Tanya MATA (jembatan agen terisolasi) ---- */
 var chatOpen=false, chatTimer=null;
 function cesc(s){{var d=document.createElement('div');d.textContent=s||'';return d.innerHTML;}}
 function cbubble(who,text,tag){{
  var log=document.getElementById('chatlog'), d=document.createElement('div');
  d.className='cmsg '+who;
  d.innerHTML='<span></span>'+(tag?'<span class="tag">'+cesc(tag)+'</span>':'');
  d.firstChild.textContent=text; log.appendChild(d); log.scrollTop=log.scrollHeight; return d;
 }}
 function cpoll(id,el){{
  fetch('/api/chat?id='+id).then(function(r){{return r.json();}}).then(function(d){{
   if(d.state==='done'){{el.remove();
    cbubble('ai',d.answer||'(kosong)','via '+(d.mode==='hermes'?'agen Hermes':'jawab lokal')+' · indikasi, bukan vonis');
   }} else setTimeout(function(){{cpoll(id,el);}},2000);
  }}).catch(function(){{el.remove();cbubble('ai','Jaringan gagal. Coba lagi.');}});
 }}
 function csend(q){{
  q=(q||'').trim(); if(!q) return;
  cbubble('me',q);
  var t=document.createElement('div'); t.className='cmsg ai';
  t.innerHTML='<span class="typing"><i></i><i></i><i></i></span>';
  var log=document.getElementById('chatlog'); log.appendChild(t); log.scrollTop=log.scrollHeight;
  fetch('/api/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{q:q}})}})
   .then(function(r){{return r.json();}}).then(function(d){{
    if(d.ok) cpoll(d.id,t);
    else {{t.remove();cbubble('ai',d.error||'Gagal.');}}
   }}).catch(function(){{t.remove();cbubble('ai','Jaringan gagal. Coba lagi.');}});
 }}
 document.getElementById('chatfab').onclick=function(){{
  chatOpen=!chatOpen;
  document.getElementById('chatpanel').classList.toggle('show',chatOpen);
  if(chatOpen&&!document.getElementById('chatlog').children.length)
   cbubble('ai','Halo, saya MATA. Tanya apa saja soal data di dashboard ini.');
 }};
 document.getElementById('chatx').onclick=function(){{chatOpen=false;
  document.getElementById('chatpanel').classList.remove('show');}};
 document.getElementById('chatw').onclick=function(){{
  document.getElementById('chatpanel').classList.toggle('wide');}};
 document.getElementById('cform').onsubmit=function(e){{e.preventDefault();
  var i=document.getElementById('cinput'); csend(i.value); i.value='';}};
 document.querySelectorAll('.csug button').forEach(function(b){{
  b.onclick=function(){{csend(b.getAttribute('data-q'));}};
 }});
}})();
/* ============ MATA UI/UX module v3 — toast · reveal · count-up · bars · swap · mobile ============ */
(function(){{
 var RM = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
 /* ---- M4: sistem toast ---- */
 var T = document.getElementById('toasts');
 function toast(msg, kind){{
  if(!T) return;
  var ic = kind==='ok' ? '✓' : (kind==='err' ? '⚠' : 'ℹ');
  var d = document.createElement('div');
  d.className = 'toast ' + (kind || 'info');
  d.setAttribute('role','status');
  d.innerHTML = '<span class="t-ic"></span><span class="t-msg"></span>';
  d.children[0].textContent = ic;
  d.children[1].textContent = msg;
  T.appendChild(d);
  while(T.children.length > 4) T.firstChild.remove();
  setTimeout(function(){{ d.classList.add('out'); setTimeout(function(){{ d.remove(); }}, 260); }}, 4200);
 }}
 window.__mataToast = toast;
 /* Gagal fetch API → toast (throttle 60 dtk per endpoint) */
 var lastT = {{}};
 var of = window.fetch;
 window.fetch = function(u, o){{
  return of.apply(this, arguments).catch(function(e){{
   try{{
    var path = String(u).split('?')[0], now = Date.now();
    if(path.indexOf('/api/') === 0 && (!lastT[path] || now - lastT[path] > 60000)){{
     lastT[path] = now;
     toast('Jaringan gagal ('+path+') — akan dicoba lagi otomatis.', 'err');
    }}
   }}catch(_e){{}}
   throw e;
  }});
 }};
 /* ---- M5: scroll reveal (h2 / ticker / grid4) ---- */
 var rvs = document.querySelectorAll('h2, .ticker, .grid4');
 if('IntersectionObserver' in window && !RM && rvs.length){{
  var io = new IntersectionObserver(function(es){{
   es.forEach(function(e){{ if(e.isIntersecting){{ e.target.classList.add('on'); io.unobserve(e.target); }} }});
  }}, {{threshold:.15}});
  rvs.forEach(function(el){{ io.observe(el); }});
 }} else {{ rvs.forEach(function(el){{ el.classList.add('on'); }}); }}
 /* ---- M5: count-up angka (hero tiles + kartu statistik) ---- */
 function countUp(el){{
  var raw = (el.textContent || '').trim();
  var m = raw.match(/^([\\d.,]+)(.*)$/);
  if(!m) return;
  var num = parseFloat(m[1].replace(/[.,]/g, ''));
  if(!isFinite(num) || num <= 0) return;
  if(/[\\d]/.test(m[2])) return; /* angka majemuk (mis. "48 / 30") dibiarkan statis */
  if(RM) return;
  var suf = m[2], t0 = null, D = 950;
  function frame(ts){{
   if(t0 === null) t0 = ts;
   var p = Math.min(1, (ts - t0) / D), e = 1 - Math.pow(1 - p, 3);
   el.textContent = Math.round(num * e).toLocaleString('id-ID') + suf;
   if(p < 1) requestAnimationFrame(frame);
   else el.textContent = raw;
  }}
  requestAnimationFrame(frame);
 }}
 var nums = document.querySelectorAll('.tile .t-n, .card .n');
 if('IntersectionObserver' in window && !RM && nums.length){{
  var io2 = new IntersectionObserver(function(es){{
   es.forEach(function(e){{ if(e.isIntersecting){{ countUp(e.target); io2.unobserve(e.target); }} }});
  }}, {{threshold:.4}});
  nums.forEach(function(el){{ io2.observe(el); }});
 }}
 /* ---- M5: animasi bar (vendor + bulanan) ---- */
 document.querySelectorAll('.bar > div[style]').forEach(function(d){{
  var w = (d.getAttribute('style') || '').match(/width:\\s*([\\d.]+)%/);
  if(w) d.setAttribute('data-w', w[1] + '%');
 }});
 document.querySelectorAll('.mcol > div[style]').forEach(function(b){{
  var h = (b.getAttribute('style') || '').match(/height:\\s*(\\d+)px/);
  if(h) b.setAttribute('data-h', h[1] + 'px');
 }});
 if(!RM){{
  setTimeout(function(){{
   document.querySelectorAll('.bar > div[data-w]').forEach(function(d){{
    d.style.width = '0%';
    requestAnimationFrame(function(){{ requestAnimationFrame(function(){{ d.style.width = d.getAttribute('data-w'); }}); }});
   }});
   document.querySelectorAll('.mcol > div[data-h]').forEach(function(b){{
    b.style.height = '0px';
    requestAnimationFrame(function(){{ requestAnimationFrame(function(){{ b.style.height = b.getAttribute('data-h'); }}); }});
   }});
  }}, 420);
 }}
 /* ---- M5: transisi isi pembaca ---- */
 var rb = document.getElementById('reader-body');
 if(rb && 'MutationObserver' in window){{
  var mo = new MutationObserver(function(){{
   rb.classList.remove('swap'); void rb.offsetWidth; rb.classList.add('swap');
  }});
  mo.observe(rb, {{childList:true, subtree:true}});
 }}
 /* ---- M6: chatfab naik saat banner lokasi tampil ---- */
 var lb = document.getElementById('locbanner');
 if(lb && 'MutationObserver' in window){{
  var sync = function(){{ document.body.classList.toggle('loc-open', lb.classList.contains('show')); }};
  new MutationObserver(sync).observe(lb, {{attributes:true, attributeFilter:['class']}});
  sync();
 }}
 /* ---- M4: feedback sukses (iklim termuat) ---- */
 var ikbox = document.getElementById('iklim-box'), ikDone = false;
 if(ikbox && 'MutationObserver' in window){{
  var mo2 = new MutationObserver(function(){{
   if(!ikDone && ikbox.querySelector('.orow')){{ ikDone = true; toast('Data Iklim Gayo termuat (cache 30 mnt).', 'ok'); }}
  }});
  mo2.observe(ikbox, {{childList:true, subtree:true}});
 }}
}})();
/* ============ SPSE publik — PBJ Aceh Tengah (live, tanpa izin) ============ */
(function(){{
 var body = document.getElementById('spse-body'), meta = document.getElementById('spse-meta');
 if(!body || !meta) return;
 function fmtRp(v){{
  if(v == null) return '—';
  if(typeof v === 'string') return v;
  return 'Rp ' + Number(v).toLocaleString('id-ID');
 }}
 function render(d){{
  var rows = d.packages && d.packages.length ? d.packages
           : (d.tender || []).concat(d.nontender || []);
  if(!rows.length){{
   body.innerHTML = '<p class="note">' + (d.error ? 'Tak termuat: ' + d.error
                    : 'Belum ada paket terbuka tercatat.') + '</p>';
   meta.textContent = 'KOSONG';
   return;
  }}
  var h = '<table class="light"><tr><td>Paket</td><td class="num">HPS</td>'
        + '<td>Tutup pendaftaran</td><td>Jenis</td><td></td></tr>';
  rows.forEach(function(p){{
   h += '<tr><td>' + (p.nama || p.name || '—')
      + (p.ulang ? ' <span class="risk r-mid">ULANG</span>' : '') + '</td>'
      + '<td class="num mono">' + fmtRp(p.hps != null ? p.hps : p.hps_str) + '</td>'
      + '<td>' + (p.tutup || '—') + '</td>'
      + '<td class="small">' + (p.jenis === 'nontender' ? 'Non-tender' : 'Tender') + '</td>'
      + '<td class="num"><a href="' + (p.url || '') + '" target="_blank" rel="noopener">SPSE ↗</a></td></tr>';
  }});
  body.innerHTML = h + '</table>';
  var age = d.fetched_at ? Math.max(0, Math.round(Date.now()/1000 - d.fetched_at)/60) : null;
  meta.textContent = rows.length + ' PAKET TERBUKA'
    + (d.stale ? ' · CACHE LAMA' : (age != null ? ' · ' + age + ' MNT' : ''));
 }}
 fetch('/api/spse')
  .then(function(r){{ return r.json(); }})
  .then(render)
  .catch(function(){{
   body.innerHTML = '<p class="note">Tak termuat — coba lagi.</p>';
   meta.textContent = 'ERROR';
   if(window.__mataToast) window.__mataToast('Panel SPSE tak termuat.', 'err');
  }});
}})();
/* ============ SAPA — indikator resmi kabupaten (API resmi, tanpa login) ============ */
(function(){{
 var body = document.getElementById('sapa-body'), meta = document.getElementById('sapa-meta');
 var base = document.getElementById('sapa-baseline');
 if(!body || !meta) return;
 function render(d){{
  if(!d || d.count === 0){{
   body.innerHTML = '<p class="note">' + (d && d.error ? 'Tak termuat: ' + d.error
                    : 'Belum ada data indikator.') + '</p>';
   meta.textContent = (d && d.stale) ? 'CACHE LAMA' : 'KOSONG';
   if(base) base.textContent = '';
   return;
  }}
  if(base) base.innerHTML = 'Realisasi Belanja APBD: <b>' + ((d.baseline && d.baseline.apbd_str) || '—') +
   '</b> (BPKAD) · ' + d.count + ' indikator · ' + d.n_opd + ' OPD' +
   (d.tahun && d.tahun.length ? ' · ' + d.tahun.join(', ') : '');
  var kat = (d.baseline && d.baseline.kategori) || [];
  var h = '<div class="idxgrid">' + kat.map(function(k){{
   return '<div class="idx"><div class="v">' + esc(k.str || '—') + '</div>' +
    '<div class="k">' + esc(k.nama || '') + '</div></div>';}}).join('') + '</div>';
  body.innerHTML = h || '<p class="note">Belum ada rincian kategori.</p>';
  var age = d.fetched_at ? Math.max(0, Math.round(Date.now()/1000 - d.fetched_at)/60) : null;
  meta.textContent = (d.status === 'live' ? 'LIVE' : 'CACHE LAMA')
    + (age != null ? ' · ' + age + ' MNT' : '');
 }}
 fetch('/api/sapa')
  .then(function(r){{ return r.json(); }})
  .then(render)
  .catch(function(){{
   body.innerHTML = '<p class="note">Tak termuat — coba lagi.</p>';
   meta.textContent = 'ERROR';
   if(window.__mataToast) window.__mataToast('Panel SAPA tak termuat.', 'err');
  }});
}})();
/* ============ INAPROC — realisasi pengadaan (API publik, VPS-direk) ============ */
(function(){{
 var body = document.getElementById('inaproc-body'), meta = document.getElementById('inaproc-meta');
 var base = document.getElementById('inaproc-baseline'), upd = document.getElementById('inaproc-upd');
 if(!body || !meta) return;
 function pick(r, keys){{
  for(var i=0;i<keys.length;i++){{ var v = r[keys[i]]; if(v != null && v !== '') return v; }}
  return null;
 }}
 function fmtNilai(v){{
  if(v == null) return '—';
  var n = Number(v);
  if(isNaN(n)) return String(v);
  if(n >= 1e12) return 'Rp ' + (n/1e12).toLocaleString('id-ID', {{maximumFractionDigits: 2}}) + ' T';
  if(n >= 1e9) return 'Rp ' + (n/1e9).toLocaleString('id-ID', {{maximumFractionDigits: 1}}) + ' M';
  if(n >= 1e6) return 'Rp ' + (n/1e6).toLocaleString('id-ID', {{maximumFractionDigits: 0}}) + ' jt';
  return 'Rp ' + n.toLocaleString('id-ID');
 }}
 function render(d){{
  var rows = (d && d.realisasi && d.realisasi.rows) || [];
  if(!rows.length){{
   body.innerHTML = '<p class="note">' + (d && d.error ? 'Tak termuat: ' + d.error
                    : 'Belum ada data realisasi.') + '</p>';
   meta.textContent = (d && d.stale) ? 'CACHE LAMA' : 'KOSONG';
   if(base) base.textContent = '';
   return;
  }}
  var hasWinner = rows.some(function(r){{ return pick(r, ['nama_penyedia','penyedia','nama_pemenang','pemenang']) != null; }});
  if(base) base.innerHTML = '<b>' + rows.length + ' paket</b> (halaman pertama, TA' + (d.tahun || '—') +
   ')' + (hasWinner ? ' · pemenang + nilai realisasi' : '') +
   ' · sumber: ' + (d.instansi || '');
  if(upd) upd.textContent = (d.last_update || '—') + ' (server INAPROC)';
  var h = '<table class="light"><tr><td>Paket</td><td>SKPD</td><td>Jenis</td>'
        + '<td>Status</td>' + (hasWinner ? '<td>Penyedia</td>' : '')
        + '<td class="num">Nilai</td></tr>';
  rows.forEach(function(r){{
   var paket = pick(r, ['nama_paket','nama_paket_pengadaan','paket','nama_kegiatan']);
   var skpd = pick(r, ['nama_satuan_kerja','satker','satuan_kerja','instansi']);
   var jenis = pick(r, ['jenis_pengadaan','kategori','kategori_pengadaan']);
   var status = pick(r, ['status_paket','status','status_kontrak']);
   var nilai = pick(r, ['total_nilai','nilai_kontrak','nilai_realisasi','nilai']);
   var winner = pick(r, ['nama_penyedia','penyedia','nama_pemenang','pemenang']);
   h += '<tr><td>' + (paket || '—') + '</td><td class="small">' + (skpd || '—') + '</td>'
      + '<td class="small">' + (jenis || '—') + '</td><td>' + (status || '—') + '</td>'
      + (hasWinner ? '<td class="small">' + (winner || '—') + '</td>' : '')
      + '<td class="num mono">' + fmtNilai(nilai) + '</td></tr>';
  }});
  body.innerHTML = h + '</table>';
  meta.textContent = (d.status === 'live' ? 'LIVE' : 'CACHE LAMA') + ' · INAPROC';
 }}
 fetch('/api/inaproc')
  .then(function(r){{ return r.json(); }})
  .then(render)
  .catch(function(){{
   body.innerHTML = '<p class="note">Tak termuat — coba lagi.</p>';
   meta.textContent = 'ERROR';
   if(window.__mataToast) window.__mataToast('Panel INAPROC tak termuat.', 'err');
  }});
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
        elif path == "/api/iklim":
            from urllib.parse import parse_qs
            lid = parse_qs(urlparse(self.path).query).get("id", ["takengon"])[0]
            try:
                self._send(json.dumps(iklim.get(lid), ensure_ascii=False),
                           "application/json")
            except Exception as e:
                self._send(json.dumps({"ok": False, "error": str(e)[:120]},
                                      ensure_ascii=False), "application/json")
        elif path == "/api/spse":
            self._send(json.dumps(spse_pub.load(), ensure_ascii=False),
                       "application/json")
        elif path == "/api/sapa":
            self._send(json.dumps(sapa_pub.load(), ensure_ascii=False),
                       "application/json")
        elif path == "/api/inaproc":
            self._send(json.dumps(inaproc_pub.load(), ensure_ascii=False),
                       "application/json")
        elif path == "/api/edge":
            self._send(json.dumps(edge_feed.summary(), ensure_ascii=False),
                       "application/json")
        elif path == "/api/chat":
            from urllib.parse import parse_qs
            from . import chat as _chat
            jid = parse_qs(urlparse(self.path).query).get("id", [""])[0]
            self._send(json.dumps(_chat.result(jid), ensure_ascii=False),
                       "application/json")
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
        elif path == "/api/chat":
            from . import chat as _chat
            self._send(json.dumps(_chat.submit(ip, body.get("q", ""))),
                       "application/json")
        elif path == "/api/spse-push":
            # Jalur B: kolektor laptop push data penuh (token: spse.push_token)
            self._send(json.dumps(spse_pub.push(body.get("token"),
                                                 body.get("data") or {}),
                                  ensure_ascii=False), "application/json")
        elif path == "/api/edge-push":
            # Jalur G: Edge Collector laptop push capture (token: edge.push_token)
            self._send(json.dumps(edge_feed.push(body.get("token"), body),
                                  ensure_ascii=False), "application/json")
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
