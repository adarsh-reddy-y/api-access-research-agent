import json,glob
# pass2 -> pass3 corrections after targeted primary-source checks. field names:
F=["n","app","category","auth","tier","access","api","mcp","verdict","blocker","urls","conf","flag"]
recs={}
for f in sorted(glob.glob("review/b0*.txt")):
    for l in open(f):
        l=l.rstrip("\n")
        if not l.strip(): continue
        p=l.split("|"); assert len(p)==13,(f,l[:60],len(p))
        recs[int(p[0])]=dict(zip(F,p))
C={ # n: ({field:new}, note)
1:({"conf":"high"},"confirmed: Developer Edition free, API on by default"),
6:({"conf":"high"},"confirmed: API free on all plans, 250/1000 per hr; Progress-owned"),
7:({"conf":"high"},"confirmed: Free edition has API, 5000 credits/24h"),
9:({"mcp":"Copper MCP page says 'coming soon' (not live as of check)","conf":"high"},"MCP claim corrected: pass2 treated page as live MCP"),
11:({"conf":"high"},"confirmed 14-day trial"),
15:({"conf":"med"},"third-party sources only: no free plan, trial via sales"),
18:({"conf":"high"},"confirmed API paid-only, MCP on paid plans"),
19:({"conf":"high"},"confirmed REST on all plans, 7-day trial"),
24:({"auth":"tenant_access_token (app_id + app_secret, custom apps); user_access_token via OAuth2","conf":"med"},"auth was 'not confirmed' in pass2; filled from open.larksuite.com docs"),
25:({"conf":"med"},"API key via free CAKE.com API add-on confirmed; API breadth still unverified"),
26:({"auth":"Bot token ('Authorization: Bot <token>'), OAuth2 bearer, Basic for client credentials","blocker":"Privileged intents need Discord review for verified bots (75+ servers); small bots self-serve","conf":"high"},"auth detail added"),
27:({"conf":"high"},"confirmed Bot API token from BotFather on core.telegram.org"),
28:({"verdict":"Ready with caveat","blocker":"Test number self-serve; production needs Meta business verification","conf":"med"},"VERDICT CHANGED: pass2 said Blocked; Meta docs show self-serve test token and hello_world template"),
29:({"mcp":"Official Aircall MCP (beta, read-only) per support.aircall.io","conf":"med"},"MCP confirmed as official beta"),
35:({"conf":"high"},"confirmed free accounts get API, some endpoints plan-gated"),
36:({"conf":"high"},"confirmed private keys on all plans incl. free"),
40:({"conf":"high"},"confirmed free plan retired May 2025, 60-day trial now"),
41:({"conf":"high","blocker":"Public apps need protected-customer-data approval; custom/dev-store apps do not"},"confirmed gate"),
44:({"conf":"high"},"confirmed realm/subscription needed; on-demand sandbox only inside a realm"),
45:({"mcp":"Official Adobe Commerce Storefront MCP (Adobe docs, Nov 2026)","conf":"med"},"MCP corrected: pass2 said none confirmed"),
46:({"tier":"S2","access":"Developer API keys need a paid Squarespace plan (Advanced/Commerce Advanced)","conf":"med"},"TIER CHANGED G1->S2: it is a paid-plan gate, not a review"),
47:({"conf":"high"},"confirmed API only on paid plans; free upgrade offered to devs"),
49:({"conf":"high"},"confirmed registration and restricted-role architecture review"),
50:({"app":"fanbasis (now Commas)","conf":"med"},"rename found: docs at commasdocs.com"),
51:({"conf":"high"},"confirmed $1 trial credit + free sandbox"),
54:({"tier":"S1","access":"Free plan, no card (llms.txt); paid tiers vary by source","conf":"med"},"TIER CHANGED S2->S1; third-party pricing sources disagree"),
56:({"conf":"high"},"confirmed 1,000 free credits/mo"),
60:({"tier":"S1","access":"Public API said to be on all plans incl Free (Clay launch post via third party); table queries Enterprise only","conf":"med"},"TIER CHANGED S2->S1: found by pass-3 audit"),
84:({"verdict":"Not verified (vendor ambiguous)","blocker":"List hint says NMI-powered Paygent; search surfaced other Paygent products (paygenthq.ai, withpaygent.com, gopaygent.com). Could not confirm which is meant.","conf":"low"},"VERDICT WITHDRAWN: likely researched the wrong vendor"),
37:({"conf":"low","blocker":"API plan gate unresolved: third-party says native integrations on every plan, API limits vary by plan"},"left unresolved honestly"),
65:({"auth":"Project API keys + JWT (data plane); Management API: personal access token (scopable) or OAuth2","conf":"high"},"confirmed"),
66:({"tier":"S2","access":"Aura API credentials need payment info on file, even for Free tier","conf":"high"},"TIER CHANGED S1->S2: conflict resolved from Aura CLI docs"),
67:({"conf":"high"},"confirmed 30-day trial, $400, no card"),
68:({"conf":"med"},"Free M0 cluster confirmed; Admin API on free not stated directly"),
69:({"conf":"high"},"confirmed 14-day trial, no free plan"),
72:({"conf":"high","blocker":"Free plan capped at 1,000 API calls/workspace/month"},"confirmed cap"),
74:({"conf":"med"},"Free plan up to 10 users; API on Free not stated in one primary line"),
81:({"conf":"high"},"confirmed sandbox on signup, live needs activation"),
83:({"auth":"API key + signed requests (HMAC, RSA or Ed25519)","conf":"med"},"signature types confirmed on binance-spot-api-docs"),
86:({"tier":"G1","access":"Sandbox self-serve; production keys need Intuit app assessment","blocker":"Production needs app assessment questionnaire","conf":"high"},"TIER CHANGED S1->G1 for production"),
88:({"conf":"med","blocker":"Own account: key from Brex admin; partner OAuth needs partner registration"},"two paths clarified"),
89:({"auth":"OAuth2 (client credentials, authorization code), Basic on token call","conf":"high"},"auth confirmed"),
92:({"auth":"Personal API key (Bearer) from Integrations > Developer; Enterprise workspaces only","conf":"high"},"auth filled in from help.otter.ai"),
94:({"auth":"API key in x-api-key header","conf":"high"},"auth confirmed; Free plan 30 calls/mo"),
97:({"tier":"S2","access":"Pay-as-you-go balance, $5 minimum top-up","conf":"high"},"confirmed"),
98:({"conf":"high"},"confirmed CLI repo"),
99:({"tier":"S1","access":"100 free signup credits, then credits","mcp":"Official hosted MCP at transcriptapi.com/mcp","conf":"med"},"TIER CHANGED S2->S1; vendor disambiguated to transcriptapi.com"),
58:({"conf":"high"},"confirmed local CLI"),
}
log=[]
for n,(ch,note) in C.items():
    r=recs[n]; diff={k:(r[k],v) for k,v in ch.items() if r[k]!=v}
    r.update(ch); r["verified"]="Y"; log.append({"n":n,"app":r["app"],"changes":diff,"note":note})
for n,r in recs.items(): r.setdefault("verified","N")
json.dump([recs[i] for i in sorted(recs)],open("final/final.json","w"),indent=1)
json.dump(log,open("final/changes.json","w"),indent=1)
print(len(recs),"records;",len(log),"touched;",sum(1 for l in log if {"tier","verdict","mcp","auth"}&set(l["changes"])),"materially changed")
