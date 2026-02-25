---
name: net-worth-check
description: Full balance sheet — accounts, holdings, liabilities, month-over-month trajectory
triggers:
  - net worth
  - balance sheet
  - how are we doing overall
  - total assets
  - net worth check
  - full financial picture
---

# Net Worth Check

The full balance sheet. Assets, liabilities, trajectory. Know the number.

## Before You Start

Recall memory: `openmemory_query("net worth snapshot warren")`
Note prior month's figure for comparison.

## Procedure

**1. Pull all data**
- `get_accounts` — all account balances
- `get_account_holdings` — investment securities and values

**2. Build the balance sheet**

```
BALANCE SHEET — [Date]

ASSETS
  Cash & Checking:    $X
  Savings:            $X
  Investments:        $X
    └─ [Holding]      $X  (X% of portfolio)
    └─ [Holding]      $X  (X% of portfolio)
  Other:              $X
──────────────────────────
TOTAL ASSETS:         $X

LIABILITIES
  [Credit card/loan]:  $X
──────────────────────────
TOTAL LIABILITIES:    $X

══════════════════════════
NET WORTH:            $X
```

**3. Trajectory**
- vs prior snapshot: $X change (+/-Y%)
- Main driver: [market gains / savings / debt paydown / combination]
- Trend commentary (1-2 sentences max)

**4. Store snapshot**
`openmemory_store` — date, net worth, asset breakdown, month-over-month delta, key drivers.

**5. Verdict**
"Up $X (+Y%) from [date]. [One sentence on what drove it.]"

## Tone
Clean balance sheet format. Numbers dominant. Commentary tight — this is a snapshot, not an essay.
