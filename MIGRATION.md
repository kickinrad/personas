# Migration to Personas 6.0.0

Version 6.0.0 keeps `AGENTS.md` as the portable persona definition and folds
creation, evolution, reconciliation, and native activation into `persona-dev`.

## Target folder

```text
AGENTS.md
CLAUDE.md
skills/
.claude/settings.json
.codex/config.toml
user/                       # optional and ignored
```

Use `personas:persona-dev` to inspect an existing folder and propose
the migration before writing.

## Move portable meaning once

Move shared identity, voice, role, and boundaries into `AGENTS.md`. Reduce
`CLAUDE.md` to an `@AGENTS.md` import. Keep reusable role procedure in
`skills/`. Claude Code and Codex then consume the same portable persona through
their native entry files.

Do not bulk-replace persona-owned content. Preserve `user/profile.md`,
`user/memory/`, local settings, and integrations.

## Optional native agents

For an on-demand global Claude or Codex agent, run the bundled sync helper
without `--apply` first. It derives its name and description from `AGENTS.md`,
keeps adapters marked and collision-safe, and reads the live absolute source
instead of copying identity text. If `.mcp.json` exists, it translates only
stdio and streamable HTTP servers; unsupported transports, fields, and literal
credentials stop the run.

## Remove transitional machinery

After reviewing the exact paths, remove obsolete framework stamps, the public
`bin/personas` CLI, Cloud repository markers, visibility adapters, generated
privacy workflows, publishing guards, and default persona hooks. They are not
part of the current folder contract.

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
