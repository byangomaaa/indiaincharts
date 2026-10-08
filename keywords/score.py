"""Preliminary keyword scoring (CLAUDE.md §8, step 5) from a Keyword Planner "Keyword Stats" export.

priority = demand x winnability x data_quality   (winnability is a page-type proxy until SERPs are checked)

Usage: python keywords/score.py 2026-10
Reads  keywords/<run>/candidates-all.csv and keywords/<run>/planner-export/*.csv
Writes keywords/<run>/scored.csv
"""
import csv
import glob
import io
import math
import os
import sys

RUN = sys.argv[1]
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), RUN)


def read_planner(path):
    raw = open(path, "rb").read()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig")
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("Keyword\t") or l.startswith("Keyword,"))
    delim = "\t" if "\t" in lines[start] else ","
    out = {}
    for r in csv.DictReader(io.StringIO("\n".join(lines[start:])), delimiter=delim):
        k = (r.get("Keyword") or "").strip().lower()
        v = (r.get("Avg. monthly searches") or "").strip().replace(",", "")
        if k:
            out[k] = float(v) if v else 0.0
    return out


volume = {}
for p in glob.glob(os.path.join(BASE, "planner-export", "*.csv")):
    volume.update(read_planner(p))

# Winnability proxy by page type (CLAUDE.md §8: boost rankings/comparisons/time series/tools;
# penalise headline national numbers Google answers directly or news owns).
WIN = {"ranking": 1.5, "comparison": 1.5, "trend": 1.3, "metric": 1.0, "national/ranking": 0.8,
       "national/ranking/release": 0.6, "national/release/tool": 0.8, "national": 0.6,
       "national/release": 0.6}
DATA = {"ready": 1.0, "licence_check": 0.6}

rows = []
for c in csv.DictReader(open(os.path.join(BASE, "candidates-all.csv"))):
    v = volume.get(c["keyword"])
    win = WIN.get(c["page_type"], 1.0)
    if "price today" in c["keyword"]:
        win *= 0.4  # needs daily data; SERP owned by news/price sites
    if c["keyword"] in {"tool"} or "calculator" in c["keyword"]:
        win *= 1.5
    demand = math.log10(v) if v and v > 0 else 0.0  # buckets are 10x apart -> log scale
    pri = round(demand * win * DATA.get(c["data_status"], 0.5), 3)
    rows.append({**c, "avg_monthly_searches": "" if v is None else int(v), "winnability_proxy": win,
                 "priority": pri})

rows.sort(key=lambda r: -r["priority"])
with open(os.path.join(BASE, "scored.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"scored {len(rows)} keywords; {sum(1 for r in rows if r['priority'] > 0)} with demand")
