# Migration to Personas 4.0.0

Version 3.0.0 returned to the original product model: a persona is a folder.
Version 4.0.0 keeps that contract and renames the plugin itself to `personas`.

## Target folder

```text
PERSONA.md
CLAUDE.md
AGENTS.md
skills/
.claude/settings.json
.codex/config.toml
user/                       # optional and ignored
```

Use `personas:persona-update` to inspect an existing folder and propose
the migration before writing.

## Move portable meaning once

Move shared identity, voice, role, and boundaries into `PERSONA.md`. Reduce
`CLAUDE.md` and `AGENTS.md` to native entry points that load it. Keep reusable
role procedure in `skills/`. Claude Code and Codex then consume the same
portable persona through their own native entry files.

Do not bulk-replace persona-owned content. Preserve `user/profile.md`,
`user/memory/`, local settings, and integrations.

## Remove transitional machinery

After reviewing the exact paths, remove obsolete framework stamps, the public
`bin/personas` CLI, Cloud repository markers, visibility adapters, generated
privacy workflows, publishing guards, and default persona hooks. They are not
part of the 3.0.0 folder contract.

Cloud uses the same publishable folder. A private repository is recommended for
personalized use, but visibility is user-managed and credentials remain
forbidden from Git.

## Repository history

Personas is the single root plugin. The former Dashboard is retired. The
former `persona-manager` plugin identifier and `plugins/persona-manager/`
source layout are no longer active.
Personas Mesh was preserved with history in a separate local project before its
core source was removed; Mesh review and publication remain separate work.

Use [ROLLBACK.md](ROLLBACK.md) for source rollback. Framework rollback never
authorizes mutation of live persona folders.
