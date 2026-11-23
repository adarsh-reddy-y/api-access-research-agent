#!/usr/bin/env python3
"""Applies the independent agent re-check (second pass) from final/recheck.json to final/final.json.
Run after apply_corrections.py and before verify.py / build_page.py. Idempotent.
Each row records old->new values in final/recheck_log.json. This is an AI re-check, not human verification."""
import json
R=json.load(open("final/final.json")); by={int(r["n"]):r for r in R}
RC=json.load(open("final/recheck.json")); log=[]
for row in RC["rows"]:
    r=by[row["n"]]
    diff={k:[r.get(k),v] for k,v in row["changes"].items() if r.get(k)!=v}
    r.update(row["changes"]); r["second_pass"]=row["result"]
    log.append({"n":row["n"],"app":r["app"],"result":row["result"],"changes":diff})
json.dump(R,open("final/final.json","w"),indent=1)
json.dump(log,open("final/recheck_log.json","w"),indent=1)
print("applied second-pass re-check to",len(log),"rows;",sum(1 for l in log if l["result"].startswith("Disagree")),"disagreements")
