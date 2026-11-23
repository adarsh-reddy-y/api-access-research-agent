#!/usr/bin/env python3
"""Stage 2: fetch candidate docs pages for each app and extract auth/access/API/MCP signal snippets.
Input : data/apps.json, search/<n>_docs.json, search/<n>_mcp.json  (stage 1 search results)
Output: evidence/<n>.json  (pages fetched + keyword-in-context snippets per signal)"""
import json, re, sys, os, time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

SIGNALS = {
 "oauth2": r"oauth ?2|oauth 2\.0|authorization code|client credentials|openid",
 "api_key": r"api[ _-]?key|x-api-key|api token|personal access token|bearer token|access token|secret key|private app",
 "basic": r"basic auth|http basic|username and password",
 "graphql": r"graphql",
 "rest": r"\brest(ful)?\b|openapi|swagger|endpoint",
 "mcp": r"\bmcp\b|model context protocol",
 "gated": r"contact (our )?sales|contact us|partner program|become a partner|apply for access|request access|app review|approval|waitlist|enterprise plan|business plan|paid plan|upgrade|premium plan|whitelist|allowlist|not publicly available|invite[- ]only|private beta",
 "self_serve": r"free (account|plan|tier|trial)|sign up|create (an )?(account|app|api key)|developer account|generate (an )?(api )?(key|token)|self[- ]serve|sandbox",
}
UA = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}

def pick_urls(n, hint, k=4):
    urls = []
    for kind in ("docs", "mcp"):
        try: res = json.load(open(f"search/{n}_{kind}.json"))
        except Exception: res = []
        for r in res:
            u = r.get("url", "")
            if kind == "docs":
                score = 0
                if re.search(r"auth|oauth|api|developer|docs|reference", u, re.I): score += 2
                if re.search(r"auth|oauth|token|key|getting-started|quickstart|overview", u, re.I): score += 2
                if re.search(r"reddit|medium\.com|youtube|stackoverflow|g2\.com|capterra|linkedin\.com/pulse|github\.com/[^/]+/[^/]+/(issues|pull)", u, re.I): score -= 5
                urls.append((score, u))
    urls.sort(key=lambda x: -x[0])
    seen, out = set(), []
    for s, u in urls:
        if u not in seen and s > 0:
            seen.add(u); out.append(u)
        if len(out) >= k: break
    return out

def clean(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "nav", "footer", "svg"]): t.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" "))

def kwic(text, pat, width=140, maxn=3):
    out = []
    for m in re.finditer(pat, text, re.I):
        s = max(0, m.start() - width); e = min(len(text), m.end() + width)
        out.append(text[s:e])
        if len(out) >= maxn: break
    return out

def fetch(u):
    try:
        r = requests.get(u, headers=UA, timeout=20)
        ct = r.headers.get("content-type", "")
        if r.status_code != 200 or "html" not in ct and "text" not in ct and "json" not in ct:
            return {"url": u, "status": r.status_code, "text": ""}
        return {"url": u, "status": r.status_code, "text": clean(r.text)[:200000]}
    except Exception as e:
        return {"url": u, "status": f"err:{type(e).__name__}", "text": ""}

def do(app):
    n = app["n"]; fn = f"evidence/{n}.json"
    if os.path.exists(fn): return
    urls = pick_urls(n, app["hint"])
    pages = [fetch(u) for u in urls]
    # fold in search highlights (already text from the docs pages) as additional evidence
    hl = []
    for kind in ("docs", "mcp", "access"):
        try: res = json.load(open(f"search/{n}_{kind}.json"))
        except Exception: res = []
        for r in res:
            hl.append({"kind": kind, "url": r.get("url"), "title": r.get("title"), "text": " ".join(r.get("highlights", []))[:4000]})
    sig = {}
    for name, pat in SIGNALS.items():
        hits = []
        for p in pages:
            for s in kwic(p["text"], pat, maxn=2): hits.append({"url": p["url"], "ctx": s})
        sig[name] = {"count": sum(len(re.findall(pat, p["text"], re.I)) for p in pages), "hits": hits[:4]}
    json.dump({"n": n, "app": app["app"], "fetched": [{"url": p["url"], "status": p["status"], "chars": len(p["text"])} for p in pages],
               "signals": sig, "search_highlights": hl}, open(fn, "w"), indent=1)

if __name__ == "__main__":
    apps = json.load(open("data/apps.json"))
    with ThreadPoolExecutor(8) as ex: list(ex.map(do, apps))
    print("evidence files:", len(os.listdir("evidence")))
