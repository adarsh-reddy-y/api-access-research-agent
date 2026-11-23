# 100-app API access research agent

Researches 100 apps (auth methods, self-serve vs gated, API surface, MCP, buildability, evidence URL),
scores itself against a sampled audit, and builds a one-page HTML report.

## Layout
- `data/apps.json` the 100 apps (n, app, hint, list_category)
- `search.py` stage 1: 3 searches per app -> `search/`
- `fetch_evidence.py` stage 2: fetch doc pages, extract signals -> `evidence/`
- `pass1_rules.py` stage 3: rules-only baseline -> `data/pass1.json`
- `review/b01..b09.txt` stage 4: LLM review, one pipe-delimited record per app (13 fields)
- `ver_fetch.py`, `apply_corrections.py` stage 5: targeted doc checks, corrections with old->new log -> `final/final.json`, `final/changes.json`
- `data/audit_truth.json`, `verify.py` stage 6: seeded sample audit, accuracy for pass 1, 2, 3 -> `final/accuracy.json`
- `build_page.py` -> `final/index.html`, also served as `index.html` (live page via GitHub Pages)

## Run
```
pip install requests beautifulsoup4
python3 search.py            # needs a search backend, see search()
python3 fetch_evidence.py
python3 pass1_rules.py
# stage 4: give each app's evidence/{n}.json to an LLM, ask for the 13-field record (see review/ for format)
python3 apply_corrections.py
python3 verify.py
python3 build_page.py
```
Stages 4 and 5 are done by an LLM reading evidence; scripts do the plumbing and scoring.

## Honest limits
Ground truth for the audit is an AI's fresh reading of vendor docs, not a human. No live API calls were made.
