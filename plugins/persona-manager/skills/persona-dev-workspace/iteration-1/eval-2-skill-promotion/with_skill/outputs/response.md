# Response: Promoting Tax Calculations to a Skill

Yes, Wils — this is a textbook skill promotion case. The persona-dev skill is explicit on this: when a 3+ step ad-hoc workflow recurs 3+ times without an existing skill, it's time to draft a SKILL.md and propose it.

Quarterly tax math hits both bars comfortably (multi-step workflow, recurring 4-5 times). Here's how to actually make it happen:

---

## Why This Qualifies

From the persona-dev self-management rules:

> **Skill gap detection:** When handling a request that involves 3+ steps with no existing skill... After 3 occurrences, draft a SKILL.md and propose it to the user.

Quarterly estimated tax calculation is definitely 3+ steps — it typically involves:
1. Pulling YTD income (W2, 1099, business income)
2. Estimating deductions
3. Applying the appropriate tax bracket / SE tax rates
4. Calculating what's already been paid (withholding or prior quarterly payments)
5. Computing what's owed and when (Q1-Q4 deadlines)
6. Optionally stress-testing against safe harbor thresholds

That's a repeatable, non-trivial workflow that deserves a skill.

---

## What to Create

A new skill file at:

```
plugins/warren/skills/finance/quarterly-tax-estimate/SKILL.md
```

Here's a draft:

```markdown
---
name: quarterly-tax-estimate
description: Walk through estimated quarterly federal (and optionally state) tax calculations for the current tax year. Use this when the user asks about quarterly taxes, estimated payments, what they owe, Q1/Q2/Q3/Q4 estimates, or safe harbor calculations.
triggers:
  - quarterly taxes
  - estimated taxes
  - what do I owe
  - quarterly payment
  - safe harbor
  - tax estimate
  - self-employment tax
  - 1040-ES
---

# Quarterly Tax Estimate

## What This Skill Does

Walks through a full quarterly estimated tax calculation session: income gathering, deduction estimation, tax owed, prior payments, and the resulting estimated payment — with safe harbor check.

## Before You Start

Read `profile.md` for:
- Filing status (single, MFI, MFJ, HoH)
- Income sources (W2, 1099/self-employment, investment, rental)
- State of residence (for state tax layer)
- Any known deductions (mortgage interest, business expenses, retirement contributions)

If profile.md is missing this info, ask before proceeding.

## Workflow

### Step 1 — Gather YTD Income

Ask the user for (or pull from Monarch if connected):
- W2 income YTD
- 1099/freelance/business net income YTD
- Investment income (dividends, realized gains)
- Any other taxable income

Annualize each source if mid-year: `(YTD amount / months elapsed) * 12`

### Step 2 — Estimate Deductions

- Standard deduction (current year amount by filing status) OR itemized — ask which applies
- Self-employment deduction (50% of SE tax, if applicable)
- Qualified business income deduction (20% of QBI, if applicable)
- Retirement contributions (401k, SEP-IRA, IRA) — ask if any

Calculate estimated taxable income:
`Taxable Income = Gross Income - Deductions`

### Step 3 — Calculate Federal Tax

Apply current year tax brackets for the filing status. Show the math bracket by bracket.

If self-employed income exists:
- Calculate SE tax: `Net SE income * 0.9235 * 0.153`
- Add to income tax for total federal tax liability

### Step 4 — Credit for Prior Payments

Ask for:
- W2 withholding YTD
- Any prior quarterly estimated payments made this year (Q1, Q2, Q3)

`Tax Still Owed = Total Federal Tax - (W2 Withholding + Prior Quarterly Payments)`

### Step 5 — Current Quarter Payment

Determine the current quarter and its due date:
- Q1: April 15
- Q2: June 15
- Q3: September 15
- Q4: January 15 (following year)

Split remaining owed across remaining quarters (or recommend paying it all now if significantly behind).

### Step 6 — Safe Harbor Check

Safe harbor avoids underpayment penalties. The threshold is the lesser of:
- 100% of prior year's tax liability (110% if prior year AGI > $150k)
- 90% of current year's estimated tax liability

Show the user which threshold they're working against and whether they're on track.

### Step 7 — State Tax (Optional)

If the user wants state tax included:
- Ask for state, filing status, and state-specific deductions
- Apply state brackets or flat rate
- State estimated payment deadlines often mirror federal

### Step 8 — Summary

Present a clean summary:
```
Federal tax liability (estimated):    $X,XXX
Withholding + prior payments:        -$X,XXX
Remaining owed:                       $X,XXX
Recommended this quarter:             $X,XXX
Safe harbor threshold:                $X,XXX  [on track / behind]
Next payment due:                     [date]
```

## Memory

After completing:
- Save the session date, quarter, estimated liability, and recommended payment to MEMORY.md
- Note any assumptions made (income annualization method, deduction estimates)
- Flag if the user was significantly behind or ahead — that's worth tracking year over year

## What to Watch For

- If income is highly variable (freelance), note that estimates may need mid-quarter adjustment
- If the user had a major life event (marriage, new business, property sale), flag that a CPA review is warranted
- Never give this as definitive tax advice — it's a planning tool, not a filing tool
```

---

## How to Wire It Up

1. Create the file at `plugins/warren/skills/finance/quarterly-tax-estimate/SKILL.md`
2. Add the trigger phrases to Warren's `skill-rules.json` so forced-eval fires automatically — no manual `/skill` invocation needed
3. Bump Warren's version (patch increment — this is a skill addition, so it's a minor bump per the version rules)
4. Commit and push

After that, any time you say "quarterly taxes", "what do I owe", "estimated payment", etc., Warren will auto-load the workflow instead of walking through it fresh from scratch each time.

---

## Also Worth Doing: Note in MEMORY.md

Per the self-management rules, if Warren has a MEMORY.md, it would be worth adding a note that this workflow recurred and has now been promoted to a skill — that gives Warren context for future `/update --comprehensive` audits.

---

## Want Me to Just Do It?

Say the word and I'll:
1. Write the SKILL.md
2. Check and update `skill-rules.json`
3. Bump the version in both `plugin.json` and `marketplace.json`
4. Commit it all

The skill is live the moment the file exists — no reinstall required.
