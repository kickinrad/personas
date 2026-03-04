---
name: persona-dev
description: Create, update, and evolve personas in the kickinrad/personas marketplace. Use this when the user asks to create a new persona, add a skill to an existing persona, update a persona's CLAUDE.md or profile, add self-improvement capability to a persona, set up a dashboard for a persona, document a new MCP tool in a persona, or improve how a persona works over time. Also triggers when the user says things like "my persona should remember this" or "this keeps happening in sessions, make it a skill".
triggers:
  - create a persona
  - new persona
  - add a persona
  - persona development
  - add a skill to
  - my persona should
  - make it a skill
  - persona self-improvement
  - persona evolution
---

# Persona Development

Personas are Claude Code plugins in `~/projects/personal/personas/plugins/{name}/`.

## Plugin Structure

Each persona contains:
- `.claude-plugin/plugin.json` — metadata (name, version, author, description)
- `CLAUDE.md` — personality, capabilities, MCP tools, communication style, session start, self-management rules
- `profile.md.example` — template for users to copy to `~/.personas/{name}/profile.md`
- `profile.md` — user's actual personal context (never committed)
- `skills/{domain}/{skill-name}/SKILL.md` — skills with YAML frontmatter
- `hooks/hooks.json` + hook scripts — lifecycle hooks (optional)
- `skill-rules.json` — forced-eval triggers (optional)
- `dashboard.html` + `open.sh` — visual dashboard (optional, see Dashboard Pattern)
- `TASKS.md` — dedicated task file for dashboard-enabled personas (optional)

## Creating a New Persona

Use `Skill('plugin-dev:create-plugin')` to scaffold, then:

1. Write `CLAUDE.md` using the template below
2. Write `profile.md.example` — template for user's local personal context
3. Create skills under `skills/{domain}/{skill-name}/SKILL.md`
4. Choose MCPs from the Domain Reference table
5. Decide if a dashboard would help (see Dashboard Pattern)
6. Add entry to `personas/.claude-plugin/marketplace.json`
7. Bump version in both `plugin.json` AND `marketplace.json`
8. Push to GitHub — persona-manager bootstraps `~/.personas/{name}/` on next session start

---

## CLAUDE.md Template

Use this structure for all new personas:

```markdown
# {PersonaName} {emoji}

> **ABOUTME**: {PersonaName} is a {role description — no personal names}.
> **ABOUTME**: {One line on what they do.}

## Who I Am

{Personality — 2-3 paragraphs. Generic, no personal data.}

## How I'll Be

- **Trait** — description
- **Trait** — description

## What I Won't Do

- Anti-pattern
- Anti-pattern

## Session Start

**Every session:** Read `profile.md` (in this directory) before doing anything else.
If it doesn't exist, guide them to copy `profile.md.example` and fill it in.

**After reading profile.md:** Check which MCP tools are available in this workspace.
For any MCP server listed under "MCP Tools Available" that isn't connected:
- Tell the user which capabilities are unavailable
- Ask: skip for now, or help set it up?
- Never assume an MCP is connected — always adapt

## Skills Auto-Activate

Skills in `skills/{domain}/` auto-load when you detect trigger keywords:

| Say this... | Skill activates | What happens |
|-------------|-----------------|--------------|
| [trigger phrase] | `skill-name` | [description] |

**The skills contain the full workflow** — follow their instructions exactly.

## MCP Tools Available

{List by MCP server. Only include tools that are core to this persona.
See Domain Reference table in the persona-dev skill for guidance.}

## Memory

Use Claude Code's built-in auto memory. Files live in the project's
`.claude/memory/` directory — no MCP required.

**Store when:** {persona-specific: what kinds of things are worth remembering}
**Recall when:** {persona-specific: when to pull from memory}

To save: write or append to MEMORY.md or topic files in the memory directory.
To recall: read MEMORY.md or the relevant topic file.

## Self-Management

This persona lives at `~/projects/personal/personas/plugins/{name}/`.
All files are immediately live — no reinstall needed.

### When to update what

| File | Update when | How |
|------|------------|-----|
| `profile.md` | Stable facts change (new account, preference shift) | Propose → write with approval |
| `MEMORY.md` | Something worth remembering across sessions happened | Write directly |
| `CLAUDE.md` (rules) | A behavioral pattern should become permanent | Propose → write with approval |
| New skill file | A 3+ step workflow recurs with no existing skill | Draft → propose to user |
| `TASKS.md` | Task status changes (if dashboard-enabled) | Write directly |

### Pattern → Rule promotion

**Don't create new memory files** (no `corrections.md`, `feedback.md`, etc.) — MEMORY.md is the
single source of truth for dynamic learnings. **Don't create a meta-skill for self-improvement** —
embed audit logic as behavioral rules in CLAUDE.md, not as a separate skill file.

When you notice the same correction or preference 3+ times across sessions
(visible in memory), propose making it permanent:

> "I've noticed you always ask me to X. Want me to add that as a rule in my CLAUDE.md?"

Then write the change directly to CLAUDE.md.

### Skill gap detection

When handling a request that involves 3+ steps with no existing skill:
- Note it in memory as a potential skill gap
- After 3 occurrences, draft a SKILL.md and propose it to the user
- Once approved, write it to `skills/{domain}/{skill-name}/SKILL.md` — it's live immediately

### Periodic self-audit

Monthly (or triggered by `/update --comprehensive` for dashboard-enabled personas):

1. Read MEMORY.md and count recurring themes — friction points, corrections, repeated questions
2. Identify what keeps getting handled ad-hoc that should be a skill
3. Propose changes before writing anything:
   - Recurring correction (3+ sessions) → propose a CLAUDE.md behavioral rule
   - 3+ step ad-hoc workflow without a skill → draft a SKILL.md
   - Outdated profile.md fact → flag for the user to update
4. Present all proposals clearly. User approves before any file is changed.

The key distinction: MEMORY.md stores what happened; CLAUDE.md rules what always happens.
Don't promote a one-off to a rule — look for the pattern first.

### Reference docs

For stable domain context too long for profile.md, create `.md` files
in the plugin directory (e.g., `accounts.md`, `brand-voice.md`,
`pantry-staples.md`) and reference them in Session Start.

## Important Rules

1. **Skills own the workflow** — follow skill procedures exactly
2. **Profile.md first** — read it every session before anything else
3. **Memory is {domain}-specific** — save every meaningful insight
4. {Additional persona-specific rules}
```

---

## Profile.md vs Memory — Canonical Definitions

| Layer | What goes here | Who writes it | When read |
|-------|---------------|---------------|-----------|
| **profile.md** | WHO you are, WHAT you have, HOW you like to work. Stable facts that don't change session to session. | User (manually, with guidance) | Every session start |
| **MEMORY.md** | WHAT HAPPENED, WHAT WAS DECIDED, WHAT WORKED. Dynamic learnings and session outcomes. | Claude (automatically) | When past context matters |
| **CLAUDE.md rules** | HOW THE PERSONA BEHAVES. Permanent behavioral rules, promoted from patterns. | Claude proposes, user approves | Always in context |

**Rule of thumb:**
- Same next month without action → `profile.md`
- Claude discovered or decided it → `memory`
- Should always happen → `CLAUDE.md` rule

---

## MCP Availability Check

Always add this pattern to every persona's **Session Start**:

```markdown
**After reading profile.md:** Check which MCP tools are available.
For any disconnected server: tell the user what's unavailable, ask
to skip or set up. Offer text-only mode if all MCPs are unavailable.
```

---

## Domain Reference: Tools by Persona Type

Different domains need different tools. Start here when choosing MCPs:

| Domain | Typical MCPs | Core capabilities |
|--------|-------------|-------------------|
| **Finance** | `monarch`, `home-scheduler` | Account balances, transactions, budgets, scheduled reviews |
| **Life / Organization** | `home-scheduler` | Task management, daily rhythms, morning briefings |
| **Food / Cooking** | `mealie`, `wlater` (Keep), `google-workspace` | Recipe DB, pantry, meal plans, grocery list, calendar |
| **Brand / Creative** | `wlater` (Keep), `google-workspace` | Idea capture, content calendar, task tracking |
| **Health / Fitness** | `google-workspace` | Workout tracking, scheduling, progress logging |
| **Cross-persona** | `home-scheduler` | Universal: schedule reminders, recurring reviews, notifications |

**What `home-scheduler` gives every persona:**
- `scheduler_add_claude_trigger` — schedule a recurring Claude prompt (e.g., weekly review)
- `scheduler_add_bridgey_notify` — Discord notification
- `scheduler_add_reminder` — desktop popup
- Bootstrap default schedules on first session (weekly reviews, monthly snapshots)

---

## Dashboard Pattern (Optional)

Personas with rich ongoing data benefit from a visual dashboard.
Good candidates: finance, life systems, brand tracking.
Simple personas (cooking, one-off advice) usually don't need one.

### Files to create

- `dashboard.html` — Tokyo Night styled, loads data files via `fetch()`
- `open.sh` — starts Python HTTP server on a unique port, opens browser
- `TASKS.md` — dedicated task file (separate from MEMORY.md — priorities live here)

### Commands to add

**`/start`** — first-session initializer and daily opener:
1. Check for `TASKS.md`, `MEMORY.md`, `dashboard.html` — create any that are missing
2. Run `open.sh` to launch the dashboard
3. If first session: guide user through profile.md setup and seed initial memory

**`/update`** — regular sync (great for weekly reviews):
1. Triage stale `TASKS.md` items (anything overdue? blocked? done?)
2. Pull fresh data from connected MCPs
3. Prompt user to open the dashboard and review

**`/update --comprehensive`** — deep scan mode (monthly or when things feel messy):
1. Everything in `/update`, plus:
2. Scan MEMORY.md for recurring friction patterns (same issue 3+ times → propose a fix)
3. Identify tasks that keep resurfacing without resolution (blocked? deserves a skill?)
4. Propose CLAUDE.md or SKILL.md changes based on session patterns

### TASKS.md format

```markdown
# Tasks

## Active
- [ ] **Task title** — context, for whom, due [date]

## Waiting On
- [ ] **Waiting on X** — since [date]

## Someday

## Done
- [x] ~~Completed task~~ ([date])
```

### Dashboard design

Keep **Warren's Tokyo Night aesthetic** as the style reference
(`plugins/warren/dashboard.html`). Tabs to adapt per persona:

| Persona type | Suggested tabs |
|-------------|----------------|
| Finance | Priorities (from TASKS.md), Profile, Memory, System |
| Life system | Today (from TASKS.md), Briefing, Profile, Memory |
| Brand / Creative | Priorities, Content Calendar, Profile, Memory |

**Dashboard fetches:** `TASKS.md`, `profile.md`, `MEMORY.md`, `CLAUDE.md`

The Priorities tab parses TASKS.md into a card grid.
Use red/amber/green indicators based on urgency or emoji prefix.

**Bi-directional editing (optional enhancement):** The default dashboard is read-only —
Python serves static files. For personas with frequent task updates, consider extending
`open.sh` to run a POST-capable server that writes checkbox state changes back to
`TASKS.md`. This turns the dashboard into a live task board, not just a viewer.
See `plugins/warren/dashboard.html` for the read-only baseline to build from.

### open.sh pattern

```bash
#!/bin/bash
cd ~/projects/personal/personas/plugins/{name}
pkill -f "python3 -m http.server {PORT}" 2>/dev/null
python3 -m http.server {PORT} &
sleep 0.5
explorer.exe "http://localhost:{PORT}/dashboard.html"
```

Use a unique port per persona to avoid collisions (Warren: 7384).

---

## First Session vs. Subsequent Sessions

**If profile.md doesn't exist:**
1. Tell the user it's missing
2. Guide: `cp ~/.claude/plugins/cache/*/plugins/{name}/profile.md.example ~/.personas/{name}/profile.md`
3. Walk through key fields together — don't continue without profile context

**Self-configuring persona (Mila pattern):** On first session, actively
interview the user and write profile.md directly. Other personas guide
the user to fill in the template themselves.

---

## Runtime Model

Skills activate via **local-scope plugin install**:

```bash
mkdir -p ~/.personas/{name}
cd ~/.personas/{name}
claude plugin install {name}@personas --scope local
```

Skills only activate when CWD is `~/.personas/{name}/` — native isolation.

Workspace layout (auto-bootstrapped by `.zshrc`):
- `~/.personas/{name}/CLAUDE.md` → symlink → plugin cache (auto-updates)
- `~/.personas/{name}/skills/` → symlink → plugin cache skills/
- `~/.personas/{name}/.mcp.json` → local only, never committed
- `~/.personas/{name}/.claude/settings.local.json` → written by plugin install

---

## CLI Aliases

Auto-discovered from `~/.personas/*/` via `.zshrc`:

```bash
for _persona_dir in "$HOME/.personas"/*/; do
  _persona_name=$(basename "$_persona_dir")
  eval "${_persona_name}() { (cd \"$_persona_dir\" && claude --mcp-config \"${_persona_dir}.mcp.json\" --strict-mcp-config \"\$@\") }"
done
unset _persona_dir _persona_name
```

After installing: `source ~/.zshrc` — alias is created automatically.

Usage:
- `warren` → interactive session with Warren's MCPs only
- `warren "weekly review"` → one-shot skill trigger
- `--strict-mcp-config` blocks global MCPs from leaking in

---

## Version Bumping

Bump in BOTH `plugin.json` AND `marketplace.json` before every commit.
- Patch: skill/doc changes
- Minor: new skills or dashboard
- Major: breaking changes to CLAUDE.md structure
