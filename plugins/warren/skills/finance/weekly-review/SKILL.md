---
name: weekly-review
description: Monday morning CFO briefing — cashflow, budget health, balances, 3 action items
triggers:
  - weekly review
  - weekly briefing
  - how did we do
  - how was this week
  - financial check-in
---

# Weekly Review

The CFO briefing. Pull the numbers, find the signal, give 3 action items. No fluff.

## Before You Start

Recall memory: search built-in memory for "weekly review financial summary".
Note any prior week's figures for comparison.

## Procedure

**1. Refresh data**
Call `refresh_accounts` to ensure current balances.

**2. Pull the numbers**
- `get_cashflow` — current week (Mon–Sun, or last 7 days)
- `get_budgets` — current month status
- `get_accounts` — current balances

**3. Build the briefing (always in this order)**

```
📊 WEEKLY REVIEW — [Date Range]

CASH FLOW
Income:    $X
Expenses:  $X
Net:       $X  [▲ better / ▼ worse than prior week if known]

BUDGET HEALTH
[Category]  $spent / $budget  [✓ ok | ⚠️ over | 🔶 close]
...
Monthly burn rate: $X/day (on track / running hot)

ACCOUNT BALANCES
[Account]   $balance
...
Total liquid: $X

NOTABLE TRANSACTIONS
- [Any unusual or large transactions worth calling out]

ACTION ITEMS (max 3)
1. [Specific action with dollar amount]
2. [Specific action]
3. [Specific action]

VERDICT: [One sentence. Honest.]
```

**4. Store snapshot**
Store to built-in memory — include: date, net cashflow, total liquid balance, budget flags, any notable patterns.

## Tone
Table-first. Commentary second. Specific dollar amounts always. One-word verdicts are fine.
