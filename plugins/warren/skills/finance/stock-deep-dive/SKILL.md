---
name: stock-deep-dive
description: >
  Multi-API stock analysis engine. Produces composite score, Buy/Hold/Sell rating,
  3 entry levels, 3 exit targets, and stop loss for any ticker.
  Triggered from trading-review Mode B after the four thesis questions are answered.
  Also triggered for: stock deep dive, analyze TICKER, score this stock, entry levels,
  price targets, technical analysis, fundamental analysis, buy rating, sell rating.
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

If any API > 70% of free limit, flag it to the user.
