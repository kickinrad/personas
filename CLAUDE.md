---
title: personas
---

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
    │   ├── settings.json                 # Sandbox + statusLine config (committed)
    │   ├── settings.local.json          # autoMemoryDirectory + outputStyle (gitignored, created during setup)
    │   ├── output-styles/               # Personality, tone, style (committed)
    │   ├── hooks/
    │   │   └── public-repo-guard.sh     # Blocks personal data in public repos (committed)
    │   └── skills/
    │       ├── {domain}/{skill}/SKILL.md # Domain skills (committed)
    │       └── self-improve/SKILL.md     # Ships with every persona
    ├── hooks.json                        # SessionStart + Stop + StopFailure + PreCompact + PostCompact + PreToolUse hooks (committed)
    ├── .framework-version                # Framework version stamp (committed)
    ├── .claude-flags                     # Per-persona CLI launch flags (committed)
    ├── .persona-cwd                      # Optional: redirect cwd to another path (stub-mode personas only)
    ├── docs/                              # Reference materials, plans (committed)
    ├── .mcp.json                         # MCP server config (gitignored)
    ├── tools/                            # Utilities, scripts, pipelines (committed)
    └── user/                             # Personal data silo (optionally gitignored)
        ├── profile.md                    # User's personal data (filled from interview)
        └── memory/                       # Native auto-memory
            ├── MEMORY.md                 # Index (first 200 lines loaded)
            └── *.md                      # Topic files (read on demand)
```

## What Is a Persona?

**A persona is a self-contained AI assistant.** It combines standard Claude Code features — identity (CLAUDE.md), output style (`.claude/output-styles/`), user context (`user/profile.md`), skills, hooks, MCP tools, sandbox settings, statusline, scheduled tasks, and native auto-memory (`user/memory/`) — into a specialized agent that evolves over time. The persona maintains all of these itself; identity changes require human approval, everything else evolves automatically.

The persona's content splits between two files: **output-style** (`.claude/output-styles/`) defines WHO the persona IS — voice, personality, opinions, narrative expertise, character-driven refusals. **CLAUDE.md** defines WHAT the persona DOES — role summary, operational procedures, skills, tools, security rules. Boundary test: "Would this change how the persona SOUNDS, or what it DOES?"

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
| macOS / Linux / WSL2 | `--name {name} --setting-sources project,local --dangerously-skip-permissions --remote-control` |
| Windows native | `--name {name} --setting-sources project,local --remote-control` |

**Available flags:**
- `--name {name}` — labels the session in the terminal title and prompt bar with the persona's name
- `--setting-sources project,local` — loads only persona's `settings.json` and `settings.local.json`, ignoring `~/.claude/settings.json`. Keeps permissions, sandbox, MCP config, and memory config isolated. **Note:** this flag does NOT affect `CLAUDE.md` loading — `~/.claude/CLAUDE.md` is blocked separately via `claudeMdExcludes` in the persona's `.claude/settings.json` (see [Inheritance & Isolation Matrix](#inheritance--isolation-matrix))
- `--dangerously-skip-permissions` — skips permission prompts. **Only safe when OS-level sandbox is available** (macOS/Linux/WSL2). **⚠ NEVER use on Windows native** — no sandbox means unrestricted filesystem + network access
- `--remote-control` — enables browser extension and external tool integration
- `--chrome` — enables Claude in Chrome browser automation (requires extension install). Only add for personas that need web interaction

If `.claude-flags` is missing, the alias falls back to safe defaults (no `--dangerously-skip-permissions`).

**Optional `.persona-cwd` redirect.** A persona can live somewhere other than `~/.personas/{name}/` by making that directory a stub: keep `CLAUDE.md`, `.claude-flags`, `.framework-version`, plus a single-line `.persona-cwd` file containing the absolute target path. The alias loader reads `.persona-cwd` and `cd`s into that path before launching `claude`. Used for personas that share a working directory with another tool (e.g. Piper lives at the Obsidian vault root, `/mnt/c/Users/wilst/Vault/`). The stub still appears under `Areas/Personas/{name}/` when the vault uses Folder Bridge to surface `~/.personas/`, which avoids recursing into the redirect target. Without `.persona-cwd`, the alias `cd`s into `${_persona_dir}` as before — fully backwards-compatible.

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

Each persona ships `.claude/settings.json` with sandbox config. No Docker required — uses OS-level isolation:

| Platform | Sandbox implementation | Prerequisites |
|---|---|---|
| macOS | Seatbelt (kernel-level) | None (built-in) |
| Linux / WSL2 | bubblewrap (user-space) | `sudo apt install bubblewrap socat` |
| Windows native | **Not available** | Sandbox planned but not yet supported |

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
  },
  "extraKnownMarketplaces": {
    "personas": {
      "source": { "source": "github", "repo": "kickinrad/personas" }
    }
  },
  "enabledPlugins": {
    "persona-manager@personas": true
  }
}
```

Each persona customizes allowed domains for its MCP servers and APIs. Personas cannot read parent directories or other personas' files. The `extraKnownMarketplaces` and `enabledPlugins` entries auto-install persona-manager, giving every persona access to persona-dev for self-evolution.

**Windows native caveat:** Since sandbox is not available, `--dangerously-skip-permissions` must never be used. Windows personas run with standard permission prompts. The `.claude-flags` file for Windows personas omits this flag.

## Inheritance & Isolation Matrix

What persona sessions inherit from `~/.claude/` and how to control it. The framework picks isolation defaults, but the user can adjust per-persona.

| Surface | User-level location | Default in personas | Control mechanism |
|---------|---------------------|---------------------|-------------------|
| `settings.json` | `~/.claude/settings.json` | **Isolated** | `--setting-sources project,local` (in `.claude-flags`) |
| `CLAUDE.md` | `~/.claude/CLAUDE.md` | **Isolated** | `claudeMdExcludes: ["**/.claude/CLAUDE.md"]` in persona's `.claude/settings.json` |
| Plugins | `~/.claude/plugins/marketplaces/` | **Opt-in only** — persona declares which plugins to load | `enabledPlugins` map in persona's `.claude/settings.json` |
| Hooks | declared in plugins or persona's `hooks.json` | Persona-controlled | Plugin's `hooks.json` (loads with the plugin) + persona's `hooks.json` |
| MCPs (CLI / Desktop Code tab) | (none — project-scoped) | Per-persona | `.mcp.json` in persona root (gitignored) |
| MCPs (Desktop Chat / Cowork) | `claude_desktop_config.json` | Shared globally | Edit Desktop config — out of band |
| Loose skills/agents/commands | `~/.claude/{skills,agents,commands}/` | Anthropic docs are silent on `--setting-sources` interaction. Surface is minimal in practice — most components ship via plugins | None documented (no `skillExcludes` etc.) |
| Statusline | `~/.claude/statusline.sh` | **Deliberately shared** | Persona's `settings.json` references `~/.claude/statusline.sh` so all sessions render consistently |

**Granularity model:** Each persona's `.claude/settings.json` is the granularity surface. Edit `enabledPlugins` to add/remove plugin inheritance; edit `claudeMdExcludes` to add/remove path exclusions; remove the statusLine entry to drop the shared statusline. The scaffold (`persona-dev`) asks about inheritance posture during creation.

## Self-Improvement (Core Feature)

Every persona ships with a `self-improve` skill that drives evolution:

- **SessionStart hook** (`hooks.json`): Instructs the persona to read `user/profile.md` on every session (or triggers the first-session interview if unfilled)
- **Native auto-memory** (`user/memory/`): Redirected via `autoMemoryDirectory` in `.claude/settings.local.json` (not settings.json — Claude ignores it there as a security measure). Must use an **absolute path** (relative paths break on WSL). Personas never manually write to `user/memory/` — auto-memory owns that directory entirely. Stop and PreCompact hooks prompt reflection (not file writes); StopFailure and PostCompact hooks handle crash recovery
- **Self-improve skill** (`skills/self-improve/SKILL.md`): Handles rule promotion, skill creation, tool & integration discovery, workspace hygiene, and periodic audits

The four levels: memory (automatic/native), rule promotion (propose), skill creation (propose), tool & integration discovery (research existing MCP servers, CLI tools, APIs, then propose skills, agents, hooks, or scripts as needed). Periodic audits include workspace hygiene — cleaning stale files, pruning unused tools, keeping the persona lean. See the self-improve skill for the full workflow.

## Session Start

On first session, `user/profile.md` contains an unfilled template with placeholders and interview instructions. The SessionStart hook instructs the persona to read it, then uses `AskUserQuestion` to interview the user section by section — structured input, not a wall of conversational text. The persona fills `user/profile.md` in place. On returning sessions, the hook instructs the persona to read the populated profile and check for completeness.

## Lifecycle

All lifecycle operations use native Claude Code features or persona-manager skills:

| Action | How |
|--------|-----|
| Install persona-manager | `/plugin marketplace add kickinrad/personas` then `/plugin install persona-manager@personas` (first time only — each persona auto-installs it via `enabledPlugins` in settings.json) |
| Create persona | `Skill('persona-manager:persona-dev')` — scaffolds to `~/.personas/` |
| Add dashboard | `Skill('persona-dashboard:install')` — expansion pack |
| Update persona | `Skill('persona-manager:persona-update')` — diffs against templates, persona applies changes |
| Validate persona | `persona-validator` agent — checks scaffold completeness and framework compliance |
| Push to GitHub | `gh repo create` during scaffolding, or `git push` anytime |
| Daily use | Shell alias (`{name}`, `{name} "prompt"`) |

## Private vs Public Personas

- **All personas are independent repos** in `~/.personas/{name}/`, each with their own git history
- **Private (default)**: Safe to commit everything including `user/`. Keep local or push to a private repo
- **Public**: The persona handles the transition — uncomments `user/` in `.gitignore`, removes `user/` from tracking, and creates a fresh remote. The `public-repo-guard.sh` hook blocks any commit/push that would expose personal data in a public repo
- **Going public later**: The persona handles it automatically — don't rely on the user to remember. Create a fresh remote rather than pushing history that may contain personal data

## Security Rules

- **Never commit secrets** — `.mcp.json` is always gitignored; `user/` is optionally gitignored for public sharing
- **Use environment variables** for credentials in `.mcp.json` (e.g., `${API_KEY}`) or a CLI password manager if available
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

**Version bumping:** Bump `version` in `plugins/persona-manager/.claude-plugin/plugin.json` on every feature or fix commit to persona-manager. Plugin.json is the single source of truth for version. Never add a `version` field to `marketplace.json` `plugins[]` entries — that field belongs in plugin.json only. Separately, `.claude-plugin/marketplace.json#metadata.version` is the marketplace's own structural version and bumps only when the marketplace itself changes. Use semver: patch for fixes, minor for features, major for breaking changes.

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

Every persona ships six hooks in `hooks.json`:
- **PreToolUse** (command, matcher: Bash): Runs `public-repo-guard.sh` before git commit/push — blocks personal data exposure in public repos
- **SessionStart** (command): Instructs the persona to read `user/profile.md` and interview if unfilled. Dependency-free — just echoes a JSON instruction
- **Stop** (prompt): Prompts the persona to reflect on session insights — native auto-memory captures them automatically. No manual file writes
- **StopFailure** (command): Writes a crash marker (`user/memory/.last-crash`) when a session dies from an API error — enables crash recovery on next session
- **PreCompact** (prompt): Prompts reflection before compaction — auto-memory handles persistence. No manual file writes
- **PostCompact** (command): After compaction, checks for the crash marker and reminds the persona to review lost context

## Statusline

Every persona's `.claude/settings.json` wires `statusLine` to `~/.claude/statusline.sh` — the user's machine-level statusline script. The path uses `~` expansion (no hardcoded home dir), so the same committed setting works for any user. If the script doesn't exist on a host, the statusline silently no-ops (cosmetic only — no functional impact). Personas don't ship the script itself; that lives at the user level so a single source of truth styles every Claude Code session including all personas.

## Scheduled Tasks

Claude Code has built-in scheduling via `CronCreate`, `CronList`, and `CronDelete` tools. Any persona can use these — scheduling is a core capability, not tied to any expansion pack.

**Session-scoped:** Tasks live in the current Claude Code process and are gone when you exit. For durable scheduling that survives restarts, use [web scheduled tasks](#web-scheduled-tasks-durable).

### How personas use scheduling

Personas can schedule tasks using natural language — Claude handles the cron expression:

| Use case | Example |
|----------|---------|
| Timed reminder | "remind me at 3pm to push the release branch" |
| Delayed check | "in 45 minutes, check whether the integration tests passed" |
| Recurring check | "every 30 minutes, check if the deploy finished" |

### Key details

- **Natural language** is the primary interface — describe what and when, Claude creates the cron job
- **Cron expressions** are standard 5-field format when using `CronCreate` directly
- **All times are local timezone**, not UTC
- **3-day expiry** — recurring tasks auto-expire after 3 days. Cancel and recreate for longer runs
- **Max 50 tasks** per session
- Tasks fire between turns (not mid-response). If Claude is busy, the task waits
- **Disable** with `CLAUDE_CODE_DISABLE_CRON=1`

### Web scheduled tasks (durable)

For scheduling that survives session restarts, use **scheduled tasks on claude.ai/code**. These are persistent, project-scoped tasks that run on a cron-like frequency (daily, weekly, etc.) without an active session.

**How it works:**
1. Open [claude.ai/code](https://claude.ai/code) and click **Scheduled** in the sidebar
2. Create a new task: name, prompt, frequency, time, and select the persona's repo as the project
3. The task runs server-side at the scheduled time — the persona's CLAUDE.md and project context load automatically

**Key differences from session-scoped scheduling:**

| | `CronCreate` (CLI) | Web scheduled tasks |
|---|---|---|
| Persistence | Session-scoped — gone on exit | Durable — survives restarts |
| MCP access | `.mcp.json` (project-scoped) | **Connected integrations only** (Gmail, Calendar, etc. from [claude.ai/settings/connectors](https://claude.ai/settings/connectors)) |
| Platform | CLI, Desktop | Web (claude.ai/code) |
| Branch pushes | N/A | Configurable — can allow unrestricted pushes |

**Important:** Web scheduled tasks can only use **connected integrations** (cloud-configured MCP servers), not the persona's `.mcp.json`. If a persona needs external service access in scheduled tasks, those services must be connected at [claude.ai/settings/connectors](https://claude.ai/settings/connectors).

**Persona use cases:**
- Daily self-improvement audits (memory cleanup, skill gap checks)
- Recurring domain tasks (morning briefings, PR reviews, report generation)
- Autonomous commits to the persona's own repo (with unrestricted branch pushes enabled)

## Gotchas

- Personas activate only when CWD is the persona's directory — `--setting-sources project,local` isolates `settings.json` only; CLAUDE.md isolation requires `claudeMdExcludes` in the persona's `.claude/settings.json`
- MCP servers need to be in both `.mcp.json` (CLI/Code tab) and `claude_desktop_config.json` (Desktop Chat/Cowork) — persona-dev handles this
- `.claude/settings.json` (sandbox config) IS committed — `.claude/settings.local.json` is gitignored
- Personas live in `~/.personas/`, NOT in this framework repo
- Output styles live in `.claude/output-styles/` — personality/tone is separate from rules in CLAUDE.md
- `--dangerously-skip-permissions` must NEVER be used on Windows native (no sandbox)
- Desktop app is macOS + Windows only — Linux users are CLI-only
- Cowork is macOS Apple Silicon only — cannot create symlinks outside mounted folders
- Per-persona launch flags live in `.claude-flags` (read by `.aliases.sh`)
- Scheduled tasks (`CronCreate`) are session-scoped — they vanish when the session exits. For durable scheduling, use [web scheduled tasks](#web-scheduled-tasks-durable)

## Testing

```bash
bash tests/personas-test.sh
```
