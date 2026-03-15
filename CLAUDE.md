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
    ├── CLAUDE.md                         # Role, rules, skill refs (committed)
    ├── .claude/
    │   ├── settings.json                 # Sandbox + autoMemoryDirectory (committed)
    │   ├── output-styles/               # Personality, tone, style (committed)
    │   └── settings.local.json          # (always gitignored)
    ├── hooks.json                        # SessionStart hook (committed)
    ├── profile-template.md               # Template for user context (committed)
    ├── .mcp.json                         # MCP server config (gitignored)
    ├── skills/
    │   ├── {domain}/{skill}/SKILL.md     # Domain skills (committed)
    │   └── self-improve/SKILL.md         # Ships with every persona
    ├── tools/                            # Utilities, scripts, pipelines (committed)
    ├── docs/                             # Reference docs, plans (committed)
    └── user/                             # Personal data silo (optionally gitignored)
        ├── profile.md                    # User's personal data (filled from interview)
        └── memory/                       # Native auto-memory
            ├── MEMORY.md                 # Index (first 200 lines loaded)
            └── *.md                      # Topic files (read on demand)
```

## What Is a Persona?

**A persona is a self-contained AI assistant.** It combines standard Claude Code features — identity (CLAUDE.md), output style (`.claude/output-styles/`), user context (`user/profile.md`), skills, hooks, MCP tools, sandbox settings, and native auto-memory (`user/memory/`) — into a specialized agent that evolves over time. The persona maintains all of these itself; identity changes require human approval, everything else evolves automatically.

## CLI Aliases

Each persona is invokable by name from any directory. Shell functions in `~/.personas/.aliases.sh` auto-discover persona dirs and create aliases:

```bash
warren              # interactive session
warren "do weekly"  # one-shot prompt
```

The aliases file works in both bash and zsh. Source it from your shell config:

```bash
# In .bashrc or .zshrc:
[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"
```

Each alias `cd`s into `~/.personas/{name}/` and runs `claude --setting-sources project --dangerously-skip-permissions --remote-control`. These flags:
- Loads persona's `CLAUDE.md` (personality)
- Loads persona's `.claude/settings.json` (sandbox config)
- Loads persona's `.mcp.json` (tools)
- Ignores global `~/.claude/CLAUDE.md` and `~/.claude/settings.json`
- Skips permission prompts (safe because sandbox restricts filesystem + network)
- Enables browser extension and external tool integration via remote control

## Running Personas

| Mode | Command |
|------|---------|
| Interactive | `{name}` (sandbox + skip-permissions via alias) |
| One-shot | `{name} "prompt"` (sandbox + skip-permissions via alias) |

## Native Sandboxing

Each persona ships `.claude/settings.json` with sandbox config and `autoMemoryDirectory`. No Docker required — uses OS-level isolation (bubblewrap on Linux, Seatbelt on macOS).

```json
{
  "autoMemoryDirectory": "user/memory",
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

Every persona ships with a `self-improve` skill that drives evolution:

- **SessionStart hook** (`hooks.json`): Reads `user/profile.md` on every session (or triggers the first-session interview if unfilled)
- **Native auto-memory** (`user/memory/`): Handled automatically by Claude Code via `autoMemoryDirectory` — no custom hooks needed
- **Self-improve skill** (`skills/self-improve/SKILL.md`): Handles rule promotion, skill creation, tool & integration discovery, workspace hygiene, and periodic audits

The four levels: memory (automatic/native), rule promotion (propose), skill creation (propose), tool & integration discovery (research existing solutions first, then propose). Periodic audits include workspace hygiene — cleaning stale files, pruning unused tools, keeping the persona lean. See the self-improve skill for the full workflow.

## Session Start

On first session, `user/profile.md` exists as an unfilled copy of `profile-template.md`. The SessionStart hook reads it, follows the embedded interview instructions to ask the user the right questions, and populates each section. On returning sessions, the hook reads `user/profile.md` and checks for completeness.

## Lifecycle

All lifecycle operations use native Claude Code features or persona-manager skills:

| Action | How |
|--------|-----|
| Install persona-manager | `/plugin marketplace add kickinrad/personas` then `/plugin install persona-manager@personas` |
| Create persona | `Skill('persona-manager:persona-dev')` — scaffolds to `~/.personas/` |
| Add dashboard | `Skill('persona-dashboard:install')` — expansion pack |
| Push to GitHub | `gh repo create` during scaffolding, or `git push` anytime |
| Daily use | Shell alias (`{name}`, `{name} "prompt"`) |

## Private vs Public Personas

- **All personas are independent repos** in `~/.personas/{name}/`, each with their own git history
- **Public**: Uncomment `# user/` in `.gitignore`, push to a public GitHub repo
- **Private**: Keep local or push to a private repo
- **Going public**: Since each persona is its own repo, just create a fresh remote — no history scrubbing needed

## Security Rules

- **Never commit secrets** — `.mcp.json` is always gitignored; `user/` is optionally gitignored for public sharing
- **Use `pass`** for credentials in `.mcp.json`: `$(pass show service/key-name)`
- **Never hardcode** OAuth tokens, API keys, or JWT tokens
- **Sandbox** restricts each persona to its own directory + whitelisted network domains

## Gitignored (Never Commit)

Each persona's `.gitignore` handles its own secrets:

- `user/` — uncomment to share persona publicly (keeps personal data private)
- `.mcp.json` — API keys and secrets (always ignored)
- `.claude/settings.local.json` — local overrides (always ignored)
- `*.local.json`, `*.local.md` — local config variants
- `*.db*`, `*.log` — local databases and logs

## Git Flow

`feat/*` / `fix/*` / `docs/*` → `main`

Commits: `type(scope): description` — scope is `framework` for this repo, persona name for persona repos

## Gotchas

- Personas activate only when CWD is the persona's directory — `--setting-sources project` ensures total isolation
- MCP servers must be configured per-persona in `.mcp.json` (gitignored), not globally
- `.claude/settings.json` (sandbox config) IS committed — `.claude/settings.local.json` is gitignored
- Personas live in `~/.personas/`, NOT in this framework repo
- Output styles live in `.claude/output-styles/` — personality/tone is separate from rules in CLAUDE.md
