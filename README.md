# 100-app API access research agent

Researches 100 apps to compare authentication, access requirements, API coverage, MCP support, and buildability, then produces a source-backed HTML report and checks a sample against a fresh audit.

**Live report:** https://adarsh-reddy-y.github.io/api-access-research-agent/

## Layout
- `data/apps.json`: the 100 apps (n, app, hint, list_category)
- `search.py`: stage 1, 3 searches per app -> `search/` (needs a search API key, see below)
- `fetch_evidence.py`: stage 2, fetch doc pages, extract signals -> `evidence/`
- `pass1_rules.py`: stage 3, rules-only baseline -> `data/pass1.json`
- `review/b01..b09.txt`: stage 4, LLM review, one pipe-delimited record per app (13 fields)
- `ver_fetch.py`, `apply_corrections.py`: stage 5, targeted doc checks and corrections with old->new log -> `final/final.json`, `final/changes.json`
- `final/recheck.json`, `apply_recheck.py`: independent agent re-check (second pass) of 10 rows against official vendor docs (23 Nov 2026); applies corrections to `final/final.json`, logs old->new in `final/recheck_log.json`. An AI re-check, not human verification
- `data/audit_truth.json`, `verify.py`: stage 6, seeded sample audit, accuracy for passes 1, 2, 3 -> `final/accuracy.json`
- `build_page.py` -> `final/index.html`; the repo-root `index.html` is the same page, served live via GitHub Pages

## What is automated vs what needs a model or a human
- **Automated scripts:** `search.py` (web search), `fetch_evidence.py` (fetch pages + extract signal snippets), `pass1_rules.py` (keyword baseline), `apply_corrections.py` (applies the logged corrections), `verify.py` (scoring), `build_page.py` (report page). These run unattended.
- **Needs an LLM in the loop:** stage 4 (each record in `review/` is written by an LLM reading that app's `evidence/{n}.json`) and stage 5 (the corrections inside `apply_corrections.py` come from targeted doc re-checks on flagged rows; the script only applies them).
- **Needs a human:** `data/audit_truth.json` is an AI's fresh reading of vendor docs, not an independent human's. Ten rows also got an independent agent re-check (second pass, a second AI agent reading official docs from scratch; 8 agree, 2 disagree, see report section 6 and `final/recheck.json`). That is not human verification. The author's own manual check of those rows is still pending.

## Run

### What a reviewer can run with no keys and no LLM
All research artifacts (`data/`, `review/`, `final/`) are committed, so scoring and the report rebuild end to end:
```bash
pip install requests beautifulsoup4
python3 apply_recheck.py # applies the second-pass re-check corrections to final/final.json (idempotent)
python3 verify.py        # scores all three passes against data/audit_truth.json -> final/accuracy.json
python3 build_page.py    # rebuilds the report -> final/index.html
```

### Re-running the research pipeline from scratch
Stages 1-2 outputs (`search/`, `evidence/`) are not committed (600+ files), so reproducing stage 3 onward means re-running them:
```bash
pip install requests beautifulsoup4
export BRAVE_API_KEY=...   # https://brave.com/search/api/ - or swap search() in search.py for another provider
python3 search.py          # stage 1: 3 searches per app -> search/ (fails loudly if the key is missing or a search fails)
python3 fetch_evidence.py  # stage 2: fetch doc pages, extract signals -> evidence/
python3 pass1_rules.py     # stage 3: rules-only baseline -> data/pass1.json
# stage 4 (LLM): give each evidence/{n}.json to a model, ask for the 13-field pipe-delimited record (format: review/b01..b09.txt)
# stage 5 (LLM + targeted fetches): re-check flagged rows against vendor docs (ver_fetch.py helps), record corrections in apply_corrections.py
python3 apply_corrections.py
python3 apply_recheck.py   # second-pass corrections for 10 rows (re-run after apply_corrections.py, which rebuilds final.json)
python3 verify.py
python3 build_page.py
```

## Honest limits
Ground truth for the audit is an AI's fresh reading of vendor docs, not a human. Ten rows got an independent agent re-check (second pass), which is not human verification; the author's own manual check is pending (report page, section 6). No live API calls were made to any app; everything is from docs, which can be stale or wrong.
