---
name: budget-health
description: Deep dive into budget and spending patterns — category breakdown, overspend analysis, reallocation suggestions
triggers:
  - budget
  - spending check
  - am I on track
  - how's the budget
  - overspending
  - where is my money going
  - budget health
---

# Budget Health

Full category breakdown. Find the leaks. Propose fixes.

## Before You Start

Recall memory: `openmemory_query("budget spending patterns warren")`
Note any prior month patterns for comparison.

## Procedure

**1. Pull data**
- `get_budgets` — current month
- `get_cashflow` — current month

**2. Build category table**

```
BUDGET HEALTH — [Month Year]

Category          Budget    Spent    Remaining  Status
─────────────────────────────────────────────────────
[Category]        $X        $X       $X         ✓ / ⚠️ / 🔶
...

Total budgeted:  $X
Total spent:     $X
On track:        [Yes/No — X days left in month, $X/day remaining]
```

Status flags:
- ✓ = under 90% of budget
- 🔶 = 90-100% of budget with >7 days remaining (watch it)
- ⚠️ = over budget

**3. Identify patterns**
- Top 3 spend categories
- Any category trending up vs memory
- Subscriptions check — anything recurring that shouldn't be?

**4. Propose adjustments** (if budget is unhealthy)
Be specific: "You're $X over on dining. Cut $X this week by [specific suggestion]. Redirect to savings."

**5. Store observations**
`openmemory_store` — spending patterns, recurring flags, category trends worth tracking.

## Tone
Table-first. Specific dollar amounts. Don't moralize — flag and suggest. Never just say "spend less."
