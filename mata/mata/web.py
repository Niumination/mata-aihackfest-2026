"""Web dashboard MATA — tema "living codex" (cream/ink/ember, serif display).

Rute:
  /                 dashboard (filter level, cari paket, detail per indikasi)
  /api/status       status monitor (JSON)
  /api/flags        indikasi terkini (JSON)
  /api/records.csv  seluruh record (CSV, untuk verifikasi publik)

Pembuka (boot): overlay fullscreen dengan visual + backsound sintesis WebAudio.
Browser memblokir suara autoplay — suara hanya berbunyi setelah pengunjung
menekan tombol MASUK. Tanpa file audio eksternal; ganti dengan MP3 sendiri
via tautan <audio> bila sudah ada asetnya.
"""
import csv
import html
import io
import json
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


def render():
    st = _status()
    flags = db.read_flags()
    recs = db.load_records()
    mode = _mode(recs)
    total = sum(r["value"] for r in recs if r.get("vendor"))
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
    badge = ('<span class="badge ok">● MONITOR ONLINE</span>' if ok
             else '<span class="badge err">● MONITOR ERROR</span>')
    mode_badge = ('<span class="badge live">MODE: LIVE</span>' if mode == "LIVE"
                  else '<span class="badge syn">MODE: SYNTHETIC (demo)</span>')

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
            f'<details class="flag" data-sev="{_esc(f["severity"])}">'
            f'<summary><span class="rule">[{_esc(f["rule_id"])}]</span> '
            f'<span class="{sev}">{_esc(f["severity"].upper())}</span>'
            f'<span class="flag-title">{_esc(f["title"])}</span></summary>'
            f'<ul class="ev">{ev}</ul>'
            f'<div class="meta">Record: <b>{rids or "-"}</b></div>'
            f'<div class="meta">Penjelasan: {_esc(f.get("explanation", ""))}</div>'
            f'<div class="meta">Langkah lanjut: {_esc(f.get("recommendation", ""))}</div>'
            f'</details>')

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
    vs = visitors.stats()
    vtop = ", ".join(f"{_esc(t['path'])} ({t['hits']})" for t in vs["top_today"][:3]) or "-"
    vrows = "".join(
        f'<tr><td class="small mono">{_esc(v["ts"] or "")}</td><td class="small">{_esc(v["path"])}</td>'
        f'<td class="small">{_esc(v["browser"])} · {_esc(v["os"])}</td></tr>' for v in vs["recent"])
    widget = (
        f'<h2><span class="h-num">08</span> Pengunjung live</h2>'
        f'<div class="grid">'
        f'<div class="card"><div class="n mono" id="v-online">{vs["online"]}</div>'
        f'<div class="l">online (5 mnt terakhir)</div></div>'
        f'<div class="card"><div class="n mono" id="v-today">{vs["today_hits"]} / {vs["today_unique"]}</div>'
        f'<div class="l">kunjungan / unik hari ini</div></div>'
        f'<div class="card"><div class="n mono" id="v-total">{vs["total_hits"]} / {vs["total_unique"]}</div>'
        f'<div class="l">kunjungan / unik total</div></div>'
        f'<div class="card"><div class="n small-n" id="v-top">{vtop}</div>'
        f'<div class="l">halaman teratas hari ini</div></div></div>'
        f'<table><tr><td>Waktu (UTC)</td><td>Halaman</td><td>Perangkat</td></tr>'
        f'<tbody id="v-recent">{vrows or "<tr><td colspan=3 class=small>Belum ada kunjungan tercatat.</td></tr>"}</tbody></table>'
        f'<p class="note">Angka segar otomatis tiap 30 detik · privasi minimal: IP asli tidak disimpan, '
        f'hanya hash 8 karakter untuk menghitung pengunjung unik.</p>')
    aceh = ((ctx.get("sirup") or {}).get("aceh")) or {}
    kat = ctx.get("katalog") or {}
    ctx_cards = ""
    if aceh:
        topkat = ", ".join(f"{_esc(k)} ({v})" for k, v in (kat.get("top_categories") or [])[:4])
        ctx_cards = (
            f'<h2><span class="h-num">02</span> Konteks open data — {_esc(ctx.get("region", ""))}</h2>'
            f'<div class="grid">'
            f'<div class="card"><div class="n mono">{_rupiah(aceh.get("rup_total"))}</div>'
            f'<div class="l">total RUP SIRUP (LKPP)</div></div>'
            f'<div class="card"><div class="n mono">{_esc(aceh.get("paket_total", "-"))}</div>'
            f'<div class="l">paket RUP SIRUP</div></div>'
            f'<div class="card"><div class="n mono">{_esc(kat.get("produk_total", "-"))}</div>'
            f'<div class="l">produk katalog ({_esc(kat.get("komoditas_count", "-"))} komoditas)</div></div>'
            f'<div class="card"><div class="n small-n">{topkat or "-"}</div>'
            f'<div class="l">kategori katalog teratas</div></div></div>'
            f'<p class="note">Diambil {_esc(ctx.get("fetched_at", "-"))} · Sumber: LKPP — data.lkpp.go.id '
            f'(open data, agregat per daerah — bukan per paket).</p>')

    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MATA — penjaga uang publik</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{{
 --ink:#241d17; --ink-soft:#5c5347; --cream:#f6f1e7; --surface:#efe8d8;
 --border:#ddd2bd; --ember:#c8501a; --ember-deep:#93350e;
 --red:#b3261e; --amber:#96690a; --green:#35703c; --spot:#00e5ff;
}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
body{{
 font-family:'Inter',system-ui,sans-serif; color:var(--ink); background:var(--cream);
 background-image:radial-gradient(900px 600px at 100% 0%, rgba(200,80,26,.14), transparent 60%),
  radial-gradient(700px 500px at 0% 100%, rgba(36,29,23,.08), transparent 60%);
 background-attachment:fixed; min-height:100vh;
}}
body::before{{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
 background-image:radial-gradient(rgba(36,29,23,.07) 1px, transparent 1px); background-size:20px 20px;
 -webkit-mask-image:radial-gradient(ellipse at center, black 30%, transparent 80%);
 mask-image:radial-gradient(ellipse at center, black 30%, transparent 80%);}}
#app{{position:relative;z-index:1}}
.wrap{{max-width:1080px;margin:0 auto;padding:32px 20px 60px}}
.eyebrow{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.28em;color:var(--ember);margin-bottom:10px}}
h1{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:clamp(34px,6vw,58px);line-height:1.02;margin:0 0 8px}}
h1 em{{color:var(--ember)}}
.sub{{color:var(--ink-soft);font-size:13px;line-height:2.1;margin-bottom:6px}}
.mono{{font-family:'JetBrains Mono',monospace}}
.badge{{display:inline-block;padding:3px 12px;border-radius:999px;font-size:11px;font-weight:600;border:1px solid var(--border);background:#fffdf7;white-space:nowrap}}
.badge.ok{{color:var(--green);border-color:var(--green)}}
.badge.err{{color:var(--red);border-color:var(--red)}}
.badge.live{{color:#0b6bcb;border-color:#0b6bcb}}
.badge.syn{{color:var(--amber);border-color:var(--amber)}}
/* ticker */
.ticker{{overflow:hidden;white-space:nowrap;border-top:1px solid var(--border);border-bottom:1px solid var(--border);
 background:var(--ink);color:var(--cream);margin:20px -20px;padding:9px 0;font-size:12px}}
.ticker-inner{{display:inline-block;animation:marquee 36s linear infinite}}
@keyframes marquee{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.tk-item b{{color:#f0a35e}} .tk-sep{{color:#f0a35e;margin:0 18px}}
/* cards */
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0}}
@media(max-width:700px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
.card{{background:#fffdf7;border:1px solid var(--border);border-radius:20px;padding:16px;
 box-shadow:0 1px 0 rgba(36,29,23,.06);animation:rise .7s cubic-bezier(.16,1,.3,1) both}}
.card:nth-child(2){{animation-delay:.08s}} .card:nth-child(3){{animation-delay:.16s}} .card:nth-child(4){{animation-delay:.24s}}
@keyframes rise{{from{{opacity:0;transform:translateY(12px);filter:blur(6px)}}to{{opacity:1;transform:none;filter:none}}}}
.card .n{{font-size:24px;font-weight:600;word-break:break-word}}
.card .l{{color:var(--ink-soft);font-size:12px;margin-top:4px}}
.card .small-n{{font-size:13px;line-height:1.6}}
h2{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:26px;margin:34px 0 6px}}
.h-num{{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ember);vertical-align:super;margin-right:8px}}
.note{{color:var(--ink-soft);font-size:12px}}
/* flags */
.flag{{background:#fffdf7;border:1px solid var(--border);border-radius:16px;padding:12px 16px;margin:10px 0}}
.flag summary{{cursor:pointer;font-size:14px;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}}
.flag .rule{{font-family:'JetBrains Mono',monospace;color:var(--ember);font-size:12px}}
.flag-title{{font-weight:600}}
.sev-tinggi{{color:var(--red);font-weight:800}} .sev-sedang{{color:var(--amber);font-weight:700}} .sev-rendah{{color:var(--green);font-weight:600}}
.flag .ev{{font-size:13px;color:#3d352b}} .flag .meta{{font-size:12px;color:var(--ink-soft);margin-top:4px}}
/* tables */
table{{width:100%;border-collapse:collapse;font-size:13px;background:#fffdf7;border:1px solid var(--border);border-radius:16px;overflow:hidden}}
td{{padding:8px 10px;border-bottom:1px solid var(--border);vertical-align:top}}
.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.small{{color:var(--ink-soft)}}
a{{color:var(--ember-deep)}}
.bar{{background:var(--surface);border-radius:6px;height:10px;min-width:120px;overflow:hidden}}
.bar div{{background:linear-gradient(90deg,var(--ember),#f0a35e);height:10px;border-radius:6px}}
.months{{display:flex;align-items:flex-end;gap:8px;padding:12px 4px;overflow-x:auto}}
.mcol{{text-align:center;min-width:44px}} .bar{{width:34px;margin:0 auto}}
.bar-dec{{width:34px;background:linear-gradient(180deg,#d8483c,#7e1d12);margin:0 auto;border-radius:4px 4px 0 0}}
.mlabel{{font-size:10px;color:var(--ink-soft);margin-top:4px}} .mval{{font-size:10px}}
.demo-tag{{color:var(--ink-soft);border:1px dashed var(--border);border-radius:6px;padding:1px 8px;font-size:11px;cursor:help}}
/* toolbar */
.toolbar{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;align-items:center}}
.toolbar input[type=search]{{background:#fffdf7;border:1px solid var(--border);color:var(--ink);border-radius:10px;padding:8px 12px;font-size:13px;min-width:230px;font-family:inherit}}
.btn{{background:#fffdf7;border:1px solid var(--border);color:var(--ink);border-radius:10px;padding:8px 14px;font-size:12px;cursor:pointer;text-decoration:none;display:inline-block;font-family:inherit}}
.btn.on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}
.btn:hover{{border-color:var(--ember)}}
/* boot overlay */
#boot{{position:fixed;inset:0;z-index:50;background:#171310;color:#f5efe6;display:flex;align-items:center;justify-content:center;
 transition:opacity .8s ease, visibility .8s}}
#boot.gone{{opacity:0;visibility:hidden;pointer-events:none}}
.boot-inner{{text-align:center;max-width:420px;padding:24px;position:relative}}
.boot-eye{{width:92px;height:92px;margin:0 auto 18px;position:relative}}
.boot-eye svg{{width:100%;height:100%;animation:breathe 3.2s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{opacity:.6;transform:scale(1)}}50%{{opacity:1;transform:scale(1.07)}}}}
.boot-eye::after{{content:"";position:absolute;inset:-6px;border-radius:50%;border:1px solid #e05a1e;animation:pulse-ring 2.4s ease-out infinite}}
@keyframes pulse-ring{{0%{{transform:scale(.85);opacity:.7}}100%{{transform:scale(1.5);opacity:0}}}}
.boot-title{{font-family:'Instrument Serif',Georgia,serif;font-size:44px;margin:0}}
.boot-title em{{color:#f0a35e}}
.boot-sub{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.25em;color:#b8ab98;margin:8px 0 20px}}
.boot-log{{font-family:'JetBrains Mono',monospace;font-size:11px;color:#8f8474;min-height:56px;text-align:left;
 border:1px solid #3a322a;border-radius:12px;padding:12px 14px;margin-bottom:18px;background:#1e1915}}
.boot-log div{{animation:stream-in .4s both}}
@keyframes stream-in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.boot-bar{{height:3px;background:#3a322a;border-radius:99px;overflow:hidden;margin-bottom:22px}}
.boot-bar i{{display:block;height:100%;width:40%;background:linear-gradient(90deg,#e05a1e,#f0a35e);border-radius:99px;animation:load 1.6s ease-in-out infinite}}
@keyframes load{{0%{{margin-left:-40%}}100%{{margin-left:100%}}}}
.boot-btn{{background:#e05a1e;color:#fff;border:none;border-radius:999px;padding:13px 34px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit}}
.boot-btn:hover{{background:#f0a35e;color:#171310}}
.boot-quiet{{display:block;margin-top:12px;font-size:12px;color:#8f8474;text-decoration:underline;cursor:pointer;background:none;border:none;font-family:inherit}}
.foot{{margin-top:40px;color:var(--ink-soft);font-size:11px;border-top:1px solid var(--border);padding-top:14px;line-height:2}}
.foot button{{background:none;border:none;color:var(--ember-deep);text-decoration:underline;cursor:pointer;font-size:11px;font-family:inherit;padding:0}}
::selection{{background:var(--ember);color:var(--cream)}}
</style></head><body>
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
 <div class="eyebrow">WATCHDOG AKUNTABILITAS PENGADAAN · KAB. ACEH TENGAH</div>
 <h1>Mata, penjaga <em>uang publik.</em></h1>
 <div class="sub">Data publik PBJ · aturan transparan · <b>INDIKASI, BUKAN VONIS</b><br>
  {badge} {mode_badge} &nbsp;terakhir: <span class="mono">{_esc(st.get("last_run", "-"))}</span></div>
 <div class="ticker"><div class="ticker-inner">{ticker_items}{ticker_items}</div></div>
 <h2><span class="h-num">01</span> Sekilas angka</h2>
 <div class="grid">
  <div class="card"><div class="n mono">{_esc(n_records)}</div><div class="l">pengumuman dipindai</div></div>
  <div class="card"><div class="n mono" style="color:var(--red)">{_esc(n_flags)}</div><div class="l">indikasi aktif</div></div>
  <div class="card"><div class="n mono">{_rupiah(sum(r["value"] or 0 for r in recs))}</div><div class="l">nilai pengadaan terdata</div></div>
  <div class="card"><div class="n mono">{len(vendors)}</div><div class="l">penyedia terdata</div></div>
 </div>
 {ctx_cards}
 <h2><span class="h-num">03</span> Indikasi — klik untuk bukti &amp; langkah lanjut</h2>
 <div class="toolbar">
  <button class="btn on" data-f="semua">Semua</button>
  <button class="btn" data-f="tinggi">Tinggi</button>
  <button class="btn" data-f="sedang">Sedang</button>
  <button class="btn" data-f="rendah">Rendah</button>
  <a class="btn" href="/api/flags" target="_blank">JSON</a>
 </div>
 <div id="flags">{flag_cards or "<p class='note'>Belum ada indikasi.</p>"}</div>
 <h2><span class="h-num">04</span> Konsentrasi penyedia</h2>
 <table><tr><td>Penyedia</td><td class="num">Proyek</td><td class="num">Total nilai</td><td>Porsi</td></tr>{vendor_rows}</table>
 <h2><span class="h-num">05</span> Nilai kontrak per bulan <span class="note">(merah = jendela akhir tahun)</span></h2>
 <div class="months">{month_bars}</div>
 <h2><span class="h-num">06</span> Cari paket <span class="note">({_esc(len(recs))} record — kolom Sumber untuk verifikasi)</span></h2>
 <div class="toolbar">
  <input type="search" id="q" placeholder="Cari nama paket / instansi / vendor / ID…">
  <a class="btn" href="/api/records.csv" download>Unduh CSV</a>
  <a class="btn" href="/api/status" target="_blank">Status JSON</a>
 </div>
 <table><tr><td>ID</td><td>Paket</td><td>Instansi</td><td class="num">Nilai</td><td>Pemenang</td><td>Tgl</td><td>Sumber</td></tr>
 <tbody id="pkgs">{pkg_rows}</tbody></table>
 <h2><span class="h-num">07</span> Lapor &amp; verifikasi</h2>
 <p class="note">MATA tidak mengirim laporan otomatis. Verifikasi ke sumber di atas, lalu laporkan via kanal resmi:
  <a href="https://www.lapor.go.id" target="_blank" rel="noopener">LAPOR!</a> ·
  <a href="https://www.ombudsman.go.id" target="_blank" rel="noopener">Ombudsman RI</a> ·
  KPK (whistleblower) · APIP/BPKP.</p>
 {widget}
 <div class="foot">MATA · AI HackFest 2026 · indikasi berbasis data, bukan vonis hukum ·
  {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ·
  <button id="reboot">putar ulang pembuka</button></div>
</div></div>
<script>
(function(){{
 var NREC={n_records}, NFLG={n_flags};
 /* ---- boot log ---- */
 var lines=["▸ menghubungi arsip data publik…","▸ memuat "+NREC+" pengumuman pengadaan…",
  "▸ memeriksa "+NFLG+" indikasi anomali…","▸ siap. selamat datang, pengawas."];
 var log=document.getElementById('bootlog'), li=0;
 var timer=setInterval(function(){{ if(li<lines.length){{ var d=document.createElement('div'); d.textContent=lines[li++]; log.appendChild(d); }} else {{ clearInterval(timer); }} }},450);
 /* ---- backsound: pad sintesis WebAudio (tanpa file eksternal) ---- */
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
 /* ---- filter level ---- */
 var fbtns=document.querySelectorAll('[data-f]');
 fbtns.forEach(function(b){{b.onclick=function(){{
  fbtns.forEach(function(x){{x.classList.remove('on')}});b.classList.add('on');
  var f=b.getAttribute('data-f');
  document.querySelectorAll('#flags .flag').forEach(function(c){{
   c.style.display=(f==='semua'||c.getAttribute('data-sev')===f)?'':'none';}});}}}});
 /* ---- cari paket ---- */
 var q=document.getElementById('q');
 q.oninput=function(){{
  var s=q.value.toLowerCase();
  document.querySelectorAll('#pkgs .pkg').forEach(function(r){{
   r.style.display=r.getAttribute('data-q').toLowerCase().indexOf(s)>=0?'':'none';}});}};
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

    def log_message(self, *a):  # sunyi
        pass


def serve(port=8080, host="0.0.0.0"):
    srv = ThreadingHTTPServer((host, port), H)
    print(f"MATA dashboard: http://{host}:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    serve()
