#!/usr/bin/env python3
"""Stage 1: three web searches per app (docs/auth, MCP, access/pricing) -> search/{n}_{kind}.json.
Needs a search command that prints JSON results. Here: the `tools web_search` CLI used in the original run.
Swap `search()` for any search API (Exa, Brave, Tavily, SerpAPI) returning [{title,url,highlights}]."""
import json,subprocess,sys,os
from concurrent.futures import ThreadPoolExecutor
apps=json.load(open("data/apps.json")); os.makedirs("search",exist_ok=True)
Q={"docs":"{a} API developer documentation authentication","mcp":"{a} MCP server official",
   "access":"{a} API access get credentials free developer account paid plan required approval"}
def search(q):
    r=subprocess.run(["tools","web_search","--query",q,"--limit","8","--json"],capture_output=True,text=True,timeout=60)
    return r.stdout or "[]"
def run(a):
    for k,t in Q.items():
        fn=f"search/{a['n']}_{k}.json"
        if not os.path.exists(fn): open(fn,"w").write(search(t.format(a=a["app"])))
lo,hi=(int(sys.argv[1]),int(sys.argv[2])) if len(sys.argv)>2 else (1,100)
with ThreadPoolExecutor(10) as ex: list(ex.map(run,[a for a in apps if lo<=a["n"]<=hi]))
