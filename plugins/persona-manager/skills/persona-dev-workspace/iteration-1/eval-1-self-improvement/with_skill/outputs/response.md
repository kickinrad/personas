# Warren Self-Improvement Capability

Hey the user! A few months of Warren usage and you want him to actually *learn* — love it. This is exactly what the self-management system in the persona architecture is designed for. Let me walk through what we're adding and what already exists vs. what needs to be built.

---

## What Warren Already Has (Good News)

Warren's `CLAUDE.md` already has a `Self-Management` section, but it's light — it covers profile.md updates and memory topic file splitting. It does **not** have:

- Pattern-to-rule promotion logic (the "3 corrections → permanent rule" mechanic)
- Skill gap detection
- `/update --comprehensive` command definition

Warren also has a dashboard (`dashboard.html` + `open.sh`), which means he qualifies for the full Dashboard Pattern from the skill — including `/update --comprehensive` deep scan mode.

---

## What We're Adding

### 1. Pattern → Rule Promotion (Automatic Learning from Corrections)

This is the core of what you asked for. Here's the mechanism:

**How it works:**
- Warren watches for repeated corrections or preferences across sessions
- He tracks these in MEMORY.md (already his memory store)
- After 3+ occurrences of the same pattern, he proactively proposes a CLAUDE.md rule
- You approve, he writes it

**What Warren's CLAUDE.md needs added** — a proper `Self-Management` block replacing the current thin version:

```markdown
## Self-Management

This persona lives at `~/projects/personal/personas/plugins/warren/`.
All files are immediately live — no reinstall needed.

### When to update what

| File | Update when | How |
|------|------------|-----|
| `profile.md` | Stable facts change (new account, income shift, priority changes) | Propose → write with approval |
| `MEMORY.md` | Something worth remembering across sessions happened | Write directly |
| `CLAUDE.md` (rules) | A behavioral pattern should become permanent | Propose → write with approval |
| New skill file | A 3+ step workflow recurs with no existing skill | Draft → propose to user |
| `TASKS.md` | Task status changes | Write directly |

### Pattern → Rule promotion

When you notice the same correction or preference 3+ times across sessions
(visible in memory), propose making it permanent:

> "I've noticed you always ask me to X. Want me to add that as a rule in my CLAUDE.md?"

Then write the change directly to CLAUDE.md with approval.

### Skill gap detection

When handling a request that involves 3+ steps with no existing skill:
- Note it in memory as a potential skill gap
- After 3 occurrences, draft a SKILL.md and propose it to the user
- Once approved, write it to `skills/finance/{skill-name}/SKILL.md` — it's live immediately

### Periodic self-audit

Monthly (or triggered by `/update --comprehensive`):

1. Read MEMORY.md and count recurring themes — friction points, corrections, repeated questions
2. Identify what keeps getting handled ad-hoc that should be a skill
3. Propose changes before writing anything:
   - Recurring correction (3+ sessions) → propose a CLAUDE.md behavioral rule
   - 3+ step ad-hoc workflow without a skill → draft a SKILL.md
   - Outdated profile.md fact → flag for the user to update
4. Present all proposals clearly. You approve before any file is changed.

The key distinction: MEMORY.md stores what happened; CLAUDE.md rules what always happens.
Don't promote a one-off to a rule — look for the pattern first.
```

---

### 2. `/update --comprehensive` Command

Warren already has a dashboard, so he already supports the `/update` pattern from the skill. We need to explicitly define both commands in his CLAUDE.md.

**What to add to CLAUDE.md** — a `Commands` section:

```markdown
## Commands

**`/update`** — weekly sync (great before reviews):
1. Triage stale `TASKS.md` items (overdue? blocked? done?)
2. Pull fresh data from Monarch MCP (accounts, budgets, cashflow)
3. Prompt to open the dashboard and review

**`/update --comprehensive`** — deep audit mode (monthly or when things feel off):
1. Everything in `/update`, plus:
2. Read MEMORY.md — count recurring themes, corrections, friction points
3. For any pattern appearing 3+ sessions: propose a CLAUDE.md behavioral rule
4. Identify 3+ step workflows handled ad-hoc with no existing skill → draft a SKILL.md
5. Flag any profile.md facts that look stale (account closed, income changed, etc.)
6. Present ALL proposals in a numbered list — nothing changes without approval
7. After approval, write changes directly to the relevant files
```

---

### 3. Memory Tagging for Pattern Detection

For the promotion mechanic to work, Warren needs to tag corrections in MEMORY.md in a way he can scan later. We add a lightweight convention:

**Memory format for corrections** (Warren writes this automatically when corrected):

```markdown
## Corrections / Preferences
<!-- PATTERN-TRACK: Warren tracks these for rule promotion -->

- [2026-01-15] User prefers gross income figures, not net, when discussing salary benchmarks
- [2026-02-03] User prefers gross income figures (reminded again)
- [2026-02-28] User prefers gross income — flagging for CLAUDE.md promotion (3rd time)
```

When Warren runs `/update --comprehensive`, he scans for entries that appear 3+ times or are flagged, and surfaces them as rule proposals.

---

## The Exact Files Changed

### File 1: `plugins/warren/CLAUDE.md`

**Replace** the current thin `Self-Management` section (lines 107-110) with the full block above.

**Add** a new `Commands` section after `Skills Auto-Activate`.

**Add** to `Important Rules`:
```
8. **Track corrections** — when corrected, note it in MEMORY.md under "Corrections / Preferences"; after 3 occurrences, propose a CLAUDE.md rule
```

### File 2: No new skill files needed

The self-improvement logic lives in CLAUDE.md rules (it's behavioral), not a skill. A skill would be appropriate if the `/update --comprehensive` workflow gets complex enough to need step-by-step procedure docs — but Warren's existing skill structure handles the financial review pieces, and the audit logic is simple enough to inline.

### File 3: `plugins/warren/TASKS.md` (if it doesn't exist)

Warren has a dashboard but may be missing `TASKS.md`. We'd create it with the standard format:

```markdown
# Warren Tasks

## Active

## Waiting On

## Someday

## Done
```

---

## What You'll See in Practice

**Session-to-session learning:**
After you correct Warren (e.g., "stop recommending index funds for my taxable account, I'm already maxed on that"), he notes it in MEMORY.md. If you correct the same pattern two more sessions, Warren says:

> "I've noticed you've redirected me on taxable account recommendations 3 times now. Here's what I'd add as a permanent rule: 'Don't recommend additional index fund purchases for taxable accounts — user is already at target allocation.' Want me to write that into my CLAUDE.md?"

You say yes, it's done. Next session it's in context automatically.

**`/update --comprehensive` flow:**
Warren reads MEMORY.md, identifies patterns, and presents something like:

```
Comprehensive audit complete. Here's what I found:

PROPOSED RULE CHANGES (3 items):
1. [3 corrections] Add rule: "Always show gross income figures, not net"
2. [4 corrections] Add rule: "Don't flag dining overspend if it's a client meal — ask first"
3. [2 corrections — not yet 3] Watching: preference for weekly snapshots over monthly

PROPOSED NEW SKILLS (1 item):
4. Tax-loss harvesting review — you've asked me to walk through this 3 times ad-hoc.
   I can formalize it as a skill. Want me to draft a SKILL.md?

STALE PROFILE.md FLAGS (1 item):
5. profile.md references your Ally savings account — you closed that in January.
   Want me to remove it?

Approve all, approve some, or skip?
```

---

## Version Bump

After writing these changes to CLAUDE.md:
- Bump `plugin.json` and `marketplace.json` from current version to next **minor** (new behavioral capability, not just docs)

---

## Ready to Execute?

I've scoped exactly what changes, which files, and where they go. If you give the go-ahead, I'll:
1. Edit `plugins/warren/CLAUDE.md` with the Self-Management block and Commands section
2. Add rule #8 to Important Rules
3. Create `plugins/warren/TASKS.md` if it's missing
4. Bump versions in both JSON files
5. Commit with `feat(warren): add self-improvement and /update --comprehensive`

One question before I write: do you want the `/update --comprehensive` audit to also check whether Warren's *existing skills* still match your usage patterns (e.g., if you never trigger `trading-review`, should it be retired or reworked)? The skill spec supports that — just want to confirm before I bake it in.
