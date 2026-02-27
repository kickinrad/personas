# kickinrad/personas

> Persistent, personal AI assistants for Claude Code — each one lives in its own workspace, remembers your context, and activates the right skills automatically.

```
$ luna "good morning"

🌙 Good morning! Let me pull your day together...

🌤  Weather   — 62°F, partly cloudy. Light jacket weather.
📅  Calendar  — 10am standup, 2pm 1:1 with Marco
✅  Tasks     — 3 due today: Review PR #47, Call insurance, Groceries
📝  Big 3     — From last night: ship auth refactor, gym, newsletter draft

Energy check: how are you feeling today?
```

---

## How It Works

Personas are Claude Code plugins. Each one is three layers of context stacked on each other:

| Layer | File | Who writes it | What it is |
|-------|------|---------------|------------|
| **Personality** | `CLAUDE.md` | Plugin developer | Role, skills, rules — no personal data |
| **Context** | `~/.personas/{name}/profile.md` | You | Your name, location, preferences — never committed |
| **Memory** | `~/.personas/{name}/.claude/memory/` | Claude, automatically | What was learned, decided, noticed across sessions |

Personas activate only when your working directory is `~/.personas/{name}/` — no global state bleed, no shared context. Each persona is its own isolated Claude Code project.

---

## Build Your Own ⭐

The included personas are reference implementations. The real power is building your own.

**Prerequisites:** [Claude Code](https://claude.ai/code) + persona-manager installed (see Installation).

### Step 1 — Scaffold your persona

In any Claude Code session with persona-manager installed, run:

```
/persona-dev
```

This interactive skill walks you through the full persona creation flow.

### Step 2 — Define the personality

Write your persona's `CLAUDE.md`. The key sections:

- **Who I Am** — personality in 2–3 paragraphs, no personal data
- **Session Start** — read `profile.md` first, check MCP availability, handle first-run gracefully
- **Skills Auto-Activate** — trigger phrases mapped to skill files
- **MCP Tools Available** — only tools core to this persona
- **Memory** — what to store, when to recall

### Step 3 — Create skills

Skills are markdown files with YAML frontmatter. They load automatically when trigger keywords are detected:

```yaml
---
name: weekly-review
description: Full financial pulse check
triggers:
  - weekly review
  - how did we do
  - financial check-in
---

# Weekly Review
...
```

### Step 4 — Write profile.md.example

Ship a `profile.md.example` with your plugin — the template users fill in with their personal context. Use `[placeholder]` syntax. This file is committed; the filled-in copy is not.

### Step 5 — Register and publish

Add your persona to `marketplace.json`, bump the version in both `plugin.json` and `marketplace.json`, and push to GitHub. persona-manager bootstraps `~/.personas/{name}/` on next session start.

---

## Installation

### Install persona-manager

```bash
claude plugin install persona-manager@personas
```

### Install a persona

```bash
# Create the workspace
mkdir -p ~/.personas/luna
cd ~/.personas/luna

# Install the plugin
claude plugin install luna@personas --scope local

# Copy and fill in your profile
cp ~/.claude/plugins/cache/*/plugins/luna/profile.md.example ~/.personas/luna/profile.md
# Edit profile.md — add your name, location, and preferences
```

Repeat for each persona you want.

### Shell aliases

Add once to your `.bashrc` or `.zshrc` — aliases are auto-discovered from installed personas:

```sh
# Persona aliases — auto-discovered from ~/.personas/*/
for _p in "$HOME/.personas"/*/; do
  _n=$(basename "$_p")
  alias "$_n"="(cd \"$_p\" && claude)"
done
unset _p _n
```

After adding, run `source ~/.bashrc` (or `source ~/.zshrc`). You'll have a `luna` command, a `warren` command, etc. Open a new terminal to start a session.

> The full alias with MCP isolation (`--mcp-config --strict-mcp-config`) is documented in the `/persona-dev` skill for personas that use MCP servers.

---

## Included Personas

These ship as reference implementations — use them as-is or as templates for your own.

| Persona | Role | Skills | What they do |
|---------|------|--------|--------------|
| **luna** 🌙 | Life assistant | 4 | Morning briefings, brain dump triage, evening shutdown, stuck-mode support |
| **julia** 👩‍🍳 | Personal chef | 1 | Meal planning, pantry tracking, grocery lists, recipe discovery |
| **warren** 📊 | Personal CFO | 4 | Weekly financial reviews, budget health, net worth tracking, trading review |
| **mila** ✨ | Brand strategist | 6 | Content planning, weekly reviews, agency growth, music career, writing practice, quarterly goals |

Each persona ships with a `profile.md.example` — the only setup required after install.

---

## Repository Structure

```
personas/
├── .claude-plugin/
│   └── marketplace.json      ← plugin registry
└── plugins/
    ├── persona-manager/      ← scaffolding + bootstrap tool
    ├── luna/                 ← life assistant
    ├── julia/                ← personal chef
    ├── warren/               ← personal CFO
    └── mila/                 ← brand strategist
```
