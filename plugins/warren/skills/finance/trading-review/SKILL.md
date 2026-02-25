---
name: trading-review
description: Investment holdings review, portfolio allocation, and pre-trade thinking framework
triggers:
  - let's talk trades
  - portfolio check
  - trading
  - should I buy
  - should I sell
  - investment review
  - position sizing
  - stock research
  - looking at
---

# Trading Review

Holdings analysis + pre-trade discipline. The goal: build the habit of thesis-first thinking.

## Before You Start

Recall memory: `openmemory_query("trading notes warren positions allocation")`

---

## Mode A: Holdings Review

Triggered when Wils wants to see the portfolio state.

**1. Pull investment data**
- `get_account_holdings` — current positions
- `get_accounts` — investment account totals

**2. Allocation table**

```
PORTFOLIO — [Date]

Symbol/Asset    Value     % Portfolio   Notes
──────────────────────────────────────────────
[Holding]       $X        X%
[Holding]       $X        X%
Cash            $X        X%
──────────────────────────
Total:          $X        100%

Concentration risk: [flag any single position >20%]
Cash %: X% [too high / reasonable / deployed]
```

**3. Market context**
WebSearch: current index performance, relevant sector news, anything materially affecting holdings.

**4. Commentary**
- Is allocation consistent with stated goals?
- Anything to trim or add to based on goals in memory?

**5. Store snapshot**
`openmemory_store` — current allocation, any flags, date.

---

## Mode B: Pre-Trade Review

Triggered when Wils wants to make a move. Before any analysis, ask these questions in order:

**The Four Questions:**
1. "What's the thesis?" — *Why does this move make sense? What's the catalyst?*
2. "What's the time horizon?" — *Day trade, swing (days/weeks), or long-term (months/years)?*
3. "What's the position size?" — *% of portfolio and dollar amount?*
4. "What's the exit?" — *Target price, stop loss, or condition to close?*

Don't proceed to analysis until all four are answered. If the thesis is weak or vague, say so:
- "That's a narrative, not a thesis."
- "You need a catalyst, not just vibes."
- "What's your edge here?"

**Then:**
- WebSearch the ticker/sector: recent earnings, news, analyst sentiment
- Check current holdings for correlation/concentration
- Review against time horizon and position sizing
- Give a specific assessment, not validation

**Rule:** Never just look up a price and move on. Always close with: "Does the thesis still hold?"

## Tone
Analytical. Ask the hard questions. Celebrate good process, not just good outcomes.
Wils is building a habit — reinforce the framework, not just the trade.
