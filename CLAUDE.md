# Personas

Public framework for self-evolving AI assistants built on Claude Code plugins. The framework repo contains persona-manager (the meta-tool); individual personas live in `~/.personas/{name}/` as independent git repos.

## Architecture

```
personas/                                 # Framework repo
├── CLAUDE.md                             # Framework-level context
├── .claude-plugin/marketplace.json       # Plugin registry (persona-manager)
├── plugins/
│   └── persona-manager/                  # Meta-tool: scaffolds + evolves personas
├── tests/personas-test.sh
└── docs/plans/

~/.personas/                              # Personas live here (outside this repo)
└── {persona}/                            # Each persona is its own git repo
    ├── .claude-plugin/plugin.json
    ├── CLAUDE.md                         # Personality + rules (committed)
    ├── profile.md.example                # Template for user context (committed)
    ├── profile.md                        # User's personal data (gitignored)
    ├── .mcp.json                         # MCP server config (gitignored)
    ├── .claude/
    │   ├── settings.json                 # Sandbox + permissions (committed)
    │   └── memory/                       # Auto-memory (gitignored)
    ├── skills/                           # Domain skills (committed)
    ├── docs/                             # Reference docs (committed, persona-writable)
    └── scripts/                          # Tools and utilities (committed, persona-writable)
```

## Three-Layer Model

Every persona uses three layers — never mix them:

| Layer | File | Who Writes | Content |
|-------|------|-----------|---------|
| **Personality** | `CLAUDE.md` | Human (Claude proposes) | Role, rules, skills, communication style |
| **Context** | `profile.md` | Human (guided by Claude) | Personal data, accounts, preferences |
| **Memory** | `.claude/memory/` | Claude (automatic) | Session outcomes, learnings, patterns |

## CLI Aliases

Each persona is invokable by name from any directory. Shell functions in `~/.config/zsh/.personas.zsh` auto-discover persona dirs in `~/.personas/` and create aliases:

```bash
warren              # interactive session
warren "do weekly"  # one-shot prompt
```

The shell function `cd`s into `~/.personas/{name}/` and runs `claude --setting-sources project --dangerously-skip-permissions`. These flags:
- Loads persona's `CLAUDE.md` (personality)
- Loads persona's `.claude/settings.json` (sandbox config)
- Loads persona's `.mcp.json` (tools)
- Ignores global `~/.claude/CLAUDE.md` and `~/.claude/settings.json`
- Skips permission prompts (safe because sandbox restricts filesystem + network)

## Running Personas

| Mode | Command |
|------|---------|
| Interactive | `{name}` (sandbox + skip-permissions via alias) |
| One-shot | `{name} "prompt"` (sandbox + skip-permissions via alias) |
| Remote/scheduled | Scheduler MCP (`scheduler_add_claude_trigger`) on remote server via rsync + Tailscale (crontab as fallback) |

## Native Sandboxing

Each persona ships `.claude/settings.json` with sandbox config. No Docker required — uses OS-level isolation (bubblewrap on Linux, Seatbelt on macOS).

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

Each persona customizes allowed domains for its MCP servers and APIs. Personas cannot read parent directories or other personas' files.

## Self-Improvement (Core Feature)

Personas are self-evolving. They have full write access to their own directory and can grow new capabilities over time.

**Level 1 — Memory** (automatic, every session):
Update `.claude/memory/MEMORY.md` with learnings, corrections, observed patterns.

**Level 2 — Rule Promotion** (propose to user):
Edit own `CLAUDE.md` to add/refine behavioral rules. Edit `profile.md` to capture missing context. Commit: `improve(self): description`.

**Level 3 — Skill Creation** (propose to user):
Write new `skills/{name}/SKILL.md` files. Write reference docs to `docs/`. Commit: `feat(self): add {skill-name} skill`.

**Level 4 — Tool Creation** (propose to user):
Write scripts to `scripts/`. Propose MCP server additions to `.mcp.json`. Create config files for new integrations. Commit: `feat(self): add {tool-name}`.

**Level 5 — Publish** (user-initiated only):
Bump `plugin.json` version. `git push`. Update `marketplace.json` if public.

## Session Start (No Hooks)

First-run scaffolding is handled by instructions in each persona's CLAUDE.md, not hooks. On first session, if `profile.md` doesn't exist, the persona copies from `profile.md.example` and guides the user through setup. No global hook side effects.

## Plugin Distribution

The persona-manager is distributed via the Claude Code plugin marketplace:

```bash
/plugin marketplace add kickinrad/personas
/plugin install persona-manager@personas
```

Individual personas are independent git repos in `~/.personas/`. They can optionally be published to their own marketplace repos.

## Lifecycle (No Custom CLI)

All lifecycle operations use native Claude Code features or persona-manager skills:

| Action | How |
|--------|-----|
| Install persona-manager | `/plugin install persona-manager@personas` |
| Create persona | `Skill('persona-manager:persona-dev')` — scaffolds to `~/.personas/` |
| Deploy to remote | `Skill('persona-manager:deploy')` |
| Publish to marketplace | `Skill('persona-manager:publish')` |
| Daily use | Shell alias (`warren`, `julia`, etc.) |

## Private vs Public Personas

- **All personas are independent repos** in `~/.personas/{name}/`, each with their own git history
- **Public**: Push to a public GitHub repo, optionally list in a `marketplace.json`
- **Private**: Keep local or push to a private repo
- **Going public**: Since each persona is its own repo, just create a fresh remote — no history scrubbing needed

## Security Rules

- **Never commit secrets** — `.mcp.json` and `profile.md` are gitignored per-persona
- **Use `pass`** for credentials in `.mcp.json`: `$(pass show service/key-name)`
- **Never hardcode** OAuth tokens, API keys, or JWT tokens
- **Sandbox** restricts each persona to its own directory + whitelisted network domains

## Gitignored (Never Commit)

Each persona's `.gitignore` handles its own secrets. Common patterns:

- `profile.md` — personal data
- `.mcp.json` — API keys and secrets
- `.claude/memory/` — auto-memory
- `.claude/settings.local.json` — local overrides
- `*.db*` — local databases
- `*.log`, `*.local.json`, `*.local.md`

## Git Flow

`feat/*` / `fix/*` / `docs/*` → `main`

Commits: `type(scope): description` — scope is `framework` for this repo, persona name for persona repos

## Gotchas

- Personas activate only when CWD is the persona's directory — `--setting-sources project` ensures total isolation
- MCP servers must be configured per-persona in `.mcp.json` (gitignored), not globally
- The scheduler MCP server lives outside this repo at `~/projects/personal/home-base/services/home-scheduler`
- On WSL2, AdGuard may block Yahoo Finance domains — allowlist `fc.yahoo.com` for Warren's financial analysis
- `.claude/settings.json` (sandbox config) IS committed — `.claude/settings.local.json` is gitignored
- Personas live in `~/.personas/`, NOT in this framework repo
