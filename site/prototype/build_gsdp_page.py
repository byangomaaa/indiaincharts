"""Prototype: build the "GDP of {state}" page from MoSPI state accounts data.

This is the reference template for single-metric pages (CLAUDE.md §6.2). Everything on the
page (headline, cards, charts, table, summary) is computed from the data file, so the same
script builds any state:  python site/prototype/build_gsdp_page.py "Maharashtra"

Input:  data/raw/prototype/nas-state-2011-12.json  (MoSPI NAS, base 2011-12, Current series)
Output: site/prototype/gdp-of-<state>.html
"""
import html
import json
import math
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = sys.argv[1] if len(sys.argv) > 1 else "Maharashtra"
RAW = json.load(open(os.path.join(ROOT, "data/raw/prototype/nas-state-2011-12.json")))
D = RAW["data"]
FETCHED = RAW["fetched"]
BUILT = date.today()
SLUG = re.sub(r"[^a-z0-9]+", "-", STATE.lower()).strip("-")
URL_PATH = f"/economy/gsdp/{SLUG}/"
e = html.escape


# ---------- number formatting (Indian conventions) ----------
def num(v):
    return float(v) if v not in (None, "") else None


def indian(n, dec=0):
    """12345678 -> 1,23,45,678 (Indian digit grouping)."""
    s = f"{abs(n):.{dec}f}"
    whole, _, frac = s.partition(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
        whole = head + "," + tail
    return ("-" if n < 0 else "") + whole + ("." + frac if frac else "")


def lakh_crore(crore, dec=2):
    return f"{crore / 1e5:.{dec}f}"


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def pct(v, sign=True):
    return (f"{v:+.1f}" if sign else f"{v:.1f}").replace("-", "−") + "%"


# ---------- data ----------
def series(code, state, field):
    rows = [r for r in D[code] if r["state"] == state]
    return {r["year"]: num(r[field]) for r in rows}


gsdp_cur = series("23", STATE, "current_price")
gsdp_con = series("23", STATE, "constant_price")
growth_real = series("26", STATE, "constant_price")
growth_nom = series("26", STATE, "current_price")
pc_cur = series("25", STATE, "current_price")
years = sorted(y for y in gsdp_cur if gsdp_cur[y] is not None)
latest, first = years[-1], years[0]

# Ranks use the latest year in which every reporting state/UT has a value.
all_states = sorted({r["state"] for r in D["23"]})
def complete_year(code):
    ys = sorted({r["year"] for r in D[code]})
    for y in reversed(ys):
        vals = [num(r["current_price"]) for r in D[code] if r["year"] == y]
        if vals and all(v is not None for v in vals):
            return y
rank_year = complete_year("23")
def ranking(code, year):
    rows = [(num(r["current_price"]), r["state"]) for r in D[code] if r["year"] == year and num(r["current_price"])]
    return sorted(rows, reverse=True)
gsdp_rank = ranking("23", rank_year)
pc_rank = ranking("25", rank_year)
my_rank = [s for _, s in gsdp_rank].index(STATE) + 1
my_pc_rank = [s for _, s in pc_rank].index(STATE) + 1
n_rank = len(gsdp_rank)
runner_up = gsdp_rank[1] if my_rank == 1 else gsdp_rank[0]
ratio_to_next = gsdp_cur[rank_year] / runner_up[0]

nominal_multiple = gsdp_cur[latest] / gsdp_cur[first]
real_multiple = gsdp_con[latest] / gsdp_con[first]
n_years = years.index(latest) - years.index(first)
real_cagr = (real_multiple ** (1 / n_years) - 1) * 100
contractions = [y for y in years[1:] if growth_real.get(y) is not None and growth_real[y] < 0]
prev = years[-2]
latest_reporting = sum(1 for r in D["23"] if r["year"] == latest and num(r["current_price"]))

# ---------- facts -> prose (every number here comes from the variables above) ----------
facts = {
    "gsdp_latest_lc": lakh_crore(gsdp_cur[latest]),
    "growth_real_latest": f"{growth_real[latest]:.1f}",
    "growth_real_prev": f"{growth_real[prev]:.1f}",
    "nominal_multiple": f"{nominal_multiple:.1f}",
    "real_multiple": f"{real_multiple:.2f}",
    "real_cagr": f"{real_cagr:.1f}",
    "rank": ordinal(my_rank),
    "ratio_next": f"{ratio_to_next:.2f}",
    "runner_up": runner_up[1],
    "runner_up_lc": lakh_crore(runner_up[0]),
    "pc_latest": indian(pc_cur[latest]),
    "pc_rank": ordinal(my_pc_rank),
}

direct_answer = (
    f"{STATE}'s GDP (Gross State Domestic Product) was <strong>₹{facts['gsdp_latest_lc']} lakh crore</strong> "
    f"in {latest} at current prices, "
    + (f"the largest of any state or UT" if my_rank == 1 else f"{facts['rank']} among states and UTs")
    + f" (MoSPI, 2011-12 base)."
)

summary_paras = [
    f"{STATE}'s economy grew <strong>{facts['growth_real_latest']}%</strong> in real terms in {latest}, "
    f"after {facts['growth_real_prev']}% in {prev}. At current prices its GSDP reached ₹{facts['gsdp_latest_lc']} lakh crore.",
    f"Since {first}, the economy has grown {facts['nominal_multiple']} times at current prices and "
    f"{facts['real_multiple']} times after adjusting for prices, an average real growth of {facts['real_cagr']}% a year."
    + (f" The only year of real contraction was {', '.join(contractions)} ({pct(growth_real[contractions[0]])})." if len(contractions) == 1 else ""),
    (f"In {rank_year}, the latest year with figures for all {n_rank} reporting states and UTs, {STATE} ranked "
     f"<strong>{facts['rank']}</strong> by GSDP"
     + (f", {facts['ratio_next']} times the size of second-placed {facts['runner_up']} (₹{facts['runner_up_lc']} lakh crore)." if my_rank == 1 else ".")),
    f"Income per person tells a different story. {STATE}'s per-capita NSDP was ₹{facts['pc_latest']} in {latest}, "
    f"and in {rank_year} it ranked <strong>{facts['pc_rank']}</strong> of {n_rank}.",
]

# ---------- charts (SVG at build time) ----------
def nice_max(v):
    mag = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * mag:
            return m * mag
    return 10 * mag


def line_chart():
    W, H, L, R, T, B = 720, 340, 56, 120, 24, 40
    cur = [gsdp_cur[y] / 1e5 for y in years]
    con = [gsdp_con[y] / 1e5 for y in years]
    ymax = nice_max(max(cur))
    step = ymax / 5
    x = lambda i: L + i * (W - L - R) / (len(years) - 1)
    yv = lambda v: T + (H - T - B) * (1 - v / ymax)
    grid = "".join(
        f'<line class="grid" x1="{L}" x2="{W - R}" y1="{yv(k * step):.1f}" y2="{yv(k * step):.1f}"/>'
        f'<text class="tick" x="{L - 8}" y="{yv(k * step) + 4:.1f}" text-anchor="end">{k * step:g}</text>'
        for k in range(6))
    xt = "".join(
        f'<text class="tick" x="{x(i):.1f}" y="{H - B + 20}" text-anchor="middle">{y[:4]}–{y[-2:]}</text>'
        for i, y in enumerate(years) if i % 2 == 0 or i == len(years) - 1)
    def path(vals):
        return "M" + " L".join(f"{x(i):.1f},{yv(v):.1f}" for i, v in enumerate(vals))
    end_labels = (
        f'<text class="lbl s1" x="{x(len(years) - 1) + 10:.1f}" y="{yv(cur[-1]) + 4:.1f}">Current prices</text>'
        f'<text class="lbl s2" x="{x(len(years) - 1) + 10:.1f}" y="{yv(con[-1]) + 4:.1f}">2011-12 prices</text>')
    dots = (f'<circle class="dot s1f" cx="{x(len(years) - 1):.1f}" cy="{yv(cur[-1]):.1f}" r="4"/>'
            f'<circle class="dot s2f" cx="{x(len(years) - 1):.1f}" cy="{yv(con[-1]):.1f}" r="4"/>')
    colw = (W - L - R) / (len(years) - 1)
    hits = "".join(
        f'<rect class="hit" x="{x(i) - colw / 2:.1f}" y="{T}" width="{colw:.1f}" height="{H - T - B}" '
        f'data-i="{i}" data-year="{y}" data-cur="{indian(gsdp_cur[y])}" data-con="{indian(gsdp_con[y])}" '
        f'data-g="{pct(growth_real[y]) if growth_real.get(y) is not None else "—"}" '
        f'data-x="{x(i):.1f}" data-ycur="{yv(cur[i]):.1f}" data-ycon="{yv(con[i]):.1f}"/>'
        for i, y in enumerate(years))
    return f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-labelledby="trend-title trend-desc" id="trend-svg">
<title id="trend-title">{e(STATE)} GSDP, {first} to {latest}</title>
<desc id="trend-desc">Line chart in lakh crore rupees. At current prices GSDP rose from {lakh_crore(gsdp_cur[first])} to {facts["gsdp_latest_lc"]}; at 2011-12 prices from {lakh_crore(gsdp_con[first])} to {lakh_crore(gsdp_con[latest])}.</desc>
{grid}<line class="axis" x1="{L}" x2="{W - R}" y1="{H - B}" y2="{H - B}"/>{xt}
<text class="unit" x="{L}" y="{T - 8}">₹ lakh crore</text>
<path class="ln s1" d="{path(cur)}"/><path class="ln s2" d="{path(con)}"/>{dots}{end_labels}
<line class="xhair" id="xhair" x1="0" x2="0" y1="{T}" y2="{H - B}" visibility="hidden"/>
<circle class="dot s1f hov" id="hcur" r="5" visibility="hidden"/><circle class="dot s2f hov" id="hcon" r="5" visibility="hidden"/>
{hits}</svg>'''


def bar_chart(top=10):
    rows = gsdp_rank[:top]
    if STATE not in [s for _, s in rows]:
        rows = rows[:top - 1] + [(gsdp_cur[rank_year], STATE)]
    W, rowh, L, R = 720, 30, 150, 96
    H = rowh * len(rows) + 8
    vmax = rows[0][0] / 1e5
    out = []
    for i, (v, s) in enumerate(rows):
        w = (W - L - R) * (v / 1e5) / vmax
        y = 4 + i * rowh
        mine = " mine" if s == STATE else ""
        rk = [st for _, st in gsdp_rank].index(s) + 1
        out.append(
            f'<g class="bar{mine}"><title>{e(s)}: ₹{lakh_crore(v)} lakh crore ({rank_year}), rank {rk}</title>'
            f'<text class="blabel" x="{L - 10}" y="{y + rowh / 2 + 4:.1f}" text-anchor="end">{e(s)}</text>'
            f'<rect x="{L}" y="{y + 5}" width="{max(w, 2):.1f}" height="{rowh - 10}" rx="3"/>'
            f'<text class="bval" x="{L + w + 8:.1f}" y="{y + rowh / 2 + 4:.1f}">₹{lakh_crore(v, 1)}</text></g>')
    return (f'<svg viewBox="0 0 {W} {H}" class="chart bars" role="img" aria-label="Top {len(rows)} states and UTs by GSDP, {rank_year}, lakh crore rupees">'
            + "".join(out) + "</svg>")


def infographic():
    top5 = gsdp_rank[:5]
    vmax = top5[0][0]
    bars = ""
    for i, (v, s) in enumerate(top5):
        w = 460 * v / vmax
        y = 300 + i * 52
        fill = "#f2b544" if s == STATE else "#4b578f"
        tcol = "#121a3a" if s == STATE else "#e8ebfa"
        bars += (f'<rect x="660" y="{y}" width="{w:.0f}" height="38" rx="4" fill="{fill}"/>'
                 f'<text x="672" y="{y + 26}" font-size="20" font-weight="600" fill="{tcol}" font-family="IBM Plex Sans, sans-serif">{e(s)}</text>')
    headline = f"{STATE} is India's largest state economy" if my_rank == 1 else f"{STATE} ranks {facts['rank']} by state GDP"
    return f'''<svg viewBox="0 0 1200 675" class="info" role="img" aria-label="Infographic: {e(headline)}. GSDP ₹{facts["gsdp_latest_lc"]} lakh crore in {latest}.">
<rect width="1200" height="675" fill="#121a3a"/>
<rect x="0" y="0" width="1200" height="8" fill="#f2b544"/>
<text x="64" y="104" font-size="30" font-weight="600" fill="#b9c0e6" font-family="IBM Plex Sans, sans-serif">GDP OF {e(STATE.upper())} · {latest}</text>
<text x="64" y="170" font-size="46" font-weight="800" fill="#ffffff" font-family="Bricolage Grotesque, sans-serif">{e(headline)}</text>
<text x="64" y="340" font-size="132" font-weight="800" fill="#ffffff" font-family="Bricolage Grotesque, sans-serif">₹{facts["gsdp_latest_lc"]}</text>
<text x="70" y="392" font-size="34" font-weight="500" fill="#e8ebfa" font-family="IBM Plex Sans, sans-serif">lakh crore, current prices</text>
<text x="70" y="452" font-size="26" fill="#f2b544" font-weight="600" font-family="IBM Plex Sans, sans-serif">Real growth {facts["growth_real_latest"]}% in {latest}</text>
<text x="660" y="280" font-size="20" fill="#b9c0e6" font-family="IBM Plex Sans, sans-serif">Top 5 by GSDP, {rank_year}</text>
{bars}
<text x="64" y="612" font-size="18" fill="#b9c0e6" font-family="IBM Plex Sans, sans-serif">Source: MoSPI (eSankhyiki), State GSDP, 2011-12 base · Visualised by IndiaInCharts · CC BY 4.0</text>
<text x="64" y="644" font-size="20" font-weight="600" fill="#ffffff" font-family="IBM Plex Mono, monospace">indiaincharts.com{URL_PATH}</text>
<text x="1136" y="644" font-size="22" font-weight="800" fill="#f2b544" text-anchor="end" font-family="Bricolage Grotesque, sans-serif">IndiaInCharts</text>
</svg>'''


# ---------- table + CSV ----------
table_rows = "".join(
    f"<tr><td>{y}</td><td>{indian(gsdp_cur[y])}</td><td>{indian(gsdp_con[y])}</td>"
    f"<td>{pct(growth_real[y]) if growth_real.get(y) is not None else '—'}</td>"
    f"<td>{indian(pc_cur[y]) if pc_cur.get(y) else '—'}</td></tr>"
    for y in reversed(years))
csv_text = "year,gsdp_current_crore,gsdp_2011_12_prices_crore,real_growth_pct,per_capita_nsdp_current_rupees\n" + "".join(
    f"{y},{gsdp_cur[y]:.0f},{gsdp_con[y]:.0f},{growth_real.get(y) if growth_real.get(y) is not None else ''},{pc_cur.get(y) or ''}\n"
    for y in years)
credit = (f"Source: Ministry of Statistics and Programme Implementation (MoSPI), eSankhyiki: National Accounts Statistics, "
          f"State GSDP (2011-12 base), fetched {FETCHED}. Visualised by IndiaInCharts. Not endorsed by MoSPI.")
embed = (f'<iframe src="https://indiaincharts.com/embed{URL_PATH}" width="100%" height="420" '
         f'style="border:0" loading="lazy" title="GDP of {STATE}"></iframe>\n'
         f'<p>Chart: <a href="https://indiaincharts.com{URL_PATH}">IndiaInCharts</a> (CC BY 4.0). Data: MoSPI.</p>')

jsonld = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "Dataset", "name": f"GDP (GSDP) of {STATE}, {first} to {latest}",
         "description": f"Gross State Domestic Product of {STATE} at current and 2011-12 prices, real growth and per-capita NSDP.",
         "creator": {"@type": "Organization", "name": "Ministry of Statistics and Programme Implementation (MoSPI)"},
         "temporalCoverage": f"{first[:4]}/{int(latest[:4]) + 1}",
         "spatialCoverage": {"@type": "Place", "name": f"{STATE}, India"},
         "distribution": {"@type": "DataDownload", "encodingFormat": "text/csv",
                          "contentUrl": f"https://indiaincharts.com{URL_PATH}data.csv"},
         "isAccessibleForFree": True},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://indiaincharts.com/"},
            {"@type": "ListItem", "position": 2, "name": "Economy", "item": "https://indiaincharts.com/economy/"},
            {"@type": "ListItem", "position": 3, "name": "State GDP", "item": "https://indiaincharts.com/economy/gsdp/ranking/"},
            {"@type": "ListItem", "position": 4, "name": STATE, "item": f"https://indiaincharts.com{URL_PATH}"}]},
    ],
}

others = [s for _, s in gsdp_rank if s != STATE][:4]
related_q = [
    (f"What is the per capita income of {STATE}?", f"₹{facts['pc_latest']} (per-capita NSDP, {latest}, current prices).", f"/economy/per-capita-income/{SLUG}/"),
    ("Which is the richest state in India?", f"By total GSDP in {rank_year}: {gsdp_rank[0][1]}. By income per person: {pc_rank[0][1]}.", "/economy/gsdp/ranking/"),
    (f"How fast is {STATE}'s economy growing?", f"{facts['growth_real_latest']}% in real terms in {latest}.", f"#trend"),
    (f"Why are {STATE}'s figures on the 2011-12 base?", "MoSPI has moved national GDP to a 2022-23 base, but state series on the new base are not yet published.", "#method"),
]

# ---------- page ----------
page = f'''<title>GDP of {e(STATE)}</title>
<meta name="description" content="{e(STATE)} GDP (GSDP) is ₹{facts["gsdp_latest_lc"]} lakh crore in {latest}. Trend since {first}, real growth, rank among states and per-capita income, from MoSPI data.">
<link rel="canonical" href="https://indiaincharts.com{URL_PATH}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>
/* Layout: one mobile-first reading column; charts and tables full column width; ad slots reserved at fixed height. */
:root {{
  --bg:#f5f6f9; --surface:#ffffff; --ink:#121624; --ink-2:#4a5168; --muted:#6c7389; --line:#dde1ea;
  --accent:#3346c8; --accent-ink:#ffffff; --accent-soft:#e8ebfb; --highlight:#c27a0e;
  --s1:#3346c8; --s2:#c27a0e; --bar:#c5cad8; --note:#8a5a00; --note-bg:#fff4dc;
  --f-display:"Bricolage Grotesque", "Arial Narrow", system-ui, sans-serif;
  --f-body:"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-data:"IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
  --step-0:1rem; --step-1:1.2rem; --step-2:1.5rem; --step-3:2.1rem; --step-4:clamp(2.2rem, 6vw, 3.1rem);
  --r:6px;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#0f1117; --surface:#161922; --ink:#eef0f6; --ink-2:#b6bccd; --muted:#9097ab; --line:#2a2f3c;
  --accent:#8e9bff; --accent-ink:#0f1117; --accent-soft:#1d2242; --highlight:#e0a13a;
  --s1:#6f7ff0; --s2:#b97c1c; --bar:#3a4052; --note:#f2c46b; --note-bg:#2a2210; color-scheme:dark; }} }}
:root[data-theme="dark"] {{
  --bg:#0f1117; --surface:#161922; --ink:#eef0f6; --ink-2:#b6bccd; --muted:#9097ab; --line:#2a2f3c;
  --accent:#8e9bff; --accent-ink:#0f1117; --accent-soft:#1d2242; --highlight:#e0a13a;
  --s1:#6f7ff0; --s2:#b97c1c; --bar:#3a4052; --note:#f2c46b; --note-bg:#2a2210; color-scheme:dark; }}
* {{ box-sizing:border-box }}
body {{ background:var(--bg); color:var(--ink); font:400 var(--step-0)/1.6 var(--f-body); margin:0; }}
a {{ color:var(--accent); text-underline-offset:3px }}
a:focus-visible, button:focus-visible, th:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; border-radius:3px }}
.wrap {{ max-width:780px; margin-inline:auto; padding-inline:16px }}
.proto {{ background:var(--note-bg); color:var(--note); font:500 .85rem/1.4 var(--f-body); padding-block:8px }}
.proto .wrap {{ display:flex; gap:12px; justify-content:space-between; align-items:center; flex-wrap:wrap }}
.proto button {{ font:inherit; color:inherit; background:transparent; border:1px solid currentColor; border-radius:999px; padding:2px 10px; cursor:pointer }}
header.site {{ border-bottom:1px solid var(--line); background:var(--surface) }}
header.site .wrap {{ display:flex; align-items:center; gap:20px; padding-block:12px; flex-wrap:wrap }}
.brand {{ font:800 1.25rem/1 var(--f-display); color:var(--ink); text-decoration:none; letter-spacing:-.01em }}
.brand span {{ color:var(--accent) }}
nav.top {{ display:flex; gap:16px; flex-wrap:wrap; font-size:.9rem }}
nav.top a {{ color:var(--ink-2); text-decoration:none }}
nav.top a[aria-current] {{ color:var(--ink); font-weight:600 }}
main {{ display:grid; gap:36px; padding-block:24px 48px }}
.crumbs {{ font-size:.85rem; color:var(--muted); display:flex; gap:6px; flex-wrap:wrap }}
.crumbs a {{ color:var(--muted) }}
h1 {{ font:800 var(--step-4)/1.05 var(--f-display); letter-spacing:-.02em; margin:.3rem 0 .6rem; text-wrap:balance }}
h2 {{ font:700 var(--step-2)/1.2 var(--f-display); margin:0 0 .4rem; text-wrap:balance }}
.answer {{ font-size:var(--step-1); line-height:1.5; max-width:65ch; margin:0 }}
.updated {{ color:var(--muted); font-size:.85rem; margin-top:.6rem; font-family:var(--f-data) }}
section {{ display:grid; gap:14px; min-width:0 }}
.tag {{ display:none; font:500 .72rem/1 var(--f-data); color:var(--note); background:var(--note-bg); padding:4px 8px; border-radius:999px; width:max-content; letter-spacing:.02em }}
body.notes .tag {{ display:inline-block }}
.cards {{ display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:12px }}
@media (min-width:720px) {{ .cards {{ grid-template-columns:repeat(4, minmax(0,1fr)) }} }}
.card {{ background:var(--surface); border:1px solid var(--line); border-radius:var(--r); padding:14px; display:grid; gap:4px; align-content:start }}
.card .k {{ font-size:.78rem; color:var(--muted); text-transform:uppercase; letter-spacing:.06em }}
.card .v {{ font:800 1.7rem/1.1 var(--f-display); font-variant-numeric:tabular-nums }}
.card .s {{ font-size:.82rem; color:var(--ink-2) }}
.figure {{ background:var(--surface); border:1px solid var(--line); border-radius:var(--r); padding:16px; display:grid; gap:12px; min-width:0 }}
.figure p.cap {{ margin:0; color:var(--ink-2); font-size:.9rem }}
.btns {{ display:flex; gap:8px; flex-wrap:wrap }}
.btn {{ font:600 .85rem/1 var(--f-body); padding:9px 14px; border-radius:999px; border:1px solid var(--line); background:var(--surface); color:var(--ink); cursor:pointer }}
.btn.primary {{ background:var(--accent); color:var(--accent-ink); border-color:var(--accent) }}
.info {{ width:100%; height:auto; border-radius:4px; display:block }}
.legend {{ display:flex; gap:18px; flex-wrap:wrap; font-size:.85rem; color:var(--ink-2) }}
.legend i {{ display:inline-block; width:18px; height:3px; border-radius:2px; vertical-align:middle; margin-right:6px }}
.chartbox {{ position:relative }}
.chart {{ width:100%; height:auto; display:block; overflow:visible }}
.chart .grid {{ stroke:var(--line); stroke-width:1 }}
.chart .axis {{ stroke:var(--muted); stroke-width:1 }}
.chart .tick, .chart .unit {{ fill:var(--muted); font:400 12px var(--f-data) }}
.chart .ln {{ fill:none; stroke-width:2.5; stroke-linejoin:round; stroke-linecap:round }}
.chart .ln.s1 {{ stroke:var(--s1) }} .chart .ln.s2 {{ stroke:var(--s2) }}
.chart .s1f {{ fill:var(--s1) }} .chart .s2f {{ fill:var(--s2) }}
.chart .dot {{ stroke:var(--surface); stroke-width:2 }}
.chart .lbl {{ font:600 12px var(--f-body); fill:var(--ink-2) }}
.chart .xhair {{ stroke:var(--muted); stroke-dasharray:3 3 }}
.chart .hit {{ fill:transparent; cursor:crosshair }}
.bars .blabel {{ fill:var(--ink-2); font:400 13px var(--f-body) }}
.bars .bval {{ fill:var(--ink-2); font:500 12px var(--f-data) }}
.bars rect {{ fill:var(--bar) }}
.bars .mine rect {{ fill:var(--s1) }} .bars .mine .blabel {{ fill:var(--ink); font-weight:600 }}
.tip {{ position:absolute; pointer-events:none; background:var(--ink); color:var(--bg); font:400 .8rem/1.4 var(--f-body); padding:8px 10px; border-radius:4px; white-space:nowrap; transform:translate(-50%, -110%) }}
.tip b {{ font-family:var(--f-data); font-weight:500 }}
.embed {{ font:400 .78rem/1.5 var(--f-data); background:var(--bg); border:1px solid var(--line); border-radius:4px; padding:10px; overflow-x:auto; white-space:pre-wrap; word-break:break-all; margin:0 }}
.tablewrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:var(--r); background:var(--surface) }}
table {{ border-collapse:collapse; width:100%; font-size:.9rem; font-variant-numeric:tabular-nums }}
th, td {{ padding:9px 12px; text-align:right; border-bottom:1px solid var(--line); white-space:nowrap }}
th:first-child, td:first-child {{ text-align:left }}
th {{ font-weight:600; color:var(--ink-2); font-size:.8rem; cursor:pointer; user-select:none; background:var(--bg) }}
th[aria-sort="ascending"]::after {{ content:" ↑" }} th[aria-sort="descending"]::after {{ content:" ↓" }}
tbody tr:last-child td {{ border-bottom:0 }}
.summary p {{ max-width:65ch; margin:0 0 .9rem }}
.ad {{ height:250px; border:1px dashed var(--line); border-radius:var(--r); display:grid; place-items:center; color:var(--muted); font:500 .75rem var(--f-data); letter-spacing:.08em; text-transform:uppercase }}
dl.method {{ display:grid; grid-template-columns:minmax(0,9rem) minmax(0,1fr); gap:8px 16px; margin:0; font-size:.92rem }}
dl.method dt {{ color:var(--muted) }} dl.method dd {{ margin:0 }}
.credit {{ font-size:.85rem; color:var(--ink-2); border-left:3px solid var(--line); padding-left:12px; margin:0 }}
.faq {{ display:grid; gap:10px }}
.faq details {{ background:var(--surface); border:1px solid var(--line); border-radius:var(--r); padding:12px 14px }}
.faq summary {{ font-weight:600; cursor:pointer }}
.faq p {{ margin:.5rem 0 0; color:var(--ink-2) }}
.siblings {{ display:flex; flex-wrap:wrap; gap:8px }}
.siblings a {{ border:1px solid var(--line); border-radius:999px; padding:6px 12px; text-decoration:none; font-size:.88rem; background:var(--surface) }}
footer {{ border-top:1px solid var(--line); color:var(--muted); font-size:.82rem; padding-block:24px }}
footer .wrap {{ display:grid; gap:6px }}
@media (prefers-reduced-motion: no-preference) {{ .ln {{ transition:stroke-width .15s }} }}
</style>

<div class="proto" role="note"><div class="wrap"><span>Prototype for review: layout of a single-metric page. All numbers are real MoSPI data (fetched {FETCHED}). Buttons are placeholders.</span><button type="button" id="notes-toggle" aria-pressed="true">Hide section notes</button></div></div>

<header class="site"><div class="wrap">
  <a class="brand" href="#">India<span>In</span>Charts</a>
  <nav class="top" aria-label="Topics"><a href="#" aria-current="page">Economy</a><a href="#">Jobs</a><a href="#">Prices</a><a href="#">Education</a><a href="#">Energy</a><a href="#">Trade</a></nav>
</div></header>

<main class="wrap" id="top">
  <section aria-labelledby="h1">
    <span class="tag">1 · Question as H1 + direct answer (for Google &amp; AI citations)</span>
    <nav class="crumbs" aria-label="Breadcrumb"><a href="#">Home</a>›<a href="#">Economy</a>›<a href="#">State GDP</a>›<span>{e(STATE)}</span></nav>
    <h1 id="h1">GDP of {e(STATE)}</h1>
    <p class="answer">{direct_answer}</p>
    <p class="updated">Data: {latest} · Updated {BUILT.strftime("%-d %b %Y")} · Source: MoSPI</p>
  </section>

  <section aria-label="Key figures">
    <span class="tag">2 · Metric cards</span>
    <div class="cards">
      <div class="card"><span class="k">GSDP {latest}</span><span class="v">₹{lakh_crore(gsdp_cur[latest], 1)}</span><span class="s">lakh crore, current prices</span></div>
      <div class="card"><span class="k">Real growth</span><span class="v">{pct(growth_real[latest])}</span><span class="s">in {latest}; {pct(growth_real[prev])} in {prev}</span></div>
      <div class="card"><span class="k">Rank by GSDP</span><span class="v">{ordinal(my_rank)}</span><span class="s">of {n_rank} states &amp; UTs, {rank_year}</span></div>
      <div class="card"><span class="k">Per-capita income</span><span class="v">₹{pc_cur[latest] / 1e5:.2f}L</span><span class="s">{ordinal(my_pc_rank)} of {n_rank}, {rank_year} rank</span></div>
    </div>
  </section>

  <section aria-labelledby="h-info">
    <span class="tag">3 · Shareable infographic (1200×675 shown; 1080×1350 also generated)</span>
    <h2 id="h-info" class="visually-hidden" hidden>Infographic</h2>
    <div class="figure">
      {infographic()}
      <div class="btns"><button class="btn primary" type="button">Download image</button><button class="btn" type="button">Download portrait (1080×1350)</button><button class="btn" type="button">Share on LinkedIn</button><button class="btn" type="button">Share on X</button></div>
    </div>
  </section>

  <div class="ad" aria-hidden="true">Advertisement · reserved space</div>

  <section aria-labelledby="h-trend" id="trend">
    <span class="tag">4 · Main chart (SVG built at build time; hover is a tiny script)</span>
    <h2 id="h-trend">{e(STATE)}'s GDP since {first}</h2>
    <div class="figure">
      <div class="legend"><span><i style="background:var(--s1)"></i>At current prices</span><span><i style="background:var(--s2)"></i>At 2011-12 prices (real)</span></div>
      <div class="chartbox" id="trend-box">{line_chart()}<div class="tip" id="tip" hidden></div></div>
      <p class="cap">The gap between the two lines is inflation. Real growth is measured on the 2011-12 prices line.</p>
      <div class="btns"><button class="btn" type="button" id="embed-btn" aria-expanded="false" aria-controls="embed-code">Embed this chart</button></div>
      <pre class="embed" id="embed-code" hidden>{e(embed)}</pre>
    </div>
  </section>

  <section aria-labelledby="h-rank">
    <span class="tag">4b · Context chart: where the state ranks</span>
    <h2 id="h-rank">Largest state economies, {rank_year}</h2>
    <div class="figure">{bar_chart()}<p class="cap">GSDP at current prices, ₹ lakh crore. <a href="#">See all {n_rank} states and UTs</a>.</p></div>
  </section>

  <section aria-labelledby="h-table">
    <span class="tag">5 · Data table (sortable) + CSV</span>
    <h2 id="h-table">{e(STATE)} GSDP by year</h2>
    <div class="tablewrap"><table id="data-table">
      <caption class="visually-hidden" hidden>{e(STATE)} GSDP, ₹ crore</caption>
      <thead><tr><th scope="col" tabindex="0">Year</th><th scope="col" tabindex="0">GSDP, current (₹ cr)</th><th scope="col" tabindex="0">GSDP, 2011-12 prices (₹ cr)</th><th scope="col" tabindex="0">Real growth</th><th scope="col" tabindex="0">Per-capita NSDP (₹)</th></tr></thead>
      <tbody>{table_rows}</tbody></table></div>
    <div class="btns"><button class="btn" type="button" id="csv-btn">Copy CSV</button><button class="btn" type="button">Download CSV</button></div>
  </section>

  <section aria-labelledby="h-sum" class="summary">
    <span class="tag">6 · Summary: every number is computed from the data and checked by a test</span>
    <h2 id="h-sum">What the numbers show</h2>
    {"".join(f"<p>{p}</p>" for p in summary_paras)}
  </section>

  <div class="ad" aria-hidden="true">Advertisement · reserved space</div>

  <section aria-labelledby="h-method" id="method">
    <span class="tag">7 · Source &amp; method</span>
    <h2 id="h-method">Source and method</h2>
    <dl class="method">
      <dt>Dataset</dt><dd>National Accounts Statistics: State GSDP, NSDP and per-capita NSDP (MoSPI, eSankhyiki)</dd>
      <dt>Base year</dt><dd>2011-12. MoSPI has moved national GDP to a 2022-23 base; state series on the new base are not yet published. Figures here are not comparable with the new national series.</dd>
      <dt>Prices</dt><dd>“Current prices” are in each year's rupees. “2011-12 prices” remove inflation and are used for real growth.</dd>
      <dt>Coverage</dt><dd>{n_rank} states and UTs report. Ranks use {rank_year}, the latest year with all of them; {latest} has {latest_reporting} so far.</dd>
      <dt>Revisions</dt><dd>Recent years are often revised in later releases. We keep every release and log changes on the corrections page.</dd>
      <dt>Next update</dt><dd>When MoSPI publishes revised state estimates.</dd>
    </dl>
    <p class="credit">{e(credit)} Data licence: see <a href="#">our sources page</a>. Charts and text: CC BY 4.0.</p>
  </section>

  <section aria-labelledby="h-rel">
    <span class="tag">8 · Related questions + internal links</span>
    <h2 id="h-rel">Related questions</h2>
    <div class="faq">{"".join(f'<details><summary>{e(q)}</summary><p>{e(a)} <a href="{h}">More</a></p></details>' for q, a, h in related_q)}</div>
    <div class="siblings">{"".join(f'<a href="#">GDP of {e(s)}</a>' for s in others)}<a href="#">All states ranked</a><a href="#">{e(STATE)} vs Gujarat</a></div>
  </section>
</main>

<footer><div class="wrap">
  <span><strong>IndiaInCharts</strong> turns published government statistics into clear answers. Not affiliated with or endorsed by any government body.</span>
  <span>Charts, infographics and text: CC BY 4.0. Underlying data keeps its original licence. <a href="#">Corrections</a> · <a href="#">Methodology</a> · <a href="#">About</a></span>
</div></footer>

<script>
(function () {{
  var body = document.body; body.classList.add("notes");
  var t = document.getElementById("notes-toggle");
  try {{ if (localStorage.getItem("iic-notes") === "off") {{ body.classList.remove("notes"); t.setAttribute("aria-pressed","false"); t.textContent = "Show section notes"; }} }} catch (e) {{}}
  t.addEventListener("click", function () {{
    var on = body.classList.toggle("notes");
    t.setAttribute("aria-pressed", on); t.textContent = on ? "Hide section notes" : "Show section notes";
    try {{ localStorage.setItem("iic-notes", on ? "on" : "off"); }} catch (e) {{}}
  }});

  // Line chart hover: crosshair + tooltip.
  var svg = document.getElementById("trend-svg"), tip = document.getElementById("tip"), box = document.getElementById("trend-box");
  var xh = document.getElementById("xhair"), hc = document.getElementById("hcur"), hk = document.getElementById("hcon");
  function show(r) {{
    var s = svg.getBoundingClientRect().width / {720};
    xh.setAttribute("x1", r.dataset.x); xh.setAttribute("x2", r.dataset.x); xh.setAttribute("visibility", "visible");
    hc.setAttribute("cx", r.dataset.x); hc.setAttribute("cy", r.dataset.ycur); hc.setAttribute("visibility", "visible");
    hk.setAttribute("cx", r.dataset.x); hk.setAttribute("cy", r.dataset.ycon); hk.setAttribute("visibility", "visible");
    tip.innerHTML = "<strong>" + r.dataset.year + "</strong><br>Current: ₹<b>" + r.dataset.cur + "</b> cr<br>2011-12 prices: ₹<b>" + r.dataset.con + "</b> cr<br>Real growth: <b>" + r.dataset.g + "</b>";
    var x = Math.min(Math.max(r.dataset.x * s, 90), box.clientWidth - 90);
    tip.style.left = x + "px"; tip.style.top = (r.dataset.ycur * s) + "px"; tip.hidden = false;
  }}
  function hide() {{ tip.hidden = true; [xh, hc, hk].forEach(function (n) {{ n.setAttribute("visibility", "hidden"); }}); }}
  svg.querySelectorAll(".hit").forEach(function (r) {{
    r.addEventListener("mouseenter", function () {{ show(r); }});
    r.addEventListener("touchstart", function () {{ show(r); }}, {{ passive: true }});
  }});
  svg.addEventListener("mouseleave", hide);

  // Embed toggle + copy buttons.
  var eb = document.getElementById("embed-btn"), ec = document.getElementById("embed-code");
  eb.addEventListener("click", function () {{ ec.hidden = !ec.hidden; eb.setAttribute("aria-expanded", !ec.hidden); }});
  var csv = {json.dumps(csv_text)};
  var cb = document.getElementById("csv-btn");
  cb.addEventListener("click", function () {{
    var done = function () {{ cb.textContent = "Copied"; setTimeout(function () {{ cb.textContent = "Copy CSV"; }}, 1500); }};
    if (navigator.clipboard) navigator.clipboard.writeText(csv).then(done, function () {{ cb.textContent = "Copy not allowed here"; }});
  }});

  // Sortable table.
  var table = document.getElementById("data-table");
  table.querySelectorAll("th").forEach(function (th, col) {{
    function sort() {{
      var dir = th.getAttribute("aria-sort") === "descending" ? "ascending" : "descending";
      table.querySelectorAll("th").forEach(function (h) {{ h.removeAttribute("aria-sort"); }});
      th.setAttribute("aria-sort", dir);
      var rows = Array.prototype.slice.call(table.tBodies[0].rows);
      var key = function (tr) {{ var t = tr.cells[col].textContent.replace(/[,%₹+]/g, "").replace("−", "-"); var n = parseFloat(t); return isNaN(n) ? t : n; }};
      rows.sort(function (a, b) {{ var x = key(a), y = key(b); return (x > y ? 1 : x < y ? -1 : 0) * (dir === "ascending" ? 1 : -1); }});
      rows.forEach(function (r) {{ table.tBodies[0].appendChild(r); }});
    }}
    th.addEventListener("click", sort);
    th.addEventListener("keydown", function (ev) {{ if (ev.key === "Enter" || ev.key === " ") {{ ev.preventDefault(); sort(); }} }});
  }});
}})();
</script>
'''

out = os.path.join(ROOT, "site/prototype", f"gdp-of-{SLUG}.html")
open(out, "w").write(page)

# Number-match check (CLAUDE.md §6.3): every number in the summary must exist in the data-derived facts.
summary_text = re.sub(r"<[^>]+>", "", " ".join(summary_paras))
allowed = set(facts.values()) | {lakh_crore(gsdp_cur[latest])} | set(years) | {rank_year, prev, first, latest, str(n_rank)} \
    | {pct(growth_real[y]) for y in contractions}
no_years = re.sub(r"\b\d{4}-\d{2}\b", " ", summary_text)
nums = re.findall(r"[−-]?\d[\d,]*(?:\.\d+)?(?:%|st|nd|rd|th)?", no_years)
bad = [n for n in nums if n.rstrip(".,").strip("%") not in {a.strip("%") for a in allowed}]
print(f"wrote {out}  ({len(page) // 1024} KB)")
print("number-match:", "PASS" if not bad else f"FAIL {bad}")
print("summary:", summary_text)
for k, v in facts.items():
    print(f"  {k}: {v}")
