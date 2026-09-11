"""Web dashboard MATA (zero-dependency, stdlib only) — adegan "monitor 24/7" di video.

Jalankan: python3 run.py web -p 8080
Menampilkan: status monitor, jumlah record, indikasi terkini, konsentrasi vendor,
dan konsentrasi nilai per bulan (termasuk jendela akhir tahun).
"""
import os
import json
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _status():
    if os.path.exists(db.STATUS_PATH):
        with open(db.STATUS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"ok": False, "last_error": "belum ada siklus"}


def _rupiah(v):
    return f"Rp {int(v):,}".replace(",", ".")


def render():
    st = _status()
    flags = db.read_flags()
    recs = db.load_records()
    total = sum(r["value"] for r in recs if r.get("vendor"))
    by_vendor = {}
    by_month = {}
    for r in recs:
        if r.get("vendor") and total:
            d = by_vendor.setdefault(r["vendor"], {"n": 0, "value": 0.0})
            d["n"] += 1
            d["value"] += r["value"]
        if r.get("date_signed"):
            by_month[r["date_signed"][:7]] = by_month.get(r["date_signed"][:7], 0) + r["value"]
    vendors = sorted(by_vendor.items(), key=lambda kv: -kv[1]["value"])[:8]
    months = sorted(by_month.items())
    max_m = max((v for _, v in months), default=1)
    max_v = max((d["value"] for _, d in vendors), default=1)

    ok = st.get("ok")
    badge = ('<span class="badge ok">MONITOR ONLINE</span>' if ok
             else '<span class="badge err">MONITOR ERROR</span>')
    flag_rows = ""
    for f in flags:
        sev = {"tinggi": "sev-tinggi", "sedang": "sedang", "rendah": "rendah"}.get(f["severity"], "")
        first = (f.get("evidence") or [""])[0]
        flag_rows += (f'<tr><td>[{f["rule_id"]}]</td><td class="{sev}">{f["severity"].upper()}</td>'
                      f'<td>{f["title"]}</td><td class="small">{first}</td></tr>')
    vendor_rows = ""
    for name, d in vendors:
        pct = d["value"] / max_v * 100
        vendor_rows += (f'<tr><td>{name}</td><td class="num">{d["n"]}</td>'
                        f'<td class="num">{_rupiah(d["value"])}</td>'
                        f'<td><div class="bar"><div style="width:{pct:.0f}%"></div></div></td></tr>')
    month_bars = ""
    for m, v in months:
        h = max(4, int(v / max_m * 120))
        cls = "bar-dec" if m.endswith("-12") else "bar"
        month_bars += (f'<div class="mcol"><div class="{cls}" style="height:{h}px"></div>'
                       f'<div class="mlabel">{m[5:]}/{m[2:4]}</div>'
                       f'<div class="mval">{v/1e9:.1f}M</div></div>')

    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MATA — Watchdog Akuntabilitas Pengadaan</title>
<style>
 body{{font-family:system-ui,Segoe UI,Roboto,sans-serif;margin:0;background:#0e1220;color:#e8ecf5}}
 .wrap{{max-width:1080px;margin:0 auto;padding:28px 20px}}
 h1{{font-size:22px;margin:0 0 4px}} h1 b{{color:#7fd4ff}}
 .sub{{color:#9aa7c4;font-size:13px;margin-bottom:18px}}
 .badge{{padding:3px 10px;border-radius:20px;font-size:12px;font-weight:700}}
 .ok{{background:#123c2b;color:#5fe3a1}} .err{{background:#4a1520;color:#ff8fa3}}
 .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}}
 .card{{background:#161c2e;border:1px solid #232c47;border-radius:12px;padding:14px}}
 .card .n{{font-size:26px;font-weight:800}} .card .l{{color:#9aa7c4;font-size:12px}}
 h2{{font-size:15px;margin:22px 0 8px;color:#c7d2ec}}
 table{{width:100%;border-collapse:collapse;font-size:13px}}
 td{{padding:6px 8px;border-bottom:1px solid #1f2842}}
 .num{{text-align:right;font-variant-numeric:tabular-nums}}
 .small{{color:#9aa7c4}} .sev-tinggi{{color:#ff8fa3;font-weight:700}}
 .sedang{{color:#ffd28f;font-weight:600}} .rendah{{color:#9fd0a5}}
 .bar{{background:#1f2842;border-radius:6px;height:10px;min-width:120px}}
 .bar div{{background:linear-gradient(90deg,#4f8cff,#7fd4ff);height:10px;border-radius:6px}}
 .months{{display:flex;align-items:flex-end;gap:8px;padding:10px 0}}
 .mcol{{text-align:center}} .bar{{width:34px;background:#243056;margin:0 auto}}
 .bar-dec{{width:34px;background:linear-gradient(180deg,#ff6b81,#b3233f);margin:0 auto}}
 .mlabel{{font-size:10px;color:#9aa7c4;margin-top:4px}} .mval{{font-size:10px}}
 .foot{{margin-top:26px;color:#5f6c8f;font-size:11px;border-top:1px solid #1f2842;padding-top:12px}}
</style></head><body><div class="wrap">
 <h1><b>MATA</b> — Watchdog Akuntabilitas Pengadaan</h1>
 <div class="sub">Data publik PBJ · aturan transparan · INDIKASI, BUKAN VONIS &nbsp; {badge}
   &nbsp; terakhir: {st.get("last_run","-")}</div>
 <div class="grid">
  <div class="card"><div class="n">{st.get("n_records", len(recs))}</div><div class="l">pengumuman dipindai</div></div>
  <div class="card"><div class="n" style="color:#ff8fa3">{st.get("n_flags", len(flags))}</div><div class="l">indikasi aktif</div></div>
  <div class="card"><div class="n">{_rupiah(sum(r['value'] for r in recs))}</div><div class="l">nilai pengadaan terdata</div></div>
  <div class="card"><div class="n">{len(vendors)}</div><div class="l">penyedia terdata</div></div>
 </div>
 <h2>Indikasi terkini</h2>
 <table><tr><td>Aturan</td><td>Level</td><td>Indikasi</td><td>Bukti pertama</td></tr>{flag_rows}</table>
 <h2>Konsentrasi penyedia</h2>
 <table><tr><td>Penyedia</td><td class="num">Proyek</td><td class="num">Total nilai</td><td>Porsi</td></tr>{vendor_rows}</table>
 <h2>Nilai kontrak per bulan (merah = jendela akhir tahun)</h2>
 <div class="months">{month_bars}</div>
 <div class="foot">MATA · AI HackFest 2026 · berjalan 24/7 di AI Hosting IDwebhost × CloudBaik ·
  sumber data: LPSE/Panda LKPP, e-Katalog, e-Kontrak (data publik) · {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
</div></body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = render().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # sunyi
        pass


def serve(port=8080, host="0.0.0.0"):
    srv = ThreadingHTTPServer((host, port), H)
    print(f"MATA dashboard: http://{host}:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    serve()
