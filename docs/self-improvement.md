# Self-Improvement

Personas are designed to evolve. Every persona ships with a `self-improve` skill (`skills/self-improve/SKILL.md`) and hooks (`hooks.json`) that automate the evolution process. They have full write access to their own directory and can grow new capabilities over time through a structured five-level model.

## The Five Levels

### Level 1: Memory (Automatic)

Every session, the persona writes learnings to `.claude/memory/MEMORY.md`. This happens automatically — no user action needed.

**What gets stored:**
- Session outcomes and decisions
- User corrections and preferences discovered
- Patterns observed ("user always asks for X on Mondays")
- Things that worked well or poorly

**Example:**
```
## 2026-03-08

- User prefers Mediterranean-style meals on weeknights
- Household is doing low-carb this month — adjust all meal plans
- Grocery list format: group by store section, not by recipe
```

Memory is the raw material for all other levels. It accumulates context that makes the persona more effective session after session.

**Hooks automate this:** The Stop hook reminds the persona to update memory before ending each session. The PreCompact hook saves context before compaction so nothing is lost mid-session.

### Level 2: Rule Promotion (Claude Proposes, User Approves)

When a pattern appears 3 or more times in memory, the persona proposes making it a permanent behavioral rule in `CLAUDE.md`.

**The flow:**
1. Persona notices a recurring correction or preference in memory
2. It proposes: "I've noticed you always ask me to group groceries by store section. Want me to add that as a rule?"
3. User approves
4. Persona writes the rule to its own `CLAUDE.md`

**Example rule promotion:**
```markdown
## Important Rules
- Always group grocery lists by store section, not by recipe
```

The persona can also propose updates to `profile.md` when stable facts change (new account, shifted preference).

### Level 3: Skill Creation (Claude Proposes, User Approves)

When the persona handles a multi-step workflow ad-hoc 3 or more times without an existing skill, it proposes creating one.

**The flow:**
1. Persona notes in memory: "Handled pantry audit again — no skill for this"
2. After 3 occurrences, it drafts a `SKILL.md`
3. It proposes the skill to the user with a preview
4. User approves
5. Persona writes `skills/{domain}/{skill-name}/SKILL.md` — it is live immediately

**Example:**
```markdown
---
name: pantry-audit
description: Full pantry inventory check — what's running low, what's expiring, what to restock.
triggers:
  - pantry audit
  - what do we have
  - check the pantry
---

# Pantry Audit

## Steps
1. Read current pantry inventory from Keep note
2. Check for items expiring within 7 days
3. Cross-reference with this week's meal plan
4. Generate restock recommendations
5. Update pantry note with current state
```

### Level 4: Tool Creation (Claude Proposes, User Approves)

When a persona needs capabilities beyond conversation — scripts, data processing, new integrations — it can create tools.

**What this includes:**
- Writing scripts to `scripts/` (data fetchers, formatters, analyzers)
- Proposing new MCP server additions to `.mcp.json`
- Creating reference documents in `docs/`
- Building dashboards (`dashboard.html` + `open.sh`)

**Example:**
```bash
# scripts/fetch-prices.sh
# Fetches current stock prices for portfolio holdings
curl -s "https://api.example.com/quotes?symbols=$1" | jq '.results[]'
```

### Level 5: Publish (User-Initiated Only)

Publishing is always a manual decision. The persona never publishes itself.

**Steps:**
1. Bump version in `plugin.json`
2. Commit and push the persona's own git repo
3. Others can clone or pull the updated persona into their `~/.personas/`

## The Pattern Promotion Rule

The "3+ occurrences" threshold is the core heuristic:

| Occurrences | Action |
|-------------|--------|
| 1 | Note it in memory |
| 2 | Note the recurrence in memory |
| 3+ | Propose a permanent change (rule, skill, or tool) |

This prevents one-off preferences from becoming permanent rules while ensuring real patterns get promoted.

## What Personas Can Do Autonomously

| Action | Autonomous? | Details |
|--------|-------------|---------|
| Write to MEMORY.md | Yes | Every session |
| Read profile.md | Yes | Every session start |
| Read CLAUDE.md | Yes | Always in context |
| Propose CLAUDE.md changes | Yes (proposes) | User must approve the write |
| Propose profile.md changes | Yes (proposes) | User must approve the write |
| Propose new skills | Yes (proposes) | User must approve the write |
| Write scripts or tools | No | Must propose and get approval |
| Modify other personas | No | Sandbox prevents cross-directory access |
| Push to GitHub | No | User-initiated only |
| Install new MCP servers | No | Must propose, user configures |

## Reviewing Persona Evolution

Each persona has its own git repo, so all changes are tracked independently. To see how a persona has evolved:

```bash
# See all changes to a persona's rules
cd ~/.personas/warren
git log --oneline CLAUDE.md

# See all skill additions
git log --oneline -- skills/

# See the full diff of a self-improvement commit
git show <commit-hash>
```

Self-improvement commits follow the convention:
- `improve(self): description` — rule changes
- `feat(self): add {skill-name} skill` — new skills
- `feat(self): add {tool-name}` — new tools

## The Self-Audit Cycle

The self-improve skill includes a periodic audit workflow. Trigger it monthly or on request ("time for a self-audit"):

1. **Read memory** — Scan MEMORY.md for recurring themes
2. **Identify friction** — What keeps getting handled ad-hoc?
3. **Propose changes:**
   - Recurring correction (3+ sessions) → CLAUDE.md rule
   - Recurring multi-step workflow → new SKILL.md
   - Outdated fact in profile.md → flag for user update
4. **Present proposals** — All changes are shown to the user before writing
5. **Execute approved changes** — Write files, commit with appropriate message

## Best Practices for Guiding Persona Growth

### Do

- **Correct the persona explicitly.** Say "no, always do X instead" — this creates clear memory entries that can be promoted to rules.
- **Review memory periodically.** Read `.claude/memory/MEMORY.md` to see what the persona is learning. Delete entries that are wrong.
- **Approve good promotions.** When the persona proposes a rule or skill that matches your needs, approve it. This is how it gets better.
- **Use trigger phrases consistently.** Skills activate on keywords — using them consistently trains you and the persona.

### Avoid

- **Vague feedback.** "Be better at this" gives the persona nothing to work with. Be specific.
- **Overriding memory manually.** If memory has wrong entries, tell the persona to correct them rather than editing files yourself — this creates a correction event that strengthens future behavior.
- **Skipping the approval step.** The proposal/approval pattern exists for a reason. Personas should not silently change their own rules.

## Key Distinction

**Memory stores what happened. Rules define what always happens.**

Memory is exploratory — it captures context, outcomes, and patterns. Rules are prescriptive — they enforce behavior. The promotion from memory to rule is the mechanism that makes personas genuinely adaptive rather than just stateful.

## Next Steps

- [Creating Personas](creating-personas.md) — Build a persona with self-improvement built in
- [Remote Deployment](remote-deployment.md) — Evolving personas that run unattended
