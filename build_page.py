import json,re,html,collections as C
R=json.load(open("final/final.json")); CH=json.load(open("final/changes.json")); ACC=json.load(open("final/accuracy.json"))
CATS=["CRM & Sales","Support & Helpdesk","Communications","Marketing, Ads, Email, Social","Ecommerce","Data, SEO, Scraping","Developer, Infra, Data platforms","Productivity & PM","Finance & Fintech","AI, Research, Media"]
for r in R: r["cat"]=CATS[(int(r["n"])-1)//10]; r["n"]=int(r["n"])
mat=[c for c in CH if {"tier","verdict","mcp","auth"}&set(c["changes"])]
tiers=C.Counter(r["tier"] for r in R); ver=C.Counter(r["verdict"] for r in R)
def mcp_yes(r): return not re.match(r"(no |unclear)",r["mcp"],re.I) and "coming soon" not in r["mcp"]
mcpn=sum(mcp_yes(r) for r in R)
def aset(t):
    t=re.sub(r"\([^)]*\)","",t); s=set()
    if re.search("oauth",t,re.I): s.add("O")
    if re.search(r"key|token",t,re.I): s.add("K")
    return s
both=sum(1 for r in R if aset(r["auth"])=={"O","K"}); oauth=sum(1 for r in R if "O" in aset(r["auth"])); key=sum(1 for r in R if "K" in aset(r["auth"]))
oonly=sum(1 for r in R if aset(r["auth"])=={"O"}); konly=sum(1 for r in R if aset(r["auth"])=={"K"})
bycat=[]
for i,c in enumerate(CATS):
    rs=[r for r in R if r["cat"]==c]; t=C.Counter(r["tier"] for r in rs); bycat.append((c,t["S1"],t["S2"],t["G1"],t["G2"]))
def bar(c):
    a,b,d,e=c[1:]; return "".join(f'<span class="seg {k}" style="width:{v*10}%" title="{k}: {v}">{v if v else ""}</span>' for k,v in zip(["S1","S2","G1","G2"],[a,b,d,e]))
catrows="".join(f'<div class="row"><div class="lbl">{html.escape(c[0])}</div><div class="bar">{bar(c)}</div></div>' for c in bycat)
a1,a2,a3=ACC["pass1_rules"],ACC["pass2_llm_draft"],ACC["pass3_final"]
def appacc(m,total=21):
    bad={x[0] for x in m["misses"]}; return total-len(bad)
data=json.dumps([{k:r[k] for k in ["n","app","cat","category","auth","tier","access","api","mcp","verdict","blocker","urls","conf"]} for r in R]).replace("</","<\\/")
chrows="".join(f'<tr><td>{c["n"]}</td><td>{html.escape(c["app"])}</td><td>{"; ".join(html.escape(k)+": "+html.escape(v[0][:60])+" → "+html.escape(v[1][:60]) for k,v in c["changes"].items() if k in("tier","verdict","mcp","auth","app"))}</td><td>{html.escape(c["note"])}</td></tr>' for c in mat)
# Independent agent re-check (second pass) of 10 rows, from final/recheck.json (applied to final.json by apply_recheck.py).
# This is an AI re-check, NOT human verification; the author's manual check is still pending.
RC=json.load(open("final/recheck.json"))
SPOT_NS=[x["n"] for x in RC["rows"]]
by_n={int(r["n"]):r for r in R}
def firsturl(u):
    for x in u.split(";"):
        x=x.strip()
        if x.startswith("http"): return x
    return ""
def srclinks(x): return " ".join(f'<a href="{html.escape(u)}" target="_blank" rel="noopener">[{k+1}]</a>' for k,u in enumerate(x["sources"]))
def rcpill(t): return "bl" if t.startswith("Disagree") else "ok"
spotrows="".join(f'<tr><td>{x["n"]}</td><td>{html.escape(x["app"])}</td><td><span class="pill {rcpill(x["result"])}">{html.escape(x["result"])}</span></td><td><span class="pill {by_n[x["n"]]["tier"]}">{by_n[x["n"]]["tier"]}</span> {html.escape(by_n[x["n"]]["verdict"])}</td><td>{html.escape(x["summary"])}</td><td>{srclinks(x)}</td></tr>' for x in RC["rows"])
nagree=sum(1 for x in RC["rows"] if x["result"].startswith("Agree")); ndis=len(RC["rows"])-nagree
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>100 apps: who lets an agent in? Auth, access and buildability research</title>
<style>
:root{{--s1:#2e9e5b;--s2:#8cc34a;--g1:#f0a030;--g2:#d9473f;--ink:#1c2230;--mut:#5d6677;--bg:#f6f7f9}}
*{{box-sizing:border-box}}body{{font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);background:var(--bg);margin:0}}
main{{max-width:1100px;margin:0 auto;padding:24px 18px 80px}}h1{{font-size:28px;margin:0 0 6px}}h2{{font-size:20px;margin:36px 0 10px;border-bottom:2px solid #dde1e8;padding-bottom:4px}}
.sub{{color:var(--mut);margin-bottom:18px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}
.card{{background:#fff;border-radius:10px;padding:14px;box-shadow:0 1px 3px #0001}}.card b{{font-size:26px;display:block}}
.card small{{color:var(--mut)}}.legend span{{display:inline-block;margin-right:12px}}.dot{{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:4px;vertical-align:-1px}}
.row{{display:flex;align-items:center;margin:5px 0}}.lbl{{width:230px;font-size:13px}}.bar{{flex:1;display:flex;height:22px;background:#e6e9ef;border-radius:4px;overflow:hidden}}
.seg{{color:#fff;font-size:12px;text-align:center;line-height:22px}}.S1{{background:var(--s1)}}.S2{{background:var(--s2)}}.G1{{background:var(--g1)}}.G2{{background:var(--g2)}}
table{{border-collapse:collapse;width:100%;background:#fff;font-size:13px}}th,td{{padding:6px 8px;border-bottom:1px solid #e6e9ef;text-align:left;vertical-align:top}}th{{background:#eef1f6;position:sticky;top:0;cursor:pointer}}
.tw{{max-height:620px;overflow:auto;border-radius:8px;box-shadow:0 1px 3px #0001}}.pill{{padding:1px 7px;border-radius:9px;color:#fff;font-size:12px}}
.ok{{background:#2e9e5b}}.cv{{background:#8cc34a;color:#143}}.bl{{background:#d9473f}}.na{{background:#7a8294}}
input,select{{padding:6px;margin:0 6px 8px 0;border:1px solid #ccd;border-radius:6px}}.note{{background:#fff7e0;border-left:4px solid #f0a030;padding:10px 14px;border-radius:4px;margin:12px 0}}
.flow{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:8px}}.step{{background:#fff;padding:10px;border-radius:8px;border-top:4px solid #4a6fa5;font-size:13px}}.step b{{display:block}}
code{{background:#eceff4;padding:1px 5px;border-radius:4px}}a{{color:#2a5db0}}ul{{margin:6px 0 6px 20px;padding:0}}.small{{font-size:12px;color:var(--mut)}}
</style></head><body><main>
<h1>100 apps: who lets an agent in, and how?</h1>
<div class="sub">Auth, access, API surface, MCP and buildability for the 100 apps on the Composio take-home list. Research run 23 Nov 2026 (docs and pricing change; each row has its evidence link). 2-minute read: patterns, then the agent, then proof, then where it was wrong.</div>

<h2>1. Patterns up top</h2>
<div class="cards">
<div class="card"><b>{key} of 100 take an API key/token</b><small>{oauth} support OAuth2. {both} offer both, {konly} are key/token only, {oonly} are OAuth2 only. Keys are the easy door; OAuth is for multi-user apps.</small></div>
<div class="card"><b>{tiers["S1"]} free self-serve</b><small>Sign up, get a key, call the API, no human. Another {tiers["S2"]} need a paid or trial account (S2).</small></div>
<div class="card"><b>{tiers["G1"]+tiers["G2"]} gated</b><small>{tiers["G1"]} need app review or approval (G1), {tiers["G2"]} need a sales or partner contract (G2). Most common blocker overall: a paid plan (S2), then app review.</small></div>
<div class="card"><b>{mcpn} of 100 have an official MCP</b><small>Most vendors now ship one. MCP is no longer the differentiator; access to the API is.</small></div>
</div>
<p class="legend"><span><i class="dot S1"></i>S1 free self-serve</span><span><i class="dot S2"></i>S2 trial or paid account</span><span><i class="dot G1"></i>G1 approval or app review</span><span><i class="dot G2"></i>G2 sales or partner contract</span></p>
{catrows}
<ul>
<li><b>Easy wins ({ver["Ready"]} Ready, {ver["Ready with caveat"]} Ready with caveat):</b> Productivity/PM (10 of 10 ready), Developer/Infra (10 of 10), Comms (10 of 10, but WhatsApp has a 250-recipient daily limit at first and Aircall needs extra steps), most CRMs.</li>
<li><b>Needs outreach ({ver["Blocked until outreach"]}):</b> enterprise-only APIs (DealCloud, Pylon, Gladly, Salesforce Commerce Cloud, Otter, Waterfall.io), finance partners (Brex, Ramp, PitchBook), and review-gated ads/social/commerce (Meta Ads, LinkedIn Ads, Pinterest, Threads, Amazon SP-API). Another 5 are self-serve to start but gated for production (Aircall, Google Ads, Plaid, QuickBooks, Xero).</li>
<li><b>Not buildable as an API integration ({ver["Not API-buildable"]}):</b> Sherlock and Mermaid CLI are local CLIs, no hosted API. {ver["Not verified (vendor ambiguous)"]} app (Paygent Connect) is not verified: pass 2 researched the wrong company, and the right one (gopaygent.com) has thin public docs.</li>
<li><b>Pattern:</b> marketing/ads and finance are the most gated categories; dev tools and PM tools are almost all self-serve with a token.</li>
</ul>

<h2>2. Findings table (all 100)</h2>
<input id="q" placeholder="Search app, auth, blocker..."><select id="ct"><option value="">All categories</option>{"".join(f"<option>{html.escape(c)}</option>" for c in CATS)}</select><select id="tr"><option value="">All tiers</option><option>S1</option><option>S2</option><option>G1</option><option>G2</option></select><select id="vd"><option value="">All verdicts</option><option>Ready</option><option>Ready with caveat</option><option>Blocked until outreach</option><option>Not API-buildable</option><option>Not verified</option></select>
<div class="tw"><table id="t"><thead><tr><th>#</th><th>App</th><th>Category / function</th><th>Auth</th><th>Access</th><th>API / MCP</th><th>Verdict, blocker</th><th>Conf.</th><th>Evidence</th></tr></thead><tbody></tbody></table></div>
<div class="small">Tier: S1 free self-serve, S2 trial or paid account, G1 approval/review, G2 sales/partner. Confidence is the agent's own; "low" rows are the ones to check first. And more: every row is also in the downloadable CSV/JSON in the repo.</div>

<h2>3. The agent</h2>
<div class="flow">
<div class="step"><b>1 List</b>100 app names and hints pulled from the assignment page (lazy tables, needed a browser scroll).</div>
<div class="step"><b>2 Search</b>3 searches per app (docs/auth, MCP, access/pricing): 300 results files. <code>search.py</code></div>
<div class="step"><b>3 Fetch</b>Pull the doc pages and keep auth/access signal snippets. <code>fetch_evidence.py</code></div>
<div class="step"><b>4 Rules baseline</b>Keyword rules, no LLM. This is the weak first pass. <code>pass1_rules.py</code></div>
<div class="step"><b>5 LLM review</b>An AI model reads each app's evidence and writes a 13-field record with a confidence and a check flag. 53 flags.</div>
<div class="step"><b>6 Verify loop</b>Targeted searches and direct doc fetches on flagged apps; corrections logged old to new. <code>apply_corrections.py</code></div>
<div class="step"><b>7 Audit</b>Seeded random sample of 25, fresh fetch, score vs truth. <code>verify.py</code></div>
</div>
<p><b>Where a human was needed.</b> (a) Getting the app list out of lazy-rendered Notion tables (I had to scroll a browser). (b) Disambiguating vendors when search returned a look-alike (Otter, Sherlock, Mermaid, Paygent, YouTube Transcript). (c) Judging gated vs paid (S2 vs G1) when docs are vague. (d) Sign-off on the 3 lowest-confidence rows. Steps 5 to 7 were done by an AI assistant working in the repo workspace, not by an unattended script: the scripts do search, fetch, baseline and scoring; the reading and judgement is the model. A human (Adarsh) has not yet spot-checked rows. Ten rows got an independent agent re-check (second pass), which is not a human check; see section 6.</p>

<h2>4. Proof</h2>
<p>Every number above is computed from <code>final/final.json</code>; run <code>python3 verify.py</code> and <code>python3 build_page.py</code> in the repo to reproduce the accuracy table and this page from the data. The full pipeline (<code>search.py</code> then <code>fetch_evidence.py</code>, <code>pass1_rules.py</code>, review, <code>apply_corrections.py</code>, <code>verify.py</code>) needs a search API key and an LLM; see the README. Each table row links to the vendor page it relied on.</p>

<h2>5. Verification: hits, misses, and accuracy moving up</h2>
<div class="note"><b>Read this with care.</b> Ground truth here is my own fresh reading of vendor docs (an AI), not an independent human. Pass 3 is scored after fixing what the audit found, so it is optimistic. The sample is {a1["fields"]//4} apps x 4 fields (auth methods, self-serve vs gated, official MCP, buildable), 4 sampled apps excluded because they could not be re-verified (SFCC docs returned 403, fanbasis had no primary doc, Paygent vendor ambiguous, systeme.io access unresolved).</div>
<table><thead><tr><th>Pass</th><th>What it is</th><th>Field accuracy</th><th>Apps fully right</th></tr></thead><tbody>
<tr><td>1</td><td>Keyword rules only</td><td><b>{a1["accuracy_4dims"]}%</b> ({a1["hits"]}/{a1["fields"]})</td><td>{appacc(a1)}/21</td></tr>
<tr><td>2</td><td>LLM reads evidence (before corrections)</td><td><b>{a2["accuracy_4dims"]}%</b> ({a2["hits"]}/{a2["fields"]})</td><td>{appacc(a2)}/21</td></tr>
<tr><td>3</td><td>After verification loop and audit fixes</td><td><b>{a3["accuracy_4dims"]}%</b> ({a3["hits"]}/{a3["fields"]}), in-sample</td><td>{appacc(a3)}/21</td></tr></tbody></table>
<p>The sample numbers flatter pass 2, because many sampled apps were easy. The harder measure: the verification loop on the 53 flagged apps changed a material field (tier, verdict, MCP status or auth) on <b>{len(mat)} of 100 apps</b>. So pass 2 was not better than roughly {100-len(mat)}% on those fields. The 47 unflagged apps got only the sample audit, not a full re-check.</p>
<p><b>Misses found by the audit:</b> Lark auth was "not confirmed" in pass 2 (docs page was JS-rendered; fixed from open.larksuite.com), Clay tier S2 should be S1 (its public API is on all plans, per a third-party quote of Clay's launch post). The pass-1 rules had 11/21 auth right: they match keywords on a page, not what a vendor actually requires.</p>
<h3>Corrections the verification loop made (old to new)</h3>
<div class="tw"><table><thead><tr><th>#</th><th>App</th><th>Change</th><th>Why</th></tr></thead><tbody>{chrows}</tbody></table></div>

<h2>6. Independent agent re-check (second pass); human check pending</h2>
<div class="note"><b>Status: this is an agent re-check, not human verification.</b> On 23 Nov 2026 a second AI agent re-read the official vendor docs for 10 rows from scratch (one per category, chosen as the lowest-confidence, gated, flipped-by-verification or third-party-evidence rows) and compared them with the pass-3 claims: auth type, access gate, official MCP, and whether the evidence supports the claim. Result: <b>{nagree} agree, {ndis} disagree</b> (WhatsApp Business: tier and MCP corrected; Paygent Connect: wrong vendor found). Corrections are applied in the data and the table in section 2. <b>The author's own manual check of these rows is still pending</b> and will be added when done. Both the original research and this re-check are AI work, so they share blind spots; neither replaces a human reading the docs.</div>
<table><thead><tr><th>#</th><th>App</th><th>Re-check result</th><th>Claim now (tier, verdict)</th><th>What the re-check found and changed</th><th>Sources</th></tr></thead><tbody>{spotrows}</tbody></table>
<p class="small">Method per row: fetch the vendor's own pages fresh (auth, pricing or plan, MCP), ignore the earlier agent's notes, mark agree or disagree, and correct the row. Old and new values are in <code>final/recheck_log.json</code>; the full record is <code>final/recheck.json</code>; <code>apply_recheck.py</code> applies it. The accuracy table in section 5 is unchanged: it scores the original 25-app audit sample, not these rows.</p>

<h2>7. Where the agent was wrong or an app defeated it</h2>
<ul>
<li><b>Wrong vendor from search:</b> Otter (hit a food-delivery product), Mermaid (datamermaid.org), Sherlock (AI products), YouTube Transcript (look-alikes). Caught at review, not by the script.</li>
<li><b>Paygent Connect: wrong vendor in pass 2.</b> The list hint says "NMI-powered". Pass 2 researched withpaygent.com (an AI usage-billing SDK). The second-pass re-check found gopaygent.com/products/connect, an NMI-based payments API with thin public docs, moved it to G1 and kept it not verified.</li>
<li><b>Copper MCP</b> was reported as a live MCP in pass 2; the vendor page says "coming soon".</li>
<li><b>WhatsApp Business</b> was "Blocked until outreach" in pass 2, then "Ready with caveat" at G1 in pass 3. The second-pass re-check moved it to S2: direct developers need no App Review, business verification only raises the 250-recipient daily limit, and messages are paid per delivery. Meta also runs an official WhatsApp MCP server.</li>
<li><b>Tier flips:</b> Squarespace (G1 to S2: paid plan, not review), WhatsApp Business (G1 to S2 in the second-pass re-check), Neo4j Aura (S1 to S2: card on file), QuickBooks (S1 to G1 for production: assessment), MrScraper (S2 to S1), YouTube Transcript (S2 to S1), Clay (S2 to S1).</li>
<li><b>Pages the fetcher could not read:</b> Lark docs (JS-rendered), Salesforce Commerce Cloud docs (403), Binance docs (JS). These rely on search excerpts or other pages.</li>
<li><b>DealCloud and Pylon:</b> pass 3 rested on third-party pages. The second-pass re-check found Pylon's own pricing FAQ (trials via sales, no free plan) and DealCloud's demo-request-only site; both stay G2.</li>
<li><b>Noise:</b> a repeated odd snippet on several fetched vendor pages claimed "free tier, no form"; I treated it as unreliable and ignored it.</li>
<li><b>Not done:</b> No live API calls were made to apps to prove access. Everything is from docs, which can be stale or wrong.</li>
</ul>
<h2>8. Source</h2>
<p>Repo (scripts, data, review records, corrections log, accuracy scoring, README on running it): <a href="https://github.com/adarsh-reddy-y/api-access-research-agent">github.com/adarsh-reddy-y/api-access-research-agent</a>. This page: <a href="https://adarsh-reddy-y.github.io/api-access-research-agent/">adarsh-reddy-y.github.io/api-access-research-agent</a>. Key files: <code>final/final.json</code>, <code>final/changes.json</code>, <code>final/accuracy.json</code>, <code>verify.py</code>.</p>
</main>
<script>
const D={data};
const tb=document.querySelector("#t tbody");
const vc=v=>v.startsWith("Ready with")?"cv":v.startsWith("Ready")?"ok":v.startsWith("Blocked")?"bl":"na";
function esc(s){{return s.replace(/[&<>"]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]))}}
function render(){{
 const q=document.getElementById("q").value.toLowerCase(),c=document.getElementById("ct").value,t=document.getElementById("tr").value,v=document.getElementById("vd").value;
 tb.innerHTML=D.filter(r=>(!c||r.cat==c)&&(!t||r.tier==t)&&(!v||r.verdict.startsWith(v))&&(!q||JSON.stringify(r).toLowerCase().includes(q))).map(r=>{{
  const u=r.urls.split(";").filter(x=>x.trim().startsWith("http")||x.includes(".")).slice(0,2).map(x=>{{x=x.trim();const h=x.startsWith("http")?x:"https://"+x;return `<a href="${{esc(h)}}" target="_blank" rel="noopener">${{esc(x.replace(/^https?:\\/\\//,"").slice(0,32))}}</a>`}}).join("<br>");
  return `<tr><td>${{r.n}}</td><td><b>${{esc(r.app)}}</b></td><td>${{esc(r.category)}}</td><td>${{esc(r.auth)}}</td><td><span class="pill ${{r.tier}}">${{r.tier}}</span> ${{esc(r.access)}}</td><td>${{esc(r.api)}}<br><i>MCP:</i> ${{esc(r.mcp)}}</td><td><span class="pill ${{vc(r.verdict)}}">${{esc(r.verdict)}}</span><br>${{esc(r.blocker)}}</td><td>${{r.conf}}</td><td>${{u}}</td></tr>`}}).join("");}}
["q","ct","tr","vd"].forEach(i=>document.getElementById(i).addEventListener("input",render));render();
</script></body></html>'''
open("final/index.html","w").write(page); print(len(page))
