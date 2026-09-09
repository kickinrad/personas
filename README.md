<p align="center">
  <img src="assets/banner.svg" alt="Personas" width="650">
</p>

# Personas

A persona is a folder that gives an AI collaborator a durable role.
Create one for **Claude Code or Codex**, with its own voice, boundaries,
workflows, and optional private context.

[![CI](https://github.com/kickinrad/personas-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/kickinrad/personas-framework/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

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
Use personas:persona-dev to create a software-review persona named Atlas.
```

The skill helps define the role and shows a folder plan for approval.
Once created, open the folder in Claude Code or Codex and ask Atlas to review
a small change. See the [complete Atlas example](examples/atlas/README.md).

```text
atlas/
├── AGENTS.md              # identity, voice, role, and boundaries
├── CLAUDE.md              # imports AGENTS.md for Claude Code
├── skills/                # reusable role workflows
├── .claude/settings.json  # Claude project settings
├── .codex/config.toml     # Codex project settings
└── user/                  # optional, ignored profile and memory
```

Use `personas:persona-dev` to evolve the folder or activate native agents.
Use `personas:self-improve` to turn repeated feedback into a focused improvement.
Your model choice stays with your runtime or explicit persona settings.

## Learn more

Keep personal context, local connections, and credentials out of Git. A fresh
clone, including a Claude Code Cloud checkout, uses the portable definition
without ignored local context.

- [Usage, memory, and native adapters](docs/usage.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Migrating an existing persona](docs/migration.md)
- [Contributing and testing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

For a few shared instructions, an `AGENTS.md` or `CLAUDE.md` is enough.
Personas helps when a collaborator needs a distinct role that carries across
sessions and runtimes.
