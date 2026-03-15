<p align="center">
  <img src="assets/banner.svg" alt="personas" width="650">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/kickinrad/personas?style=flat" alt="License"></a>
</p>

Self-evolving AI personas built on Claude Code.

Each persona is a standalone git-tracked directory with its own personality, skills, memory, and OS-level sandbox. Install the framework, scaffold a persona, and you have a dedicated AI assistant that remembers your context and improves itself over time. No Docker, no infrastructure, no configuration servers.

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

**A persona is a self-contained AI assistant.** It combines standard Claude Code features — identity (CLAUDE.md), output style (`.claude/output-styles/`), user context (`user/profile.md`), skills, hooks, MCP tools, sandbox settings, and native auto-memory (`user/memory/`) — into a specialized agent that evolves over time. The persona maintains all of these itself; identity changes require human approval, everything else evolves automatically.

### Self-Improvement

Personas ship with a `self-improve` skill and a SessionStart hook that drive automatic evolution:

1. **Memory** — native auto-memory via `autoMemoryDirectory` captures learnings automatically; SessionStart hook reads profile context
2. **Rule promotion** — after a pattern appears 3+ times in memory, the persona proposes a permanent rule in CLAUDE.md
3. **Skill creation** — after an ad-hoc workflow repeats 3+ times, the persona drafts a reusable skill
4. **Tool & integration discovery** — researches existing MCP servers, CLI tools, and expansion packs before building custom solutions

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

### MCP Servers & Tools

Personas can connect to external services via MCP servers (recipe APIs, financial data, calendars, etc.). During setup, persona-dev researches available MCP servers for your domain and configures them automatically.

- **CLI + Code tab** — MCP config lives in the persona's `.mcp.json` (gitignored)
- **Desktop Chat + Cowork** — persona-dev merges the same servers into `claude_desktop_config.json` so Desktop Chat and Cowork can access them too

Local scripts and utilities go in `tools/` — the persona creates and invokes these via bash. MCP is for external service connections.

### Shell Aliases

Shell aliases auto-discover personas in `~/.personas/` and create callable functions. Each persona stores its launch flags in `.claude-flags` (configured during setup). On sandboxed platforms (macOS/Linux/WSL2) the default is `--setting-sources project --dangerously-skip-permissions --remote-control`. On Windows native, `--dangerously-skip-permissions` is omitted because there's no OS-level sandbox.

## What's Included

This repo ships **persona-manager** — the meta-tool that scaffolds and manages personas.

| Skill | What it does |
|-------|-------------|
| **persona-dev** | Scaffolds a new persona with CLAUDE.md, output style, profile template, sandbox config, hooks, self-improve skill, gitignore, and optional GitHub repo. Also handles persona updates and evolution. |


## Expansion Packs

| **persona-dashboard** (separate plugin) | Adds an HTML dashboard with task tracking, profile viewer, memory browser, and system overview. Single-file app served locally on ports 7300-7399. |

Every scaffolded persona includes:
- `CLAUDE.md` with role, rules, session start, skills table
- `.claude/output-styles/{name}.md` with personality and tone
- `profile-template.md` as interview reference (persona writes `user/profile.md` from user answers)
- `hooks.json` with SessionStart, Stop, and PreCompact hooks
- `self-improve` skill for the evolution engine
- `.claude/settings.json` with sandbox config and `autoMemoryDirectory`
- `.gitignore` protecting secrets (`.mcp.json` always ignored; `user/` optionally ignored for public sharing)

## Documentation

All documentation lives in the persona-manager skill system — install the plugin and the skills guide you through everything:

| Skill | What it covers |
|-------|---------------|
| `persona-dev` | Creating, updating, and evolving personas — discovery, scaffolding, shell setup, testing, troubleshooting |
| `persona-dashboard:install` | Expansion pack — adds HTML dashboard with task tracking and status overview (separate plugin) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kickinrad/personas&type=Date)](https://star-history.com/#kickinrad/personas&Date)

## License

[Apache-2.0](LICENSE)
