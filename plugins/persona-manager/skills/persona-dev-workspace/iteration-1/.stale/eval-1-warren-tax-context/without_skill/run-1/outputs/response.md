# Response: Warren Tax Context

## Diagnosis

Warren asks about your tax situation at the start of weekly reviews because that context isn't in his permanent setup files — it exists only implicitly, scattered across the profile (income sources, account notes), but there's no explicit, consolidated tax-filing section he can read without having to reconstruct it from first principles every session.

The fix is straightforward: **add a dedicated Tax Filing Context section to `profile.md`**. This is the right file because it's the permanent user context Warren reads every session before doing anything else (per his `CLAUDE.md` Session Start rules). It is not the right thing to put in `CLAUDE.md` (behavioral rules) or `MEMORY.md` (dynamic session learnings) — this is stable, structural context about who you are as a taxpayer, not a rule and not something that changes week to week.

---

## File to Update

```
/home/wilst/projects/personal/personas/plugins/warren/profile.md
```

---

## What to Add

Insert the following section **between the existing "Income Sources" section and the "2025 Tax Summary" section** (after line 108, before line 112 in the current file). This placement groups it logically near income — tax situation flows naturally from income type.

```markdown
---

## Tax Filing Context (Stable)

| Key | Detail |
|-----|--------|
| Filing status | **Married Filing Jointly** (with Sako) |
| Primary income types | W2 (Sako — Upspring) + Self-employment / Schedule C (Wils — b.f.f.) |
| Self-employment tax | Yes — SE tax applies to b.f.f. net profit. Deduct 50% of SE tax from gross income. |
| Quarterly estimated taxes | **Required** — Wils has no withholding on b.f.f. income. 2026 quarters: Apr 15, Jun 16, Sep 15, Jan 15. |
| Home office deduction | Simplified method — ~200 sqft / ~1,200 sqft total = ~1/6. Max $5/sqft = $1,000/year. |
| ACA / health insurance | Marketplace policy (Sentara, 955447). ACA premium deduction applies for Wils as self-employed. |
| Inherited IRA / RMDs | Annual RMDs required through 2034. Must fully deplete by Dec 31, 2035. Pair with SEP-IRA contributions. |
| SEP-IRA | Self-employed retirement vehicle — contributions reduce Schedule C net profit and AGI. |
| State | Virginia — files VA state return separately. |
| Dad's gift (~$1,150/mo) | NOT taxable income. Gift from father's personal checking. Do not include in income calculations. |
| Otherthings.jpg (Sako) | Sako's side business — tracked separately, not consolidated into household Schedule C. |

*This section should be treated as stable context. Update only when filing status, employment status, or structure changes.*
```

---

## Why This Works

**Profile.md is read every session before anything else** — Warren's `CLAUDE.md` says so explicitly under Session Start. Adding the tax context here means Warren has it available at session open without asking. The format mirrors the existing table style in `profile.md`, so it fits naturally.

**This is not MEMORY.md material.** MEMORY.md is for dynamic learnings — observations Warren picks up during sessions. The filing status (MFJ), income types (W2 + freelance), and SE tax obligations are stable structural facts, not session-learned insights.

**The 2025 Tax Summary section already exists** (lines 112–128) and covers the specific numbers. This new section covers the *standing context* — the stuff Warren needs to orient himself before looking at any numbers. Think of the new section as "who are we as taxpayers" and the existing 2025 Tax Summary as "what did we do last year."

---

## Complete Edit (with surrounding context for placement)

In `/home/wilst/projects/personal/personas/plugins/warren/profile.md`, find this existing block:

```markdown
*Note: Always fetch live income from Monarch `get_cashflow` for current period analysis*

---

## 2025 Tax Summary (derived analysis — not live data)
```

Replace it with:

```markdown
*Note: Always fetch live income from Monarch `get_cashflow` for current period analysis*

---

## Tax Filing Context (Stable)

| Key | Detail |
|-----|--------|
| Filing status | **Married Filing Jointly** (with Sako) |
| Primary income types | W2 (Sako — Upspring) + Self-employment / Schedule C (Wils — b.f.f.) |
| Self-employment tax | Yes — SE tax applies to b.f.f. net profit. Deduct 50% of SE tax from gross income. |
| Quarterly estimated taxes | **Required** — Wils has no withholding on b.f.f. income. 2026 quarters: Apr 15, Jun 16, Sep 15, Jan 15. |
| Home office deduction | Simplified method — ~200 sqft / ~1,200 sqft total = ~1/6. Max $5/sqft = $1,000/year. |
| ACA / health insurance | Marketplace policy (Sentara, 955447). ACA premium deduction applies for Wils as self-employed. |
| Inherited IRA / RMDs | Annual RMDs required through 2034. Must fully deplete by Dec 31, 2035. Pair with SEP-IRA contributions. |
| SEP-IRA | Self-employed retirement vehicle — contributions reduce Schedule C net profit and AGI. |
| State | Virginia — files VA state return separately. |
| Dad's gift (~$1,150/mo) | NOT taxable income. Gift from father's personal checking. Do not include in income calculations. |
| Otherthings.jpg (Sako) | Sako's side business — tracked separately, not consolidated into household Schedule C. |

*This section should be treated as stable context. Update only when filing status, employment status, or structure changes.*

---

## 2025 Tax Summary (derived analysis — not live data)
```

---

## Nothing Else Needs Changing

- **CLAUDE.md** — no change needed. Warren's behavioral rules already say "read profile.md every session." The new data will be picked up automatically.
- **MEMORY.md** — doesn't exist yet and isn't needed for this. If/when it's created, it should not duplicate this stable context.
- **weekly-review SKILL.md** — no change needed. The skill's "Before You Start" step recalls memory; Warren will now have the tax context from profile.md before the skill even runs.
- **CLAUDE.md Session Start** — no change needed. It already reads profile.md unconditionally.
