#!/usr/bin/env python3
"""Stage 1: three web searches per app (docs/auth, MCP, access/pricing) -> search/{n}_{kind}.json.

Needs a public web search API. Default provider: Brave Search API.
    export BRAVE_API_KEY=...        # get a key at https://brave.com/search/api/
The script fails loudly (non-zero exit, clear message) when the key is missing
or a search call fails, so a partial or empty run is obvious, never silent.
To use another provider (Exa, Tavily, SerpAPI, ...), replace search() below; it
must return a list of {"title","url","highlights"} dicts.
"""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
import requests

BRAVE_KEY = os.environ.get("BRAVE_API_KEY")
if not BRAVE_KEY:
    sys.exit("ERROR: BRAVE_API_KEY is not set. Get a key at https://brave.com/search/api/ "
             "and export it, or swap search() in search.py for another search provider.")

apps = json.load(open("data/apps.json")); os.makedirs("search", exist_ok=True)
Q = {"docs": "{a} API developer documentation authentication",
     "mcp": "{a} MCP server official",
     "access": "{a} API access get credentials free developer account paid plan required approval"}

def search(q):
    for attempt in range(3):
        r = requests.get("https://api.search.brave.com/res/v1/web/search",
                         headers={"Accept": "application/json", "X-Subscription-Token": BRAVE_KEY},
                         params={"q": q, "count": 8}, timeout=30)
        if r.status_code == 429:            # rate limited: back off and retry
            time.sleep(2 * (attempt + 1)); continue
        r.raise_for_status()
        return [{"title": w.get("title", ""), "url": w.get("url", ""),
                 "highlights": [w.get("description", "")]}
                for w in r.json().get("web", {}).get("results", [])]
    raise RuntimeError(f"search failed after retries (HTTP 429): {q}")

def run(a):
    for k, t in Q.items():
        fn = f"search/{a['n']}_{k}.json"
        if not os.path.exists(fn):
            json.dump(search(t.format(a=a["app"])), open(fn, "w"))

if __name__ == "__main__":
    lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 100)
    todo = [a for a in apps if lo <= a["n"] <= hi]
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(run, todo))             # any search error raises here and stops the run
    print("search files:", len(os.listdir("search")))
