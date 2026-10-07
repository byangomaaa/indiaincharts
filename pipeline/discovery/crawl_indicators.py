"""MoSPI discovery tooling (Phase 0). Not part of the production pipeline.

Usage: python crawl_indicators.py <work_dir>
Run in order: crawl_indicators.py -> crawl_metadata.py -> summarise.py, all with the same work_dir
(e.g. data/raw/discovery/mospi-mcp/<yyyy-mm-dd>/, which is git-ignored).
"""
import json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mospi_mcp_client import init, tool
os.makedirs(sys.argv[1], exist_ok=True); os.chdir(sys.argv[1])
init()
os.makedirs("ind", exist_ok=True)
json.dump(tool("list_datasets", {}), open("datasets.json", "w"), indent=1, ensure_ascii=False)
ds=list(json.load(open("datasets.json"))["datasets"].keys())
for d in ds:
    r=tool("get_indicators",{"dataset":d})
    json.dump(r,open(f"ind/{d}.json","w"),indent=1,ensure_ascii=False)
    s=json.dumps(r,ensure_ascii=False)
    print(d, len(s), s[:300].replace("\n"," "))
    time.sleep(0.5)
