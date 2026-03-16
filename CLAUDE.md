# Personas

Public framework for self-evolving AI assistants built on Claude Code. The framework repo contains persona-manager (the meta-tool); individual personas live in `~/.personas/{name}/` as independent git-tracked directories with sandbox isolation.

## Architecture

```
personas/                                 # Framework repo
├── CLAUDE.md                             # Framework-level context
├── .claude-plugin/marketplace.json       # Plugin registry (persona-manager)
├── plugins/
│   └── persona-manager/                  # Meta-tool: scaffolds + evolves personas
├── assets/                               # Logo + branding
└── tests/personas-test.sh

~/.personas/                              # Personas live here (outside this repo)
├── .aliases.sh                           # Shell functions for all personas (bash/zsh)
└── {persona}/                            # Each persona is its own git-tracked directory
    ├── CLAUDE.md                         # Role, rules, skill refs (committed)
    ├── .claude/
    │   ├── settings.json                 # Sandbox + autoMemoryDirectory (committed)
    │   ├── output-styles/               # Personality, tone, style (committed)
    │   ├── hooks/
    │   │   └── public-repo-guard.sh     # Blocks personal data in public repos (committed)
    │   └── settings.local.json          # (always gitignored)
    ├── hooks.json                        # SessionStart + Stop + PreCompact + PreToolUse hooks (committed)
    ├── .claude-flags                     # Per-persona CLI launch flags (committed)
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

## Running Personas

| Mode | How |
|------|-----|
| Interactive (CLI) | `{name}` — shell alias, sandboxed session |
| One-shot (CLI) | `{name} "prompt"` — runs prompt and exits |
| Desktop | Select `~/.personas/{name}/` as project folder |

### CLI Aliases

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

Each alias reads per-persona flags from `~/.personas/{name}/.claude-flags` (configured during persona setup). **All flags are optional** — persona-dev walks users through each one during Phase 7. Defaults by platform:

| Platform | Default flags |
|----------|---------------|
| macOS / Linux / WSL2 | `--setting-sources project --dangerously-skip-permissions --remote-control` |
| Windows native | `--setting-sources project --remote-control` |

**Available flags:**
- `--setting-sources project` — loads only persona's settings.json (ignores global `~/.claude/settings.json`). Keeps permissions, sandbox, and MCP config isolated
- `--dangerously-skip-permissions` — skips permission prompts. **Only safe when OS-level sandbox is available** (macOS/Linux/WSL2). **⚠ NEVER use on Windows native** — no sandbox means unrestricted filesystem + network access
- `--remote-control` — enables browser extension and external tool integration
- `--chrome` — enables Claude in Chrome browser automation (requires extension install). Only add for personas that need web interaction

If `.claude-flags` is missing, the alias falls back to safe defaults (no `--dangerously-skip-permissions`).

### Desktop

Select the persona directory as your project folder when starting a Claude Desktop session. Desktop reads the same CLAUDE.md, `.claude/settings.json`, hooks, output styles, and `.mcp.json` — the persona activates automatically. Desktop is available on **macOS and Windows only** — Linux users are CLI-only.

### Cross-Platform Setup

**macOS / Linux:** CLI and Desktop share `~/` — no extra setup needed.

**Windows + WSL2:** CLI runs inside WSL2 (`/home/user/`) while Desktop sees `C:\Users\user\`. During persona creation, persona-dev detects this and asks the user's preference:

- **CLI only**: personas stay in WSL2's `~/.personas/` (better I/O performance)
- **Desktop only**: personas go to `/mnt/c/Users/{WINUSER}/.personas/`
- **Both**: personas on Windows side + symlink from WSL2's `~/.personas/`. The symlink must be created from WSL terminal (not Cowork/Desktop): `ln -s /mnt/c/Users/{WINUSER}/.personas ~/.personas`

**Windows native (no WSL):** Personas live at `%USERPROFILE%\.personas\{name}\`. No bash aliases — use PowerShell functions or launch via Desktop. No sandbox support — `--dangerously-skip-permissions` is never used.

## Claude Environments

Personas run across multiple Claude environments. Each has different capabilities:

| Environment | Sandboxed? | Filesystem | MCP Config | Platform |
|---|---|---|---|---|
| **CLI** | Yes (Seatbelt/bubblewrap) | Full access within sandbox rules | `.mcp.json` (project) | macOS, Linux, WSL2, Windows* |
| **Desktop Code tab** | Yes (OS-level) | Same as CLI sandbox | `.mcp.json` (project) | macOS, Windows |
| **Desktop Chat** | No (server-side) | No direct filesystem access | `claude_desktop_config.json` (global) | macOS, Windows |
| **Cowork** | Yes (Linux VM) | Folder-scoped only, blocks symlink escapes | `claude_desktop_config.json` (global) | macOS (Apple Silicon only) |

*Windows native CLI has no sandbox support — `--dangerously-skip-permissions` must never be used.

**Key implications for personas:**
- MCP servers need to be in `.mcp.json` (CLI/Code tab) AND `claude_desktop_config.json` (Desktop Chat/Cowork) for full coverage
- Cowork cannot create symlinks outside its mounted folder — cross-environment setup must be done from a terminal
- Desktop Chat has no filesystem access — it relies entirely on MCP servers and conversation

## Platform Support

| Platform | CLI | Desktop | Sandbox | Home dir | Notes |
|---|---|---|---|---|---|
| **macOS** | Yes | Yes | Seatbelt (built-in) | `/Users/{USER}` | Cowork requires Apple Silicon |
| **Linux** | Yes | No | bubblewrap + socat | `/home/{USER}` | CLI only, install `bubblewrap socat` |
| **WSL2** | Yes | No* | bubblewrap + socat | `/home/{USER}` | Access Windows via `/mnt/c/`; I/O penalty across filesystems |
| **Windows native** | Yes | Yes | **Not supported** | `C:\Users\{USER}` | Requires Git for Windows; uses Git Bash internally |

*WSL2 users access Desktop through Windows — select persona folder on Windows side or via `/mnt/c/` symlink.

## Native Sandboxing

Each persona ships `.claude/settings.json` with sandbox config and `autoMemoryDirectory`. No Docker required — uses OS-level isolation:

| Platform | Sandbox implementation | Prerequisites |
|---|---|---|
| macOS | Seatbelt (kernel-level) | None (built-in) |
| Linux / WSL2 | bubblewrap (user-space) | `sudo apt install bubblewrap socat` |
| Windows native | **Not available** | Sandbox planned but not yet supported |

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

**Windows native caveat:** Since sandbox is not available, `--dangerously-skip-permissions` must never be used. Windows personas run with standard permission prompts. The `.claude-flags` file for Windows personas omits this flag.

## Self-Improvement (Core Feature)

Every persona ships with a `self-improve` skill that drives evolution:

- **SessionStart hook** (`hooks.json`): Reads `user/profile.md` on every session (or triggers the first-session interview if unfilled)
- **Native auto-memory** (`user/memory/`): Handled automatically by Claude Code via `autoMemoryDirectory` — no custom hooks needed
- **Self-improve skill** (`skills/self-improve/SKILL.md`): Handles rule promotion, skill creation, tool & integration discovery, workspace hygiene, and periodic audits

The four levels: memory (automatic/native), rule promotion (propose), skill creation (propose), tool & integration discovery (research existing MCP servers, CLI tools, APIs, then propose skills, agents, hooks, or scripts as needed). Periodic audits include workspace hygiene — cleaning stale files, pruning unused tools, keeping the persona lean. See the self-improve skill for the full workflow.

## Session Start

On first session, `user/profile.md` exists as an unfilled copy of `profile-template.md`. The SessionStart hook reads it, then the persona uses `AskUserQuestion` to interview the user section by section — structured input, not a wall of conversational text. On returning sessions, the hook reads `user/profile.md` and checks for completeness.

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
- **Private (default)**: Safe to commit everything including `user/`. Keep local or push to a private repo
- **Public**: The persona handles the transition — uncomments `user/` in `.gitignore`, removes `user/` from tracking, and creates a fresh remote. The `public-repo-guard.sh` hook blocks any commit/push that would expose personal data in a public repo
- **Going public later**: The persona handles it automatically — don't rely on the user to remember. Create a fresh remote rather than pushing history that may contain personal data

## Security Rules

- **Never commit secrets** — `.mcp.json` is always gitignored; `user/` is optionally gitignored for public sharing
- **Use `pass`** for credentials in `.mcp.json`: `$(pass show service/key-name)`
- **Never hardcode** OAuth tokens, API keys, or JWT tokens
- **Sandbox** restricts each persona to its own directory + whitelisted network domains
- **Never use `--dangerously-skip-permissions` on Windows native** — no OS-level sandbox exists; this flag grants unrestricted access to the entire filesystem and network. persona-dev enforces this during setup and must refuse even if the user insists

### Public Repo Guard

Every persona ships with a `public-repo-guard.sh` hook (`.claude/hooks/public-repo-guard.sh`) that fires on `git commit` and `git push` via a PreToolUse hook in `hooks.json`. For public repos, the guard blocks if:
- `user/` is not gitignored (personal data would be exposed)
- `user/` files are staged for commit
- `.mcp.json` is tracked (API keys would be exposed)
- Files matching secret patterns (`*.env`, `*.key`, `*.pem`, etc.) are staged

Private repos are allowed through without checks — personal data backup is safe there.

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

**Version bumping:** Bump `plugins/persona-manager/.claude-plugin/plugin.json` AND `.claude-plugin/marketplace.json` version fields together on every feature or fix commit to persona-manager. Use semver — patch for fixes, minor for features, major for breaking changes.

## MCP Server Configuration

MCP servers are configured in two places depending on the environment:

| Environment | Config file | Scope |
|-------------|-----------|-------|
| CLI + Desktop Code tab | `.mcp.json` (in persona dir) | Per-persona, gitignored |
| Desktop Chat + Cowork | `claude_desktop_config.json` | Global, per-machine |

**Why two files?** CLI and the Desktop Code tab read project-scoped `.mcp.json`. But Desktop Chat and Cowork run as part of Claude Desktop and only read the global `claude_desktop_config.json`. If users want MCP tools available across all environments, servers need to be in both files.

**Desktop config location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json` (from WSL2: `/mnt/c/Users/{WINUSER}/AppData/Roaming/Claude/claude_desktop_config.json`)

During persona setup, persona-dev offers to merge MCP servers into `claude_desktop_config.json` when setup mode includes Desktop. The user just needs to restart Claude Desktop for changes to take effect.

**Credential handling:** Use environment variable expansion in `.mcp.json` (`${API_KEY}`). Never hardcode secrets — `.mcp.json` is gitignored but should still be clean.

**`tools/` vs MCP:**
- `tools/` — local scripts and utilities invoked by the persona via bash
- MCP servers — persistent connections to external services (APIs, databases)
- Don't mix them

## Hooks

Every persona ships four hooks in `hooks.json`:
- **PreToolUse** (command, matcher: Bash): Runs `public-repo-guard.sh` before git commit/push — blocks personal data exposure in public repos
- **SessionStart** (command): Reads `user/profile.md` into session context; triggers interview if unfilled
- **Stop** (prompt): Reminds persona to persist meaningful learnings to `user/memory/` before ending
- **PreCompact** (prompt): Saves session context to memory before compaction

## Gotchas

- Personas activate only when CWD is the persona's directory — `--setting-sources project` isolates settings.json (permissions, sandbox, MCP) but global `~/.claude/CLAUDE.md` still loads
- MCP servers need to be in both `.mcp.json` (CLI/Code tab) and `claude_desktop_config.json` (Desktop Chat/Cowork) — persona-dev handles this
- `.claude/settings.json` (sandbox config) IS committed — `.claude/settings.local.json` is gitignored
- Personas live in `~/.personas/`, NOT in this framework repo
- Output styles live in `.claude/output-styles/` — personality/tone is separate from rules in CLAUDE.md
- `--dangerously-skip-permissions` must NEVER be used on Windows native (no sandbox)
- Desktop app is macOS + Windows only — Linux users are CLI-only
- Cowork is macOS Apple Silicon only — cannot create symlinks outside mounted folders
- Per-persona launch flags live in `.claude-flags` (read by `.aliases.sh`)

## Testing

```bash
bash tests/personas-test.sh
```
