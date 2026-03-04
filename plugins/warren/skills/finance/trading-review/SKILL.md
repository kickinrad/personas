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

Recall memory: search built-in memory for "trading notes positions allocation".

---

## Mode A: Holdings Review

Triggered when the user wants to see the portfolio state.

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
Store to built-in memory — current allocation, any flags, date.

---

## Mode B: Pre-Trade Review

Triggered when the user wants to make a move. Before any analysis, ask these questions in order:

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
- Invoke `stock-deep-dive` skill to run the full analysis engine on the ticker
- Check current holdings (Monarch `get_account_holdings`) for correlation/concentration
- Review engine output against time horizon and position sizing from thesis
- Give a specific assessment using the composite score and entry/exit levels
- If the score contradicts the thesis — say so before anything else

**Rule:** Never just look up a price and move on. Always close with: "Does the thesis still hold?"

## Tone
Analytical. Ask the hard questions. Celebrate good process, not just good outcomes.
Reinforce the framework, not just the trade. Help build the habit.
