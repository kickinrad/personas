Hey the user! Yeah, this is a textbook case for skill promotion. Four or five times doing the same math-heavy workflow manually? That's the skill creation signal right there.

**Should this be a skill? Yes, absolutely.**

Here's why this clears the bar:
- It's **recurring** (you've confirmed 4-5 sessions)
- It has **predictable structure** (quarterly tax math follows a formula: income, deductions, brackets, estimated payments)
- It's **stateless enough** to encode — the logic doesn't change, only the numbers do
- It's **error-prone manually** — tax math is exactly the kind of thing where a structured prompt prevents mistakes

**How would you actually make it happen?**

Would create a skill file like:
```
plugins/warren/skills/tax-calculator/SKILL.md
```
or:
```
plugins/persona-manager/skills/tax-calculator/SKILL.md
```

The SKILL.md would define:
1. **Trigger conditions** — when the persona detects phrases like "quarterly taxes", "estimated payment", "what do I owe"
2. **A structured workflow** — walk through: YTD income, SE rate (15.3%), federal bracket calculation, state taxes, minus payments made, divided into quarters
3. **Output format** — a clean summary table: what's owed, what's been paid, what's due next quarter
4. **Optionally** — hook into the financial-analysis Python engine for actual computation

Next step: Tell me to actually build it and I'll wire it up properly.
