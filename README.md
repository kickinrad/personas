<p align="center">
  <img src="assets/banner.svg" alt="personas" width="650">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/kickinrad/personas?style=flat" alt="License"></a>
</p>

Self-evolving AI personas built on Claude Code.

Each persona is a standalone git-tracked directory with its own personality, skills, memory, and OS-level sandbox. Install the framework, scaffold a persona, and you have a dedicated AI assistant that remembers your context and improves itself over time. No Docker, no infrastructure, no configuration servers.

```
$ warren "weekly review"

📊 Weekly Financial Review — Mar 3-8, 2026

Income:   $4,200  ✓ on track
Spending: $2,847  ⚠️ dining out up 34% vs. last month
Savings:  $1,353  → auto-transferred to HYSA

Action items:
1. Dining budget is trending $400 over — cut back or reallocate?
2. Car insurance renewal hits Thursday — I found a $180/yr cheaper quote
3. Roth IRA contribution room: $2,500 remaining for 2026
```

## Quick Start

### Claude Code (CLI)

```bash
# 1. Install persona-manager as a Claude Code plugin
/plugin marketplace add kickinrad/personas
/plugin install persona-manager@personas

# 2. Create your first persona
persona-manager "create a personal CFO persona called warren"
# Scaffolds to ~/.personas/warren/ with sandbox, hooks, shell aliases — all automatic

# 3. First session — persona interviews you and builds your profile
warren
# Warren asks about your accounts, income, goals — writes user/profile.md from your answers

# 4. From now on, just use it
warren              # interactive session
warren "weekly review"  # one-shot prompt
```

### Claude Desktop (Cowork)

```bash
# 1. Install persona-manager as a Claude Code plugin
/plugin marketplace add kickinrad/personas
/plugin install persona-manager@personas

# 2. Create your first persona
persona-manager "create a personal CFO persona called warren"
# Scaffolds to ~/.personas/warren/ — same path on all platforms

# 3. Open the persona as a project folder in Claude Desktop
#    File → Open Project → ~/.personas/warren/

# 4. First session — persona interviews you and builds your profile
#    Warren asks about your accounts, income, goals — writes user/profile.md from your answers
```

Personas work identically in both environments — same directory structure, same sandbox config, same skills. The persona-dev skill auto-detects your environment and adjusts setup accordingly (shell aliases for CLI, project folder guidance for Desktop).

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

Personas can only write to their own directory, can't read parent directories or other personas' files, and can only reach whitelisted network domains. Each persona customizes `allowedDomains` for its own MCP servers.

### Running Personas

| Mode | How |
|------|-----|
| Interactive (CLI) | `warren` — shell alias, launches sandboxed session |
| One-shot (CLI) | `warren "weekly review"` — runs prompt and exits |
| Desktop (Cowork) | Open `~/.personas/warren/` as project folder |

Shell aliases auto-discover personas in `~/.personas/` and create callable functions. Under the hood: `cd ~/.personas/{name}/ && claude --setting-sources project --dangerously-skip-permissions --remote-control`. The flags load only the persona's config, skip permission prompts (safe because sandbox restricts everything), and enable external tool integration.

## What's Included

This repo ships **persona-manager** — the meta-tool that scaffolds and manages personas.

| Skill | What it does |
|-------|-------------|
| **persona-dev** | Scaffolds a new persona with CLAUDE.md, output style, profile template, sandbox config, hooks, self-improve skill, gitignore, and optional GitHub repo. Also handles persona updates and evolution. |
| **persona-dashboard** (separate plugin) | Expansion pack — adds an HTML dashboard with task tracking, profile viewer, memory browser, and system overview. Single-file app served locally on ports 7300-7399. |

Every scaffolded persona includes:
- `CLAUDE.md` with role, rules, session start, skills table
- `.claude/output-styles/{name}.md` with personality and tone
- `profile-template.md` as interview reference (persona writes `user/profile.md` from user answers)
- `hooks.json` with SessionStart hook (native auto-memory handles the rest)
- `self-improve` skill for the evolution engine
- `.claude/settings.json` with sandbox config and `autoMemoryDirectory`
- `.gitignore` protecting secrets (`.mcp.json` always ignored; `user/` optionally ignored for public sharing)

<details>
<summary>Persona Directory Structure</summary>

```
~/.personas/{name}/                       # Each persona is its own git-tracked directory
├── CLAUDE.md                             # Role, rules, skill refs (committed)
├── .claude/
│   ├── settings.json                     # Sandbox + autoMemoryDirectory (committed)
│   ├── output-styles/                    # Personality, tone, style (committed)
│   └── settings.local.json              # (always gitignored)
├── hooks.json                            # SessionStart hook (committed)
├── profile-template.md                    # Context template (committed)
├── .mcp.json                             # MCP servers + API keys (gitignored)
├── .gitignore                            # Secret protection (committed)
├── skills/
│   ├── {domain}/{skill}/SKILL.md         # Domain-specific skills
│   └── self-improve/SKILL.md             # Evolution engine
├── tools/                                # Utilities + scripts (persona-writable)
├── docs/                                 # Reference docs (persona-writable)
└── user/                                 # Personal data silo (optionally gitignored)
    ├── profile.md                        # Your personal data (filled from interview)
    └── memory/                           # Native auto-memory
        ├── MEMORY.md                     # Index (first 200 lines loaded)
        └── *.md                          # Topic files (read on demand)
```

</details>

<details>
<summary>Framework Repo Structure</summary>

```
personas/                            # This repo
├── plugins/
│   ├── persona-manager/             # Meta-tool
│   │   ├── skills/
│   │   │   └── persona-dev/         # Scaffolding + evolution skill
│   │   │       └── references/      # Templates copied to every persona
│   │   └── skill-rules.json         # Activation triggers
│   └── persona-dashboard/           # Dashboard expansion pack (separate plugin)
│       ├── skills/install/          # Dashboard installation skill
│       │   └── assets/              # HTML dashboard template
│       └── skill-rules.json         # Activation triggers
├── assets/                          # Logo + branding
└── tests/
    └── personas-test.sh             # Structure + secret validation
```

</details>

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
