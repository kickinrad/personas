<p align="center">
  <img src="assets/banner.svg" alt="Personas" width="650">
</p>

# Personas

Build purpose-made AI workspaces for **Claude Code and Codex**.

Instead of squeezing every rule, tool, and workflow into one global setup,
give each job its own folder. A persona can have its own instructions, skills,
settings, private context, and connected tools. It uses the native features of
Claude Code or Codex and the account you already use with that runtime—there's
no separate AI service hiding underneath it.

[![CI](https://github.com/kickinrad/personas/actions/workflows/ci.yml/badge.svg)](https://github.com/kickinrad/personas/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## What could you build?

### Julia — a personal chef

> “Plan three easy dinners from what we already have, add anything missing to
> the grocery list, and put the plan on our calendar.”

Julia can combine a meal-planning skill with your private food preferences and
the tools you choose to connect: a recipe library, pantry, grocery list, or
calendar. She can turn scattered information into one useful plan, show it to
you, and wait for approval before changing anything. The
[Julia example](examples/julia/README.md) works without any connections, so you
can try the basic machinery first and add tools later.

### Jesse — a market researcher

> “Revisit our original thesis, check it against current evidence, and tell me
> plainly what got stronger, what broke, and what we still don't know.”

Jesse's workspace can hold the research process, decision rules, and private
thesis context for that job. Connect market data or research tools and he can
use fresh information without turning your global assistant into a trading
terminal. The result is a focused research workflow with clear limits—not a
promise of returns and not permission to place trades.

### Atlas — a code reviewer

> “Review this branch using our standards. Run the focused checks, separate
> real blockers from nits, and give me the smallest safe path forward.”

Atlas can carry your review checklist as a reusable skill, load the project's
standards, and use native development tools such as Git, tests, and linters.
Those rules stay with the reviewer instead of leaking into Julia's kitchen—or
every other Claude Code and Codex session you start.

## The machinery

| Persona | Skills | Private context | Optional tools |
|---|---|---|---|
| Julia | Meal planning, groceries | Food preferences and household routines | Recipes, pantry, shopping list, calendar |
| Jesse | Thesis research, portfolio review | Research notes and decision context | Market data and research sources |
| Atlas | Code review, architecture checks | Project conventions | Git, tests, linters, repository tools |

Underneath, each persona is a small, readable folder:

```text
julia/
├── AGENTS.md              # role and rules
├── CLAUDE.md              # Claude Code entry point
├── skills/                # repeatable workflows
├── user/                  # private profile and memory
├── .mcp.json              # optional tool connections
├── .claude/settings.json  # Claude Code settings
└── .codex/config.toml     # Codex settings
```

Share the useful parts without sharing your life: `user/`, local settings,
tool credentials, and connections stay out of Git by default. Personas work
alongside your usual setup; during creation you can instead choose focused use
with fewer user-level customizations.

## Install

In Claude Code:

```text
/plugin marketplace add kickinrad/personas
/plugin install personas@personas
```

For Codex:

```bash
codex plugin marketplace add kickinrad/personas
codex plugin add personas --marketplace personas
```

## Create your first persona

Ask your agent:

```text
Use personas:persona-dev to create a personal chef named Julia.
I want help with easy weeknight dinners and using what I already have.
```

It helps you choose the instructions, skills, settings, context, and tools the
job needs, then walks you through the folder plan before creating anything.
Open the new folder in Claude Code or Codex and start working.

Want to change something later? Ask `personas:persona-dev`. Keep giving the
same feedback? Ask `personas:self-improve` to suggest an improvement you can review.

[Make it your own](docs/usage.md) · [Need a hand?](docs/troubleshooting.md) ·
[Updating an older persona](docs/migration.md) · [Contributing](CONTRIBUTING.md)
