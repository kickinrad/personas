<p align="center">
  <img src="assets/banner.svg" alt="Personas" width="650">
</p>

# Personas

Your AI chef shouldn't need your code-review rules.

Personas helps you create AI collaborators with their own personality, skills,
settings, and context. Each one lives in a folder you can open in **Claude Code
or Codex**. A chef for dinner, a gardener for your plants, a thoughtful reviewer
for your code. Give each a job, make it your own, and pick up where you left off.

[![CI](https://github.com/kickinrad/personas-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/kickinrad/personas-framework/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## Meet Julia

It's dinner time. You're tired. There's food in the fridge, but somehow no dinner.

```text
Julia, I have chickpeas, spinach, rice, and half a lemon. Dinner for two,
about 20 minutes, and I'd really rather not go shopping. What can we make?
```

Julia is a warm, practical personal chef. Her meal-planning skill starts with
what you have and how much effort you want to spend. She helps you choose a
meal, work through the cooking, and plan around leftovers. No recipe app or
grocery connection needed to get started.

[Try the Julia example](examples/julia/README.md), then change her to suit your
kitchen. The example is ordinary, editable text—not a service you have to run.

## Why a persona?

- **Stop starting from scratch.** Keep the role, your preferences, and useful
  lessons in files the agent can read next time.
- **Give each collaborator its own space.** Keep cooking skills with your chef
  and review rules with your reviewer, instead of putting everything in your
  global setup.
- **Make it yours.** Choose the voice, boundaries, workflows, and optional tool
  connections. Read and edit the whole definition yourself.
- **Take it with you.** Use the same role definition in Claude Code and Codex;
  keep personal context local while sharing the reusable parts.

A persona is self-contained as a role, not as a sandbox or a separate AI model.
Your runtime still controls permissions and may load global instructions and
tools. See [settings and tools](docs/usage.md#settings-and-tools).

## Install

In Claude Code:

```text
/plugin marketplace add kickinrad/personas-framework
/plugin install personas@personas
```

For Codex:

```bash
codex plugin marketplace add kickinrad/personas-framework
codex plugin add personas --marketplace personas
```

## Create your first persona

Ask your agent:

```text
Use personas:persona-dev to create a personal chef named Julia.
I want help with easy weeknight dinners and using what I already have.
```

The skill helps you shape the role and shows you a folder plan before creating
it. Open the new folder in Claude Code or Codex and start talking.

```text
julia/
├── AGENTS.md              # who Julia is and how she helps
├── CLAUDE.md              # points Claude Code to the same definition
├── skills/                # how she handles recurring tasks
├── .claude/settings.json  # Claude project settings
├── .codex/config.toml     # Codex project settings
└── user/                  # optional, ignored profile and memory
```

Use `personas:persona-dev` when you want to change or extend a persona.
Use `personas:self-improve` to turn recurring feedback into a proposed change
you can review. Neither requires you to use a particular model.

## Learn more

You can share a persona without sharing your life. Keep personal context,
local connections, and credentials out of Git. A fresh clone gets the role,
not your ignored private files.

- [Usage, memory, and native adapters](docs/usage.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Migrating an existing persona](docs/migration.md)
- [Contributing and testing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

If you only need a few shared instructions, an `AGENTS.md` or `CLAUDE.md` is
plenty. Use Personas when you want a collaborator with a role of its own.
