---
name: persona-dev
description: Use when the user asks to create, evolve, reconcile, or activate a persona folder, or connect an approved capability to it.
---

# Develop a persona

A persona is a readable folder. Keep its portable definition, runtime adapters,
private local context, and external knowledge sources distinct.

## Create

1. Discover the name, role, outcomes, voice, boundaries, workflows, context,
   and runtimes. Ask for a Claude agent color (red, blue, green, yellow,
   purple, orange, pink, or cyan) and whether Claude Code should use focused
   launch; integrated use is the default for both runtimes and keeps user
   configuration.
2. Read the templates in `assets/`. Read `references/environments.md` when
   choosing a home or launch mode. Read
   `references/research-toolkit.md` when the persona needs a new capability.
3. Present a folder plan covering `AGENTS.md`, importing `CLAUDE.md`, skills,
   settings, ignored context, integrations, and launch choice. Write nothing
   before approval.
4. After approval, create the folder directly with normal file operations:
   - `AGENTS.md` owns identity, voice, role, boundaries, and shared doctrine;
   - `CLAUDE.md` imports `AGENTS.md` for Claude Code;
   - `.claude/settings.json` and `.codex/config.toml` contain minimal native
     project settings;
   - `skills/` contains portable role workflows;
   - `user/` contains optional ignored profile and explicit memory.
5. Replace every placeholder with reviewed persona-specific content.
6. Create no hook merely for symmetry, reminders, framework drift, repository
   visibility, or memory simulation.
7. Keep everything tracked in Git safe to publish. Never put profile, memory,
   local settings, connections, or credentials in tracked files.
8. Inspect the resulting tree and exact diff. Confirm `AGENTS.md` is the only
   resident persona authority and `CLAUDE.md` imports it.
9. Ask separately before plugin installation, repository creation, external
   connection, publishing, or changes to an existing persona's private data.

## Evolve or reconcile

For an existing persona, inspect its folder first and edit only the owning
surface; `self-improve`'s "Route the change" list owns content routing. Prefer
an existing capability over a new wrapper.

Compare existing folders with the current portable contract, classify each
difference as adapter drift, persona-owned customization, obsolete machinery,
or ambiguity, and show the reconciliation plan before writing. Preserve
persona-owned meaning and optional ignored `user/` context.

## Activate native adapters

Run `scripts/persona-native-sync.py --persona PATH --runtime claude|codex|all
[--color COLOR]` to report drift for the persona's native subagents. Add
`--apply` only after explicit approval. Each agent reads the live `AGENTS.md`
and resolves relative paths from the folder; omitting `--color` keeps the
existing color. Only servers named in the ignored `.mcp.json`
`agentMcpServers` list are projected; agree that list with the user. When the
helper refuses an unowned or older file, move it aside only with approval. The
helper never changes global runtime permissions.

## Verify

Read the finished folder as a user would. Check that it is understandable,
contains no duplicated doctrine, keeps private state ignored, and provides
equivalent Claude and Codex entry paths. For each approved capability, execute
the `research-toolkit.md` controls: installed plugin, settings/MCP alignment,
private bindings, resolver success, fresh-session discovery, and isolation.
Run the framework test suite when changing the framework itself.
