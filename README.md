# Personas

**Self-evolving AI assistants built on Claude Code plugins.**

Each persona is a standalone Claude Code plugin with its own personality, skills, memory, and sandbox. Use persona-manager to scaffold one, type its name, and you have a dedicated AI assistant that remembers your context and gets better over time — no Docker, no infrastructure, no configuration servers.

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
# Scaffolds to ~/.personas/warren/

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

See [Getting Started](docs/getting-started.md) for the full setup guide.

## What's Included

| Component | Role | What it does |
|-----------|------|--------------|
| **persona-manager** | Meta-tool | Scaffolds new personas to `~/.personas/`, manages deployment and publishing |

Persona-manager can create any persona you need — a personal chef, a CFO, a brand strategist, a fitness coach, a writing editor. Each one is scaffolded as an independent repo in `~/.personas/`.

## How It Works

Every persona is three layers stacked together:

| Layer | File | Purpose |
|-------|------|---------|
| **Personality** | `CLAUDE.md` | Role, rules, communication style — committed to git |
| **Context** | `profile.md` | Your personal data — gitignored, never shared |
| **Memory** | `.claude/memory/` | Auto-written learnings across sessions — gitignored |

Personas run in native OS sandboxes (bubblewrap on Linux, Seatbelt on macOS). Each one is restricted to its own directory and whitelisted network domains. No Docker required.

The real magic is **self-improvement**: personas observe patterns across sessions and propose new skills, rules, and tools. A chef that learns your family's preferences. A CFO that spots your spending blind spots. They get better because they're designed to.

## Create Your Own

```bash
# Use the persona-manager skill
persona-manager "create a fitness coach persona"
# Creates ~/.personas/fitness-coach/ with full plugin structure
```

Or scaffold manually — see [Creating Personas](docs/creating-personas.md) for the full guide.

## Documentation

| Guide | What you'll learn |
|-------|-------------------|
| [Getting Started](docs/getting-started.md) | Full setup, first session walkthrough |
| [Creating Personas](docs/creating-personas.md) | Build a custom persona from scratch |
| [Self-Improvement](docs/self-improvement.md) | How personas evolve over time |
| [Remote Deployment](docs/remote-deployment.md) | Run personas on servers with cron |

## Project Structure

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

## Contributing

Contributions welcome. This repo contains the persona-manager framework — individual personas live in their own repos.

To contribute:

1. Fork the repo
2. Improve persona-manager (scaffolding, deployment, publishing skills)
3. Open a PR with a description of your changes

Please follow the [Creating Personas](docs/creating-personas.md) guide for persona structure conventions.

## License

MIT
