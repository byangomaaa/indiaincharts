import json, sys, urllib.request
URL="https://mcp.mospi.gov.in/"
H={"Content-Type":"application/json","Accept":"application/json, text/event-stream","User-Agent":"IndiaInCharts-discovery/0.1"}
def rpc(method, params, i=[1]):
    i[0]+=1
    body=json.dumps({"jsonrpc":"2.0","id":i[0],"method":method,"params":params}).encode()
    r=urllib.request.urlopen(urllib.request.Request(URL,body,H),timeout=120).read().decode()
    for line in r.splitlines():
        if line.startswith("data:"): return json.loads(line[5:])
    return json.loads(r)
def init():
    rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"iic","version":"0.1"}})
def tool(name, args):
    res=rpc("tools/call",{"name":name,"arguments":args})
    if "error" in res: return {"error":res["error"]}
    out=[]
    for c in res["result"].get("content",[]):
        if c.get("type")=="text":
            try: out.append(json.loads(c["text"]))
            except Exception: out.append(c["text"])
    return out[0] if len(out)==1 else out
if __name__=="__main__":
    init()
    if sys.argv[1]=="list":
        for t in rpc("tools/list",{})["result"]["tools"]:
            print("##",t["name"]); print(t.get("description","")[:1500]); print(json.dumps(t["inputSchema"].get("properties",{}))[:800]); print()
    else:
        print(json.dumps(tool(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv)>2 else {}), indent=1, ensure_ascii=False))
