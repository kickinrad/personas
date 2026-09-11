# Runtime acceptance evidence

## 0.6.0 focused-launch check — 2026-09-11

Codex CLI 0.154.0 rejected `--ignore-user-config` as an unexpected argument.
Focused launch is therefore documented only for Claude Code; Codex remains
integrated. This is a CLI capability check, not a fresh persona-session probe.

Disposable Claude Code 2.1.268 and Codex CLI 0.154.0 homes both installed
Personas 6.2.2, then accepted the same local marketplace at 0.6.0. Claude's
`plugin update` and Codex's `plugin add` each reported 0.6.0. These are
installation-state checks, not live persona sessions.

Claude Code 2.1.268 ran the public Julia example in print mode with
`--setting-sources project,local` and no session persistence. Codex CLI 0.154.0
ran the same example with its normal integrated configuration, `--ephemeral`,
and a read-only sandbox. Both identified Julia and her ask-before-ordering
boundary. Codex reported unrelated configured-MCP OAuth refresh errors, but no
MCP was used and the prompt completed. This probes instruction loading and the
focused/integrated launch boundary, not native-agent or MCP activation.

## 6.2.1 folder probe — 2026-09-09

A temporary copy of the Atlas example, with synthetic ignored context, was
tested in Claude Code 2.1.266 (`claude-sonnet-5`, medium) and Codex CLI 0.153.4
(`gpt-5.6-sol`, medium). The Claude settings had no model override.

Claude ran in print/plan mode with Read, Glob, and Grep tools, project/local
settings, and no session persistence. Codex ran ephemeral and read-only. Both
were asked to return identity, voice,
boundaries, local role skill, preferred name, and the explicit-memory phrase.

Both returned Atlas, its evidence-led voice and permission boundaries,
`atlas-review`, the synthetic name `River`, and `cobalt compass`. Claude
reported no permission denials. This exercises native instruction loading,
role-skill reading, and optional local context without changing a live persona.

The offline gate separately checks folder structure, private-file exclusion,
adapter generation, collision handling, and source exports. These checks do
not establish live runtime behavior by themselves.

Codex CLI 0.153.4 also loaded a generated profile through `--profile` and
`mcp list --json`, preserving the literal MCP name `weather.tool` and
environment key `PLAIN.KEY`. This check inspected configuration without
starting an MCP server.

## Earlier evidence and limits

The 2026-08-17 v5 probe exercised both native entry paths, profile, memory, and
role-skill reading. Earlier v3 CLI evidence was recorded on 2026-07-31. Full
historical records remain in Git history before the 6.2.1 cleanup.

Claude Code Cloud was not rerun for 6.2.1. Earlier Cloud evidence covered an
older folder contract; current Cloud support describes the publishable folder
model. Neither these probes nor Personas synchronize runtime-native memory.
