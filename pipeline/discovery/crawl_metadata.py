"""MoSPI discovery tooling (Phase 0). Not part of the production pipeline.

Usage: python crawl_metadata.py <work_dir>
Run in order: crawl_indicators.py -> crawl_metadata.py -> summarise.py, all with the same work_dir
(e.g. data/raw/discovery/mospi-mcp/<yyyy-mm-dd>/, which is git-ignored).
"""
import json, sys, time, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mospi_mcp_client import init, tool
os.makedirs(sys.argv[1], exist_ok=True); os.chdir(sys.argv[1])
init()
os.makedirs("meta", exist_ok=True)
def walk(o, ctx=None, out=None):
    if out is None: out=[]
    if isinstance(o, dict):
        code = o.get("indicator_code", o.get("code"))
        name = o.get("description") or o.get("label") or o.get("name") or o.get("desc") or o.get("indicator_name")
        if isinstance(code,int) and name:
            rec={"code":code,"name":name.strip(),"ctx":ctx}
            for k in ("survey_code","module","viz"): 
                if k in o: rec[k]=o[k]
            out.append(rec)
        for k,v in o.items():
            walk(v, k if isinstance(k,str) and k.startswith("frequency_code_") else ctx, out)
    elif isinstance(o, list):
        for v in o: walk(v, ctx, out)
    return out
jobs=[]
special={"CPI":[{"base_year":b,"level":l} for b in ("2024","2012") for l in ("Group","Item")],
 "IIP":[{"base_year":b,"frequency":f} for b in ("2022-23","2011-12") for f in ("Annually","Monthly")],
 "WPI":[{"base_year":b} for b in ("2022-23","2011-12")],
 "ASI":[{"classification_year":"2008"}], "ISP":[{}]}
for d in json.load(open("datasets.json"))["datasets"]:
    if d in special:
        for p in special[d]: jobs.append((d,None,p,None))
        continue
    inds=walk(json.load(open(f"ind/{d}.json")))
    seen=set()
    for r in inds:
        p={"indicator_code":r["code"]}
        if r["ctx"]: p["frequency_code"]=int(re.search(r"frequency_code_(\d)",r["ctx"]).group(1))
        if "survey_code" in r: p["survey_code"]=r["survey_code"]
        if "module" in r: p["module"]=r["module"]
        if d=="NAS":
            for b in ("2022-23","2011-12"): jobs.append((d,r,dict(p,base_year=b),b))
            continue
        key=json.dumps(p,sort_keys=True)
        if key in seen: continue
        seen.add(key); jobs.append((d,r,p,None))
print("jobs",len(jobs),flush=True)
for i,(d,r,p,b) in enumerate(jobs):
    fn="meta/"+d+"__"+"_".join(f"{k}-{v}" for k,v in sorted(p.items())).replace("/","")+".json"
    if os.path.exists(fn): continue
    for attempt in range(3):
        try:
            res=tool("get_metadata",dict(dataset=d,**p)); break
        except Exception as e:
            res={"error":str(e)}; time.sleep(3)
    json.dump({"dataset":d,"indicator":r,"params":p,"result":res},open(fn,"w"),ensure_ascii=False)
    if i%25==0: print(i,d,flush=True)
    time.sleep(0.4)
print("done",flush=True)
