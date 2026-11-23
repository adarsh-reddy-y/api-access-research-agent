#!/usr/bin/env python3
"""Scores pass1 (rules), pass2 (LLM draft, pre-correction), pass3 (final) against audit truth.
Usage: python3 verify.py   (reads data/pass1.json, review/b*.txt, final/final.json, data/audit_truth.json)"""
import json,glob,re
T=json.load(open("data/audit_truth.json"))["truth"]
P1={r["n"]:r for r in json.load(open("data/pass1.json"))}
F=["n","app","category","auth","tier","access","api","mcp","verdict","blocker","urls","conf","flag"]
P2={}
for f in glob.glob("review/b0*.txt"):
    for l in open(f):
        if l.strip(): p=l.rstrip("\n").split("|"); P2[int(p[0])]=dict(zip(F,p))
P3={int(r["n"]):r for r in json.load(open("final/final.json"))}
def aset(t):
    t=t.strip()
    if re.match(r"(none|cli: none)",t,re.I): return "N"
    t=re.sub(r"\([^)]*\)","",t); t=re.sub(r"basic for[^;,]*","",t,flags=re.I)
    s=""
    if re.search("oauth",t,re.I): s+="O"
    if re.search(r"key|token",t,re.I): s+="K"
    return s or "?"
def mcpy(t): return "N" if re.match(r"(no |unclear)",t,re.I) or re.search(r"coming soon|not live",t,re.I) else "Y"  # 'coming soon'/'not live' is not a live MCP
def build(v): return "Y" if v.startswith("Ready") else "N"
def p1(n):
    r=P1[n]; a="".join(sorted({"OAuth2":"O","API key/token":"K"}.get(x,"") for x in r["auth"]))
    return {"auth":a,"bin":"S" if r["access"]=="self-serve" else "G","mcp":"Y" if r["mcp"]=="yes" else "N","build":"Y" if r["buildable"]=="yes" else "N"}
def p23(r): return {"auth":"".join(sorted(aset(r["auth"]))),"tier":r["tier"],"bin":"S" if r["tier"][0]=="S" else "G","mcp":mcpy(r["mcp"]),"build":build(r["verdict"])}
out={}
for name,get in [("pass1_rules",lambda n:p1(n)),("pass2_llm_draft",lambda n:p23(P2[n])),("pass3_final",lambda n:p23(P3[n]))]:
    hit=tot=0; miss=[]; dims={"auth":[0,0],"bin":[0,0],"mcp":[0,0],"build":[0,0],"tier":[0,0]}
    for n,(a,t,m,b) in T.items():
        n=int(n); g=get(n); truth={"auth":"".join(sorted(a)),"bin":"S" if t[0]=="S" else "G","mcp":m,"build":b,"tier":t}
        for d in dims:
            if d=="tier" and "tier" not in g: continue
            ok=g[d]==truth[d]; dims[d][0]+=ok; dims[d][1]+=1
            if d!="tier": hit+=ok; tot+=1
            if not ok: miss.append((n,P3[n]["app"],d,g[d],truth[d]))
    out[name]={"accuracy_4dims":round(100*hit/tot,1),"hits":hit,"fields":tot,"by_dim":{d:f"{v[0]}/{v[1]}" for d,v in dims.items() if v[1]},"misses":miss}
json.dump(out,open("final/accuracy.json","w"),indent=1)
for k,v in out.items(): print(k,v["accuracy_4dims"],"%",v["hits"],"/",v["fields"],v["by_dim"]); 
for m in out["pass2_llm_draft"]["misses"]: print("  pass2 miss",m)
for m in out["pass3_final"]["misses"]: print("  pass3 miss",m)
