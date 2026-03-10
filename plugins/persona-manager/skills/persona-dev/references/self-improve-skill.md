---
name: self-improve
description: Self-improvement workflow for evolving this persona — memory management, rule promotion, skill creation, tool creation, and periodic audits. Triggers when you notice recurring patterns, want to propose a new rule or skill, or it's time for a self-audit.
triggers:
  - self-improve
  - self-audit
  - time for a self-audit
  - promote this to a rule
  - this should be a skill
  - update my rules
  - improve yourself
---

# Self-Improvement

This persona lives at `~/.personas/{name}/`. All files are immediately live — no reinstall needed.

## When to Update What

| File | Update when | How |
|------|------------|-----|
| `MEMORY.md` | Something worth remembering happened | Write directly |
| `profile.md` | Stable facts change (new account, preference shift) | Propose, write with approval |
| `CLAUDE.md` (rules) | A behavioral pattern should become permanent | Propose, write with approval |
| New skill file | A 3+ step workflow recurs with no existing skill | Draft, propose to user |
| New script/tool | A capability gap needs automation | Draft, propose to user |
| `docs/*.md` | Stable domain context too long for profile.md | Write with approval |

## Level 1: Memory Management (Automatic)

Every session, update `.claude/memory/MEMORY.md` with:
- Session outcomes and key decisions
- User corrections and discovered preferences
- Observed patterns ("user always asks for X on Mondays")
- Things that worked well or poorly

**Conventions:**
- Use date headers (`## YYYY-MM-DD`)
- Keep entries concise — one line per learning
- Don't duplicate what's already in profile.md
- Don't create extra memory files (no `corrections.md`, `feedback.md`) — MEMORY.md is the single source

## Level 2: Rule Promotion (Propose to User)

When you notice the same correction or preference **3+ times** across sessions (visible in memory):

1. Cite the evidence: "I've seen this in sessions on [dates]"
2. Propose the rule: "Want me to add this to my CLAUDE.md?"
3. Wait for approval
4. Write the change directly to CLAUDE.md
5. Commit: `improve(self): {description}`

**What makes a good rule:**
- Specific and actionable ("always group by store section", not "be more organized")
- Based on repeated evidence, not a single occurrence
- Fills a gap — doesn't duplicate an existing rule

## Level 3: Skill Creation (Propose to User)

When handling a request that involves **3+ steps** with no existing skill, and it has happened **3+ times**:

1. Note it in memory as a potential skill gap on first occurrence
2. After 3 occurrences, draft a `SKILL.md` with:
   - YAML frontmatter (name, description, triggers)
   - Clear step-by-step workflow
   - Expected output format
3. Propose the skill with a preview
4. On approval, write to `skills/{domain}/{skill-name}/SKILL.md`
5. Update the Skills table in CLAUDE.md
6. Commit: `feat(self): add {skill-name} skill`

## Level 4: Tool Creation (Propose to User)

When a capability gap needs automation beyond conversation:

1. Identify what's needed (script, reference doc, MCP addition)
2. Draft the artifact:
   - Scripts go to `scripts/`
   - Reference docs go to `docs/`
   - MCP proposals describe the server + required domains
3. Propose with a preview
4. On approval, write the files
5. For MCP changes: remind user to update `.mcp.json` and `.claude/settings.json`
6. Commit: `feat(self): add {tool-name}`

## Periodic Audit

Run monthly, or when the user says "time for a self-audit":

1. **Read memory** — scan MEMORY.md for recurring themes, friction points, repeated questions
2. **Check for promotable patterns:**
   - Recurring correction (3+ sessions) → propose CLAUDE.md rule
   - Recurring multi-step workflow → propose new SKILL.md
   - Outdated profile.md fact → flag for user update
3. **Review existing rules** — any that no longer apply? Propose removal
4. **Review existing skills** — any that need updating based on recent sessions?
5. **Present all proposals** clearly in a single summary:

```
## Self-Audit Results

### Proposed Rule Changes
- **Add:** "{rule}" — seen in [dates], evidence: {summary}
- **Remove:** "{rule}" — no longer relevant because {reason}

### Proposed New Skills
- **{skill-name}** — handles {workflow}, triggered {N} times ad-hoc

### Profile.md Updates
- **Flag:** {fact} may be outdated — please verify

### No Action Needed
- Memory is clean, rules are current, no skill gaps detected
```

6. Wait for approval on each proposal before writing anything

## The Key Distinction

**Memory stores what happened. Rules define what always happens.**

Don't promote a one-off to a rule — look for the pattern first. Three occurrences is the threshold, not one strong opinion.
