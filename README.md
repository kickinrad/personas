<p align="center">
  <img src="assets/banner.svg" alt="personas" width="650">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/kickinrad/personas?style=flat" alt="License"></a>
</p>

Self-evolving AI personas built on Claude Code.

Personas are not chat workspaces with sticky instructions — they're standalone AI agents that learn about you, grow new skills, and improve themselves over time. Each one is a git-tracked directory with its own personality, memory, sandbox, hooks, and tool integrations. Scaffold one, launch it by name from any terminal, and watch it evolve from a blank slate into a specialized assistant that knows how you work. No Docker, no infrastructure, no configuration servers — just native Claude Code features composed into something greater.

```
$ chef "what should I make tonight?"

🍳 Based on what's in your pantry + this week's goals:

You have chicken thighs defrosting, plus rice and that gochujang
from last week. Let's do dakgalbi (spicy Korean chicken stir-fry).

  Prep: 15 min  Cook: 20 min  Calories: ~480

I'll skip the cabbage since you mentioned hating it last time.
Want the shopping list for sides, or just rolling with what you have?
```

## Quick Start

### Step 1: Install the plugin and create a persona

Persona creation requires the persona-manager plugin. Install it once — after setup, the persona works everywhere.

<details open>
<summary><strong>Claude Code (CLI)</strong></summary>

```
/plugin marketplace add kickinrad/personas
/plugin install persona-manager@personas
```

Launch Claude Code as normal and get your ideas ready. 

</details>

<details>
<summary><strong>Claude Desktop</strong></summary>

Open Claude Desktop and navigate to Customize pane→ **Personal Plugins +** → **Browse Plugins** -> Personal ->  + Add Marketplace from Github,  enter `kickinrad/personas` and install **persona-manager** and any desired expansion packs. Create a new Cowork instance starting in your default user directory, and invoke the plugin to begin. 

Alternatively, navigate to the "Customize" menu, select the Persona Manager personal plugin, the select the Persona Dev skill and use the three dot menu to copy the skill or run it in Claude Desktop Chat. Because of CoWork's sandboxing, this can be preferable for setting up WSL compatibility, aliases, and advanced configs.

</details>

Then ask Claude to create your persona: 

```
create a personal chef persona called chef
```

The `persona-dev` skill activates automatically — it scaffolds everything to `~/.personas/chef/` including sandbox config, hooks, output style, self-improve skill, and gitignore. It asks whether you'll use CLI, Desktop, or both, and configures paths and MCP servers accordingly.

### Step 2: Launch your persona

Once created, the persona works in any environment:

| Mode | How |
|------|-----|
| CLI | `chef` or `chef "what should I make?"` — shell aliases set up during creation |
| Cowork | Select `~/.personas/chef/` as project folder |
| Desktop Chat | Select `~/.personas/chef/` as project folder |

If the persona uses MCP servers, persona-dev offers to configure them in your `claude_desktop_config.json` so Cowork and Desktop Chat can access them too.

On first launch, the persona interviews you to build your profile — it asks the right questions based on its role, then writes `user/profile.md` from your answers. Every session after that, it reads your profile and picks up where you left off.

### Cross-platform notes

- **macOS / Linux** — CLI and Desktop share `~/`, so `~/.personas/` works everywhere. No extra setup.
- **Windows (native)** — Personas live at `%USERPROFILE%\.personas\`. No bash aliases — use PowerShell functions or launch via Desktop. No sandbox support, so `--dangerously-skip-permissions` is never used.
- **WSL** — CLI runs in WSL (`/home/user/`) while Desktop sees `C:\Users\user\`. If you use both, persona-dev creates personas on the Windows side and symlinks `~/.personas/` in WSL so both environments see the same files. If you only use CLI, personas stay in WSL for better I/O performance.

## How It Works

Personas interview you on first launch, remember what they learn across sessions, propose new rules when patterns emerge, draft reusable skills when workflows repeat, and discover tools and integrations for their domain. They run from your terminal, live in git, and are sandboxed at the OS level so they can't touch anything outside their own directory.

**A persona is a self-contained AI assistant.** It combines standard Claude Code features — identity (CLAUDE.md), output style (`.claude/output-styles/`), user context (`user/profile.md`), skills, hooks, MCP tools, sandbox settings, and native auto-memory (`user/memory/`) — into a specialized agent that evolves over time. The persona maintains all of these itself; identity changes require human approval, everything else evolves automatically.

### Self-Improvement

Personas ship with a `self-improve` skill and a SessionStart hook that drive automatic evolution:

1. **Memory** — native auto-memory via `autoMemoryDirectory` captures learnings automatically; SessionStart hook reads profile context
2. **Rule promotion** — after a pattern appears 3+ times in memory, the persona proposes a permanent rule in CLAUDE.md
3. **Skill creation** — after an ad-hoc workflow repeats 3+ times, the persona drafts a reusable skill
4. **Tool & integration discovery** — researches MCP servers, CLI tools, APIs, and expansion packs; creates skills to wrap them, agents for autonomous subtasks, hooks for behavioral automation, and scripts for data processing — always preferring existing solutions over custom builds

Every level above memory requires your approval before changes are committed. You stay in control; the persona does the legwork.

### Sandboxing

Each persona runs in a native OS sandbox (bubblewrap on Linux, Seatbelt on macOS) configured in `.claude/settings.json`:

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

Personas can only write to their own directory, can't read parent directories or other personas' files, and can only reach whitelisted network domains. Each persona customizes `allowedDomains` for its own MCP servers. Sandboxing not available on Windows Claude Code CLI. 

### Tools & Integrations

Personas have a full toolkit available — not just MCP servers. During setup, persona-dev researches your domain and recommends the right mix:

| Type | Where it lives | Best for |
|------|---------------|----------|
| MCP servers | `.mcp.json` + sandbox allowlist | Persistent connections to external services |
| CLI tools | Documented in CLAUDE.md or wrapped in skills | Leveraging mature existing tools |
| APIs | `tools/` scripts or skill instructions | Direct HTTP calls without an MCP server |
| Skills | `skills/{domain}/{name}/SKILL.md` | Reusable workflows wrapping any of the above |
| Agents | `.claude/agents/{name}.md` | Autonomous subtasks needing their own context |
| Hooks | `hooks.json` | Behavioral automation tied to session events |
| Scripts | `tools/` | Data pipelines, formatters, utilities |

For MCP servers specifically:
- **CLI + Code tab** — config lives in the persona's `.mcp.json` (gitignored)
- **Desktop Chat + Cowork** — persona-dev merges servers into `claude_desktop_config.json` so all environments can access them

### Shell Aliases

Shell aliases auto-discover personas in `~/.personas/` and create callable functions. Each persona stores its launch flags in `.claude-flags` (configured during setup). During setup, persona-dev walks through each flag with the user:

- `--setting-sources project` — isolates persona's settings from global config
- `--dangerously-skip-permissions` — autonomous mode (only on sandboxed platforms: macOS/Linux/WSL2, never Windows)
- `--remote-control` — enables external tool connections
- `--chrome` — enables Chrome browser automation (only for personas that need web interaction)

### Public Repo Safety

Personas collect personal data — your profile, preferences, and session memories live in `user/`. Every persona ships with a **public repo guard** (`.claude/hooks/public-repo-guard.sh`) that automatically blocks `git commit` and `git push` if personal data would be exposed in a public repository.

- **Private repos** — safe to commit everything, including `user/`. Great for backup and cross-machine sync
- **Public repos** — the guard checks that `user/` is gitignored, no personal files are staged, and no secret patterns (`*.env`, `*.key`, `*.pem`) are being committed. If any check fails, the commit is blocked with instructions to fix it

When a persona goes public, it handles the transition itself — updating `.gitignore`, removing `user/` from tracking, and creating a fresh remote so old history with personal data never reaches the public repo.

## What's Included

This repo ships **persona-manager** — the meta-tool that scaffolds and manages personas.

| Skill | What it does |
|-------|-------------|
| **persona-dev** | Scaffolds a new persona with CLAUDE.md, output style, profile template, sandbox config, hooks, self-improve skill, gitignore, and optional GitHub repo. Also handles persona updates and evolution. |


## Expansion Packs

| Pack | What it does |
|------|-------------|
| **persona-dashboard** | Adds an HTML dashboard with task tracking, profile viewer, memory browser, and system overview. Single-file app served locally on ports 7300-7399. |
| **remote-deploy** | Deploys a persona to a remote server as a Docker container with Tailscale SSH access and bidirectional sync. Guided 7-phase walkthrough covers server setup, hardening, Tailscale, Docker, deployment, and post-install tooling (`/sync`, `/remote-status`, remote shell alias). |

Every scaffolded persona includes:
- `CLAUDE.md` with role, rules, session start, skills table
- `.claude/output-styles/{name}.md` with personality and tone
- `profile-template.md` as interview reference (persona writes `user/profile.md` from user answers)
- `hooks.json` with SessionStart, Stop, PreCompact, and public repo guard hooks
- `.claude/hooks/public-repo-guard.sh` — blocks commits/pushes that would expose personal data in public repos
- `self-improve` skill for the evolution engine
- `.claude/settings.json` with sandbox config and `autoMemoryDirectory`
- `.gitignore` protecting secrets (`.mcp.json` always ignored; `user/` optionally ignored for public sharing)

## Documentation

All documentation lives in the persona-manager skill system — install the plugin and the skills guide you through everything:

| Skill | What it covers |
|-------|---------------|
| `persona-dev` | Creating, updating, and evolving personas — discovery, scaffolding, shell setup, testing, troubleshooting |
| `persona-dashboard:install` | Expansion pack — adds HTML dashboard with task tracking and status overview |
| `remote-deploy:install` | Expansion pack — deploys persona to a remote server with Docker, Tailscale SSH, and bidirectional sync |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kickinrad/personas&type=Date)](https://star-history.com/#kickinrad/personas&Date)

## License

[Apache-2.0](LICENSE)
