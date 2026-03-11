# Personas

Public framework for self-evolving AI assistants built on Claude Code. The framework repo contains persona-manager (the meta-tool); individual personas live in `~/.personas/{name}/` as independent git-tracked directories with sandbox isolation.

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
├── .aliases.sh                           # Shell functions for all personas (bash/zsh)
└── {persona}/                            # Each persona is its own git-tracked directory
    ├── CLAUDE.md                         # Personality + rules (committed)
    ├── profile.md.example                # Template for user context (committed)
    ├── profile.md                        # User's personal data (gitignored)
    ├── .mcp.json                         # MCP server config (gitignored)
    ├── hooks.json                        # Stop + PreCompact hooks (committed)
    ├── .claude/
    │   ├── settings.json                 # Sandbox + permissions (committed)
    │   └── memory/                       # Auto-memory (gitignored)
    ├── skills/
    │   ├── {domain}/                     # Domain skills (committed)
    │   └── self-improve/SKILL.md         # Ships with every persona
    ├── docs/                             # Reference docs, plans (committed, persona-writable)
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

Each persona is invokable by name from any directory. Shell functions in `~/.personas/.aliases.sh` auto-discover persona dirs and create aliases:

```bash
warren              # interactive session
warren "do weekly"  # one-shot prompt
```

The aliases file works in both bash and zsh. Fish users need a separate config (see persona-dev skill for the fish snippet). Source it from your shell config:

```bash
# In .bashrc or .zshrc:
[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"
```

Each alias `cd`s into `~/.personas/{name}/` and runs `claude --setting-sources project --dangerously-skip-permissions`. These flags:
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

Every persona ships with a `self-improve` skill and hooks that automate evolution:

- **Hooks** (`hooks.json`): Stop hook reminds persona to update memory; PreCompact hook saves context before compaction
- **Self-improve skill** (`skills/self-improve/SKILL.md`): Handles rule promotion, skill creation, tool & integration discovery, workspace hygiene, and periodic audits

The four levels: memory (automatic), rule promotion (propose), skill creation (propose), tool & integration discovery (research existing solutions first, then propose). Periodic audits include workspace hygiene — cleaning stale files, pruning unused tools, keeping the persona lean. See the self-improve skill for the full workflow.

## Session Start

First-run scaffolding is handled by instructions in each persona's CLAUDE.md. On first session, if `profile.md` doesn't exist, the persona guides the user through setup (guide or interview pattern). Hooks handle memory automation (Stop, PreCompact) but not scaffolding.

## Lifecycle

All lifecycle operations use native Claude Code features or persona-manager skills:

| Action | How |
|--------|-----|
| Install persona-manager | `/plugin marketplace add kickinrad/personas` then `/plugin install persona-manager@personas` |
| Create persona | `Skill('persona-manager:persona-dev')` — scaffolds to `~/.personas/` |
| Add dashboard | `Skill('persona-manager:persona-dashboard')` — expansion pack |
| Push to GitHub | `gh repo create` during scaffolding, or `git push` anytime |
| Daily use | Shell alias (`{name}`, `{name} "prompt"`) |

## Private vs Public Personas

- **All personas are independent repos** in `~/.personas/{name}/`, each with their own git history
- **Public**: Push to a public GitHub repo
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
- `.claude/settings.json` (sandbox config) IS committed — `.claude/settings.local.json` is gitignored
- Personas live in `~/.personas/`, NOT in this framework repo
