---
name: persona-dev
description: Create, update, and evolve personas. Use this when the user asks to create a new persona, add a skill to an existing persona, update a persona's CLAUDE.md or profile, set up hooks or self-improvement, document a new MCP tool in a persona, or improve how a persona works over time. Also triggers when the user says things like "my persona should remember this", "this keeps happening, make it a skill", "create a persona for", or "build me a persona".
triggers:
  - create a persona
  - new persona
  - add a persona
  - build a persona
  - persona development
  - add a skill to
  - my persona should
  - make it a skill
  - persona self-improvement
  - persona evolution
---

# Persona Development

Personas live in `~/.personas/{name}/`, each as its own git repo.

## Persona Structure

Each persona contains:

```
~/.personas/{name}/
├── .claude-plugin/plugin.json     # Metadata (name, version, author)
├── .claude/
│   ├── settings.json              # Sandbox config (committed)
│   └── memory/                    # Auto-memory (gitignored)
├── .gitignore                     # Secrets exclusion
├── hooks.json                     # Stop + PreCompact hooks
├── CLAUDE.md                      # Personality + rules
├── profile.md.example             # Profile template (committed)
├── profile.md                     # User's personal context (gitignored)
├── .mcp.json                      # MCP server config (gitignored)
└── skills/
    ├── {domain}/{skill}/SKILL.md  # Domain skills
    └── self-improve/SKILL.md      # Ships with every persona
```

## Creating a New Persona

### Step 1: Scaffold with plugin-dev

Use `Skill('plugin-dev:create-plugin')` to scaffold the base directory at `~/.personas/{name}/`.

### Step 2: Write CLAUDE.md

Use the template from `references/claude-md-template.md` in this skill's directory. Key decisions:

- **Session Start pattern**: Guide (user fills template) vs Interview (persona writes directly)
- **Personality**: Be specific about traits and anti-patterns. Give it opinions.
- **Self-Improvement**: Point to the self-improve skill (one line, not inline)

### Step 3: Write profile.md.example

Create a template with sections relevant to the persona's domain. Include:
- Personal info placeholders relevant to this domain
- Account/service connections
- Preferences and constraints
- Anything the persona needs to know about the user

### Step 4: Create first domain skill

Write at least one skill under `skills/{domain}/{skill-name}/SKILL.md` with:
- YAML frontmatter (name, description, triggers)
- Step-by-step workflow
- Expected output format

### Step 5: Copy self-improve skill

Copy `references/self-improve-skill.md` to `skills/self-improve/SKILL.md`. Replace `{name}` with the persona name. This ships with every persona — it handles memory management, rule promotion, skill creation, and periodic audits.

### Step 6: Set up hooks

Copy `references/hooks-template.json` to `hooks.json` in the persona root. These hooks:
- **Stop**: Reminds the persona to update memory before ending
- **PreCompact**: Saves session context before compaction

### Step 7: Create .gitignore

Copy `references/gitignore-template` to `.gitignore`.

### Step 8: Configure sandbox

Copy `references/settings-template.json` to `.claude/settings.json`. Add any persona-specific network domains for MCP servers to `allowedDomains`.

### Step 9: Initialize git repo

```bash
cd ~/.personas/{name}
git init
git add -A
git commit -m "feat({name}): initial scaffold"
```

### Step 10: Optional GitHub remote

Ask the user: "Want to set up a GitHub repo for this persona?"
- If yes: `gh repo create kickinrad/{name} --private --source=. --push`
- If no: Skip — can always add a remote later

---

## Three-Layer Model

Every persona uses three layers — never mix them:

| Layer | File | Who Writes | Content |
|-------|------|-----------|---------|
| **Personality** | `CLAUDE.md` | Human (Claude proposes) | Role, rules, skills, communication style |
| **Context** | `profile.md` | Human (guided by Claude) | Personal data, accounts, preferences |
| **Memory** | `.claude/memory/` | Claude (automatic) | Session outcomes, learnings, patterns |

---

## Profile.md vs Memory — Canonical Definitions

| Question | Answer | File |
|----------|--------|------|
| Will this be true next month without action? | Yes | `profile.md` |
| Did Claude discover or decide this? | Yes | `MEMORY.md` |
| Should this always happen, every session? | Yes | `CLAUDE.md` rule |

**profile.md** = WHO you are, WHAT you have, HOW you like to work. Stable facts.
**MEMORY.md** = WHAT HAPPENED, WHAT WAS DECIDED, WHAT WORKED. Dynamic learnings.
**CLAUDE.md rules** = HOW THE PERSONA BEHAVES. Permanent, promoted from patterns.

---

## CLI Aliases

Auto-discovered from `~/.personas/*/` via shell function in `~/.config/zsh/.personas.zsh`:

```bash
for _persona_dir in "$HOME/.personas"/*/; do
  _persona_name=$(basename "$_persona_dir")
  eval "${_persona_name}() { (cd \"$_persona_dir\" && claude --setting-sources project --dangerously-skip-permissions \"\$@\") }"
done
unset _persona_dir _persona_name
```

After creating a persona: `source ~/.config/zsh/.personas.zsh` — the alias is created automatically.

Usage:
- `{name}` — interactive session
- `{name} "do weekly review"` — one-shot prompt

---

## First Session Patterns

**Pattern A — Guide** (default): The persona tells the user to copy `profile.md.example` to `profile.md` and walks through each section together. Best for personas where the user knows their own context well.

**Pattern B — Interview**: The persona actively interviews the user and writes `profile.md` directly from answers. Best for personas where the user needs help articulating their context (e.g., financial goals, health history).

Choose the pattern in `CLAUDE.md` Session Start. See `references/claude-md-template.md` for both patterns.

---

## MCP Availability Check

Always embed this pattern in every persona's Session Start (already in the CLAUDE.md template):

```
After reading profile.md: Check which MCP tools are available.
For any disconnected server, tell the user what's unavailable
and ask: skip for now, or help set it up?
Offer text-only mode if all MCPs are unavailable.
```

When adding MCP servers:
1. Document tools in CLAUDE.md under "MCP Tools Available"
2. Add domains to `.claude/settings.json` → `network.allowedDomains`
3. Configure the server in `.mcp.json` (gitignored)

---

## Expansion Packs

Some capabilities are optional and can be installed into personas after creation:

| Pack | Skill | What it adds |
|------|-------|-------------|
| Dashboard | `persona-manager:persona-dashboard` | Visual dashboard (HTML), task tracking, open.sh |

These are separate skills in persona-manager — invoke them when the user asks for the capability.

---

## Version Bumping

Bump `plugin.json` version before every commit:
- **Patch**: Skill/doc changes
- **Minor**: New skills or capabilities
- **Major**: Breaking changes to CLAUDE.md structure
