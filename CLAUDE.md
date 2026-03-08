# Personas

Public framework for self-evolving AI assistants built on Claude Code plugins. Each persona is a self-contained, self-improving plugin with personality, tools, memory, and full write access to its own directory.

## Architecture

```
personas/
├── CLAUDE.md                             # Framework-level context
├── .claude-plugin/marketplace.json       # Plugin registry (public personas)
├── plugins/
│   ├── persona-manager/                  # Meta-tool: scaffolds + evolves personas
│   ├── julia/                            # Personal chef
│   ├── warren/                           # Personal CFO
│   ├── mila/                             # Brand strategist
│   └── {persona}/                        # Each persona is a Claude Code plugin
│       ├── .claude-plugin/plugin.json
│       ├── CLAUDE.md                     # Personality + rules (committed)
│       ├── profile.md.example            # Template for user context (committed)
│       ├── profile.md                    # User's personal data (gitignored)
│       ├── .mcp.json                     # MCP server config (gitignored)
│       ├── .claude/
│       │   ├── settings.json             # Sandbox + permissions (committed)
│       │   └── memory/                   # Auto-memory (gitignored)
│       ├── skills/                       # Domain skills (committed)
│       ├── docs/                         # Reference docs (committed, persona-writable)
│       └── scripts/                      # Tools and utilities (committed, persona-writable)
├── tests/personas-test.sh
└── docs/plans/
```

## Three-Layer Model

Every persona uses three layers — never mix them:

| Layer | File | Who Writes | Content |
|-------|------|-----------|---------|
| **Personality** | `CLAUDE.md` | Human (Claude proposes) | Role, rules, skills, communication style |
| **Context** | `profile.md` | Human (guided by Claude) | Personal data, accounts, preferences |
| **Memory** | `.claude/memory/` | Claude (automatic) | Session outcomes, learnings, patterns |

## CLI Aliases

Each persona is invokable by name from any directory. Shell functions in `~/.config/zsh/.personas.zsh` auto-discover persona dirs and create aliases:

```bash
warren              # interactive session
warren "do weekly"  # one-shot prompt
```

The shell function `cd`s into the persona dir and runs `claude --setting-sources project --dangerously-skip-permissions`. These flags:
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

Personas are distributed via Claude Code plugin marketplace:

```bash
/plugin marketplace add kickinrad/personas
/plugin install warren@personas
```

Versions tracked in both `plugin.json` and `marketplace.json`. Bump both before committing.

## Lifecycle (No Custom CLI)

All lifecycle operations use native Claude Code features or persona-manager skills:

| Action | How |
|--------|-----|
| Install persona | `/plugin install {name}@personas` |
| Create persona | `Skill('persona-manager:persona-dev')` |
| Update persona | `/plugin update {name}@personas` |
| Deploy to remote | `Skill('persona-manager:deploy')` |
| Publish to marketplace | `Skill('persona-manager:publish')` |
| Daily use | Shell alias (`warren`, `julia`, etc.) |

## Private vs Public Personas

- **Public**: Listed in a clean public repo's `marketplace.json`, installable by anyone
- **Private**: This repo (full history, personal data in gitignored files)
- **Going public**: Create fresh repo from clean snapshot — no history carries over. Use `Skill('persona-manager:publish')` to prepare a persona for public release
- **Separate private repo**: Alternative for private personas with own `marketplace.json`

## Security Rules

- **Never commit secrets** — `.mcp.json` and `profile.md` are gitignored
- **Use `pass`** for credentials in `.mcp.json`: `$(pass show service/key-name)`
- **Never hardcode** OAuth tokens, API keys, or JWT tokens
- **Sandbox** restricts each persona to its own directory + whitelisted network domains

## Gitignored (Never Commit)

- `plugins/*/profile.md` — personal data
- `plugins/*/.mcp.json` — API keys and secrets
- `plugins/*/.claude/memory/` — auto-memory
- `plugins/*/.claude/settings.local.json` — local overrides
- `plugins/*/*.db*` — local databases
- `*.log`, `*.local.json`, `*.local.md`

## Git Flow

`feat/*` / `fix/*` / `docs/*` → `main`

Commits: `type(scope): description` — scope is persona name or `framework`

## Gotchas

- Personas activate only when CWD is the persona's directory — `--setting-sources project` ensures total isolation
- MCP servers must be configured per-persona in `.mcp.json` (gitignored), not globally
- `marketplace.json` and `plugin.json` versions must stay in sync
- The scheduler MCP server lives outside this repo at `~/projects/personal/home-base/services/home-scheduler`
- On WSL2, AdGuard may block Yahoo Finance domains — allowlist `fc.yahoo.com` for Warren's financial analysis
- `.claude/settings.json` (sandbox config) IS committed — `.claude/settings.local.json` is gitignored
