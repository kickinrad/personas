<p align="center">
  <img src="assets/banner.svg" alt="Personas" width="650">
</p>

<h1 align="center">Personas</h1>

<p align="center">
  A persona is a folder that teaches an AI collaborator how to work with you.
</p>

<p align="center">
  <a href="https://github.com/kickinrad/personas-framework/actions/workflows/ci.yml"><img src="https://github.com/kickinrad/personas-framework/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="Apache 2.0 license"></a>
</p>

Re-explaining your role, preferences, and working style in every AI session gets
old. Personas helps you create one durable collaborator as readable
Markdown, shared skills, and small native adapters for **Claude Code local**,
**Claude Code Cloud**, and **Codex**.

```text
atlas/
├── PERSONA.md                 # identity, role, voice, and boundaries
├── CLAUDE.md                  # Claude Code entry point
├── AGENTS.md                  # Codex entry point
├── skills/                    # reusable role workflows
├── .claude/settings.json      # native Claude project settings
├── .codex/config.toml         # native Codex project settings
└── user/                      # optional, ignored local context
    ├── profile.md
    └── memory/MEMORY.md
```

That folder is the product. There is no persona daemon, database, account, or
required management CLI.

## Install

### Claude Code

```text
/plugin marketplace add kickinrad/personas-framework
/plugin install personas@personas
```

### Codex

```bash
codex plugin marketplace add kickinrad/personas-framework
codex plugin add personas --marketplace personas
```

## Create your first persona

Ask the installed plugin:

```text
Use personas:persona-dev to create a software-review persona named
Atlas. Show me the complete folder plan before writing anything.
```

Personas helps define the role, voice, boundaries, and useful workflows;
shows the proposed folder; and waits for approval before writing it. Start with
the [sanitized Atlas example](examples/atlas-sanitized/README.md) if you want to
inspect a finished folder first.

## How the folder works

`PERSONA.md` is the portable source of truth. It contains the collaborator's
identity and behavior without referring to a particular AI runtime.

Claude Code discovers `CLAUDE.md`. Codex discovers `AGENTS.md`. Each native
entry point loads the same `PERSONA.md`, optional local user context, and
relevant workflows under `skills/`.

The `.claude/` and `.codex/` directories contain only native project settings.
They are adapters, not competing persona definitions. Personas adds no
default lifecycle hooks; instructions and skills should carry the behavior
unless a future feature demonstrates that mechanical enforcement is necessary.

## Memory

`user/memory/MEMORY.md` is explicit persona memory: ordinary ignored Markdown
that both Claude Code and Codex can read when it exists locally. You control
what goes into it.

Native auto-memory is separate:

- Claude may maintain runtime-owned memory through its own settings.
- Codex can maintain experimental local memories under `$CODEX_HOME/memories`.

Those native stores do not synchronize, and persona identity never depends on
them. A fresh Cloud checkout normally has no ignored `user/` directory and
still works from its publishable persona definition.

## Claude Code Cloud

Cloud uses the same persona folder—there is no special Cloud profile. Commit
only the publishable definition and open its repository in Claude Code Cloud.

Use a private repository for a personalized Cloud persona. Personas
trusts you to choose and maintain that visibility; it does not require a
GitHub token, marker file, visibility preflight, generated CI workflow, or
startup guard. More importantly, keep `user/`, local settings, connections, and
credentials out of Git regardless of repository visibility.

## Core workflows

| Goal | Skill |
|---|---|
| Create or extend a persona | `personas:persona-dev` |
| Reconcile an existing folder | `personas:persona-update` |
| Improve identity or procedure from real evidence | `personas:self-improve` |

Each workflow plans first, preserves persona-owned content, and keeps one source
for each piece of meaning.

## Why not just use `CLAUDE.md` or `AGENTS.md`?

For a few instructions, you should. Personas becomes useful when the
collaborator has a distinct role, reusable workflows, private local context, or
needs to work in both Claude Code and Codex.

It adds a neutral persona definition, shared skills, native runtime entry
points, and a careful update workflow while keeping every file readable.

## Runtime support

| Runtime | Status | Adapter |
|---|---|---|
| Claude Code local | Supported | `CLAUDE.md` and `.claude/settings.json` |
| Claude Code Cloud | Supported folder model | Same publishable Claude folder; ignored local context is absent |
| Codex | Supported | `AGENTS.md`, `.codex/config.toml`, and shared plugin skills |
| Gemini CLI / Kimi Code | Unsupported | No native adapter has been proven |

Claude Code and Codex passed the same clean identity, voice, boundary, skill,
profile, and explicit-memory canary. Parity is a release gate, not an
aspiration.

## Project documentation

- [Sanitized Atlas example](examples/atlas-sanitized/README.md)
- [Support and memory boundaries](SUPPORT.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Migration notes](MIGRATION.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Apache 2.0 license](LICENSE)

For framework development:

```bash
bash tests/run-tests.sh
```

The suite uses temporary fixtures and never modifies `~/.personas`.
