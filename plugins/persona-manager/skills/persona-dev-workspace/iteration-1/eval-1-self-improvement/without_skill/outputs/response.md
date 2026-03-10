# Warren Self-Improvement: Design & Implementation

Great feature request, the user. This is a two-part problem: **passive learning** (absorbing corrections over time) and **active auditing** (`/update --comprehensive`). Here's how I'd build both.

---

## Part 1: Passive Self-Improvement — Learning From Corrections

### The Mechanism

Warren already has a memory system (`plugins/warren/.claude/memory/`) and a self-management note in his `CLAUDE.md`:

> All files here are immediately live — no reinstall needed.

The missing piece is a **rule-capture workflow**: when Warren is corrected, he should recognize the correction, log it, and after enough repetitions, promote it to a permanent rule.

### Implementation

**1. Add a `corrections.md` memory file**

Create `plugins/warren/.claude/memory/corrections.md` as the running log:

```markdown
# Warren Correction Log

Format: [Date] | [Context] | [What I did] | [Correction] | [Count]

---
2026-02-10 | trading-review | Recommended rebalancing during earnings week | "Don't suggest rebalancing during earnings — wait until after" | 1
2026-02-18 | budget-health  | Flagged dining as overspend | "Dining in Feb includes Valentine's — don't flag seasonal spikes" | 1
2026-02-18 | trading-review | Recommended rebalancing during earnings week | (same as above) | 2
```

**2. Add a correction-detection rule to Warren's `CLAUDE.md` (Important Rules section)**

```markdown
8. **Capture corrections** — When corrected mid-session (user says "no, that's wrong", "stop doing that", "I've told you before", or similar), immediately:
   a. Acknowledge the correction
   b. Append an entry to `.claude/memory/corrections.md` in this format: `[Date] | [Skill/Context] | [What I did] | [Correction] | [Count: 1]`
   c. If the same correction already exists, increment the count
   d. If count reaches 3: propose promoting it to a permanent rule in CLAUDE.md or the relevant SKILL.md
```

**3. Promotion threshold**

When count hits 3, Warren surfaces it:

> "I've been corrected on this three times now. Want me to add a permanent rule? I'd add it to [CLAUDE.md / the trading-review skill] so I never make this mistake again."

If yes, Warren writes the rule directly to the appropriate file — `CLAUDE.md` for general behavior, or the relevant `SKILL.md` for workflow-specific rules.

### Why 3?

One correction could be a one-off. Two is a pattern. Three is a rule. Keeps the noise low without being too conservative.

---

## Part 2: Active Auditing — `/update --comprehensive`

### What It Does

This command triggers Warren to audit himself: do his current skills still reflect how you actually use him? Are there patterns in memory that should be skills? Are there skills that are never triggered?

### Implementation as a Skill

Create `plugins/warren/skills/meta/self-audit/SKILL.md`:

```yaml
---
name: self-audit
description: Audits Warren's skills, rules, and memory against actual usage patterns. Triggers a comprehensive review of whether the persona still fits how the user works.
triggers:
  - /update --comprehensive
  - audit warren
  - warren self-audit
  - update warren's skills
---
```

**Skill procedure:**

```markdown
# Self-Audit Procedure

## 1. Read Current State
- Read `CLAUDE.md` — list all active rules and skills
- Read `.claude/memory/corrections.md` — list all corrections (especially count >= 2)
- Read `.claude/memory/MEMORY.md` and topic files — identify recurring themes

## 2. Analyze Skills vs Usage
For each skill in `skills/finance/`:
- Is this skill referenced in recent memory notes?
- Have you been asked to do this manually (without the trigger phrase)?
- Any corrections that apply specifically to this skill's workflow?

Flag skills as: ACTIVE | DORMANT | NEEDS_UPDATE

## 3. Identify Missing Skills
Look for patterns in memory that repeat across sessions but don't have a skill:
- Topics you discuss that follow a consistent workflow
- Questions the user asks regularly that don't map to a trigger
- Workflows you improvise every time

Flag these as: CANDIDATE_SKILL

## 4. Review Active Rules
For each rule in `## Important Rules`:
- Is it still relevant given current usage?
- Any corrections that contradict or supersede it?

## 5. Generate the Audit Report

Present as:

---
WARREN SELF-AUDIT — [Date]

SKILLS REVIEW
[skill-name]   STATUS   Notes
...

CANDIDATE NEW SKILLS
- [Pattern observed] → suggested skill name + trigger phrase

RULE UPDATES SUGGESTED
- [Rule #X] — suggest change because [reason from corrections or usage]

PROMOTABLE CORRECTIONS (count >= 2)
- [correction] — ready to promote? Y/N

OVERALL: [One honest sentence about whether Warren still fits how you work]
---

## 6. Prompt for Action
For each flagged item, ask: "Want me to make this change now?"
Apply changes immediately to CLAUDE.md or SKILL.md files — no reinstall needed.
```

### Wiring It Up

Add to the Skills Auto-Activate table in Warren's `CLAUDE.md`:

| Say this... | Skill activates | What happens |
|-------------|-----------------|--------------|
| `/update --comprehensive`, "audit warren" | `self-audit` | Reviews skills, rules, memory — proposes updates |

And add the skill to `skill-rules.json` so it force-evals on the exact command:

```json
{
  "rules": [
    {
      "pattern": "/update --comprehensive",
      "skill": "skills/meta/self-audit/SKILL.md",
      "match": "exact"
    }
  ]
}
```

---

## Summary of Changes

| File | Change |
|------|--------|
| `plugins/warren/CLAUDE.md` | Add Rule #8 (capture corrections), add self-audit to trigger table |
| `plugins/warren/.claude/memory/corrections.md` | Create (empty initially) |
| `plugins/warren/skills/meta/self-audit/SKILL.md` | Create new skill |
| `plugins/warren/skill-rules.json` | Add `/update --comprehensive` forced-eval |

---

## One Design Note

The passive correction capture only works if Warren *recognizes* he's being corrected. The rule language in CLAUDE.md matters here — the list of correction signals ("no, that's wrong", "stop doing that", "I've told you before") should be tuned based on how you actually give feedback. If your style is more subtle ("actually, let's not do that"), add those patterns.

Want me to implement all of this now?
