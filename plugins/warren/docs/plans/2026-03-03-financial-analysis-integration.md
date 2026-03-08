# Financial Analysis Engine Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Absorb `geogons/skill-financial-analyst` scripts into Warren's plugin and wire them into the trading-review skill, replacing the vague "WebSearch" analysis step with a real multi-API scoring engine.

**Architecture:** Copy the 14 Python scripts into `warren/scripts/financial-analysis/scripts/`. Create a new `stock-deep-dive` skill that wraps the engine. Update `trading-review` Mode B to delegate analysis to `stock-deep-dive` after the four thesis questions. Drop the Daily Scanner workflow (not relevant for Warren's CFO persona).

**Tech Stack:** Python 3.9+, yfinance, pandas-ta, Finnhub, Alpha Vantage, SEC EDGAR, ApeWisdom, pass (credential management)

---

## Directory Layout (what we're building)

```
warren/
  scripts/
    financial-analysis/
      scripts/              ← all Python scripts from source repo
        api_config.py
        api_caller.py
        usage_tracker.py
        data_cache.py
        data_fetchers.py
        technical_analysis.py
        entry_exit.py
        scoring.py
        rss_feeds.py
        macro_calendar.py
        sector_rotation.py
        run_deep_dive.py
        run_portfolio_review.py
        run_daily_scanner.py  (kept but not wired in)
      references/
        api_setup_guide.md
      requirements.txt
      setup.sh              ← adapted from source
      .gitignore
  skills/finance/
    stock-deep-dive/
      SKILL.md              ← new skill
    trading-review/
      SKILL.md              ← updated to call stock-deep-dive
```

**Key structural fact:** Scripts use `_project_root = os.path.dirname(__file__) / ".."` and then import as `from scripts.api_caller import ...`. So `run_deep_dive.py` must be inside `scripts/`, with the venv/project root one level up at `financial-analysis/`. Invocations:

```bash
cd warren/scripts/financial-analysis
source .venv/bin/activate
FINNHUB_API_KEY=$(pass show apis/finnhub) \
ALPHA_VANTAGE_API_KEY=$(pass show apis/alpha-vantage) \
python scripts/run_deep_dive.py AAPL
```

---

## Task 1: Create directory structure + .gitignore

**Files:**
- Create: `scripts/financial-analysis/.gitignore`
- Create: `scripts/financial-analysis/scripts/` (directory)
- Create: `scripts/financial-analysis/references/` (directory)

**Step 1: Create directories**

```bash
mkdir -p scripts/financial-analysis/scripts
mkdir -p scripts/financial-analysis/references
```

Run from `warren/` plugin root.

**Step 2: Create .gitignore**

Create `scripts/financial-analysis/.gitignore`:

```
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
```

Note: `~/.financial-analysis/` (logs + api_keys) is outside the repo — nothing to gitignore there.

**Step 3: Commit**

```bash
git add scripts/
git commit -m "chore(warren): scaffold financial-analysis engine directory 📊"
```

---

## Task 2: Copy Python scripts from source repo

**Files:**
- Create: `scripts/financial-analysis/scripts/*.py` (all 14 files)

Fetch each file from `geogons/skill-financial-analyst` via `gh api`. All 14 scripts to copy:

```
api_config.py
api_caller.py
usage_tracker.py
data_cache.py
data_fetchers.py
technical_analysis.py
entry_exit.py
scoring.py
rss_feeds.py
macro_calendar.py
sector_rotation.py
run_deep_dive.py
run_portfolio_review.py
run_daily_scanner.py
```

**Step 1: Fetch and write each script**

For each script filename, run:
```bash
gh api "repos/geogons/skill-financial-analyst/contents/scripts/FILENAME" \
  --jq '.content' | base64 -d > scripts/financial-analysis/scripts/FILENAME
```

Do all 14. Verify file count:
```bash
ls scripts/financial-analysis/scripts/*.py | wc -l
# Expected: 14
```

**Step 2: Commit**

```bash
git add scripts/financial-analysis/scripts/
git commit -m "feat(warren): absorb financial-analysis Python engine 🐍"
```

---

## Task 3: Copy config files + adapt setup.sh

**Files:**
- Create: `scripts/financial-analysis/requirements.txt`
- Create: `scripts/financial-analysis/references/api_setup_guide.md`
- Create: `scripts/financial-analysis/setup.sh`

**Step 1: Copy requirements.txt and api_setup_guide.md**

```bash
gh api "repos/geogons/skill-financial-analyst/contents/requirements.txt" \
  --jq '.content' | base64 -d > scripts/financial-analysis/requirements.txt

gh api "repos/geogons/skill-financial-analyst/contents/references/api_setup_guide.md" \
  --jq '.content' | base64 -d > scripts/financial-analysis/references/api_setup_guide.md
```

**Step 2: Copy setup.sh verbatim** (it already uses `SCRIPT_DIR` detection — no changes needed)

```bash
gh api "repos/geogons/skill-financial-analyst/contents/setup.sh" \
  --jq '.content' | base64 -d > scripts/financial-analysis/setup.sh

chmod +x scripts/financial-analysis/setup.sh
```

**Step 3: Commit**

```bash
git add scripts/financial-analysis/
git commit -m "chore(warren): add financial-analysis config and setup script 🔧"
```

---

## Task 4: Run setup + configure API keys

**Goal:** Get the venv built and verify the scripts import cleanly. Configure any keys that exist in pass.

**Step 1: Run setup.sh**

```bash
cd scripts/financial-analysis
./setup.sh
cd ../..
```

Expected: venv created at `scripts/financial-analysis/.venv/`, packages installed, `~/.financial-analysis/api_keys.json` initialized.

**Step 2: Check which API keys exist in pass**

```bash
pass ls apis/ 2>/dev/null
```

For each key found, set it in the config. Keys that map to env vars:

| pass path | env var |
|-----------|---------|
| `apis/finnhub` | `FINNHUB_API_KEY` |
| `apis/alpha-vantage` | `ALPHA_VANTAGE_API_KEY` |
| `apis/mboum` | `MBOUM_API_KEY` |
| `apis/seeking-alpha-rapidapi` | `SEEKING_ALPHA_RAPIDAPI_KEY` |
| `apis/polygon` | `POLYGON_API_KEY` |

**Step 3: Verify API status**

```bash
cd scripts/financial-analysis
source .venv/bin/activate
FINNHUB_API_KEY=$(pass show apis/finnhub 2>/dev/null) \
ALPHA_VANTAGE_API_KEY=$(pass show apis/alpha-vantage 2>/dev/null) \
python scripts/api_config.py status
cd ../..
```

Expected: Table showing READY for keys found in pass, NEEDS KEY for missing ones.

**Step 4: Smoke test deep dive**

```bash
cd scripts/financial-analysis
source .venv/bin/activate
FINNHUB_API_KEY=$(pass show apis/finnhub 2>/dev/null) \
python scripts/run_deep_dive.py AAPL 2>&1 | head -50
cd ../..
```

Expected: Analysis output starting with AAPL data, or at least no import errors. Partial data is fine if some API keys are missing.

**Step 5: Commit .venv to .gitignore at repo level if needed**

Check if `.venv` would be tracked:
```bash
git status scripts/financial-analysis/
```

If `.venv/` shows as untracked, add to warren's root `.gitignore` (create one if it doesn't exist):
```
scripts/financial-analysis/.venv/
```

---

## Task 5: Create stock-deep-dive SKILL.md

**Files:**
- Create: `skills/finance/stock-deep-dive/SKILL.md`

This skill is the Warren-facing wrapper. It handles:
- Pre-flight check (is setup done?)
- Credential injection from pass
- Invoking `run_deep_dive.py` or `run_portfolio_review.py`
- Presenting output in Warren's analytical tone

**Create `skills/finance/stock-deep-dive/SKILL.md`:**

```markdown
---
name: stock-deep-dive
description: >
  Multi-API stock analysis engine. Produces composite score, Buy/Hold/Sell rating,
  3 entry levels, 3 exit targets, and stop loss for any ticker.
  Triggered from trading-review Mode B after the four thesis questions are answered.
---

# Stock Deep Dive

Analyst-grade scoring engine. Runs against 14+ APIs with automatic fallback chains.
Produces a 0-10 composite score (40% fundamental / 30% technical / 30% sentiment)
with actionable entry/exit levels.

## Pre-Flight

Before running, verify setup is ready:

```bash
ls ${CLAUDE_PLUGIN_ROOT}/scripts/financial-analysis/.venv/bin/activate 2>/dev/null \
  && echo "READY" || echo "NEEDS SETUP"
```

If NEEDS SETUP:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts/financial-analysis && ./setup.sh && cd -
```

## Running a Deep Dive

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts/financial-analysis
source .venv/bin/activate

FINNHUB_API_KEY=$(pass show apis/finnhub 2>/dev/null) \
ALPHA_VANTAGE_API_KEY=$(pass show apis/alpha-vantage 2>/dev/null) \
MBOUM_API_KEY=$(pass show apis/mboum 2>/dev/null) \
SEEKING_ALPHA_RAPIDAPI_KEY=$(pass show apis/seeking-alpha-rapidapi 2>/dev/null) \
python scripts/run_deep_dive.py TICKER

cd ${CLAUDE_PLUGIN_ROOT}
```

Replace `TICKER` with the actual symbol. Multiple tickers: `python scripts/run_deep_dive.py AAPL MSFT`

## Running a Portfolio Review

Used when the user wants to review all current holdings:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts/financial-analysis
source .venv/bin/activate

FINNHUB_API_KEY=$(pass show apis/finnhub 2>/dev/null) \
ALPHA_VANTAGE_API_KEY=$(pass show apis/alpha-vantage 2>/dev/null) \
python scripts/run_portfolio_review.py TICKER1:SHARES:COST TICKER2:SHARES:COST

cd ${CLAUDE_PLUGIN_ROOT}
```

Shares and cost basis are optional. Can pass Monarch holdings directly.

## After Getting Output

Present results in Warren's tone:
- Lead with composite score + rating
- Call out the weakest sub-score (the real risk)
- State entry/exit levels as concrete numbers, not ranges
- Connect back to the thesis from the four questions
- If R:R < 2:1, say so directly

## Usage Report

After any run, check API consumption:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts/financial-analysis
source .venv/bin/activate
python scripts/usage_tracker.py daily
```

If any API > 70% of free limit, flag it.
```

**Commit:**

```bash
git add skills/finance/stock-deep-dive/
git commit -m "feat(warren): add stock-deep-dive skill 📈"
```

---

## Task 6: Update trading-review SKILL.md

**Files:**
- Modify: `skills/finance/trading-review/SKILL.md`

**Current Mode B flow (lines 66–84):** After four questions → WebSearch → Check holdings → Give assessment.

**Change:** Replace "WebSearch the ticker/sector" with a call to `stock-deep-dive`.

**Find this block in Mode B:**

```markdown
**Then:**
- WebSearch the ticker/sector: recent earnings, news, analyst sentiment
- Check current holdings for correlation/concentration
- Review against time horizon and position sizing
- Give a specific assessment, not validation
```

**Replace with:**

```markdown
**Then:**
- Invoke `stock-deep-dive` skill to run the full analysis engine on the ticker
- Check current holdings (Monarch `get_account_holdings`) for correlation/concentration
- Review engine output against time horizon and position sizing from thesis
- Give a specific assessment using the composite score and entry/exit levels
- If the score contradicts the thesis — say so before anything else
```

**Commit:**

```bash
git add skills/finance/trading-review/
git commit -m "feat(warren): wire trading-review Mode B to stock-deep-dive 🔗"
```

---

## Task 7: Document required API keys

**Files:**
- Modify: `CLAUDE.md` (Warren's) — add API key table to MCP section

Add a section after "MCP Tools Available":

```markdown
## Financial Analysis Engine

Scripts live at `scripts/financial-analysis/`. Source: geogons/skill-financial-analyst (absorbed).

**API Keys (stored in pass):**

| pass path | env var | Status |
|-----------|---------|--------|
| `apis/finnhub` | `FINNHUB_API_KEY` | Required — analyst ratings, insider MSPR, earnings |
| `apis/alpha-vantage` | `ALPHA_VANTAGE_API_KEY` | Required — technicals, AI news sentiment (25/day limit) |
| `apis/mboum` | `MBOUM_API_KEY` | Optional — Congress trades, options flow |
| `apis/seeking-alpha-rapidapi` | `SEEKING_ALPHA_RAPIDAPI_KEY` | Optional — quant ratings |

Free with no key: yfinance, SEC EDGAR, ApeWisdom, StockTwits.

**Setup:** `cd scripts/financial-analysis && ./setup.sh`
**Status:** `python scripts/api_config.py status`
**Usage logs:** `python scripts/usage_tracker.py daily`
```

**Commit:**

```bash
git add CLAUDE.md
git commit -m "docs(warren): document financial-analysis engine and API keys 📝"
```

---

## Verification Checklist

After all tasks:

- [ ] `ls scripts/financial-analysis/scripts/*.py | wc -l` → 14
- [ ] `scripts/financial-analysis/.venv/` exists
- [ ] `python scripts/api_config.py status` shows READY for at least yfinance + SEC EDGAR (no key needed)
- [ ] `python scripts/run_deep_dive.py AAPL` produces output (partial data OK if API keys missing)
- [ ] `skills/finance/stock-deep-dive/SKILL.md` exists
- [ ] `trading-review/SKILL.md` Mode B references `stock-deep-dive`
- [ ] `.venv/` excluded from git tracking
- [ ] API key table in CLAUDE.md

## Missing API Keys

If Finnhub or Alpha Vantage aren't in pass yet, after the plan is done:

```bash
pass insert apis/finnhub       # then paste key from https://finnhub.io
pass insert apis/alpha-vantage # then paste key from https://alphavantage.co
```

The engine degrades gracefully — it'll still run with just yfinance + SEC EDGAR, just with lower data coverage.
