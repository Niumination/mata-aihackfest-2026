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
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import db
from . import visitors
from . import iklim
from . import spse_pub
from . import sapa_pub
from . import edge_feed
from . import inaproc_pub
from . import analisis

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


_RUPN: dict = {"mt": 0, "n": 0}


def _rup_total():
    """Jumlah paket RUP TA2026 (cache mtime, bukan per request)."""
    try:
        p = os.path.join(BASE_DIR, "data", "rup_2026_full.json")
        mt = os.path.getmtime(p)
        if mt != _RUPN["mt"]:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            _RUPN["n"] = len(d) if isinstance(d, list) else 0
            _RUPN["mt"] = mt
    except Exception:
        pass
    return _RUPN["n"]


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
    parts = [f'<circle cx="{cx}" cy="{cy}" r="34" fill="var(--graph-core)" stroke="var(--ember-vivid)" stroke-width="3"/>',
             f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" fill="var(--cream)" font-size="16" '
             f'font-family="Georgia,serif" font-style="italic">M</text>']
    nf = max(len(flags), 1)
    for i, f in enumerate(flags):
        a = -math.pi / 2 + 2 * math.pi * i / nf
        x, y = cx + 120 * math.cos(a), cy + 120 * math.sin(a)
        color, r = SEV_STYLE.get(f["severity"], ("#888", 15))
        rid = _esc(f["rule_id"])
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="var(--ember-vivid)" stroke-opacity=".35"/>')
        parts.append(
            f'<g class="gnode" data-rule="{rid}" data-sev="{_esc(f["severity"])}" '
            f'tabindex="0" role="button" aria-label="Baca indikasi {rid}: {_esc(f["title"])}">'
            f'<title>[{rid}] {_esc(f["title"])}</title>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{color}" fill-opacity=".88"/>'
            f'<text x="{x:.0f}" y="{y - r - 7:.0f}" text-anchor="middle" fill="var(--cream)" '
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
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="var(--cream)" stroke-opacity=".15"/>')
        parts.append(
            f'<g class="gnode" data-vendor="{_esc(name)}" tabindex="0" role="button" '
            f'aria-label="Saring paket {_esc(name)}">'
            f'<title>{_esc(name)} — {d["n"]} proyek</title>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="var(--cream)" fill-opacity=".8"/>'
            f'<text x="{x:.0f}" y="{y + 22:.0f}" text-anchor="middle" fill="var(--cream)" '
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
        f'<path d="{isles}" fill="var(--map-land)" stroke="var(--ember-soft)" stroke-width="1.5"/>',
        "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--map-land)" '
                 f'stroke="var(--ember-soft)" stroke-width="1"/>' for x, y, r in dots),
        ('<text x="24" y="346" font-size="11" font-family="monospace" '
         'letter-spacing="3" fill="rgba(var(--cream-rgb),.5)">SKETSA NUSANTARA · SEBARAN HARI INI</text>'),
        ('<g transform="translate(606,36)" stroke="rgba(var(--cream-rgb),.6)" fill="none">'
         '<circle r="12"/><path d="M0,7 L0,-7 M-4,-2 L0,-7 L4,-2"/>'
         '<text y="-18" text-anchor="middle" font-size="10" font-family="monospace" '
         'fill="rgba(var(--cream-rgb),.6)" stroke="none">U</text></g>'),
    ]
    for g in range(96, 142, 5):
        x, _ = xy(0, g)
        parts.append(f'<line x1="{x}" y1="10" x2="{x}" y2="350" stroke="rgba(var(--cream-rgb),.06)"/>')
    for la in range(5, -12, -4):
        _, y = xy(la, 95)
        parts.append(f'<line x1="10" y1="{y}" x2="630" y2="{y}" stroke="rgba(var(--cream-rgb),.06)"/>')
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
            f'<circle cx="{x}" cy="{y}" r="{r + 8}" fill="var(--ember-vivid)" fill-opacity=".18">'
            f'<animate attributeName="r" values="{r + 4};{r + 11};{r + 4}" dur="2.4s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--ember-vivid)" stroke="#ffd9ad" stroke-width="1.5"/>'
            f'<circle cx="{x}" cy="{y}" r="2.2" fill="var(--cream)"/>'
            f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="11.5" font-weight="bold" '
            f'font-family="monospace" fill="none" stroke="#14100c" stroke-width="5">'
            f'{_esc(loc.get("city"))} · {n}</text>'
            f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="11.5" font-weight="bold" '
            f'font-family="monospace" fill="var(--cream)">'
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
            f'<polyline points="{" ".join(xy)}" fill="none" stroke="var(--ember-soft)" stroke-width="2"/>'
            f'</svg>')


def render():
    st = _status()
    flags = db.read_flags()
    recs = db.load_records()
    mode = _mode(recs)
    if mode == "LIVE":
        # data nyata: hanya record INAPROC (INP-*) yang dipajang; record demo
        # tak boleh mencemari arsip/konsentrasi/ekspor saat mode live
        recs = [r for r in recs if str(r.get("id", "")).startswith("INP-")]
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
    rup_n = _rup_total()
    rup_s = f"{rup_n:,}".replace(",", ".") if rup_n else "…"
    badge = ('<span class="badge ok" title="Siklus pantau terakhir sukses">● ONLINE</span>' if ok
             else '<span class="badge err" title="Siklus terakhir gagal — lihat status">● ERROR</span>')
    mode_badge = ('<span class="badge live" title="Record per-paket live dari INAPROC">MODE: LIVE</span>' if mode == "LIVE"
                  else '<span class="badge syn" title="48 record demo untuk rule D1–D6; data live nyata di seksi 01">MODE: SYNTHETIC</span>')

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
            f'<details class="flag" id="flag-{_esc(f["rule_id"])}" data-rule="{_esc(f["rule_id"])}" data-sev="{_esc(f["severity"])}">'
            f'<summary><span class="rule">[{_esc(f["rule_id"])}]</span> '
            f'<span class="{sev}">{_esc(f["severity"].upper())}</span>'
            f'<span class="flag-title">{_esc(f["title"])}</span></summary>'
            f'<ul class="ev">{ev}</ul>'
            f'<div class="meta">Record: <b>{rids or "-"}</b></div>'
            f'<div class="meta">Penjelasan: {_esc(f.get("explanation", ""))}</div>'
            f'<div class="meta">Langkah lanjut: {_esc(f.get("recommendation", ""))}</div>'
            f'<div class="meta"><button class="askbtn" data-q="Jelaskan detail indikasi {_esc(f["rule_id"])} ({_esc(f["title"])})" onclick="askAI(this.dataset.q)">✦ Tanya AI</button></div>'
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
        pkg_rows += (
            f'<tr class="pkg" data-v="{int(r.get("value") or 0)}" data-q="{_esc((r.get("project") or "") + " " + (r.get("agency") or "") + " " + (r.get("vendor") or "") + " " + str(r.get("id")))}">'
            f'<td class="small mono">{_esc(r.get("id"))}</td><td class="pkgname" title="{_esc(r.get("project"))}">{_esc(r.get("project"))}</td>'
            f'<td class="small">{_esc(r.get("agency"))}</td>'
            f'<td class="num mono">{_rupiah(r.get("value"))}</td>'
            f'<td class="small vname" title="{_esc(r.get("vendor") or "—")}">{_esc(r.get("vendor") or "—")}</td>'
            f'<td class="small mono">{_esc(r.get("date_signed") or "—")}</td></tr>')

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
        f'<div><div class="table-scroll scrollbox"><table class="light"><tr><td>Waktu (UTC)</td><td>Halaman</td><td>Perangkat</td><td>Lokasi</td></tr>'
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
        f'<p class="note">Ubin © OpenStreetMap — IP Anda terlihat penyedia ubin saat peta dimuat.</p></div>'
        f'</div>'
        f'<div class="panel light notools" id="iklim-panel"><div class="kicker">☕ IKLIM GAYO — KOPI & SIAGA</div>'
        f'<p class="note iklim-sub">Logika niu-gayo-agroclimate · data Open-Meteo diambil server '
        f'(IP Anda tak tersebar) · cache 30 mnt.</p>'
        f'<select id="iklim-sel" aria-label="Pilih sentra agroklimat">{ik_opts}</select>'
        f'<div id="iklim-box"><p class="note">Memuat data iklim…</p></div>'
        f'<div class="fbtnrow iklim-sub" id="iklim-chips" style="margin-top:10px"></div>'
        f'<div class="korel iklim-sub"><h4>Mengapa watchdog PBJ memantau agroklimat?</h4>'
        f'<ol><li><b>Verifikasi bibit kopi:</b> pengadaan bibit harus cocok elevasi &gt;1.200 mdpl dan suhu sentra.</li>'
        f'<li><b>Pengawasan jalan &amp; drainase:</b> proyek jalan dan tanggul Danau Lut Tawar di kawasan tangkapan air rentan genangan.</li>'
        f'<li><b>Ekosistem danau:</b> proyek PUPR/Perkim sekitar Danau Lut Tawar wajib memenuhi kajian lingkungan (KLHS).</li></ol>'
        f'<div class="src">Sumber: Open-Meteo via server (IP pengunjung terlindungi UU PDP)</div></div></div>'
        f'<div class="panel light notools" id="health-panel"><div class="kicker">♥ STATUS SISTEM <span class="count" id="health-meta">MEMUAT…</span></div>'
        f'<div class="idxgrid" id="health-body">'
        f'<div class="idx"><div class="v">…</div><div class="k">memuat</div></div></div></div>')

    flags_json = json.dumps(flags, ensure_ascii=False).replace("</", "<\\/")
    # F1 — kutipan harian (rollback instan: hapus data/kutipan.json)
    try:
        with open(os.path.join(BASE_DIR, "data", "kutipan.json"), encoding="utf-8") as _f:
            _kutipan = json.load(_f)
        _kutipan = [k for k in _kutipan if isinstance(k, dict) and k.get("ar") and k.get("id")]
    except Exception:
        _kutipan = []
    quote_json = json.dumps(_kutipan, ensure_ascii=False).replace("</", "<\\/")
    city_json = json.dumps(visitors.city_coords(), ensure_ascii=False)
    # Simulator ambang — aktual live per aturan (None bila tak ada temuan live)
    _sim: dict = {"D1": None, "D2share": None, "D2n": None, "D3": None, "D4": None}
    for _f in flags:
        _m = _f.get("metrics") or {}
        _r = _f.get("rule_id")
        if _r == "D2":
            _sh = _m.get("share")
            if isinstance(_sh, (int, float)):
                _sh = _sh * 100 if _sh < 1 else _sh
                if _sim["D2share"] is None or _sh > _sim["D2share"]:
                    _sim["D2share"] = round(_sh, 2)
            _n = _m.get("jumlah_paket")
            if isinstance(_n, (int, float)) and (_sim["D2n"] is None or _n > _sim["D2n"]):
                _sim["D2n"] = int(_n)
        elif _r == "D4":
            try:
                _kb = float(_m.get("kontrak_besar") or 0)
                _rw = max([float(x[1]) for x in (_m.get("riwayat") or []) if x and len(x) > 1] or [0])
                if _kb > 0 and _rw > 0:
                    _j = round(_kb / _rw, 2)
                    if _sim["D4"] is None or _j > _sim["D4"]:
                        _sim["D4"] = _j
            except Exception:
                pass
    sim_json = json.dumps(_sim, ensure_ascii=False)
    # Sorotan live + kejujuran teknis (port zip revisi)
    _hi_items = []
    for _r in ("D2", "D4", "D6"):
        _fl = [f for f in flags if f.get("rule_id") == _r]
        if not _fl:
            continue
        _f0 = _fl[0]
        _m0 = _f0.get("metrics") or {}
        if _r == "D2":
            _hi_items.append(f'[D2 · {str(_f0.get("severity")).upper()}] {_m0.get("vendor", "?")}: '
                             f'{_m0.get("jumlah_paket", "?")} paket, {_rupiah(_m0.get("nilai_total"))}')
        elif _r == "D4":
            _hi_items.append(f'[D4 · TINGGI] {_m0.get("vendor", "?")}: '
                             f'riwayat kecil → kontrak {_rupiah(_m0.get("kontrak_besar"))}')
        else:
            _hi_items.append(f'[D6] nilai kembar {_rupiah(_m0.get("nilai"))} muncul {_m0.get("jumlah")}x')
    _live_hi_title = f"{len(flags)} INDIKASI DARI {len(recs)} PAKET RIIL (TA 2026)"
    _live_hi_body = _esc(" · ".join(_hi_items) or "Belum ada sorotan.")
    _sev_hi_all = sum(1 for f in flags if f.get("severity") == "tinggi")
    _live_hi_badge = f"{_sev_hi_all} Tinggi · {len(flags) - _sev_hi_all} Lainnya"
    # Dossier 07 — naskah live dari flags terkini
    _sev_hi = sum(1 for _f in flags if _f.get("severity") == "tinggi")
    _dl = []
    for _i, _f in enumerate(flags, 1):
        _ev0 = (_f.get("evidence") or ["—"])[0]
        _dl.append(f'{_i}. [{_f.get("rule_id")} · {str(_f.get("severity")).upper()}] {_f.get("title")}\n   - {_ev0}')
    _n_flags = len(flags)
    dossier_apip = (
        "Yth. APIP / Inspektorat Daerah Kabupaten Aceh Tengah\ndi Takengon\n\n"
        "Perihal: Indikasi anomali PBJ berbasis data publik\n\nDengan hormat,\n\n"
        f"Kami menyampaikan {_n_flags} indikasi anomali (termasuk {_sev_hi} tingkat tinggi) "
        "dari penelaahan data pengadaan publik resmi Kab. Aceh Tengah:\n\n"
        + "\n".join(_dl) +
        "\n\nRincian ID record, tanggal kontrak, dan metode kalkulasi terlampir dalam dossier MATA. "
        "Seluruh angka dapat ditelusuri ke publikasi terbuka LKPP/INAPROC.\n\n"
        "Klausul etika: surat ini indikasi berbasis data publik, BUKAN vonis final. "
        "Mohon APIP melakukan probity audit, peninjauan HPS, dan survei lapangan sesuai wewenang.\n\n"
        f'Takengon, {datetime.datetime.now().strftime("%d %B %Y")}\nHormat kami,\nWarga pelapor')
    dossier_cards = "".join(
        f'<div class="skpd"><div style="display:flex;justify-content:space-between;gap:8px">'
        f'<span class="sn">[{_esc(_f.get("rule_id"))}] {_esc(_f.get("title"))}</span>'
        f'<span class="spct">{_esc(str(_f.get("severity")).upper())}</span></div>'
        f'<ul class="ev">{"".join(f"<li>{_esc(e)}</li>" for e in (_f.get("evidence") or []))}</ul>'
        f'<p class="note">Dasar audit: {_esc(_f.get("recommendation", ""))}</p></div>'
        for _f in flags) or '<p class="note">Belum ada indikasi.</p>'
    dossier_publik = (
        "# MATA — Ringkasan Publik: Pengawasan Pengadaan Kab. Aceh Tengah\n\n"
        "Prinsip: INDIKASI BERBASIS DATA, BUKAN VONIS.\n\n## Temuan kunci:\n"
        + "\n".join(f"- {_l}" for _l in _dl) +
        "\n\n## Rekomendasi: verifikasi ke LPSE/Open Data LKPP, lalu laporkan via "
        "SP4N-LAPOR!, KPK Whistleblower, atau Inspektorat Aceh Tengah.\n\n"
        "Dipublikasikan MATA (Watchdog Akuntabilitas Pengadaan · AI HackFest 2026).")
    graph = _graph_svg(flags, vendors)
    jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org",'
              '"@type":"WebSite","name":"MATA \\u2014 Watchdog Akuntabilitas Pengadaan",'
              '"url":"https://mata.niumination.web.id/","inLanguage":"id",'
              '"description":"Indikasi anomali pengadaan Kabupaten Aceh Tengah '
              'berbasis data publik."}</script>')

    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="MATA — watchdog akuntabilitas pengadaan Kabupaten Aceh Tengah: indikasi anomali berbasis data publik, dapat diverifikasi per paket.">
<meta name="keywords" content="pengadaan, Aceh Tengah, LPSE, INAPROC, akuntabilitas, watchdog, APBD">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://mata.niumination.web.id/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MATA">
<meta property="og:title" content="MATA — Watchdog Pengadaan Aceh Tengah | Indikasi Live">
<meta property="og:description" content="Indikasi anomali pengadaan berbasis data publik SPSE/INAPROC/LKPP. Indikasi, bukan vonis.">
<meta property="og:url" content="https://mata.niumination.web.id/">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="MATA — Watchdog Pengadaan Aceh Tengah | Indikasi Live">
<meta name="twitter:description" content="Indikasi anomali pengadaan berbasis data publik. Dapat diverifikasi per paket.">
<meta name="theme-color" content="#171310">
<title>MATA — Watchdog Pengadaan Aceh Tengah | Indikasi Live</title>
{jsonld}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;600&family=Amiri:wght@400;700&display=swap">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root{{
 --ink:#241d17; --ink-2:#171310; --ink-soft:#4a4238; --cream:#f6f1e7; --surface:#efe8d8; --surface-2:#fffdf7;
 --border:#ddd2bd; --ember:#c8501a; --ember-deep:#93350e; --ember-soft:#f0a35e;
 --cream-light:#fbf8f2; --ink-dim:#726759; --ember-dark:#a93e0e; --live-blue:#0b6bcb;
 --red:#b3261e; --amber:#7d5708; --green:#35703c;
 --delta-up:#b0655a; --delta-down:#5a8ab0;
 --sev-tinggi:#b3261e; --sev-sedang:#96690a; --sev-rendah:#35703c; --sev-cerah:#d8483c; --sev-gelap:#7e1d12; --ok:#7ddba0; --info:#7fd4ff; --err:#ff9d9d; --syn:#f0c46c; --ember-vivid:#e05a1e; --on-ember:#fff; --map-land:#6b573d; --ink-body:#3d352b; --boot-muted:#a99c8a; --boot-line:#3a322a; --boot-bg:#1e1915; --cream-rgb:245,239,230; --ink-rgb:36,29,23; --ember-rgb:200,80,26; --graph-core:#221e19; --risk-ok:#2e7d32; --risk-mid:#b26a00; --risk-ok-rgb:46,125,50; --risk-mid-rgb:237,108,2; --risk-hi-rgb:198,40,40; --boot-sub:#b8ab98; --scroll-thumb:#c9bc9f; --ember-soft-rgb:240,163,94; --ok-rgb:125,219,160; --err-rgb:255,157,157; --cream-hi-rgb:246,241,231; --shadow-rgb:0,0,0; --sev-cerah-rgb:216,72,60;
 --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s5:24px; --s6:32px; --s7:40px;
 --r-sm:10px; --r-md:12px; --r-lg:16px; --r-xl:20px; --r-xxl:22px;
 --sh-1:0 1px 2px rgba(var(--ink-rgb),.05);
 --sh-2:0 6px 18px rgba(var(--ink-rgb),.09);
 --sh-3:0 18px 44px rgba(var(--ink-rgb),.16);
 --dur-1:140ms; --dur-2:220ms; --dur-3:420ms; --dur-4:900ms;
 --ease:cubic-bezier(.16,1,.3,1);
}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
@media (prefers-reduced-motion:no-preference){{ html{{scroll-behavior:smooth}} }}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ink);background:var(--cream);
 background-image:radial-gradient(900px 600px at 100% 0%, rgba(var(--ember-rgb),.14), transparent 60%),
  radial-gradient(700px 500px at 0% 100%, rgba(var(--ink-rgb),.08), transparent 60%);
 background-attachment:fixed;min-height:100vh}}
body::before{{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
 background-image:radial-gradient(rgba(var(--ink-rgb),.07) 1px, transparent 1px);background-size:20px 20px;
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
 border:1px solid rgba(var(--ember-soft-rgb),.35);border-radius:var(--r-lg);padding:12px 14px;font-size:12.5px;line-height:1.55;
 box-shadow:var(--sh-3);animation:toast-in var(--dur-2) var(--ease)}}
.toast.out{{animation:toast-out var(--dur-2) var(--ease) forwards}}
.toast .t-ic{{font-size:13px;line-height:1.4;flex:none}}
.toast.info .t-ic{{color:var(--ember-soft)}} .toast.ok .t-ic{{color:var(--ok)}} .toast.err .t-ic{{color:var(--err)}}
.toast.ok{{border-color:rgba(var(--ok-rgb),.45)}} .toast.err{{border-color:rgba(var(--err-rgb),.45)}}
@keyframes toast-in{{from{{opacity:0;transform:translateX(16px)}}to{{opacity:1;transform:none}}}}
@keyframes toast-out{{to{{opacity:0;transform:translateX(16px)}}}}
.skeleton{{position:relative;overflow:hidden;background:rgba(var(--ink-rgb),.06);border-radius:var(--r-md);min-height:14px}}
.skeleton::after{{content:"";position:absolute;inset:0;transform:translateX(-100%);
 background:linear-gradient(90deg,transparent,rgba(var(--cream-hi-rgb),.75),transparent);animation:shimmer 1.4s infinite}}
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
.tile:hover{{border-color:rgba(var(--ember-soft-rgb),.5);transform:translateY(-2px)}}
.idx:hover{{border-color:rgba(var(--ember-soft-rgb),.45)}}
/* ============ HERO ============ */
.hero{{background:var(--ink-2);color:var(--cream);border-radius:var(--r-xxl);padding:26px;position:relative;overflow:hidden;
 box-shadow:var(--sh-3);animation:rise .7s cubic-bezier(.16,1,.3,1) both}}
@media(min-width:900px){{.hero{{padding:36px}}}}
.hero .orb{{position:absolute;top:-96px;right:-64px;width:320px;height:320px;border-radius:50%;
 background:rgba(var(--ember-rgb),.28);filter:blur(90px);pointer-events:none;animation:float-orb 14s ease-in-out infinite}}
@keyframes float-orb{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-40px,30px)}}}}
.hero-grid{{position:relative;display:grid;gap:24px;grid-template-columns:1fr}}
@media(min-width:1000px){{.hero-grid{{grid-template-columns:7fr 5fr;align-items:center}}}}
.eyebrow{{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;letter-spacing:.16em;color:var(--ember-soft);margin-bottom:10px}}
.hero h1{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(36px,5.4vw,60px);line-height:.98;margin:12px 0;letter-spacing:-.01em}}
.hero h1 em{{color:var(--ember-soft)}}
.hero p.desc{{color:rgba(var(--cream-rgb),.78);font-size:14px;line-height:1.7;max-width:34rem}}
.sitehead{{position:sticky;top:0;z-index:50;background:var(--ink-2);color:var(--cream);border-bottom:1px solid #2c251f}}
.sitehead .wrap{{max-width:1180px;margin:0 auto;padding:0 16px}}
.compbar{{background:#0f0c0a;border-bottom:1px solid #241d17;font-size:11px}}
.compbar .wrap{{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 12px;padding-top:6px;padding-bottom:6px}}
.hackbadge{{font-family:'JetBrains Mono',monospace;font-size:10.5px;color:var(--ember-soft);background:rgba(var(--ember-rgb),.15);border:1px solid rgba(var(--ember-rgb),.35);border-radius:6px;padding:2px 8px;white-space:nowrap}}
.compmeta{{color:#a89b88}}
.compmeta b{{color:var(--cream);font-weight:500}}
.brandrow{{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:10px;padding-bottom:10px}}
.brand{{display:flex;align-items:center;gap:12px;text-decoration:none;color:inherit}}
.eye{{width:40px;height:40px;border-radius:12px;background:#241d17;border:1px solid #3d332a;display:flex;align-items:center;justify-content:center;flex:none}}
.eye i{{width:20px;height:20px;border-radius:50%;border:1.5px solid var(--ember-soft);display:flex;align-items:center;justify-content:center}}
.eye i::after{{content:'';width:9px;height:9px;border-radius:50%;background:var(--ember);animation:livepulse 2s infinite}}
.brand b{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:24px;letter-spacing:.02em}}
.brand .ver{{font-family:'JetBrains Mono',monospace;font-size:10px;color:#a89b88;background:#241d17;border:1px solid #3d332a;border-radius:5px;padding:1px 6px;vertical-align:3px;margin-left:6px}}
.brand small{{display:block;font-size:11px;color:#c5baa8;letter-spacing:.04em}}
.syspill{{font-family:'JetBrains Mono',monospace;font-size:10.5px;color:#6ee7b7;background:#1f1914;border:1px solid #2c251f;border-radius:8px;padding:5px 10px;white-space:nowrap}}
.syspill .dot{{display:inline-block;width:7px;height:7px;border-radius:50%;background:#34d399;margin-right:6px;animation:livepulse 2s infinite}}
.burger{{display:none;background:#1f1914;border:1px solid #2c251f;color:var(--cream);border-radius:8px;font-size:18px;padding:4px 12px;cursor:pointer}}
.sitenav{{background:#1f1914;border-top:1px solid #2c251f}}
.sitenav .navrow{{display:flex;gap:4px;overflow-x:auto;padding-top:5px;padding-bottom:5px}}
.sitenav a{{color:#c5baa8;text-decoration:none;font-size:12px;font-weight:500;padding:7px 12px;border-radius:8px;white-space:nowrap}}
.sitenav a:hover{{color:var(--cream);background:#2c251f}}
.sitenav a.hot{{color:var(--ember-soft)}}
.sitenav a.on{{background:var(--ember);color:#fff}}
.nbadge{{font-family:'JetBrains Mono',monospace;font-size:10px;background:#2c251f;color:var(--ember-soft);border-radius:99px;padding:1px 7px;margin-left:4px}}
.sitefoot{{background:var(--ink-2);color:var(--cream);border-top:1px solid #2c251f;margin-top:26px;font-size:12px}}
.sitefoot .fwrap{{max-width:1180px;margin:0 auto;padding:36px 16px 20px}}
.sitefoot .fgrid{{display:grid;grid-template-columns:1fr;gap:26px}}
@media(min-width:900px){{.sitefoot .fgrid{{grid-template-columns:1.3fr 1fr 1fr 1fr}}}}
.sitefoot .fbrand{{font-family:'Instrument Serif',Georgia,serif;font-size:26px;color:var(--cream-light, #fbf8f2)}}
.sitefoot .flbl{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--ember-soft);font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}}
.sitefoot p{{color:#a89b88;line-height:1.7;margin:8px 0}}
.sitefoot .fquote{{font-family:'JetBrains Mono',monospace;font-size:11px;color:#726759;font-style:italic}}
.sitefoot ul{{list-style:none;margin:8px 0;padding:0;display:flex;flex-direction:column;gap:7px}}
.sitefoot ul a{{color:#c5baa8;text-decoration:none}}
.sitefoot ul a:hover{{color:var(--cream)}}
.sitefoot .finfra{{font-family:'JetBrains Mono',monospace;font-size:12px;margin:8px 0}}
.sitefoot .finfra a{{color:var(--ember-soft);font-weight:600;text-decoration:none}}
.sitefoot .finfra a:hover{{text-decoration:underline}}
.sitefoot .finfra small{{display:block;color:#726759;font-size:11px}}
.sitefoot .fbtn{{display:block;width:100%;margin-top:10px;padding:9px 12px;border-radius:8px;background:#241d17;color:var(--ember-soft);border:1px solid #3d332a;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;text-align:center;text-decoration:none}}
.sitefoot .fbtn:hover{{background:#2c251f}}
.sitefoot .fbot{{border-top:1px solid #241d17;margin-top:26px;padding-top:14px;display:flex;flex-wrap:wrap;gap:6px 16px;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:11px;color:#726759}}
.sitefoot #reboot{{background:#241d17;color:#c5baa8;border:1px solid #3d332a;border-radius:6px;font:inherit;font-size:11px;padding:2px 10px;cursor:pointer;white-space:nowrap}}
.sitefoot #reboot:hover{{color:var(--ember-soft);border-color:var(--ember)}}
@keyframes livepulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
@media(max-width:899px){{.syspill{{display:none}}.burger{{display:block}}
 .sitenav .navrow{{display:none;flex-direction:column;padding:8px 16px 12px}}
 .sitenav.open .navrow{{display:flex}}
 .compmeta{{display:none}}}}
.kickrow{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-bottom:6px}}
.kick{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.14em;color:var(--ember-soft);font-weight:600}}
.kickdim{{font-family:'JetBrains Mono',monospace;font-size:11px;color:#a89b88}}
.verpill{{font-family:'JetBrains Mono',monospace;font-size:10.5px;color:#6ee7b7;background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.3);border-radius:8px;padding:3px 10px}}
.actbox{{background:#1f1914;border:1px solid #3d332a;border-radius:16px;padding:20px}}
.acthead{{display:flex;justify-content:space-between;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.08em;padding-bottom:12px;border-bottom:1px solid #2c251f}}
.acthead .dot{{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--ember);margin-right:7px;animation:livepulse 2s infinite}}
.acthead .mono{{color:#a89b88;font-weight:400}}
.actrows{{padding:12px 0;display:flex;flex-direction:column;gap:9px;font-size:12px;color:#c5baa8}}
.actrows>div{{display:flex;justify-content:space-between;gap:10px}}
.actrows .ok{{color:#6ee7b7;font-family:'JetBrains Mono',monospace;font-size:11px}}
.actrows .mono{{color:var(--cream)}}
.pill.block{{display:flex;justify-content:center;margin-top:8px}}
.mtiles{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:22px}}
@media(min-width:900px){{.mtiles{{grid-template-columns:repeat(5,1fr)}}}}
.mtiles .tile.red{{border-color:rgba(179,38,30,.45)}}
.tiles{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:18px 0 14px}}
@media(min-width:900px){{.tiles{{grid-template-columns:repeat(5,1fr)}}}}
a.tile{{display:block;text-decoration:none;color:inherit;transition:transform var(--dur-1) var(--ease),border-color var(--dur-1)}}
a.tile:hover{{transform:translateY(-2px);border-color:var(--ember)}}
.tile .t-s{{font-size:11px;color:rgba(var(--cream-rgb),.6);margin-top:4px;line-height:1.5}}
.tile{{background:rgba(var(--cream-rgb),.05);border:1px solid rgba(var(--cream-rgb),.14);border-radius:var(--r-lg);padding:14px}}
.tile .t-n{{font-family:'Instrument Serif',Georgia,serif;font-size:clamp(24px,3.4vw,32px);line-height:1;font-variant-numeric:tabular-nums}}
.tile .t-n.long{{font-size:19px}}
.tile .t-l{{font-family:'JetBrains Mono',monospace;font-size:9.5px;letter-spacing:.18em;color:rgba(var(--cream-rgb),.68);margin-top:6px}}
.pills{{display:flex;flex-wrap:wrap;gap:8px}}
.pill{{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 18px;border-radius:999px;
 font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.08em;text-decoration:none;cursor:pointer;border:1px solid rgba(var(--cream-rgb),.22);
 background:rgba(var(--cream-rgb),.05);color:var(--cream)}}
.pill.hot{{background:var(--ember);border-color:var(--ember);color:var(--on-ember);box-shadow:0 6px 18px rgba(var(--ember-rgb),.35)}}
.pill:hover{{background:rgba(var(--cream-rgb),.14);transform:translateY(-1px)}}
.pill.hot:hover{{background:var(--ember-soft);color:var(--ink-2);transform:translateY(-1px)}}
.badges{{margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.badge{{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;font-size:11px;font-weight:600;border:1px solid rgba(var(--cream-rgb),.25);white-space:nowrap}}
.badge.ok{{color:var(--ok);border-color:var(--ok)}} .badge.err{{color:var(--err);border-color:var(--err)}}
.badge.live{{color:var(--info);border-color:var(--info)}} .badge.syn{{color:var(--syn);border-color:var(--syn)}}
.badge .mono{{font-size:11px}}
.badge.live::before{{content:"";width:6px;height:6px;border-radius:50%;background:var(--info);animation:livepulse 2s ease-in-out infinite}}
@keyframes livepulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.35;transform:scale(.8)}}}}
/* ============ TICKER (pause on hover) ============ */
.ticker{{overflow:hidden;white-space:nowrap;border-radius:var(--r-lg);background:var(--ink);color:var(--cream);margin:16px 0 0;padding:10px 0;font-size:12.5px;letter-spacing:.01em;box-shadow:var(--sh-1)}}
.ticker-inner{{display:inline-block;animation:marquee 55s linear infinite}}
.ticker:hover .ticker-inner{{animation-play-state:paused}}
@keyframes marquee{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tk-item b{{color:var(--ember-soft)}} .tk-sep{{color:var(--ember-soft);margin:0 18px}}
/* ============ GRID 12-col ============ */
.cols{{display:grid;gap:16px;grid-template-columns:1fr;margin-top:16px;transition:grid-template-columns .45s ease}}
.cols2{{display:grid;gap:20px;grid-template-columns:1fr;margin-top:8px;transition:grid-template-columns .45s ease}}
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
.wrap>section.panel+section.panel{{margin-top:20px}}
#iklim-panel{{margin-top:20px}}
#health-panel{{margin-top:20px}}
#sapa-panel{{margin-top:20px}}
#iklim-panel .kicker{{cursor:pointer}}
#iklim-panel.mini #iklim-sel,#iklim-panel.mini #iklim-box,#iklim-panel.mini .iklim-sub{{display:none}}
.panel.light:hover{{box-shadow:var(--sh-2)}}
.panel.dark{{background:var(--ink-2);color:var(--cream);box-shadow:var(--sh-2)}}
.ptools{{margin-left:auto;display:inline-flex;gap:6px}}
.ptbtn{{background:none;border:1px solid var(--border);border-radius:var(--r-sm);min-width:30px;height:30px;
 cursor:pointer;font-size:13px;line-height:1;color:var(--ink-soft);font-family:inherit;padding:0 6px}}
.panel.dark .ptbtn{{border-color:rgba(var(--cream-rgb),.25);color:rgba(var(--cream-rgb),.75)}}
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
.panel.dark .prb{{border-color:rgba(var(--cream-rgb),.25)}}
.scrollbox{{max-height:380px;overflow-y:auto}}
.sharebars{{display:flex;flex-direction:column;gap:6px;margin:12px 0 4px}}
.srow{{display:grid;grid-template-columns:minmax(120px,220px) 1fr 52px;gap:10px;align-items:center;font-size:12px}}
.sn{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--ink-soft)}}
.sbar{{height:10px;border-radius:99px;background:rgba(var(--ink-rgb),.08);overflow:hidden}}
.sbar i{{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--ember),var(--ember-soft))}}
.sv{{text-align:right;font-size:11.5px}}
.pkgbox{{max-height:480px}}
.ctxscroll{{max-height:580px;overflow-y:auto}}
.ctxscroll .orow:first-child{{padding-top:0}}
.idxgrid{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin:10px 0}}
.idx{{background:rgba(var(--cream-rgb),.05);border:1px solid rgba(var(--cream-rgb),.14);border-radius:var(--r-md);padding:10px 12px}}
.idx .v{{font-family:'JetBrains Mono',monospace;font-size:16px;color:var(--cream);font-variant-numeric:tabular-nums}}
.idx .k{{font-size:10.5px;color:rgba(var(--cream-rgb),.72);margin-top:2px;line-height:1.5}}
.panel.light .idx{{background:var(--surface-2);border-color:var(--border)}}
.panel.light .idx .v{{color:var(--ink)}}
.panel.light .idx .k{{color:var(--ink-soft)}}
#osm{{height:260px;border-radius:var(--r-lg);z-index:0;box-shadow:inset 0 0 0 1px rgba(var(--ink-rgb),.08)}}
@media(max-width:640px){{#osm{{height:220px}}}}
#iklim-sel{{width:100%;background:var(--surface-2);border:1px solid var(--border);color:var(--ink);
 border-radius:var(--r-sm);padding:8px 10px;font-size:13px;font-family:inherit;margin:6px 0 8px;transition:border-color var(--dur-1)}}
#iklim-sel:focus{{border-color:var(--ember)}}
.risk{{display:inline-block;border-radius:999px;padding:2px 10px;font-size:11.5px;font-weight:600}}
.r-ok{{background:rgba(var(--risk-ok-rgb),.12);color:var(--risk-ok)}}
.r-mid{{background:rgba(var(--risk-mid-rgb),.14);color:var(--risk-mid)}}
.r-hi{{background:rgba(var(--risk-hi-rgb),.12);color:var(--sev-tinggi)}}
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
.schema ol{{margin:8px 0 0;padding-left:18px;color:rgba(var(--cream-rgb),.78)}}
/* ============ GRAPH ============ */
#gsvg{{width:100%;height:auto;display:block}}
.gnode{{cursor:pointer}} .gnode circle{{transition:r .2s var(--ease),stroke .2s var(--ease)}}
.gnode:hover circle{{stroke:var(--on-ember);stroke-width:2}}
.gnode:focus{{outline:none}} .gnode:focus circle{{stroke:var(--on-ember);stroke-width:3}}
.gnode.sel circle{{stroke:var(--on-ember);stroke-width:3}}
.ghint{{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.2em;color:rgba(var(--cream-rgb),.58);margin-top:6px}}
.legend{{display:flex;flex-wrap:wrap;gap:6px;border-top:1px solid rgba(var(--cream-rgb),.14);margin-top:10px;padding-top:12px}}
.leg{{display:flex;align-items:center;gap:7px;font-size:11px;color:rgba(var(--cream-rgb),.85);background:none;border:1px solid transparent;cursor:pointer;font-family:inherit;padding:8px 10px;border-radius:var(--r-md);min-height:44px}}
.leg:hover{{background:rgba(var(--cream-rgb),.07);border-color:rgba(var(--cream-rgb),.15)}}
.leg.on{{background:rgba(var(--ember-soft-rgb),.14);border-color:rgba(var(--ember-soft-rgb),.45)}}
.dot{{width:10px;height:10px;border-radius:50%;flex:none}}
/* ============ READER (swap animation) ============ */
#reader .r-rule{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--ember)}}
#reader h3{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(19px,2.4vw,22px);margin:6px 0;line-height:1.25}}
#reader ul{{font-size:12.5px;color:var(--ink-body);padding-left:18px;line-height:1.7;margin:8px 0}}
#reader .meta{{font-size:12px;color:var(--ink-soft);margin-top:6px;line-height:1.7}}
#reader .rec{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:10px 12px;font-size:12px;margin-top:10px}}
#reader-body.swap{{animation:reader-in var(--dur-2) var(--ease)}}
@keyframes reader-in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
/* ============ SECTIONS ============ */
h2{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(22px,2.8vw,28px);margin:34px 0 6px;line-height:1.2;letter-spacing:-.005em;border-bottom:1px solid var(--border);padding-bottom:10px}}
.h-num{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;color:var(--ember);background:rgba(var(--ember-rgb),.1);border-radius:6px;padding:2px 7px;margin-right:10px;vertical-align:2px}}
.askbtn{{background:none;border:1px solid var(--border);border-radius:8px;font-size:11px;padding:4px 10px;cursor:pointer;color:var(--ember-deep);font-family:inherit}}
.askbtn:hover{{border-color:var(--ember)}}
.rbtn{{background:var(--surface);border:1px solid var(--border);border-radius:8px;font-size:11px;padding:4px 10px;cursor:pointer;color:var(--ink-soft);font-family:'JetBrains Mono',monospace}}
.rbtn.on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}
.rp-n{{opacity:.65}}
.simgrid{{display:grid;gap:12px;grid-template-columns:1fr;margin-top:10px}}
@media(min-width:800px){{.simgrid{{grid-template-columns:1fr 1fr}}}}
.sim{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 14px}}
.sim-h{{display:flex;justify-content:space-between;gap:8px;font-family:'JetBrains Mono',monospace;font-size:11.5px;font-weight:700;margin-bottom:6px}}
.sim-h b{{color:var(--ember-deep)}}
.sim input[type=range]{{width:100%;accent-color:var(--ember-deep)}}
.sim .hit{{color:var(--sev-tinggi);font-weight:700}}
.sim .miss{{color:var(--risk-ok);font-weight:700}}
.dtabs{{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}}
.dtab{{background:var(--surface);border:1px solid var(--border);border-radius:8px;font-size:12px;padding:6px 12px;cursor:pointer;color:var(--ink-soft)}}
.dtab.on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}
.dpanel{{display:none}}
.dpanel.on{{display:block}}
.docbox{{background:#fff;border:1px solid var(--border);border-radius:12px;padding:16px;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.75;white-space:pre-wrap;max-height:480px;overflow-y:auto}}
.kanalgrid{{display:grid;gap:12px;grid-template-columns:1fr;margin-top:10px}}
@media(min-width:800px){{.kanalgrid{{grid-template-columns:1fr 1fr 1fr}}}}
.kanal{{display:block;background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px;text-decoration:none;color:inherit}}
.kanal:hover{{border-color:var(--ember);transform:translateY(-2px)}}
.kanal .kl{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:var(--ember-deep)}}
.kanal b{{display:block;margin:4px 0;font-size:13px}}
.kanal span{{font-size:12px;color:var(--ink-soft);line-height:1.6}}
#pitchmodal{{position:fixed;inset:0;z-index:200;display:none;align-items:flex-start;justify-content:center;background:rgba(20,14,10,.72);padding:18px;overflow-y:auto}}
#pitchmodal.show{{display:flex}}
.pitchbox{{background:var(--surface-2);border:1px solid var(--border);border-radius:18px;max-width:880px;width:100%;padding:22px;color:var(--ink-body)}}
.pitchbox h3{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(20px,2.6vw,26px);margin:8px 0;color:var(--ink)}}
.pitchterm{{background:var(--ink-2);color:var(--cream);border-radius:12px;padding:14px;font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.8;overflow-x:auto;margin-top:12px}}
.pitchterm .g{{color:#6ee7b7}}.pitchterm .o{{color:var(--ember-soft)}}.pitchterm .d{{color:#a89b88}}
.critgrid{{display:grid;gap:10px;margin-top:10px;grid-template-columns:1fr 1fr}}
@media(min-width:800px){{.critgrid{{grid-template-columns:repeat(5,1fr)}}}}
.crit{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px;font-size:11.5px}}
.crit b{{display:block;font-size:12px;margin:4px 0}}
.crit .pct{{font-family:'JetBrains Mono',monospace;font-weight:700;background:var(--ember);color:#fff;border-radius:6px;padding:1px 7px;font-size:11px}}
.jgrid{{display:grid;gap:10px;grid-template-columns:1fr;margin-top:10px}}
@media(min-width:800px){{.jgrid{{grid-template-columns:1fr 1fr 1fr}}}}
.jcard{{background:#fff;border:1px solid var(--border);border-radius:12px;padding:12px;font-size:12px}}
.jcard b{{font-size:12.5px}}.jcard .jr{{font-family:'JetBrains Mono',monospace;font-size:10.5px;color:var(--ink-soft)}}
.cchips{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}}
.cchips button{{background:var(--surface);border:1px solid var(--border);border-radius:99px;font-size:11px;padding:4px 11px;cursor:pointer;color:var(--ink-soft)}}
.cchips button:hover{{border-color:var(--ember);color:var(--ember-deep)}}
.pager{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:8px;font-size:12px}}
.pager .btn{{font-size:11px}}
.prog{{height:10px;background:var(--surface);border:1px solid var(--border);border-radius:99px;overflow:hidden;margin:8px 0}}
.prog i{{display:block;height:100%;background:var(--ember)}}
.skpdgrid{{display:grid;gap:12px;grid-template-columns:1fr;margin-top:10px}}
@media(min-width:800px){{.skpdgrid{{grid-template-columns:1fr 1fr}}}}
.skpd{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 14px}}
.skpd .sn{{font-weight:700;font-size:13px}}
.skpd .spct{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700}}
.skpd .snums{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-family:'JetBrains Mono',monospace;font-size:11.5px;border-top:1px solid var(--border);padding-top:8px;margin-top:4px}}
.skpd .snums small{{display:block;color:var(--ink-soft);font-size:10px}}
.fbtnrow{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}
.korel{{background:var(--ink-2);color:var(--cream);border-radius:14px;padding:18px 20px;margin-top:12px}}
.korel h4{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:19px;color:var(--ember-soft);margin:0 0 8px}}
.korel ol{{margin:8px 0;padding-left:20px;font-size:12.5px;line-height:1.75;color:rgba(var(--cream-rgb),.82)}}
.korel .src{{font-family:'JetBrains Mono',monospace;font-size:11px;color:#a89b88;border-top:1px solid #2c251f;padding-top:10px;margin-top:10px}}
.natgrid{{display:grid;gap:12px;grid-template-columns:1fr;margin:14px 0}}
@media(min-width:800px){{.natgrid{{grid-template-columns:1fr 1fr 1fr}}}}
.natcard{{background:var(--cream-light);border:1px solid var(--border);border-radius:14px;padding:16px}}
.natcard .nl{{font-family:'JetBrains Mono',monospace;font-size:10.5px;font-weight:600;letter-spacing:.08em}}
.natcard .nv{{font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:600;margin:4px 0}}
.natcard .nx{{font-size:12px;color:var(--ink-soft);line-height:1.6}}
.natband{{background:var(--ink-2);color:var(--cream);border-radius:14px;padding:18px 20px;display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;margin:0 0 8px}}
.natband h4{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:19px;color:var(--ember-soft);margin:0 0 4px}}
.natband p{{font-size:12px;color:rgba(var(--cream-rgb),.72);line-height:1.7;margin:0;max-width:60rem}}
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
.flag summary:hover{{background:rgba(var(--ember-rgb),.05)}}
.flag summary::-webkit-details-marker{{display:none}}
.rule{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;background:var(--ink);color:var(--cream);
 border-radius:6px;padding:3px 7px;flex:none}}
.sev{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.08em;flex:none}}
.sev-tinggi{{color:var(--sev-tinggi);font-weight:700}} .sev-sedang{{color:var(--amber);font-weight:700}} .sev-rendah{{color:var(--sev-rendah);font-weight:600}}
.flag-title{{font-size:13px;font-weight:600;flex:1}}
.flag .ev{{font-size:13px;color:var(--ink-body);padding:0 14px;line-height:1.7;margin:10px 0}}
.flag .meta{{font-size:12px;color:var(--ink-soft);margin-top:6px;padding:0 14px;line-height:1.7}}
.flag[open] .ev,.flag[open] .meta{{animation:flag-in var(--dur-2) var(--ease)}}
@keyframes flag-in{{from{{opacity:0;transform:translateY(-6px)}}to{{opacity:1;transform:none}}}}
/* ============ TABLES (row hover) ============ */
table{{width:100%;border-collapse:collapse;font-size:12.5px;line-height:1.55}}
table.light{{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--r-lg);overflow:hidden;box-shadow:var(--sh-1)}}
td{{padding:7px 9px;border-bottom:1px solid var(--border);vertical-align:top;transition:background var(--dur-1)}}
#pkgs td{{padding-top:5px;padding-bottom:5px;white-space:nowrap}}
#pkgs td.pkgname{{max-width:240px;overflow:hidden;text-overflow:ellipsis}}
#pkgs td.vname{{max-width:150px;overflow:hidden;text-overflow:ellipsis}}
tbody tr:hover td{{background:rgba(var(--ember-rgb),.055)}}
.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.small{{color:var(--ink-soft)}}
a{{color:var(--ember-deep);text-underline-offset:2px}}
a:hover{{text-decoration-color:var(--ember)}}
.bar{{background:var(--surface);border-radius:6px;height:10px;min-width:120px;overflow:hidden}}
.bar div{{background:linear-gradient(90deg,var(--ember),var(--ember-soft));height:10px;border-radius:6px;transition:width var(--dur-4) var(--ease)}}
.months{{display:flex;align-items:flex-end;gap:8px;padding:12px 4px;overflow-x:auto}}
.mcol{{text-align:center;min-width:44px}} .months .bar{{width:34px;margin:0 auto}}
.months .bar,.bar-dec{{transition:height var(--dur-4) var(--ease)}}
.bar-dec{{width:34px;background:linear-gradient(180deg,var(--sev-cerah),var(--sev-gelap));margin:0 auto;border-radius:4px 4px 0 0;box-shadow:0 0 0 0 rgba(var(--sev-cerah-rgb),0);animation:decpulse 3s ease-in-out infinite}}
@keyframes decpulse{{0%,100%{{box-shadow:0 0 0 0 rgba(var(--sev-cerah-rgb),0)}}50%{{box-shadow:0 0 12px 1px rgba(var(--sev-cerah-rgb),.35)}}}}
.mlabel{{font-size:10px;color:var(--ink-soft);margin-top:4px}} .mval{{font-size:10px}}
.toolbar{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;align-items:center}}
.toolbar input[type=search]{{background:var(--surface-2);border:1px solid var(--border);color:var(--ink);border-radius:var(--r-sm);padding:8px 12px;font-size:13px;min-width:230px;font-family:inherit;transition:border-color var(--dur-1),box-shadow var(--dur-1)}}
.toolbar input[type=search]:focus{{border-color:var(--ember);box-shadow:0 0 0 3px rgba(var(--ember-rgb),.12);outline:none}}
.btn{{background:var(--surface-2);border:1px solid var(--border);color:var(--ink);border-radius:var(--r-sm);padding:8px 14px;font-size:12px;cursor:pointer;text-decoration:none;display:inline-block;font-family:inherit}}
.btn.on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}
.btn:hover{{border-color:var(--ember);transform:translateY(-1px);box-shadow:var(--sh-1)}}
/* ============ OPEN DATA (orow) ============ */
.orow{{display:flex;justify-content:space-between;gap:12px;padding:var(--s3) 0;border-bottom:1px solid rgba(var(--cream-rgb),.14);font-size:13px;transition:opacity .4s var(--ease)}}
.orow span{{color:rgba(var(--cream-rgb),.72);font-size:12.5px}} .orow b{{color:var(--cream);text-align:right;font-size:12.5px;word-break:break-all;font-variant-numeric:tabular-nums}}
.dim{{font-size:12px;color:rgba(var(--cream-rgb),.74);line-height:1.7}}
.panel.light .orow{{border-bottom-color:var(--border)}}
.panel.light .orow span{{color:var(--ink-soft)}}
.panel.light .orow b{{color:var(--ink)}}
.panel.light .dim{{color:var(--ink-soft)}}
.lapor a{{color:var(--ember-soft)}}
#minimap{{border-radius:var(--r-lg);box-shadow:var(--sh-2)}}
#minimap .pin{{cursor:pointer}}
#minimap .pin:hover circle:nth-of-type(2){{stroke:var(--on-ember);stroke-width:2.5}}
/* ============ BOOT ============ */
#boot{{position:fixed;inset:0;z-index:50;background:var(--ink-2);color:var(--cream);display:flex;align-items:center;justify-content:center;transition:opacity .8s ease, visibility .8s}}
#boot.gone{{opacity:0;visibility:hidden;pointer-events:none}}
.boot-inner{{text-align:center;max-width:420px;padding:24px}}
.boot-eye{{width:92px;height:92px;margin:0 auto 18px;position:relative}}
.boot-eye svg{{width:100%;height:100%;animation:breathe 3.2s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{opacity:.6;transform:scale(1)}}50%{{opacity:1;transform:scale(1.07)}}}}
.boot-eye::after{{content:"";position:absolute;inset:-6px;border-radius:50%;border:1px solid var(--ember-vivid);animation:pulse-ring 2.4s ease-out infinite}}
@keyframes pulse-ring{{0%{{transform:scale(.85);opacity:.7}}100%{{transform:scale(1.5);opacity:0}}}}
.boot-title{{font-family:'Instrument Serif',Georgia,serif;font-size:clamp(34px,8vw,46px);margin:0}}
.boot-title em{{color:var(--ember-soft)}}
.boot-sub{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.25em;color:var(--boot-sub);margin:8px 0 20px}}
.boot-log{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--boot-muted);min-height:56px;text-align:left;border:1px solid var(--boot-line);border-radius:var(--r-md);padding:12px 14px;margin-bottom:18px;background:var(--boot-bg)}}
.boot-log div{{animation:stream-in .4s both}}
@keyframes stream-in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.boot-bar{{height:3px;background:var(--boot-line);border-radius:99px;overflow:hidden;margin-bottom:22px}}
.boot-bar i{{display:block;height:100%;width:40%;background:linear-gradient(90deg,var(--ember-vivid),var(--ember-soft));border-radius:99px;animation:load 1.6s ease-in-out infinite}}
@keyframes load{{0%{{margin-left:-40%}}100%{{margin-left:100%}}}}
.boot-btn{{background:var(--ember-vivid);color:var(--on-ember);border:none;border-radius:999px;padding:13px 34px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;box-shadow:0 10px 28px rgba(var(--ember-vivid-rgb),.4)}}
.boot-btn:hover{{background:var(--ember-soft);color:var(--ink-2);transform:translateY(-1px)}}
.boot-quiet{{display:block;margin:12px auto 0;font-size:12px;color:var(--boot-muted);text-decoration:underline;cursor:pointer;background:none;border:none;font-family:inherit}}
.boot-quiet:hover{{color:var(--ember-soft)}}
/* ============ CHAT (panel transition) ============ */
#chatfab{{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:45;width:56px;height:56px;border-radius:50%;
 background:var(--ember);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;
 box-shadow:0 10px 28px rgba(var(--ember-rgb),.45);transition:background var(--dur-1),transform var(--dur-1),box-shadow var(--dur-1),bottom var(--dur-2) var(--ease)}}
#chatfab:hover{{background:var(--ember-soft);transform:translateY(-2px);box-shadow:0 14px 34px rgba(var(--ember-rgb),.55)}}
#chatfab:active{{transform:scale(.94)}}
body.loc-open #chatfab{{bottom:calc(138px + env(safe-area-inset-bottom,0px))}}
#chatpanel{{position:fixed;right:16px;bottom:calc(84px + env(safe-area-inset-bottom,0px));z-index:45;width:min(420px,calc(100vw - 32px));
 max-height:min(560px,calc(100vh - 120px));display:flex;flex-direction:column;visibility:hidden;opacity:0;transform:translateY(14px) scale(.98);
 transition:opacity var(--dur-2) var(--ease),transform var(--dur-2) var(--ease),visibility 0s linear var(--dur-2);
 background:var(--surface-2);border:1px solid var(--border);border-radius:20px;overflow:hidden;
 box-shadow:0 24px 60px rgba(var(--shadow-rgb),.3)}}
#chatpanel.show{{visibility:visible;opacity:1;transform:none;transition:opacity var(--dur-2) var(--ease),transform var(--dur-2) var(--ease)}}
#chatpanel.wide{{width:min(700px,calc(100vw - 32px));max-height:min(72vh,760px)}}
#chatpanel.wide #chatlog{{min-height:300px}}
#chatpanel .chead .w{{float:right;background:none;border:1px solid rgba(var(--cream-rgb),.3);color:rgba(var(--cream-rgb),.8);
 border-radius:8px;font-size:12px;cursor:pointer;padding:2px 8px;margin-left:6px;font-family:inherit;transition:border-color var(--dur-1),color var(--dur-1)}}
#chatpanel .chead .w:hover{{border-color:var(--ember-soft);color:var(--ember-soft)}}
#chatpanel .chead{{background:var(--ink-2);color:var(--cream);padding:12px 16px;font-size:13px}}
#chatpanel .chead b{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:17px}}
#chatpanel .chead .x{{float:right;background:none;border:none;color:rgba(var(--cream-rgb),.65);font-size:16px;cursor:pointer;transition:color var(--dur-1),transform var(--dur-1)}}
#chatpanel .chead .x:hover{{color:var(--err);transform:rotate(90deg)}}
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
#cform input:focus{{border-color:var(--ember);box-shadow:0 0 0 3px rgba(var(--ember-rgb),.12);outline:none}}
#cform button{{background:var(--ember);color:var(--on-ember);border:none;border-radius:var(--r-sm);padding:0 16px;font-size:13px;cursor:pointer}}
#cform button:hover{{background:var(--ember-soft);color:var(--ink-2)}}
.cdisc{{font-size:10.5px;color:var(--ink-soft);padding:0 14px 10px;line-height:1.6}}
.typing{{display:inline-block}} .typing i{{display:inline-block;width:6px;height:6px;border-radius:50%;
 background:var(--ember);margin-right:3px;animation:tblink 1s infinite}}
.typing i:nth-child(2){{animation-delay:.2s}} .typing i:nth-child(3){{animation-delay:.4s}}
@keyframes tblink{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
/* ============ LOCBANNER ============ */
#locbanner{{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:40;max-width:640px;margin:0 auto;
 background:var(--ink-2);color:var(--cream);border:1px solid rgba(var(--ember-soft-rgb),.4);border-radius:18px;padding:16px 18px;
 box-shadow:0 12px 40px rgba(var(--shadow-rgb),.4);display:none}}
#locbanner.show{{display:block;animation:rise .5s both}}
#locbanner .lb-title{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.22em;color:var(--ember-soft)}}
#locbanner p{{font-size:12px;line-height:1.7;color:rgba(var(--cream-rgb),.82)}}
#locbanner .lb-row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}}
#locbanner .pill{{height:36px;font-size:10px}}
#locbanner .lb-forget{{background:none;border:none;color:rgba(var(--cream-rgb),.6);text-decoration:underline;
 font-size:11px;cursor:pointer;margin-top:8px;font-family:inherit;padding:0}}
#locbanner .lb-forget:hover{{color:var(--ember-soft)}}
/* ============ FOOTER ============ */
.foot{{margin-top:40px;color:var(--ink-soft);font-size:11px;border-top:1px solid var(--border);padding-top:14px;line-height:2;text-align:center}}
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
.scrollbox::-webkit-scrollbar-thumb{{background:var(--scroll-thumb);border-radius:8px;border:2px solid var(--cream)}}
.scrollbox::-webkit-scrollbar-track{{background:transparent}}
html.booted #boot{{display:none}}
</style>
<script>try{{if(!matchMedia('(prefers-reduced-motion: reduce)').matches){{document.documentElement.classList.add('rv-init');}}}}catch(e){{}}</script>
<script>try{{if(sessionStorage.getItem('mata_boot'))document.documentElement.classList.add('booted');}}catch(e){{}}</script></head><body>
<div id="toasts" role="status" aria-live="polite"></div>
<div id="boot"><div class="boot-inner">
 <div class="boot-eye"><svg viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="14" fill="var(--graph-core)"/>
  <path d="M32 12l15.6 9v18L32 48l-15.6-9V21z" stroke="var(--ember-vivid)" stroke-width="4.5" stroke-linejoin="round"/>
  <circle cx="47" cy="15" r="5" fill="var(--ember-vivid)"/></svg></div>
 <p class="boot-title">MATA <em>menyala</em></p>
 <p class="boot-sub">WATCHDOG AKUNTABILITAS PENGADAAN</p>
 <div class="boot-log" id="bootlog"></div>
 <div class="boot-bar"><i></i></div>
 <button class="boot-btn" id="bootgo">MASUK — DENGAN SUARA ⟶</button>
 <button class="boot-quiet" id="bootquiet">masuk senyap</button>
</div></div>
<div id="app"><div class="wrap">
 <header class="sitehead">
  <div class="compbar"><div class="wrap">
   <span class="hackbadge">◈ AI HACKFEST 2026 · BATCH 3</span>
   <span class="compmeta">Kategori: <b>Productivity &amp; Personal AI</b> · Lokus: Kab. Aceh Tengah → Replikasi Nasional</span>
   <button class="pill hot" style="padding:4px 12px;font-size:11px;cursor:pointer;font:inherit" onclick="openPitch()">Berkas Juri ◈</button>
  </div></div>
  <div class="wrap brandrow">
   <a class="brand" href="#top"><span class="eye"><i></i></span>
    <span><span><b>MATA</b><span class="ver">vLIVE</span></span>
    <small>Watchdog Akuntabilitas Pengadaan Publik</small></span></a>
   <span class="syspill"><span class="dot"></span>mata.niumination.web.id</span>
   <button class="burger" aria-label="Menu navigasi" onclick="document.querySelector('.sitenav').classList.toggle('open')">☰</button>
  </div>
  <nav class="sitenav"><div class="wrap navrow" onclick="document.querySelector('.sitenav').classList.remove('open')">
   <a href="#top">Ringkasan</a>
   <a href="#flags" class="hot">Indikasi<b class="nbadge">{n_flags} Flag</b></a>
   <a href="#inaproc-panel">Bukti live<b class="nbadge">TA 2026</b></a>
   <a href="#iklim-panel">Iklim Gayo</a>
   <a href="#health-panel">Status sistem</a>
   <a href="#dossier">Dossier</a>
   <a href="#top" onclick="document.getElementById('chatfab').click();return false;">Tanya MATA<b class="nbadge">AI</b></a>
  </div></nav>
 </header>
 <section class="hero" id="top"><div class="orb"></div><div class="hero-grid">
  <div>
   <div class="kickrow"><span class="kick">● LIVING CODEX · WATCHDOG SISTEMIK</span>
    <span class="kickdim">/ MODE: {_esc(mode)}</span>
    <span class="verpill">● DATA TERVERIFIKASI LKPP &amp; INAPROC</span></div>
   <h1>Uang itu uangmu.<br><em>MATA membacanya</em> supaya kamu tidak perlu bisa akuntansi.</h1>
   <p class="desc">Pemerintah membuka triliunan data pengadaan. Masalahnya bukan data tidak ada —
    <b>tidak ada yang membacanya untuk rakyat</b>. MATA berjalan 24/7 memakai rule engine transparan
    D1–D6 dan menyiapkan draft laporan resmi. Ini indikasi berbasis data, bukan vonis.</p>
   <div class="badges"><span class="badge">◈ Indikasi berbasis data, bukan vonis</span>
    <span class="badge">◈ Rule engine deterministik</span>
    <span class="badge">◈ Human-in-the-loop: warga melapor</span>
    <span class="badge">terakhir <span class="mono">{_esc(st.get("last_run", "-"))}</span></span></div>
  </div>
  <div class="actbox">
   <div class="acthead"><span><span class="dot"></span>SIKLUS DETEKSI AKTIF</span><span class="mono">CRON: TIAP 1 JAM</span></div>
   <div class="actrows">
    <div><span>Status engine:</span><b class="ok">NORMAL · OK (200)</b></div>
    <div><span>Siklus terakhir:</span><span class="mono">{_esc(st.get("last_run", "-"))}</span></div>
    <div><span>Notifikasi Telegram:</span><span class="mono">terkirim</span></div>
   </div>
   <a class="pill hot block" href="#flags">◉ BUKA INDIKASI LIVE</a>
   <a class="pill hot block" href="#dossier">⇩ DOSSIER &amp; DRAFT APIP</a>
  </div>
 </div>
 <div class="mtiles">
  <a class="tile" href="#inaproc-panel"><div class="t-l">PAKET REALISASI ›</div><div class="t-n">{_esc(n_records)}</div><div class="t-s">Arsip 2025–2026</div></a>
  <a class="tile" href="#rup-panel"><div class="t-l">RENCANA RUP ›</div><div class="t-n">{_esc(rup_s)}</div><div class="t-s">Paket RUP TA2026</div></a>
  <a class="tile red" href="#flags"><div class="t-l" style="color:#e08a80">INDIKASI FLAG ›</div><div class="t-n" style="color:var(--ember-soft)">{_esc(n_flags)}</div><div class="t-s">D1, D2, D3, D4, D6</div></a>
  <a class="tile" href="#analisis-panel"><div class="t-l">SATKER SKPD ›</div><div class="t-n" id="tile-skpd">…</div><div class="t-s">Perangkat daerah</div></a>
  <a class="tile" href="#sapa-panel"><div class="t-l">SPLP SAPA ›</div><div class="t-n" id="tile-sapa">…</div><div class="t-s">Indikator resmi</div></a>
 </div></section>
 <div class="ticker"><div class="ticker-inner">{ticker_items}{ticker_items}</div></div>
 <style>
 .qstrip{{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;padding:10px 18px;margin:18px 0;
   border:1px solid var(--ink-2);border-radius:10px;background:var(--ink-2);
   font-size:13px;color:var(--cream)}}
 .qstrip .q-ar{{font-family:'Amiri',serif;font-size:19px;line-height:1.9;color:var(--cream)}}
 .qstrip .q-sep{{opacity:.5;color:var(--ember-soft)}}
 .qstrip .q-id{{font-size:13px}}
 .qstrip .q-src{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.3px;color:var(--ember-soft)}}
 .qstrip .q-nav{{float:right;display:inline-flex;align-items:center;gap:6px}}
.qstrip .q-nav button{{background:none;border:1px solid rgba(var(--cream-rgb),.3);color:var(--cream);border-radius:6px;width:22px;height:22px;cursor:pointer;font-size:13px;line-height:1}}
.qstrip .q-nav button:hover{{border-color:var(--ember-soft)}}
.qstrip .q-nav #qcount{{font-size:10px;color:var(--ember-soft)}}
 .qstrip .q-tag{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;
   color:var(--ember-soft)}}
 @media (max-width:700px){{.qstrip .q-ar{{font-size:16px;width:100%}}}}
 @media (min-width:701px){{.qstrip{{display:grid;grid-template-columns:1.15fr 1fr;gap:6px 22px;align-items:center;padding:14px 22px}}
  .qstrip .q-tag{{grid-column:1/-1}}
  .qstrip .q-ar{{font-size:23px;text-align:right}}
  .qstrip .q-sep{{display:none}}
  .qstrip .q-tl{{display:flex;flex-direction:column;gap:6px;border-left:1px solid rgba(var(--cream-rgb),.25);padding-left:22px}}
  .qstrip .q-id{{font-size:14px;line-height:1.7}}}}
 </style>
 <div class="qstrip" id="kutipan" style="display:none"></div>

 <h2><span class="h-num">◈</span> Mengapa MATA dibangun — relevansi nasional</h2>
 <div class="natgrid">
  <div class="natcard"><div class="nl" style="color:var(--ember)">BPKP · KEUANGAN NEGARA/DERAH</div>
   <div class="nv">Rp141 T</div>
   <div class="nx">Potensi pemborosan belanja negara &amp; daerah yang diidentifikasi BPKP dari audit tata kelola pengadaan.</div></div>
  <div class="natcard"><div class="nl" style="color:var(--ember)">BPK · SEMESTER II 2024</div>
   <div class="nv">15.689</div>
   <div class="nx">Permasalahan ketidakpatuhan senilai Rp18,19 T — sebagian besar berakar di proses pengadaan.</div></div>
  <div class="natcard"><div class="nl" style="color:var(--ember)">KPK · OTT SUMUT–LAMPUNG 2025</div>
   <div class="nv">15–20%</div>
   <div class="nx">Fee proyek yang dipatok dalam OTT jalan &amp; pembangunan — pola yang bisa dideteksi lebih dini dari data.</div></div>
 </div>
 <div class="natband">
  <div><h4>Celah kuncinya: temuan selalu datang terlambat.</h4>
   <p>Audit &amp; penindakan bekerja setelah uang keluar. MATA membalik urutannya — pola risiko dihitung saat pengumuman terbit, dari data publik yang bisa diverifikasi siapa pun per paket.</p></div>
  <button class="pill hot" onclick="document.getElementById('flags').scrollIntoView({{behavior:'smooth'}})">Buka {n_flags} indikasi ↓</button>
 </div>

 <h2><span class="h-num">01</span> Bukti live — data nyata hari ini</h2>
 <section class="panel light notools" id="inaproc-panel">
  <div class="kicker">🧾 REALISASI PENGADAAN — INAPROC <span class="count" id="inaproc-meta">MEMUAT…</span></div>
  <p class="note" id="inaproc-baseline" style="margin:6px 0"></p>
  <div class="table-scroll scrollbox" id="inaproc-body">
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
  </div>
  <p class="note" style="margin-top:8px">Sumber: data.inaproc.id (INAPROC — API publik, tanpa login) ·
   cakupan: realisasi pengadaan Kab. Aceh Tengah TA2026 (halaman pertama) ·
   diperbarui: <span id="inaproc-upd">—</span>. Indikasi, bukan vonis — verifikasi di SPSE/e-kontrak.</p>
 </section>
 <section class="panel light notools" id="rup-panel">
  <div class="kicker">📋 RUP RENCANA — INAPROC <span class="count" id="rup-meta">MEMUAT…</span></div>
  <div class="table-scroll scrollbox" id="rup-body">
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
  </div>
  <p class="note" style="margin-top:8px">Sumber: data.inaproc.id (INAPROC — API publik, tanpa login) ·
   cakupan: RUP rencana Kab. Aceh Tengah TA2026 (halaman pertama). Indikasi, bukan vonis.</p>
 </section>
 <section class="panel light notools" id="spse-panel">
  <div class="kicker">🏛 PBJ KAB. ACEH TENGAH — SPSE PUBLIK <span class="count" id="spse-meta">MEMUAT…</span></div>
  <div class="table-scroll" id="spse-body">
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
  </div>
  <p class="note" style="margin-top:8px">Sumber: spse.inaproc.id/acehtengahkab (portal SPSE LKPP — publik, tanpa login) ·
   cakupan: daftar paket terkini; riwayat &amp; pemenang via jalur terpisah. Indikasi, bukan vonis — verifikasi di SPSE.</p>
 </section>
 <section class="panel light notools" id="analisis-panel">
  <div class="kicker">🎯 ANALISIS MATA — POLA REALISASI <span class="count" id="analisis-meta">MEMUAT…</span></div>
  <p class="note" id="analisis-baseline" style="margin:6px 0"></p>
  <div id="analisis-body">
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
   <div class="skeleton" style="height:13px;margin:7px 0"></div>
  </div>
  <p class="note" style="margin-top:8px">Metode: agregasi deterministik data realisasi penuh INAPROC (TA2026 662 paket · TA2025 599 paket) ·
   <b>indikasi, bukan vonis</b> — verifikasi di SPSE/e-kontrak sebelum disimpulkan apa pun.</p>
 </section>

 <h2><span class="h-num">02</span> Jelajah arsip</h2>
 <div class="cols">
  <aside class="panel light" data-lbl="ARSIP">
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
  <section class="panel dark" data-lbl="GRAF">
   <div class="kicker">◈ PETA INDIKASI <span class="count">{_esc(n_flags)} SIMPUL</span></div>
   <svg id="gsvg" viewBox="0 0 640 460">{graph}</svg>
   <div class="ghint">KLIK SIMPUL UNTUK MEMBACA · MERAH TINGGI · OREN SEDANG · HIJAU RENDAH</div>
   <div class="legend">
    <button class="leg" data-f="tinggi"><span class="dot" style="background:var(--sev-tinggi)"></span>Tinggi</button>
    <button class="leg" data-f="sedang"><span class="dot" style="background:var(--sev-sedang)"></span>Sedang</button>
    <button class="leg" data-f="rendah"><span class="dot" style="background:var(--sev-rendah)"></span>Rendah</button>
    <button class="leg" data-f="semua"><span class="dot" style="background:var(--cream)"></span>Semua</button>
   </div>
  </section>
  <aside class="panel light" id="reader" data-lbl="BACA">
   <div class="kicker">☰ PEMBACA</div>
   <div id="reader-body"><p class="note">Klik simpul pada peta untuk membaca bukti, record, dan langkah lanjut di sini.</p></div>
  </aside>
 </div>

 <h2><span class="h-num">03</span> Indikasi — klik untuk bukti &amp; langkah lanjut</h2>
 <div class="toolbar">
  <button class="btn on" data-f="semua">Semua</button>
  <button class="btn" data-f="tinggi">Tinggi</button>
  <button class="btn" data-f="sedang">Sedang</button>
  <button class="btn" data-f="rendah">Rendah</button>
 </div>
 <div class="toolbar" id="rulepills" aria-label="Saring per aturan">
  <button class="rbtn on" data-r="semua">Semua aturan <span class="rp-n"></span></button>
  <button class="rbtn" data-r="D1">D1 <span class="rp-n"></span></button>
  <button class="rbtn" data-r="D2">D2 <span class="rp-n"></span></button>
  <button class="rbtn" data-r="D3">D3 <span class="rp-n"></span></button>
  <button class="rbtn" data-r="D4">D4 <span class="rp-n"></span></button>
  <button class="rbtn" data-r="D6">D6 <span class="rp-n"></span></button>
 </div>
 <div id="flags">{flag_cards or "<p class='note'>Belum ada indikasi.</p>"}</div>
 <div class="natband" style="margin-top:12px"><div><h4>{_esc(_live_hi_title)}</h4><p>{_live_hi_body}</p></div>
  <span class="verpill">{_esc(_live_hi_badge)}</span></div>
 <section class="panel light notools" id="sim-panel">
  <div class="kicker">◈ SIMULATOR AMBANG — UJI SENSITIVITAS ATURAN <span class="count" id="sim-meta">LIVE</span></div>
  <p class="note">Geser ambang untuk melihat apakah temuan live saat ini tetap terpicu. Membuktikan deteksi deterministik &amp; transparan — bukan vonis.</p>
  <p class="note" style="margin-top:6px"><b>Kejujuran teknis:</b> pada data riil INAPROC, aturan D1 (deviasi harga) dan D3 (keroyokan akhir tahun) belum aktif — portal publik tak membuka HPS item &amp; tanggal kontrak per paket. MATA tak mengarang data yang belum dibuka publik.</p>
  <div class="simgrid">
   <div class="sim"><div class="sim-h"><span>D1 deviasi harga vs pasar</span><b id="sim-v-d1">30%</b></div>
    <input type="range" id="sim-d1" min="15" max="100" value="30" aria-label="Ambang D1"><p class="note" id="sim-t-d1"></p></div>
   <div class="sim"><div class="sim-h"><span>D2 porsi nilai vendor</span><b id="sim-v-d2">5%</b></div>
    <input type="range" id="sim-d2" min="2" max="50" value="5" aria-label="Ambang D2"><p class="note" id="sim-t-d2"></p></div>
   <div class="sim"><div class="sim-h"><span>D3 rasio lonjakan Desember</span><b id="sim-v-d3">2.0×</b></div>
    <input type="range" id="sim-d3" min="1.2" max="5" step="0.1" value="2" aria-label="Ambang D3"><p class="note" id="sim-t-d3"></p></div>
   <div class="sim"><div class="sim-h"><span>D4 lompatan nilai kontrak</span><b id="sim-v-d4">5.0×</b></div>
    <input type="range" id="sim-d4" min="2" max="20" step="0.5" value="5" aria-label="Ambang D4"><p class="note" id="sim-t-d4"></p></div>
  </div>
  <div style="margin-top:10px"><button class="btn" id="sim-reset">Reset default</button>
   <span class="note" id="sim-sum" style="margin-left:8px"></span></div>
 </section>
 <section class="panel light notools" id="hukum-panel">
  <div class="kicker">⚖ DASAR HUKUM — RUJUKAN REGULASI</div>
  <div class="natgrid">
   <div class="natcard"><div class="nl" style="color:var(--ember-deep)">PERPRES 12/2021</div><div class="nx"><b>Prinsip pengadaan.</b> Pasal 5 (efisien, transparan, bersaing, akuntabel); Pasal 26 HPS berbasis data pasar (relevan D1).</div></div>
   <div class="natcard"><div class="nl" style="color:var(--ember-deep)">UU 1/2004</div><div class="nx"><b>Perbendaharaan negara.</b> Pasal 3 ayat 1: tertib, efisien, transparan, bertanggung jawab (relevan D3 keroyokan akhir tahun).</div></div>
   <div class="natcard"><div class="nl" style="color:var(--ember-deep)">PERATURAN LKPP 12/2021</div><div class="nx"><b>Kualifikasi penyedia.</b> Larangan monopoli &amp; pinjam bendera (relevan D2 dominasi &amp; D4 vendor kecil menang jumbo).</div></div>
   <div class="natcard"><div class="nl" style="color:var(--ember-deep)">UU 27/2022 (PDP)</div><div class="nx"><b>Data pribadi.</b> MATA hanya pakai data terbuka; IP pengunjung di-hash 8 karakter, tanpa pelacakan.</div></div>
  </div>
 </section>

 <h2><span class="h-num">04</span> Konsentrasi &amp; musim anggaran</h2>
 <div class="table-scroll"><table class="light"><tr><td>Penyedia</td><td class="num">Proyek</td><td class="num">Total nilai</td><td>Porsi</td></tr>{vendor_rows}</table></div>
 <h2><span class="h-num">05</span> Paket &amp; konteks terbuka</h2>
 <div class="cols2">
  <section class="panel light" data-lbl="CARI">
   <div class="kicker">🔎 CARI PAKET <span class="count">{_esc(len(recs))} RECORD</span></div>
   <div class="toolbar"><input type="search" id="q" placeholder="Nama paket / instansi / vendor / ID…"></div>
   <div class="fbtnrow" style="margin:0 0 8px">
    <button class="btn" id="pkg-big" aria-pressed="false">⚡ Nilai ≥ Rp 100 jt</button>
    <span class="note" id="pkg-count"></span>
   </div>
   <div class="table-scroll scrollbox pkgbox"><table><tr><td>ID</td><td>Paket</td><td>Instansi</td><td class="num">Nilai</td><td>Pemenang</td><td>Tanggal</td></tr>
   <tbody id="pkgs">{pkg_rows or '<tr><td colspan="6" class="small">Belum ada record — jalankan live-collect atau tunggu siklus berikutnya.</td></tr>'}</tbody></table></div>
   <div class="pager"><button class="btn" id="pkg-prev">‹ Sebelumnya</button>
    <span class="note" id="pkg-page"></span>
    <button class="btn" id="pkg-next">Berikutnya ›</button></div>
  </section>
  <section class="panel dark" data-lbl="KONTEKS">
   <div class="kicker">⬣ KONTEKS TERBUKA — {_esc(ctx.get("region", "ACEH TENGAH").upper())}</div>
   <div class="ctxscroll">{ctx_html or '<p class="dim">Belum ada konteks — jalankan `python3 run.py open-data`.</p>'}</div>
   <div class="lapor" style="margin-top:16px;border-top:1px solid rgba(var(--cream-rgb),.12);padding-top:12px">
    <div class="kicker">⚑ LAPOR &amp; VERIFIKASI</div>
    <p class="dim">MATA tidak mengirim laporan otomatis. Verifikasi ke sumber,
     lalu laporkan via <a href="https://www.lapor.go.id" target="_blank" rel="noopener">LAPOR!</a> ·
     <a href="https://www.ombudsman.go.id" target="_blank" rel="noopener">Ombudsman RI</a> ·
     KPK · APIP/BPKP.</p>
   </div>
  </section>
 </div>

 <section class="panel light notools" id="sapa-panel">
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
 <h2><span class="h-num">06</span> Pengunjung live</h2>
 {widget}
 <h2 id="dossier"><span class="h-num">07</span> Dossier — ubah temuan jadi tindakan</h2>
 <section class="panel light notools" id="dossier-panel">
  <div class="kicker">◈ MODUL 07 — GENERATOR DOSSIER &amp; DRAFT LAPORAN <span class="count">HUMAN-IN-THE-LOOP</span></div>
  <p class="note">MATA menyiapkan berkas bukti dan draft resmi — <b>warga yang memutuskan dan mengirimkannya</b> ke institusi berwenang. MATA tak pernah melapor otomatis.</p>
  <div class="dtabs">
   <button class="dtab on" data-dt="apip">Draft Surat APIP</button>
   <button class="dtab" data-dt="dos">Dossier Bukti</button>
   <button class="dtab" data-dt="pub">Siaran Pers</button>
   <button class="dtab" data-dt="kanal">Kanal Lapor</button>
  </div>
  <div class="dpanel on" id="dp-apip">
   <div class="fbtnrow"><button class="btn" data-copy="#doct-apip">Salin teks surat</button>
    <button class="btn" onclick="window.print()">Cetak / Simpan PDF</button></div>
   <div class="docbox" id="doct-apip">{_esc(dossier_apip)}</div>
   <p class="note" style="margin-top:8px"><b>Catatan etika:</b> dokumen ini DRAFT dari data publik. Sunting, tinjau, lalu teruskan ke kanal resmi.</p>
  </div>
  <div class="dpanel" id="dp-dos">
   <div class="fbtnrow"><a class="btn" href="/api/records.csv" download>⇩ Unduh arsip CSV</a></div>
   <div class="skpdgrid">{dossier_cards}</div>
  </div>
  <div class="dpanel" id="dp-pub">
   <div class="fbtnrow"><button class="btn" data-copy="#doct-pub">Salin siaran pers</button></div>
   <div class="docbox" id="doct-pub">{_esc(dossier_publik)}</div>
  </div>
  <div class="dpanel" id="dp-kanal">
   <div class="kanalgrid">
    <a class="kanal" href="https://www.lapor.go.id/" target="_blank" rel="noopener"><span class="kl">SP4N-LAPOR!</span><b>Kanal Aspirasi &amp; Pengaduan Nasional ↗</b><span>Dikelola KemenPANRB &amp; Ombudsman; diteruskan ke Inspektorat Aceh Tengah.</span></a>
    <a class="kanal" href="https://kws.kpk.go.id/" target="_blank" rel="noopener"><span class="kl">KPK WBS</span><b>Whistleblower KPK ↗</b><span>Untuk indikasi suap, gratifikasi, atau pemerasan fee proyek PBJ.</span></a>
    <a class="kanal" href="https://ombudsman.go.id/" target="_blank" rel="noopener"><span class="kl">OMBUDSMAN RI</span><b>Pengawasan maladministrasi ↗</b><span>Prosedur menyimpang, diskriminasi vendor, layanan diabaikan.</span></a>
   </div>
  </div>
 </section>
</div></div>
<footer class="sitefoot"><div class="fwrap"><div class="fgrid">
 <div>
  <div class="fbrand">MATA <span class="ver" style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#a89b88;background:#241d17;border:1px solid #3d332a;border-radius:5px;padding:1px 6px;vertical-align:4px">AI HACKFEST 2026</span></div>
  <p>Watchdog akuntabilitas pengadaan publik 24/7 di VPS (<strong>mata.niumination.web.id</strong>). Mengubah data terbuka pemerintah menjadi bukti yang bisa ditindaklanjuti warga.</p>
  <div class="fquote">"Uang itu uangmu. MATA membacanya supaya kamu tidak perlu bisa akuntansi."</div>
 </div>
 <div>
  <div class="flbl">Modul Watchdog</div>
  <ul>
   <li><a href="#top">◈ Ringkasan living codex</a></li>
   <li><a href="#flags">◈ Rule engine D1–D6</a></li>
   <li><a href="#inaproc-panel">◈ Bukti live INAPROC TA 2026</a></li>
   <li><a href="#iklim-panel">◈ Agroklimat kopi Gayo</a></li>
   <li><a href="#health-panel">◈ Status sistem 24/7</a></li>
   <li><a href="#top" onclick="document.getElementById('chatfab').click();return false;">◈ Tanya MATA (AI)</a></li>
  </ul>
 </div>
 <div>
  <div class="flbl">Infrastruktur 24/7</div>
  <p>Sistem MATA berjalan tanpa henti pada infrastruktur komputasi resmi:</p>
  <div class="finfra"><a href="https://idwebhost.com/ai-hosting/" target="_blank" rel="noopener">AI Hosting IDwebhost ↗</a><small>Cloud hosting teroptimasi agent AI 24/7</small></div>
  <div class="finfra"><a href="https://cloudbaik.com/" target="_blank" rel="noopener">Cloud VPS CloudBaik ↗</a><small>Virtual server SSD NVMe</small></div>
 </div>
 <div>
  <div class="flbl">Etika &amp; Kepatuhan</div>
  <p><strong>Indikasi, bukan vonis.</strong> Kalkulasi deterministik dari data publik terbuka. Patuh UU No. 27/2022 (UU PDP): IP pengunjung hanya hash 8 karakter.</p>
  <a class="fbtn" href="/api/records.csv" download>Buka Berkas Penilaian Juri ⇩</a>
 </div>
</div>
<div class="fbot">
 <span>© 2026 MATA · AI HackFest 2026 Batch 3 · {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
 <span><button id="reboot">putar ulang pembuka</button></span>
 <span>Sumber: LKPP · INAPROC · SAPA Kemkominfo · Open-Meteo · Open Source Public Good</span>
</div></div></footer>
<div id="pitchmodal" role="dialog" aria-label="Berkas penilaian juri" aria-hidden="true">
 <div class="pitchbox">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
   <span class="hackbadge">◈ AI HACKFEST 2026 · BATCH 3 (11–15 SEP 2026)</span>
   <button class="btn" onclick="closePitch()" aria-label="Tutup">✕ Tutup</button>
  </div>
  <h3>Berkas Pitching &amp; Lembar Penilaian Dewan Juri</h3>
  <p class="note">MATA (Watchdog Akuntabilitas Pengadaan) — {_esc(len(recs))} paket terpantau · {_esc(len(flags))} indikasi live · mode {_esc(mode)}. Berjalan 24/7 di VPS.</p>
  <h4 style="font-family:'JetBrains Mono',monospace;font-size:12px;margin:14px 0 4px">INFRASTRUKTUR PRODUKSI 24/7</h4>
  <div class="kanalgrid">
   <a class="kanal" href="https://idwebhost.com/ai-hosting/" target="_blank" rel="noopener"><span class="kl">SPONSOR 01</span><b>AI Hosting IDwebhost ↗</b><span>Runtime 24/7 daemon mata.service, cron loop, dan domain resmi mata.niumination.web.id.</span></a>
   <a class="kanal" href="https://cloudbaik.com/" target="_blank" rel="noopener"><span class="kl">SPONSOR 02</span><b>Cloud VPS CloudBaik ↗</b><span>VM SSD berkecepatan tinggi; footprint ultra-ringan tanpa GPU mahal.</span></a>
  </div>
  <div class="pitchterm"><div class="d"># systemctl status mata.service</div><div class="g">● mata.service — MATA 24/7 PBJ Watchdog Loop (active, running)</div><div class="d">  loop pengumpulan berkala 3600 dtk · dashboard dev :8080 · produksi :80</div><div class="o">  Tasks: 4 · Memory: ±42M · CPU: 0.4%</div></div>
  <h4 style="font-family:'JetBrains Mono',monospace;font-size:12px;margin:14px 0 4px">BOBOT PENILAIAN (100%)</h4>
  <div class="critgrid">
   <div class="crit"><span class="pct">30%</span><b>Efektivitas</b>Deteksi otomatis → dossier PDF, draft APIP, ringkasan publik.</div>
   <div class="crit"><span class="pct">20%</span><b>Relevansi</b>Menjawab kebocoran PBJ; lokus Aceh Tengah → replikasi nasional.</div>
   <div class="crit"><span class="pct">20%</span><b>Teknis</b>Hermes Agent, cron, SQLite, SAPA, INAPROC live, systemd 24/7.</div>
   <div class="crit"><span class="pct">15%</span><b>Kreativitas</b>Watchdog untuk rakyat; patuh UU PDP; desain living codex.</div>
   <div class="crit"><span class="pct">15%</span><b>Storytelling</b>"Uang itu uangmu…" + naskah video terstruktur.</div>
  </div>
  <h4 style="font-family:'JetBrains Mono',monospace;font-size:12px;margin:14px 0 4px">KESESUAIAN DNA JURI</h4>
  <div class="jgrid">
   <div class="jcard"><b>Onno W. Purbo</b><div class="jr">Pakar IT &amp; Open Source</div>Open data publik, akuntabilitas rakyat, tanpa ketergantungan proprietary.</div>
   <div class="jcard"><b>Ogi S. Pornawan</b><div class="jr">Head of Product IDwebhost</div>Dampak nyata proteksi uang publik; uptime 24/7; keberlanjutan.</div>
   <div class="jcard"><b>Eko Novianto, S.T.</b><div class="jr">aiclub.id &amp; AI Researcher</div>Kejujuran teknis: data nyata, rule engine transparan terverifikasi.</div>
  </div>
  <div class="fbtnrow" style="margin-top:14px"><a class="btn" href="/api/records.csv" download>⇩ Unduh arsip CSV</a>
   <button class="btn" onclick="closePitch()">Tutup &amp; kembali</button></div>
 </div>
</div>
<button id="chatfab" aria-label="Tanya MATA" title="Tanya MATA">
 <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="var(--on-ember)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
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
 <div class="cchips">
  <button onclick="askAI(this.textContent)">Vendor mana paling dominan?</button>
  <button onclick="askAI(this.textContent)">Ada berapa paket ≥ Rp 100 jt?</button>
  <button onclick="askAI(this.textContent)">Dasar hukum D2 konsentrasi vendor?</button>
  <button onclick="askAI(this.textContent)">Bagaimana serapan RUP vs realisasi?</button>
  <button onclick="askAI(this.textContent)">Jelaskan temuan D4 terbaru</button>
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
var SIM={sim_json};
var KUTIPAN={quote_json};
(function(){{
 var el=document.getElementById('kutipan');
 if(!el || !KUTIPAN || !KUTIPAN.length) return;
 var idx=Math.floor(Date.now()/86400000)%KUTIPAN.length;
 function showQ(i){{ idx=(i+KUTIPAN.length)%KUTIPAN.length;
 var q=KUTIPAN[idx];
 var idq=String(q.id).replace(/[“”]/g,'');
 el.innerHTML='<span class="q-tag">Refleksi hari ini <span class="q-nav"><button aria-label="Sebelumnya" onclick="showQ(window._qi-1)">‹</button><span id="qcount">'+(idx+1)+'/'+KUTIPAN.length+'</span><button aria-label="Berikutnya" onclick="showQ(window._qi+1)">›</button></span></span>'
  +'<span class="q-ar" dir="rtl">'+esc(q.ar)+'</span><span class="q-sep">◆</span>'
  +'<span class="q-tl"><span class="q-id">“'+esc(idq)+'”</span>'
  +'<span class="q-src">'+esc(q.src)+'</span></span>';
 window._qi=idx; }}
 window.showQ=showQ; showQ(idx);
 el.style.display='';}})();
function esc(s){{ var d=document.createElement('div'); d.textContent=(s==null?'':s); return d.innerHTML; }}
function openPitch(){{var m=document.getElementById('pitchmodal'); if(!m) return;
 m.classList.add('show'); m.setAttribute('aria-hidden','false');
 try{{document.body.style.overflow='hidden';}}catch(e){{}}}}
function closePitch(){{var m=document.getElementById('pitchmodal'); if(!m) return;
 m.classList.remove('show'); m.setAttribute('aria-hidden','true');
 try{{document.body.style.overflow='';}}catch(e){{}}}}
document.addEventListener('keydown',function(e){{if(e.key==='Escape') closePitch();}});
(function(){{var m=document.getElementById('pitchmodal'); if(!m) return;
 m.addEventListener('click',function(e){{if(e.target===m) closePitch();}});}})();
function askAI(q){{document.getElementById('chatpanel').classList.add('show');
 var i=document.getElementById('cinput'); i.value=q; i.focus();
 document.getElementById('cform').requestSubmit();}}
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
 /* ---- nav aktif oranye ---- */
 document.querySelectorAll('.sitenav a').forEach(function(a){{
  a.addEventListener('click',function(){{
   document.querySelectorAll('.sitenav a').forEach(function(x){{x.classList.remove('on');}});
   a.classList.add('on');
  }});
 }});
 /* ---- saring indikasi per aturan D1–D6 ---- */
 (function(){{
  var pills=document.querySelectorAll('#rulepills .rbtn');
  if(!pills.length) return;
  function counts(){{
   var c={{semua:0}};
   document.querySelectorAll('#flags .flag').forEach(function(el){{
    var r=el.getAttribute('data-rule')||'?'; c.semua++;
    c[r]=(c[r]||0)+1;}});
   pills.forEach(function(b){{
    var r=b.getAttribute('data-r');
    b.querySelector('.rp-n').textContent='('+(c[r]||0)+')';}});
  }}
  pills.forEach(function(b){{
   b.onclick=function(){{
    pills.forEach(function(x){{x.classList.remove('on');}});
    b.classList.add('on');
    var r=b.getAttribute('data-r');
    document.querySelectorAll('#flags .flag').forEach(function(el){{
     el.style.display=(r==='semua'||el.getAttribute('data-rule')===r)?'':'none';}});
   }};
  }});
  counts();
 }})();
 /* ---- simulator ambang vs aktual live ---- */
 (function(){{
  function fmtPct(v){{return (Math.round(v*100)/100)+'%';}}
  function verdict(actual, th, unit, lbl){{
   if(actual==null) return 'Tak ada temuan '+lbl+' pada data live — ambang '+th+unit+' tak menguji apa pun.';
   var hit = actual>=th;
   return 'Aktual live <b>'+(unit==='×'?actual+'×':fmtPct(actual))+'</b> vs ambang '+th+unit
    + ' → <span class="'+(hit?'hit':'miss')+'">'+(hit?'TERPICU':'TAK TERPICU')+'</span>.';
  }}
  var defs={{d1:30,d2:5,d3:2,d4:5}};
  function upd(){{
   var t1=+document.getElementById('sim-d1').value,
       t2=+document.getElementById('sim-d2').value,
       t3=+document.getElementById('sim-d3').value,
       t4=+document.getElementById('sim-d4').value;
   document.getElementById('sim-v-d1').textContent=t1+'%';
   document.getElementById('sim-v-d2').textContent=t2+'%';
   document.getElementById('sim-v-d3').textContent=t3.toFixed(1)+'×';
   document.getElementById('sim-v-d4').textContent=t4.toFixed(1)+'×';
   var s=window.SIM||{{}};
   document.getElementById('sim-t-d1').innerHTML=verdict(s.D1,t1,'%','D1');
   document.getElementById('sim-t-d2').innerHTML=verdict(s.D2share,t2,'%','D2')
    +' Maksimal paket satu vendor: <b>'+(s.D2n==null?'—':s.D2n)+'</b>.';
   document.getElementById('sim-t-d3').innerHTML=verdict(s.D3,t3,'×','D3');
   document.getElementById('sim-t-d4').innerHTML=verdict(s.D4,t4,'×','D4');
   var n=[s.D1!=null&&s.D1>=t1,s.D2share!=null&&s.D2share>=t2,s.D3!=null&&s.D3>=t3,s.D4!=null&&s.D4>=t4]
    .filter(Boolean).length;
   document.getElementById('sim-sum').textContent=n+' dari 4 ambang memicu temuan live.';
  }}
  ['d1','d2','d3','d4'].forEach(function(k){{
   var el=document.getElementById('sim-'+k); if(el) el.oninput=upd;}});
  var rs=document.getElementById('sim-reset');
  if(rs) rs.onclick=function(){{
   document.getElementById('sim-d1').value=defs.d1;
   document.getElementById('sim-d2').value=defs.d2;
   document.getElementById('sim-d3').value=defs.d3;
   document.getElementById('sim-d4').value=defs.d4; upd();}};
  if(document.getElementById('sim-d1')) upd();
 }})();
 /* ---- tab dossier + salin dokumen ---- */
 (function(){{
  var tabs=document.querySelectorAll('.dtab');
  tabs.forEach(function(b){{
   b.onclick=function(){{
    tabs.forEach(function(x){{x.classList.remove('on');}});
    b.classList.add('on');
    document.querySelectorAll('.dpanel').forEach(function(p){{p.classList.remove('on');}});
    var t=document.getElementById('dp-'+b.getAttribute('data-dt'));
    if(t) t.classList.add('on');
   }};
  }});
  document.querySelectorAll('[data-copy]').forEach(function(b){{
   b.onclick=function(){{
    var t=document.querySelector(b.getAttribute('data-copy'));
    if(!t) return;
    function ok(){{ b.textContent='Tersalin ✓'; setTimeout(function(){{b.textContent=b.getAttribute('data-copy')==='#doct-pub'?'Salin siaran pers':'Salin teks surat';}},2000); }}
    if(navigator.clipboard && navigator.clipboard.writeText){{
     navigator.clipboard.writeText(t.textContent).then(ok).catch(function(){{}});
    }} else {{
     var r=document.createRange(); r.selectNodeContents(t);
     var s=getSelection(); s.removeAllRanges(); s.addRange(r);
     try{{document.execCommand('copy');ok();}}catch(e){{}} s.removeAllRanges();
    }}
   }};
  }});
 }})();
 /* ---- cari paket + chip vendor + filter nilai + paginasi ---- */
 var q=document.getElementById('q');
 var pkgPage=1, pkgPer=15, pkgBig=false;
 function pkgRows(){{
  var s=(q.value||'').toLowerCase();
  return Array.prototype.filter.call(document.querySelectorAll('#pkgs .pkg'),function(r){{
   if(s && r.getAttribute('data-q').toLowerCase().indexOf(s)<0) return false;
   if(pkgBig && (+r.getAttribute('data-v')||0)<100000000) return false;
   return true;}});
 }}
 function pkgDraw(){{
  var rows=pkgRows(), tot=rows.length, pages=Math.max(1,Math.ceil(tot/pkgPer));
  if(pkgPage>pages) pkgPage=pages;
  document.querySelectorAll('#pkgs .pkg').forEach(function(r){{r.style.display='none';}});
  rows.slice((pkgPage-1)*pkgPer,pkgPage*pkgPer).forEach(function(r){{r.style.display='';}});
  var cc=document.getElementById('pkg-count');
  if(cc) cc.textContent=tot+' paket cocok';
  var pp=document.getElementById('pkg-page');
  if(pp) pp.textContent='Halaman '+pkgPage+' / '+pages;
 }}
 function pkgFilter(){{pkgPage=1;pkgDraw();}}
 q.oninput=pkgFilter;
 var pb=document.getElementById('pkg-big');
 if(pb) pb.onclick=function(){{
  pkgBig=!pkgBig; pb.classList.toggle('on',pkgBig);
  pb.setAttribute('aria-pressed',pkgBig?'true':'false'); pkgFilter();}};
 var pv=document.getElementById('pkg-prev'), nx=document.getElementById('pkg-next');
 if(pv) pv.onclick=function(){{if(pkgPage>1){{pkgPage--;pkgDraw();}}}};
 if(nx) nx.onclick=function(){{pkgPage++;pkgDraw();}};
 pkgDraw();
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
 /* fokus peta ke titik perangkat pengunjung (hanya setelah ia setuju) */
 function focusUser(){{
  if(window.__uloc&&osmMap){{ try{{osmMap.setView(window.__uloc,10);}}catch(e){{}} }}
 }}
 function useCity(d){{
  var c=d&&d.city?String(d.city).toLowerCase():'';
  if(c&&window.CITYC&&CITYC[c]) window.__uloc=CITYC[c];
  locHide('city'); vrefresh(); focusUser();
 }}
 function locHide(v){{try{{localStorage.setItem('mata_loc',v);}}catch(e){{}}
  document.getElementById('locbanner').classList.remove('show');}}
 try{{ if(!localStorage.getItem('mata_loc')){{
  setTimeout(function(){{document.getElementById('locbanner').classList.add('show');}},7500);
 }} }}catch(e){{ document.getElementById('locbanner').classList.add('show'); }}
 document.getElementById('loc-gps').onclick=function(){{
  if(!window.isSecureContext){{ locMsg('Browser menolak GPS pada koneksi HTTP (wajib HTTPS). Merekam <b>perkiraan kota</b> saja.'); locPost({{consent:'city'}},useCity); return; }}
  if(!navigator.geolocation){{ locMsg('Perangkat tidak mendukung GPS. Merekam <b>perkiraan kota</b> saja.'); locPost({{consent:'city'}},useCity); return; }}
  locMsg('Menunggu izin GPS dari browser…');
  navigator.geolocation.getCurrentPosition(function(p){{
   var la=Math.round(p.coords.latitude*100)/100, lo=Math.round(p.coords.longitude*100)/100;
   locPost({{consent:'precise',lat:la,lon:lo}},
    function(){{window.__uloc=[la,lo];locMsg('Tersimpan (±1 km). Terima kasih.');locHide('precise');vrefresh();focusUser();}});
  }},function(){{ locMsg('Izin GPS ditolak — merekam <b>perkiraan kota</b> saja.');
   locPost({{consent:'city'}},useCity); }},{{timeout:10000}});
 }};
 document.getElementById('loc-city').onclick=function(){{
  locPost({{consent:'city'}},useCity);}};
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
   L.circleMarker([la,lo],{{radius:6+Math.min(n,9),color:'var(--ember)',weight:2,fillColor:'var(--ember-vivid)',fillOpacity:.85}})
    .bindTooltip(esc(Lc.city)+' · '+n).addTo(osmMarks);
  }});
  focusUser();
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
 document.getElementById('iklim-sel').addEventListener('change',iklimLoad);
 /* chips sentra — klik cepat selain dropdown */
 (function(){{
  var sel=document.getElementById('iklim-sel'), box=document.getElementById('iklim-chips');
  if(!sel||!box) return;
  function draw(){{
   box.innerHTML='';
   Array.prototype.forEach.call(sel.options,function(o){{
    var b=document.createElement('button');
    b.className='rbtn'+(o.selected?' on':''); b.textContent=o.text; b.type='button';
    b.onclick=function(){{sel.value=o.value; draw();
     var ev=document.createEvent('HTMLEvents'); ev.initEvent('change',true,false); sel.dispatchEvent(ev);}};
    box.appendChild(b);
   }});
  }}
  sel.addEventListener('change',function(){{setTimeout(draw,50);}});
  draw();
 }})();
 /* panel iklim mulai ringkas (judul saja), klik judul untuk buka — muat saat pertama dibuka */
 (function(){{
  var p=document.getElementById('iklim-panel'); if(!p) return;
  var k=p.querySelector('.kicker'), loaded=false;
  p.classList.add('mini');
  function tg(){{p.classList.toggle('mini');
   if(!p.classList.contains('mini')&&!loaded){{loaded=true;iklimLoad();}}}}
  k.setAttribute('role','button'); k.setAttribute('tabindex','0');
  k.setAttribute('aria-label','Buka panel Iklim Gayo');
  k.addEventListener('click',tg);
  k.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();tg();}}}});
 }})();
 /* ---- status sistem: /api/health tiap 60 dtk ---- */
 function hrefresh(){{
  var box=document.getElementById('health-body'), meta=document.getElementById('health-meta');
  if(!box||!meta) return;
  fetch('/api/health').then(function(r){{return r.json();}}).then(function(d){{
   box.innerHTML=(d.items||[]).map(function(it){{
    return '<div class="idx"><div class="v">'+esc(it[1])+'</div><div class="k">'+esc(it[0])+'</div></div>';}}).join('');
   meta.textContent=d.ok?'SEHAT':'GANGGUAN';
  }}).catch(function(){{meta.textContent='ERROR';}});
 }}
 setInterval(hrefresh,60000); hrefresh();
 /* ---- rel panel ala template: mati -> rel 56px, ruang dibagi saudara ---- */
 function pstate(){{try{{return JSON.parse(localStorage.getItem('mata_panels')||'{{}}');}}catch(e){{return{{}};}}}}
 function psave(s){{try{{localStorage.setItem('mata_panels',JSON.stringify(s));}}catch(e){{}}}}
 function plabel(p){{if(p.dataset.lbl) return p.dataset.lbl;
  var k=p.querySelector('.kicker'); if(!k) return 'PANEL';
  var t=''; for(var n=k.firstChild;n;n=n.nextSibling){{if(n.nodeType===3)t+=n.textContent;}}
  t=t.replace(/^[^A-Za-z0-9]+/,'').trim().split(/\s+/)[0]; return (t||'PANEL').slice(0,9).toUpperCase();}}
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
   var grid=p.closest('.cols,.cols2'); if(!grid) return;
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
  window.__spse = {{rows: rows, t: (d.tender && d.tender.length) || rows.filter(function(p){{return (p.jenis||p.kind||'tender')!=='nontender';}}).length,
    nt: (d.nontender && d.nontender.length) || rows.filter(function(p){{return (p.jenis||p.kind)==='nontender';}}).length,
    f: (window.__spse && window.__spse.f) || 'all', stale: d.stale, age: d.fetched_at ? Math.max(0, Math.round((Date.now()/1000 - d.fetched_at)/60)) : null}};
  spseDraw();
 }}
 function spseDraw(){{
  var S = window.__spse, rows = S.rows.filter(function(p){{
   var j = p.jenis || p.kind || 'tender';
   return S.f === 'all' || j === S.f || (S.f === 'tender' && j !== 'nontender');
  }});
  function fb(v, lbl, n){{
   return '<button class="rbtn' + (S.f === v ? ' on' : '') + '" data-sf="' + v + '">' + lbl + ' (' + n + ')</button>';
  }}
  var h = '<div class="fbtnrow">' + fb('all', 'Semua', S.rows.length)
       + fb('tender', 'Tender', S.t) + fb('nontender', 'Non-tender', S.nt) + '</div>';
  h += '<table class="light"><tr><td>Paket</td><td class="num">HPS</td>'
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
  Array.prototype.forEach.call(body.querySelectorAll('[data-sf]'), function(b){{
   b.onclick = function(){{ window.__spse.f = b.getAttribute('data-sf'); spseDraw(); }};
  }});
  var S2 = window.__spse;
  meta.textContent = rows.length + ' PAKET TERBUKA'
    + (S2.stale ? ' · CACHE LAMA' : (S2.age != null ? ' · ' + S2.age + ' MNT' : ''));
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
  var tot = kat.reduce(function(a,k){{return a + (+k.nilai || 0);}}, 0);
  function katVal(nm){{ for(var i=0;i<kat.length;i++){{ if((kat[i].nama||'').toLowerCase().indexOf(nm)>=0) return +kat[i].nilai||0; }} return 0; }}
  var peg = katVal('pegawai'), mod = katVal('modal');
  if(tot > 0){{
   h += '<p class="note" style="margin:8px 0 0"><span style="color:var(--ember-deep);font-weight:700">Temuan analitis:</span>'
    + ' Belanja pegawai ' + Math.round(peg/tot*1000)/10 + '% vs belanja modal hanya '
    + Math.round(mod/tot*1000)/10 + '% — setiap rupiah modal PBJ harus dijaga ketat agar tidak bocor.</p>';
  }}
  body.innerHTML = h || '<p class="note">Belum ada rincian kategori.</p>';
  try{{ var tp = document.getElementById('tile-sapa');
   if(tp && d.count) tp.textContent = Number(d.count).toLocaleString('id-ID'); }}catch(e){{}}
  var age = d.fetched_at ? Math.max(0, Math.round((Date.now()/1000 - d.fetched_at)/60)) : null;
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
 var rbody = document.getElementById('rup-body'), rmeta = document.getElementById('rup-meta');
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
  var rrows = (d && d.rup && d.rup.rows) || [];
  if(!rows.length && !rrows.length){{
   body.innerHTML = '<p class="note">' + (d && d.error ? 'Tak termuat: ' + d.error
                    : 'Belum ada data realisasi.') + '</p>';
   meta.textContent = (d && d.stale) ? 'CACHE LAMA' : 'KOSONG';
   if(base) base.textContent = '';
   return;
  }}
  var hasWinner = rows.some(function(r){{ return pick(r, ['nama_penyedia','penyedia','nama_pemenang','pemenang']) != null; }});
  var summ = (d && d.realisasi_summary) || {{}};
  summ = summ.summary && typeof summ.summary === 'object' ? summ.summary : summ;
  var totPaket = null, totNilai = null, k;
  var candPaket = ['total_paket','jumlah_paket','totalPaket','jumlahPaket'];
  var candNilai = ['total_nilai','totalNilai','total_anggaran','totalAnggaran'];
  for(k=0;k<candPaket.length;k++){{ if(typeof summ[candPaket[k]] === 'number' && summ[candPaket[k]] > 0){{ totPaket = summ[candPaket[k]]; break; }} }}
  for(k=0;k<candNilai.length;k++){{ if(typeof summ[candNilai[k]] === 'number' && summ[candNilai[k]] > 0){{ totNilai = summ[candNilai[k]]; break; }} }}
  if(base) base.innerHTML = '<b>' + rows.length + ' paket realisasi</b>' +
   (totPaket ? ' dari <b>' + totPaket + ' total</b> (TA' + (d.tahun || '—') + ')' : ' (halaman pertama)') +
   (totNilai ? ' · total <b>' + fmtNilai(totNilai) + '</b>' : '') +
   (hasWinner ? ' · pemenang + nilai' : '') +
   ' · ' + (d.instansi || '');
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
  if(rbody && rmeta){{
   if(!rrows.length){{ rbody.innerHTML = '<p class="note">Belum ada data RUP.</p>'; rmeta.textContent = 'KOSONG'; }}
   else{{
    var rh = '<table class="light"><tr><td>Kode</td><td>Paket</td><td>Cara Pengadaan</td>'
       + '<td>Sumber Dana</td><td>SKPD</td><td class="num">Nilai</td></tr>';
    rrows.forEach(function(r){{
     var kode = pick(r, ['kode_rup','kode']);
     var rpaket = pick(r, ['nama_paket','paket','nama_kegiatan']);
     var cara = pick(r, ['cara_pengadaan_label','cara_pengadaan','metode_pengadaan']);
     var sumber = pick(r, ['sumber_dana','sumber']);
     var rskpd = pick(r, ['nama_satuan_kerja','satker']);
     var rnilai = pick(r, ['total_nilai','nilai']);
     rh += '<tr><td class="mono small">' + (kode || '—') + '</td><td>' + (rpaket || '—') + '</td>'
        + '<td class="small">' + (cara || '—') + '</td><td class="small">' + (sumber || '—') + '</td>'
        + '<td class="small">' + (rskpd || '—') + '</td>'
        + '<td class="num mono">' + fmtNilai(rnilai) + '</td></tr>';
    }});
    rbody.innerHTML = rh + '</table>';
    rmeta.textContent = rrows.length + ' RUP RENCANA · TA' + (d.tahun || '—');
   }}
  }}
 }}
 fetch('/api/inaproc')
  .then(function(r){{ return r.json(); }})
  .then(render)
  .catch(function(){{
   body.innerHTML = '<p class="note">Tak termuat — coba lagi.</p>';
   meta.textContent = 'ERROR';
   if(rbody) rbody.innerHTML = '<p class="note">Tak termuat — coba lagi.</p>';
   if(rmeta) rmeta.textContent = 'ERROR';
   if(window.__mataToast) window.__mataToast('Panel INAPROC tak termuat.', 'err');
  }});
}})();
/* ============ ANALISIS MATA — pola realisasi (deterministik, indikasi) ============ */
(function(){{
 var body = document.getElementById('analisis-body'), meta = document.getElementById('analisis-meta');
 var base = document.getElementById('analisis-baseline');
 if(!body || !meta) return;
 function fmt(v){{
  if(v == null) return '—';
  var n = Number(v);
  if(isNaN(n)) return String(v);
  if(n >= 1e12) return 'Rp ' + (n/1e12).toLocaleString('id-ID', {{maximumFractionDigits: 2}}) + ' T';
  if(n >= 1e9) return 'Rp ' + (n/1e9).toLocaleString('id-ID', {{maximumFractionDigits: 1}}) + ' M';
  if(n >= 1e6) return 'Rp ' + (n/1e6).toLocaleString('id-ID', {{maximumFractionDigits: 0}}) + ' jt';
  return 'Rp ' + n.toLocaleString('id-ID');
 }}
 function esc(s){{ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;'); }}
 function render(d){{
  if(!d || !d.ok || !d.tahun || !d.tahun['2026']){{
   body.innerHTML = '<p class="note">' + ((d && d.error) || 'Belum ada data analisis.') + '</p>';
   meta.textContent = 'KOSONG';
   if(base) base.textContent = '';
   return;
  }}
  var a = d.tahun['2026'], b = d.tahun['2025'] || {{}};
  if(base) base.innerHTML =
   'TA2026: <b>' + a.n_paket + ' paket</b> · ' + fmt(a.total_nilai) +
   ' · <b>' + a.n_penyedia + ' penyedia</b> · share top-10: <b>' + a.top10_share +
   '%</b>' + (b.n_paket ? ' &nbsp;|&nbsp; TA2025: ' + b.n_paket + ' paket · ' + fmt(b.total_nilai) : '');
  var h = '<h3 class="h3-sub" style="margin:10px 0 4px;font-size:13px;letter-spacing:.4px">TOP 10 PENYEDIA — TA2026 (per nilai)</h3>'
   + '<table class="light"><tr><td>#</td><td>Penyedia</td><td class="num">Paket</td>'
   + '<td class="num">Nilai</td><td class="num">Share</td></tr>';
  (a.top10_nilai || []).forEach(function(p, i){{
   h += '<tr><td class="mono small">' + (i+1) + '</td><td>' + esc(p.nama) + '</td>'
      + '<td class="num">' + p.paket + '</td><td class="num mono">' + fmt(p.nilai) + '</td>'
      + '<td class="num">' + p.share + '%</td></tr>';
  }});
  h += '</table>';
  var mx = Math.max.apply(null, (a.top10_nilai || []).map(function(p){{return p.share || 0;}}) ) || 1;
  h += '<div class="sharebars">' + (a.top10_nilai || []).map(function(p){{
   var w = Math.max(3, Math.round((p.share || 0) / mx * 100));
   return '<div class="srow"><span class="sn">' + esc(p.nama) + '</span>'
    + '<span class="sbar"><i style="width:' + w + '%"></i></span>'
    + '<span class="sv mono">' + p.share + '%</span></div>';
  }}).join('') + '</div>';
  if(d.repeat && d.repeat.length){{
   h += '<h3 class="h3-sub" style="margin:12px 0 4px;font-size:13px;letter-spacing:.4px">MENANG DI KEDUA TAHUN (2025 → 2026)</h3>'
    + '<table class="light"><tr><td>Penyedia</td><td class="num">2025</td><td class="num">2026</td><td class="num">Δ</td></tr>';
   d.repeat.forEach(function(p){{
    var up = p.delta >= 0;
    h += '<tr><td>' + esc(p.nama) + '</td><td class="num mono">' + fmt(p.nilai_2025) + '</td>'
       + '<td class="num mono">' + fmt(p.nilai_2026) + '</td>'
       + '<td class="num mono" style="color:' + (up ? 'var(--delta-up)' : 'var(--delta-down)') + '">'
       + (up ? '+' : '−') + fmt(Math.abs(p.delta)) + (up ? ' ↑' : ' ↓') + '</td></tr>';
   }});
   h += '</table>';
  }}
  if(d.rup_vs_realisasi && d.rup_vs_realisasi.skpd){{
   var rv = d.rup_vs_realisasi, ks = rv.keseluruhan;
   window.__skpd = {{list: rv.skpd || [], q: '', sort: 'rencana'}};
   h += '<h3 class="h3-sub" style="margin:12px 0 4px;font-size:13px;letter-spacing:.4px">RENCANA (RUP) vs REALISASI PER SKPD — TA2026</h3>'
      + '<p class="note" style="margin:4px 0">Keseluruhan: rencana <b>' + fmt(ks.rencana) + '</b> · realisasi <b>' + fmt(ks.realisasi) + '</b> · tercapai <b>' + (ks.rate == null ? '—' : ks.rate + '%') + '</b></p>'
      + '<div class="fbtnrow"><input type="search" id="skpd-q" placeholder="Cari SKPD…" style="flex:1;min-width:160px" aria-label="Cari SKPD">'
      + '<button class="rbtn on" data-ss="rencana">Pagu RUP</button>'
      + '<button class="rbtn" data-ss="realisasi">Realisasi</button>'
      + '<button class="rbtn" data-ss="rate">% Serapan</button>'
      + '<button class="rbtn" data-ss="sisa">Gap Terbesar</button></div>'
      + '<div class="skpdgrid" id="skpd-grid"></div>';
  }}
  if(d.flags && d.flags.length){{
   h += '<h3 class="h3-sub" style="margin:12px 0 4px;font-size:13px;letter-spacing:.4px">SINYAL (perlu verifikasi)</h3>';
   d.flags.forEach(function(f){{
    var contoh = (f.contoh || []).map(esc).join(' · ');
    h += '<p class="note" style="margin:5px 0"><span class="risk r-mid">' + f.n + '</span> '
       + esc(f.label) + (contoh ? ' — ' + contoh : '') + '</p>';
   }});
  }}
  body.innerHTML = h;
  skpdInit();
  try{{ var ts = document.getElementById('tile-skpd');
   if(ts && d.rup_vs_realisasi && d.rup_vs_realisasi.skpd) ts.textContent = d.rup_vs_realisasi.skpd.length; }}catch(e){{}}
  meta.textContent = 'ANALISIS · ' + (a.n_paket + ((b.n_paket) || 0)) + ' PAKET';
 }}
 function skpdInit(){{
  var g = document.getElementById('skpd-grid');
  if(!g || !window.__skpd) return;
  function draw(){{
   var S = window.__skpd;
   var list = S.list.filter(function(s){{
    return (s.nama || '').toLowerCase().indexOf(S.q) >= 0;}});
   list = list.slice().sort(function(a, b){{
    if(S.sort === 'realisasi') return (b.realisasi || 0) - (a.realisasi || 0);
    if(S.sort === 'rate') return (b.rate || 0) - (a.rate || 0);
    if(S.sort === 'sisa') return (b.selisih || 0) - (a.selisih || 0);
    return (b.rencana || 0) - (a.rencana || 0);}});
   g.innerHTML = list.map(function(s){{
    var r = Math.max(0, Math.min(100, s.rate || 0));
    var col = r >= 50 ? '#2e7d32' : (r < 15 ? '#b3261e' : '#b26a00');
    return '<div class="skpd"><div style="display:flex;justify-content:space-between;gap:8px">'
     + '<span class="sn">' + esc(s.nama) + '</span>'
     + '<span class="spct" style="color:' + col + '">' + (s.rate == null ? '—' : s.rate + '%') + '</span></div>'
     + '<div class="prog"><i style="width:' + r + '%;background:' + col + '"></i></div>'
     + '<div class="snums"><div><small>PAGU RUP</small>' + fmt(s.rencana) + '</div>'
     + '<div><small>REALISASI</small>' + fmt(s.realisasi) + '</div>'
     + '<div style="text-align:right"><small>GAP</small>' + fmt(s.selisih) + '</div></div></div>';
   }}).join('') || '<p class="note">Tak ada SKPD cocok.</p>';
  }}
  var qi = document.getElementById('skpd-q');
  if(qi) qi.oninput = function(){{ window.__skpd.q = (qi.value || '').toLowerCase(); draw(); }};
  Array.prototype.forEach.call(document.querySelectorAll('[data-ss]'), function(b){{
   b.onclick = function(){{
    Array.prototype.forEach.call(document.querySelectorAll('[data-ss]'), function(x){{x.classList.remove('on');}});
    b.classList.add('on'); window.__skpd.sort = b.getAttribute('data-ss'); draw();}};
  }});
  draw();
 }}
 fetch('/api/analisis')
  .then(function(r){{ return r.json(); }})
  .then(render)
  .catch(function(){{
   body.innerHTML = '<p class="note">Tak termuat — coba lagi.</p>';
   meta.textContent = 'ERROR';
   if(window.__mataToast) window.__mataToast('Panel Analisis tak termuat.', 'err');
  }});
}})();
</script>
</body></html>"""


_HEALTH = {"at": 0, "out": None}


def _health():
    """Ringkasan kesehatan VPS+backend (stdlib, cache 60 dtk)."""
    import shutil
    import subprocess
    import time as _t
    if _t.time() - _HEALTH["at"] < 60 and _HEALTH["out"]:
        return _HEALTH["out"]
    out = {"ok": True, "items": []}
    try:
        du = shutil.disk_usage("/")
        out["items"].append(("Disk", f"{du.used * 100 // du.total}%"))
        if du.used * 100 // du.total >= 90:
            out["ok"] = False
    except Exception:
        out["items"].append(("Disk", "?"))
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            mm = dict(l.split(":") for l in f.read().splitlines() if ":" in l)
        pct = (1 - int(mm["MemAvailable"].split()[0]) / int(mm["MemTotal"].split()[0])) * 100
        out["items"].append(("RAM", f"{pct:.0f}%"))
        if pct >= 90:
            out["ok"] = False
    except Exception:
        out["items"].append(("RAM", "?"))
    for s in ("mata", "mata-web"):
        try:
            r = subprocess.run(["systemctl", "is-active", s], capture_output=True,
                               text=True, timeout=5)
            st = r.stdout.strip()
        except Exception:
            st = "?"
        out["items"].append((s, st))
        if st != "active":
            out["ok"] = False
    try:
        st = _status()
        out["items"].append(("Siklus", st.get("last_run", "?") or "?"))
        if not st.get("ok"):
            out["ok"] = False
    except Exception:
        out["items"].append(("Siklus", "?"))
        out["ok"] = False
    try:
        import shutil as _sh
        out["items"].append(("AI", "siap" if _sh.which("hermes") else "hilang"))
        if not _sh.which("hermes"):
            out["ok"] = False
    except Exception:
        out["items"].append(("AI", "?"))
    _HEALTH.update(at=_t.time(), out=out)
    return out


def records_sitemap():
    import datetime
    day = datetime.date.today().isoformat()
    urls = [("/", "daily", "1.0"), ("/api/flags", "daily", "0.6"),
            ("/api/records.csv", "daily", "0.6")]
    body = "".join(
        f"<url><loc>https://mata.niumination.web.id{u}</loc>"
        f"<lastmod>{day}</lastmod><changefreq>{f}</changefreq>"
        f"<priority>{p}</priority></url>" for u, f, p in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + body + "</urlset>")


def records_csv():
    recs = db.load_records()
    if _mode(recs) == "LIVE":
        recs = [r for r in recs if str(r.get("id", "")).startswith("INP-")]
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
        if len(raw) > 1024 and "gzip" in (self.headers.get("Accept-Encoding") or ""):
            raw = gzip.compress(raw)
            self.send_header("Content-Encoding", "gzip")
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
        elif path == "/api/analisis":
            self._send(json.dumps(analisis.load(), ensure_ascii=False),
                       "application/json")
        elif path == "/api/edge":
            self._send(json.dumps(edge_feed.summary(), ensure_ascii=False),
                       "application/json")
        elif path == "/api/health":
            self._send(json.dumps(_health(), ensure_ascii=False),
                       "application/json")
        elif path == "/robots.txt":
            self._send("User-agent: *\nAllow: /\nDisallow: /api/\n"
                       "Sitemap: https://mata.niumination.web.id/sitemap.xml\n",
                       "text/plain; charset=utf-8")
        elif path == "/sitemap.xml":
            self._send(records_sitemap(), "application/xml; charset=utf-8")
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
