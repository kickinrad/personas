<p align="center">
  <img src="assets/banner.svg" alt="personas" width="600">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/kickinrad/personas?style=flat" alt="License"></a>
</p>

Self-evolving AI personas built on Claude Code.

Each persona is a standalone git-tracked directory with its own personality, skills, memory, and OS-level sandbox. Install the framework, scaffold a persona, type its name from any directory — you have a dedicated AI assistant that remembers your context and improves itself over time. No Docker, no infrastructure, no configuration servers.

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

```bash
# 1. Install persona-manager as a Claude Code plugin
/plugin marketplace add kickinrad/personas
/plugin install persona-manager@personas

# 2. Create your first persona
persona-manager "create a personal CFO persona called warren"
# Scaffolds to ~/.personas/warren/ with sandbox, hooks, self-improve skill

# 3. Set up shell aliases (add to .zshrc or .bashrc)
source ~/.personas/.aliases.sh

# 4. First session — persona guides you through profile setup
warren
# Warren asks about your accounts, income, goals — saves to profile.md

# 5. From now on, just use it
warren              # interactive session
warren "weekly review"  # one-shot prompt
```

All setup and creation details live in the `persona-dev` skill — install persona-manager and it guides you through everything.

## How It Works

### Three-Layer Model

Every persona separates what it is from what it knows about you from what it learns:

| Layer | File | Who Writes | Committed? |
|-------|------|-----------|------------|
| **Personality** | `CLAUDE.md` | Human (Claude proposes) | Yes |
| **Context** | `profile.md` | Human (guided by persona) | No — gitignored |
| **Memory** | `.claude/memory/` | Persona (automatic) | No — gitignored |

Personality defines the role, rules, and communication style. Context holds your personal data. Memory accumulates session-by-session learnings. They never mix.

### Self-Improvement

Personas ship with a `self-improve` skill and hooks that drive automatic evolution:

1. **Memory** — Stop and PreCompact hooks remind the persona to write learnings after every session
2. **Rule promotion** — after a pattern appears 3+ times in memory, the persona proposes a permanent rule in CLAUDE.md
3. **Skill creation** — after an ad-hoc workflow repeats 3+ times, the persona drafts a reusable skill
4. **Tool & integration discovery** — researches existing MCP servers, CLI tools, and expansion packs before building custom solutions

Every level above memory requires your approval before changes are committed. You stay in control; the persona does the legwork.

### Sandboxing

Each persona runs in a native OS sandbox (bubblewrap on Linux, Seatbelt on macOS) configured in `.claude/settings.json`:

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

Personas can only write to their own directory, can't read parent directories or other personas' files, and can only reach whitelisted network domains. Each persona customizes `allowedDomains` for its own MCP servers.

### Shell Aliases

The alias system auto-discovers personas in `~/.personas/` and creates callable functions:

```bash
warren              # cd into ~/.personas/warren/, launch Claude Code
warren "do weekly"  # one-shot with sandboxed permissions
```

Under the hood: `cd ~/.personas/{name}/ && claude --setting-sources project --dangerously-skip-permissions`. The `--setting-sources project` flag loads only the persona's config (ignoring global settings), and `--dangerously-skip-permissions` is safe because the sandbox restricts everything.

## What's Included

This repo ships **persona-manager** — the meta-tool that scaffolds and manages personas.

| Skill | What it does |
|-------|-------------|
| **persona-dev** | Scaffolds a new persona with CLAUDE.md, profile template, sandbox config, hooks, self-improve skill, gitignore, and optional GitHub repo. Also handles persona updates and evolution. |
| **persona-dashboard** | Expansion pack — adds an HTML dashboard with task tracking, profile viewer, memory browser, and system overview. Single-file app served locally on ports 7300-7399. |

Every scaffolded persona includes:
- `CLAUDE.md` with personality template (role, rules, session start, skills table)
- `profile.md.example` for guided user setup (Guide or Interview pattern)
- `hooks.json` with Stop + PreCompact hooks for memory automation
- `self-improve` skill for the evolution engine
- `.claude/settings.json` with sandbox config
- `.gitignore` protecting secrets (profile.md, .mcp.json, memory, local overrides)

<details>
<summary>Persona Directory Structure</summary>

```
~/.personas/{name}/                  # Each persona is its own git-tracked directory
├── .claude/
│   ├── settings.json                # Sandbox config (committed)
│   └── memory/                      # Auto-memory (gitignored)
├── CLAUDE.md                        # Personality + rules (committed)
├── profile.md.example               # Context template (committed)
├── profile.md                       # Your personal data (gitignored)
├── .mcp.json                        # MCP servers + API keys (gitignored)
├── hooks.json                       # Stop + PreCompact hooks (committed)
├── .gitignore                       # Secret protection (committed)
├── skills/
│   ├── {domain}/SKILL.md            # Domain-specific skills
│   └── self-improve/SKILL.md        # Evolution engine
├── docs/                            # Reference docs (persona-writable)
└── scripts/                         # Tools + utilities (persona-writable)
```

</details>

<details>
<summary>Framework Repo Structure</summary>

```
personas/                            # This repo
├── plugins/
│   └── persona-manager/             # Meta-tool
│       ├── skills/
│       │   ├── persona-dev/         # Scaffolding + evolution skill
│       │   │   └── references/      # Templates copied to every persona
│       │   └── persona-dashboard/   # Dashboard expansion pack
│       │       └── assets/          # HTML dashboard template
│       └── skill-rules.json         # Activation triggers
├── docs/
│   └── plans/                       # Historical design documents
└── tests/
    └── personas-test.sh             # Structure + secret validation
```

</details>

## Documentation

All documentation lives in the persona-manager skill system — install the plugin and the skills guide you through everything:

| Skill | What it covers |
|-------|---------------|
| `persona-dev` | Creating, updating, and evolving personas — discovery, scaffolding, shell setup, testing, troubleshooting |
| `persona-dashboard` | Expansion pack — adds HTML dashboard with task tracking and status overview |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kickinrad/personas&type=Date)](https://star-history.com/#kickinrad/personas&Date)

## License

[Apache-2.0](LICENSE)
