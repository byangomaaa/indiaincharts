"""MoSPI discovery tooling (Phase 0). Not part of the production pipeline.

Usage: python summarise.py <work_dir>
Run in order: crawl_indicators.py -> crawl_metadata.py -> summarise.py, all with the same work_dir
(e.g. data/raw/discovery/mospi-mcp/<yyyy-mm-dd>/, which is git-ignored).
"""
import json, glob, os, re, sys
os.chdir(sys.argv[1])
def container(r):
    if not isinstance(r, dict): return {}
    if isinstance(r.get("filter_values"), dict):
        fv = r["filter_values"]; return fv.get("data", fv)
    return r.get("data", {})
def gather(c, acc):
    if isinstance(c, dict):
        for k, v in c.items():
            if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
                acc.setdefault(k, []).extend(v)
            elif isinstance(v, (dict, list)): gather(v, acc)
    elif isinstance(c, list):
        for x in c: gather(x, acc)
    return acc
def label(x):
    for k in ("label","description","name","state_name","district_name","year","id"):
        if k in x: return str(x[k]).strip()
    vals=[str(v) for k,v in x.items() if k not in ("viz",)]
    return vals[-1] if vals else ""
YR=re.compile(r"(19|20)\d\d")
def year_range(vals):
    ys=[]
    for v in vals:
        m=YR.findall(v); m=re.findall(r"(?:19|20)\d\d", v)
        if m: ys.append(int(m[0]))
    return (min(ys), max(ys), len(set(vals))) if ys else None
rows=[]
for f in sorted(glob.glob("meta/*.json")):
    d=json.load(open(f)); r=d["result"]; ind=d["indicator"] or {}
    acc=gather(container(r), {})
    dims={}; years=None; geo={}; small={}
    for k, lst in acc.items():
        vals=sorted({label(x) for x in lst})
        kl=k.lower()
        if "year" in kl and "type" not in kl and "classification" not in kl and "base" not in kl:
            yr=year_range(vals); 
            if yr and (years is None or yr[2]>years[2]): years=yr; years_key=k
            continue
        if "district" in kl: geo["district"]=len(vals); continue
        if "state" in kl or kl in ("region","geography"): geo["state"]=max(geo.get("state",0),len(vals)); continue
        if kl in ("month","quarter","quarterly","series","frequency","level") or kl.startswith(("month","quarter")): 
            dims[k]=len(vals); continue
        dims[k]=len(vals)
        if len(vals)<=8: small[k]=vals
    ok = isinstance(r, dict) and "error" not in r and (r.get("statusCode", True) is not False)
    rows.append(dict(dataset=d["dataset"], code=ind.get("code"), name=ind.get("name"), params=d["params"],
        ok=ok, empty=not acc, years=years, geo=geo, dims=dims, small=small, msg=(r.get("msg") or r.get("message")) if isinstance(r,dict) else str(r)[:80]))
json.dump(rows, open("summary.json","w"), indent=1, ensure_ascii=False)
from collections import Counter
print(len(rows), "rows;", Counter(r["dataset"] for r in rows))
print("empty:", sum(r["empty"] for r in rows), "not ok:", sum(not r["ok"] for r in rows))
print("with district:", Counter(r["dataset"] for r in rows if r["geo"].get("district")))
print("with state:", Counter(r["dataset"] for r in rows if r["geo"].get("state")))

# Flat CSV for docs/data-inventory-indicators.csv
import csv
with open("indicators.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["dataset", "indicator_code", "indicator_name", "query_params", "state_options",
                "first_year", "last_year", "n_periods", "breakdowns"])
    for r in rows:
        y = r["years"] or (None, None, None)
        w.writerow([r["dataset"], r["code"] if r["code"] is not None else "", r["name"] or "",
                    json.dumps(r["params"], sort_keys=True), r["geo"].get("state", 0),
                    y[0] or "", y[1] or "", y[2] or "",
                    "; ".join(f"{k}({n})" for k, n in sorted(r["dims"].items()))])
print("wrote indicators.csv")
