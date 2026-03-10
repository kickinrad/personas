# Personas Public Framework — Design Document

**Date**: 2026-03-08
**Status**: Approved
**Author**: Wils + Claude

## Summary

Transform the private personas monorepo into a public framework for self-evolving AI assistants built on Claude Code plugins. Zero custom tooling — the framework is a well-structured plugin directory, ~30 lines of zsh, and native Claude Code features (plugins, marketplace, sandbox, auto memory, settings hierarchy).

## Goals

1. Public repo anyone can clone, fork, or install personas from
2. Each persona is fully isolated — can't see other personas or global config
3. Personas self-improve: create their own skills, tools, docs, and rules over time
4. Simple user journey from install to first persona session
5. Support remote/autonomous deployment via cron + sandboxing
6. Private personas can be developed locally and published later

## Non-Goals

- Custom CLI wrapper (native Claude Code commands + shell aliases cover everything)
- Docker/containers for isolation (native OS sandboxing via bubblewrap/Seatbelt)
- Agent SDK integration (pure Claude Code plugin architecture)
- Web UI or GUI (CLI-first)
- Daemon/always-on process (scheduled + on-demand only)

---

## Architecture

### Core Principle: Everything Is a Plugin

Each persona is a standard Claude Code plugin. No custom runtime, no framework code, no abstractions. The "framework" is:

1. A plugin marketplace (`marketplace.json`) listing available personas
2. A meta-plugin (`persona-manager`) for scaffolding and evolving personas
3. A shell alias generator (~30 lines of zsh)
4. Documentation

### Repository Structure

```
personas/                                  ← PUBLIC REPO
├── CLAUDE.md                              ← Framework context
├── .claude-plugin/marketplace.json        ← Public persona registry
├── .gitignore                             ← Protects secrets + personal data
├── plugins/
│   ├── persona-manager/                   ← Meta-tool (always installed)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── CLAUDE.md
│   │   └── skills/
│   │       ├── persona-dev/SKILL.md       ← Create new personas
│   │       ├── deploy/SKILL.md            ← Deploy to remote servers
│   │       └── publish/SKILL.md           ← Promote to marketplace
│   ├── julia/                             ← Personal chef persona
│   ├── warren/                            ← Personal CFO persona
│   ├── mila/                              ← Brand strategist persona
│   └── {template}/                        ← Community persona template
├── tests/personas-test.sh
├── docs/
│   ├── getting-started.md
│   ├── creating-personas.md
│   ├── self-improvement.md
│   └── remote-deployment.md
└── .github/
    └── PULL_REQUEST_TEMPLATE.md           ← For community submissions
```

### Per-Persona Structure

```
{persona}/
├── .claude-plugin/plugin.json             ← Plugin metadata + version
├── CLAUDE.md                              ← Personality, rules, self-improvement instructions
├── profile.md.example                     ← Template for user context
├── profile.md                             ← User's personal data (GITIGNORED)
├── .mcp.json                              ← MCP server config (GITIGNORED)
├── .claude/
│   ├── settings.json                      ← Sandbox config (COMMITTED)
│   ├── settings.local.json                ← User overrides (GITIGNORED)
│   └── memory/
│       └── MEMORY.md                      ← Auto-memory (GITIGNORED)
├── skills/
│   └── {skill-name}/SKILL.md              ← Domain workflows
├── docs/                                  ← Reference documentation
└── scripts/                               ← Tools and utilities
```

**Committed** (shared via marketplace): `plugin.json`, `CLAUDE.md`, `profile.md.example`, `.claude/settings.json`, `skills/`, `docs/`, `scripts/`

**Gitignored** (user-local): `profile.md`, `.mcp.json`, `.claude/settings.local.json`, `.claude/memory/`

---

## Three-Layer Model

| Layer | File | Who Writes | When Read | Mutable By Persona |
|-------|------|-----------|-----------|-------------------|
| Personality | `CLAUDE.md` | Human (Claude proposes) | Every session | Yes (propose changes) |
| Context | `profile.md` | Human (guided by Claude) | Every session | Suggest additions only |
| Memory | `.claude/memory/` | Claude (automatic) | When past context matters | Yes (full write) |

**Separation rule**: Personality defines WHO the persona is. Context defines WHO the user is. Memory records WHAT happened. Never mix.

**Pattern promotion**: Memory → Personality. When Claude detects a correction or pattern 3+ times in MEMORY.md, it proposes a CLAUDE.md rule update.

---

## Isolation Model

### `--setting-sources project`

One CLI flag provides total isolation. When a shell alias runs `claude --setting-sources project`:

- Loads `CLAUDE.md` from CWD only (persona's personality)
- Loads `.claude/settings.json` from CWD only (persona's sandbox config)
- Loads `.mcp.json` from CWD only (persona's tools)
- **Ignores** `~/.claude/CLAUDE.md` (user's global instructions)
- **Ignores** `~/.claude/settings.json` (user's global settings)

No persona leaks into another. No global config leaks into a persona.

### Native Sandboxing

Each persona ships `.claude/settings.json` with sandbox config:

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["."],
      "denyRead": ["~/.aws", "~/.ssh", "~/.gnupg", "../"]
    },
    "network": {
      "allowedDomains": ["api.anthropic.com"]
    }
  }
}
```

- **Filesystem**: Full write to own directory (`.`), blocked from parent dirs (`../`) and sensitive system dirs
- **Network**: Whitelist only domains the persona needs (MCP servers, APIs)
- **Technology**: bubblewrap (Linux/WSL2), Seatbelt (macOS) — OS-level, zero overhead
- **No Docker required**

Per-persona network customization:
- **Warren**: `*.monarchmoney.com`, `*.finnhub.io`, `*.alphavantage.co`
- **Julia**: `mealie.*.ts.net`, `*.googleapis.com`
- **Mila**: `*.googleapis.com`

---

## Self-Improvement Engine

The core differentiator. Personas are self-evolving — they can create their own skills, tools, docs, and rules.

### Five Levels

**Level 1 — Memory** (automatic, every session)
- Update `.claude/memory/MEMORY.md` with learnings
- Track corrections, preferences, observed patterns
- No user approval needed

**Level 2 — Rule Promotion** (propose to user)
- Edit own `CLAUDE.md` to add/refine behavioral rules
- Suggest `profile.md` additions for missing context
- Commit: `improve(self): description`

**Level 3 — Skill Creation** (propose to user)
- Write new `skills/{name}/SKILL.md` for repeated workflows
- Write reference docs to `docs/`
- Commit: `feat(self): add {skill-name} skill`

**Level 4 — Tool Creation** (propose to user)
- Write scripts to `scripts/` (Python, bash, etc.)
- Propose MCP server additions to `.mcp.json`
- Create config files for new integrations
- Commit: `feat(self): add {tool-name}`

**Level 5 — Publish** (user-initiated only)
- Bump version in `plugin.json`
- `git push` to remote
- Update `marketplace.json` if public persona

### Trigger Rules

- **3+ corrections** on the same topic → propose CLAUDE.md rule
- **3+ ad-hoc workflows** for the same task → propose new SKILL.md
- **Repeated context gaps** → suggest profile.md additions
- **External data needs** → propose MCP server or script

### What Personas CAN Do Autonomously

- Write/edit any file in their own directory
- Create new skills, docs, scripts
- Git commit their own improvements
- Update their own MEMORY.md

### What Requires User Action

- Changes to `.mcp.json` (API keys, new services)
- `git push` to remote
- Marketplace version bumps
- Edits to `profile.md` (personal data)

---

## CLI Integration

### Shell Aliases

`~/.config/zsh/.personas.zsh` (~30 lines):

```bash
_PERSONAS_ROOT="$HOME/projects/personal/personas/plugins"

for _p_dir in "$_PERSONAS_ROOT"/*/; do
  [[ -d "$_p_dir" ]] || continue
  _p_name=$(basename "$_p_dir")
  [[ "$_p_name" == "persona-manager" ]] && continue
  [[ -f "${_p_dir}CLAUDE.md" ]] || continue

  eval "${_p_name}() {
    if [[ \$# -gt 0 ]]; then
      (cd \"${_p_dir}\" && claude --setting-sources project -p \"\$*\")
    else
      (cd \"${_p_dir}\" && claude --setting-sources project)
    fi
  }"
done
unset _PERSONAS_ROOT _p_dir _p_name
```

### Usage

```bash
warren                    # interactive session
warren "weekly review"    # one-shot prompt
julia "plan dinner"       # one-shot prompt
mila                      # interactive session
```

---

## Session Start (No Hooks)

First-run scaffolding uses instructions in each persona's CLAUDE.md, not hooks:

```markdown
## Session Start

If profile.md doesn't exist:
1. Copy profile.md.example to profile.md
2. Guide the user through filling it in
3. Do not proceed with other tasks until profile is set up
```

This only runs when Claude reads the persona's CLAUDE.md (when CWD is the persona dir). No global hooks, no side effects on other Claude Code sessions.

---

## Plugin Distribution

### Marketplace

```json
// .claude-plugin/marketplace.json
{
  "name": "personas",
  "description": "Self-evolving AI assistants for Claude Code",
  "owner": { "name": "kickinrad" },
  "plugins": [
    {
      "name": "persona-manager",
      "description": "Create and evolve personas",
      "source": { "source": "relative", "path": "plugins/persona-manager" },
      "version": "1.0.0"
    },
    {
      "name": "warren",
      "description": "Personal CFO — financial analysis, budgeting, trading",
      "source": { "source": "relative", "path": "plugins/warren" },
      "version": "1.0.0"
    }
  ]
}
```

### Install Flow

```bash
# Add marketplace
/plugin marketplace add kickinrad/personas

# Install a persona
/plugin install warren@personas

# Creates install directory with all committed files
# User fills in profile.md and .mcp.json on first session
```

### Update Flow

```bash
# Pull latest version
/plugin update warren@personas

# Only committed files update — profile.md, .mcp.json, memory/ are preserved
```

---

## Lifecycle Operations

No custom CLI. Everything uses native Claude Code or persona-manager skills:

| Action | Method | Details |
|--------|--------|---------|
| **Install** | `/plugin install {name}@personas` | Native plugin install |
| **Create** | `Skill('persona-manager:persona-dev')` | Interactive scaffolding |
| **Update** | `/plugin update {name}@personas` | Native plugin update |
| **Deploy** | `Skill('persona-manager:deploy')` | rsync + cron setup |
| **Publish** | `Skill('persona-manager:publish')` | PR to marketplace |
| **Use** | `{name}` or `{name} "prompt"` | Shell alias |

---

## Remote Deployment

### Deploy to Server

```bash
# Using persona-manager skill (interactive)
# Or manually:
rsync -avz ~/.personas/warren/ cloud:~/.personas/warren/

# Set up scheduled tasks on remote
ssh cloud 'crontab -l' # then add:
# 0 9 * * 1 cd ~/.personas/warren && claude --setting-sources project --dangerously-skip-permissions -p "weekly financial review"
```

### On-Demand Remote Access

```bash
ssh cloud 'cd ~/.personas/warren && claude --setting-sources project -p "check portfolio"'
```

### Sync Memory Back

```bash
rsync -avz cloud:~/.personas/warren/.claude/memory/ ~/.personas/warren/.claude/memory/
```

### Safety

`--dangerously-skip-permissions` is safe because:
- Sandbox restricts filesystem to persona's own directory
- Sandbox restricts network to whitelisted domains
- Persona cannot read other personas, SSH keys, AWS creds, etc.

---

## Private vs Public Personas

### Private Development

Private personas are local plugin directories not listed in any marketplace:

```bash
# Create locally
Skill('persona-manager:persona-dev')
# → scaffolds plugins/my-private-persona/

# Use via shell alias (auto-discovered by .personas.zsh)
my-private-persona "hello"
```

### Publishing

When ready to share, use persona-manager:

```bash
Skill('persona-manager:publish')
# → scrubs any personal data from committed files
# → bumps version in plugin.json
# → adds entry to marketplace.json
# → commits and opens PR
```

### Separate Private Repo

For fully private personas, create a separate repo with its own `marketplace.json`:

```bash
# Private marketplace
/plugin marketplace add kickinrad/private-personas

# Install from private marketplace
/plugin install my-secret-persona@private-personas
```

---

## Security

### What's Committed (Safe)

- `CLAUDE.md` — personality and rules (no personal data)
- `profile.md.example` — empty template
- `.claude/settings.json` — sandbox config
- `skills/`, `docs/`, `scripts/` — domain capabilities
- `plugin.json` — metadata

### What's Gitignored (Sensitive)

- `profile.md` — user's personal data
- `.mcp.json` — API keys, OAuth tokens, server URLs
- `.claude/memory/` — session history
- `.claude/settings.local.json` — user overrides
- `*.db*`, `*.log` — local state

### Credential Management

Use `pass` for secrets in `.mcp.json`:

```json
{
  "mcpServers": {
    "monarch": {
      "env": {
        "API_TOKEN": "$(pass show monarch/api-token)"
      }
    }
  }
}
```

Never hardcode tokens. Never echo secrets. Never commit `.mcp.json`.

### Pre-Public-Release Checklist

- [ ] Revoke any hardcoded OAuth tokens (Luna, Julia historical)
- [ ] Scrub git history for accidentally committed secrets
- [ ] Verify all `profile.md` files are gitignored
- [ ] Verify all `.mcp.json` files are gitignored
- [ ] Review each persona's CLAUDE.md for personal data references
- [ ] Replace personal references in committed docs with generic examples

---

## Migration Plan (Current → Public)

### Preserve

- All existing `profile.md` files (back up before migration)
- All existing `.claude/memory/` directories
- All existing `.mcp.json` configurations
- Warren's `investments.md`, `dashboard.html`, financial-analysis scripts (keep private)

### Scrub

- Remove personal names, account numbers, financial details from committed files
- Replace specific examples with generic ones in CLAUDE.md files
- Clean git history of any committed secrets

### Add

- Root `CLAUDE.md` (done)
- `.claude/settings.json` per persona (sandbox config)
- Updated shell aliases using `--setting-sources project`
- `docs/` directory with getting-started, creating-personas, etc.
- `.github/PULL_REQUEST_TEMPLATE.md` for community contributions

### Restructure

- Update `.personas.zsh` to use simplified aliases
- Move persona-manager skills to cover deploy/publish lifecycle
- Add `persona-manager:deploy` and `persona-manager:publish` skills

---

## User Journey

### New User (Installing a Public Persona)

```
1. /plugin marketplace add kickinrad/personas
2. /plugin install personal-chef@personas
3. Add alias to .zshrc (or source .personas.zsh)
4. julia                          ← first session
5. Claude notices no profile.md → guides setup
6. User fills in preferences, dietary needs
7. Julia is ready to plan meals
```

### Existing User (Creating a Custom Persona)

```
1. Already has framework installed
2. Skill('persona-manager:persona-dev')
3. Answers questions about persona's role, personality, tools
4. persona-manager scaffolds full plugin structure
5. User fills in profile.md
6. my-persona "hello"             ← first session
7. Persona evolves over time (memory → rules → skills → tools)
```

### Power User (Remote Autonomous Deployment)

```
1. Skill('persona-manager:deploy')
2. Specifies remote host (cloud via Tailscale)
3. persona-manager rsyncs workspace, sets up cron
4. Persona runs scheduled tasks autonomously
5. Memory syncs back to local on demand
```

---

## Custom Code Surface Area

| Component | Lines | Purpose |
|-----------|-------|---------|
| `.personas.zsh` | ~30 | Shell alias auto-discovery |
| `init-workspace.sh` | ~10 per persona | First-run scaffolding (optional, can be CLAUDE.md instructions instead) |
| persona-manager skills | existing + 2 new | Create, deploy, publish |

**Total custom code: ~50 lines of bash + persona-manager skills.**

Everything else is native Claude Code: plugins, marketplace, sandbox, auto memory, settings hierarchy, MCP servers, skills, hooks.

---

## Next Steps

1. Back up all existing profile.md, .mcp.json, and .claude/memory/ files
2. Scrub committed files of personal data
3. Add `.claude/settings.json` (sandbox) to each persona
4. Update `.personas.zsh` to use `--setting-sources project`
5. Create `persona-manager:deploy` and `persona-manager:publish` skills
6. Write user-facing docs (getting-started, creating-personas, etc.)
7. Scrub git history for any committed secrets
8. Make repo public
