#!/usr/bin/env python3
"""Stage 3 (first pass): deterministic keyword rules over fetched evidence -> draft record. No LLM.
This is the 'low accuracy baseline' the later LLM-review and verification loops are measured against."""
import json
apps = json.load(open("data/apps.json")); out = []
for a in apps:
    n = a["n"]; e = json.load(open(f"evidence/{n}.json")); s = e["signals"]
    c = {k: v["count"] for k, v in s.items()}
    hl = " ".join(h["text"] for h in e["search_highlights"] if h["kind"] == "docs").lower()
    mc = " ".join(h["title"] + " " + h["text"] for h in e["search_highlights"] if h["kind"] == "mcp").lower()
    auth = []
    if c["oauth2"] >= 2 or "oauth" in hl: auth.append("OAuth2")
    if c["api_key"] >= 2: auth.append("API key/token")
    if c["basic"] >= 1: auth.append("Basic")
    if not auth: auth = ["unknown"]
    access = "gated" if c["gated"] > 2 * max(1, c["self_serve"]) else "self-serve"
    out.append({"n": n, "app": a["app"], "auth": auth, "access": access,
                "api": ("GraphQL+REST" if c["graphql"] >= 3 and c["rest"] else "GraphQL" if c["graphql"] >= 3 else "REST" if c["rest"] else "unknown"),
                "mcp": "yes" if ("official" in mc and "mcp" in mc) else "unknown",
                "buildable": "yes" if access == "self-serve" and auth != ["unknown"] else "unclear"})
json.dump(out, open("data/pass1.json", "w"), indent=1)
print(len(out))
