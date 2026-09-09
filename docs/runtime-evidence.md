# Runtime acceptance evidence

## Julia example — 2026-09-09

A disposable copy of the Julia example was tested without the Personas plugin,
private context, or external integrations in Claude Code 2.1.266
(`claude-sonnet-5`, medium) and Codex CLI 0.153.4 (`gpt-5.6-sol`, medium).
Claude used print/plan mode, Read/Glob/Grep tools, project/local settings,
strict MCP configuration, and no session persistence. Codex used an ephemeral
read-only session without user configuration.

Both read the local definition and `julia-meal-plan` skill, proposed a dinner
from supplied ingredients, labeled extra pantry staples as optional, and
stated that grocery orders or shared-list changes needed approval and an
available connection. Claude reported no permission denials. The tested folder
matched the source afterward. These are instruction-following smoke checks,
not proof of cooking accuracy or every runtime configuration; Cloud and live
integrations were not tested.

## 6.2.1 folder probe — 2026-09-09

A temporary copy of the Atlas example, with synthetic ignored context, was
tested in Claude Code 2.1.266 (`claude-sonnet-5`, medium) and Codex CLI 0.153.4
(`gpt-5.6-sol`, medium). The Claude settings had no model override.

Claude ran in print/plan mode with Read, Glob, and Grep tools, project/local
settings, and no session persistence. Codex ran ephemeral, read-only, and
without user configuration. Both were asked to return identity, voice,
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
