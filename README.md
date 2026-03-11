<p align="center">
  <img src="assets/banner.svg" alt="personas" width="600">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/kickinrad/personas?style=flat" alt="License"></a>
</p>

Self-evolving AI assistants built on Claude Code plugins.

<!-- YOUR INTRO — write 1-2 sentences in your own voice -->

Each persona is a standalone Claude Code plugin with its own personality, skills, memory, and sandbox. Type its name and you have a dedicated AI assistant that remembers your context and gets better over time — no Docker, no infrastructure, no configuration servers.

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
# Scaffolds to ~/.personas/warren/ (optionally creates a GitHub repo)

# 3. Set up shell aliases (add to .zshrc or .bashrc)
source ~/.config/zsh/.personas.zsh
# Or add: for d in ~/.personas/*/; do alias "$(basename $d)"="cd $d && claude"; done

# 4. Configure your profile
cp ~/.personas/warren/profile.md.example ~/.personas/warren/profile.md
# Edit profile.md with your details

# 5. Use it
warren              # interactive session
warren "weekly review"  # one-shot prompt
```

## Features

- **Native Claude Code plugins** — no external runtime, just plugins and shell aliases
- **Three-layer model** — personality (CLAUDE.md), context (profile.md), and memory (.claude/memory/) stay cleanly separated
- **Self-improvement** — personas promote learnings from memory to rules to skills automatically
- **OS-level sandboxing** — each persona is filesystem and network isolated via bubblewrap/Seatbelt
- **Independent repos** — each persona lives in `~/.personas/{name}/` with its own git history
- **Any persona you need** — a CFO, a chef, a brand strategist, a fitness coach, a writing editor

## How It Works

Every persona is three layers stacked together:

| Layer | File | Purpose |
|-------|------|---------|
| **Personality** | `CLAUDE.md` | Role, rules, communication style — committed to git |
| **Context** | `profile.md` | Your personal data — gitignored, never shared |
| **Memory** | `.claude/memory/` | Auto-written learnings across sessions — gitignored |

Personas run in native OS sandboxes (bubblewrap on Linux, Seatbelt on macOS). Each one is restricted to its own directory and whitelisted network domains. No Docker required.

The real magic is **self-improvement**: personas observe patterns across sessions and propose new skills, rules, and tools. A chef that learns your family's preferences. A CFO that spots your spending blind spots. They get better because they're designed to.

<details>
<summary>Project Structure</summary>

```
personas/                          # This framework repo
├── plugins/
│   └── persona-manager/           # Meta-tool for scaffolding
├── tests/
└── docs/

~/.personas/                       # Your personas (independent repos)
├── warren/                        # Each persona is its own git repo
│   ├── .claude-plugin/plugin.json
│   ├── CLAUDE.md                  # Personality (committed)
│   ├── profile.md.example         # Profile template (committed)
│   ├── profile.md                 # Your data (gitignored)
│   ├── .mcp.json                  # API keys (gitignored)
│   ├── .claude/settings.json      # Sandbox config (committed)
│   ├── skills/                    # Domain skills
│   ├── docs/                      # Reference documents
│   └── scripts/                   # Tools and utilities
├── julia/
└── mila/
```

</details>

<details>
<summary>Self-Improvement Levels</summary>

1. **Memory** — automatic session learnings written to `.claude/memory/`
2. **Rule promotion** — proven patterns proposed for CLAUDE.md
3. **Skill creation** — repeated workflows proposed as new skills
4. **Tool creation** — scripts and utilities proposed for `scripts/`

Each level requires human approval before changes are committed.

</details>

## Create Your Own

```bash
# Use the persona-manager skill
persona-manager "create a fitness coach persona"
# Creates ~/.personas/fitness-coach/ with full plugin structure
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kickinrad/personas&type=Date)](https://star-history.com/#kickinrad/personas&Date)

## License

[Apache-2.0](LICENSE)
