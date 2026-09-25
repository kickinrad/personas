---
name: persona-dev
description: Use when the user asks to create, evolve, reconcile, or activate a persona folder, or connect an approved capability to it.
---

# Develop a persona

A persona is a readable folder. Keep its portable definition, runtime adapters,
private local context, and external knowledge sources distinct.

## Create

1. Interview the user with `references/interview.md`: one question at a time,
   each with a recommended answer, until the job, boundaries, context,
   workflows, runtimes, color, and launch are clear;
   integrated use is the default for both runtimes.
2. Once the role is clear, research capabilities with
   `references/research-toolkit.md` and recommend a small starting set.
3. Design a distinctive character with the interview reference, and check
   its sample lines with the user.
4. Read the templates in `assets/`, and `references/environments.md` when
   choosing a home or launch mode.
5. Present a folder plan covering `AGENTS.md`, importing `CLAUDE.md`, skills,
   settings, ignored context, approved capabilities, and launch choice. Write
   nothing before approval.
6. After approval, create the folder directly with normal file operations:
   - `AGENTS.md` owns identity, voice, role, boundaries, and shared doctrine;
   - `CLAUDE.md` imports `AGENTS.md` for Claude Code;
   - `.claude/settings.json` and `.codex/config.toml` contain minimal native
     project settings;
   - `skills/` contains portable role workflows;
   - `user/` contains optional ignored profile and explicit memory.
7. Replace every placeholder with reviewed persona-specific content. Create
   no hook merely for symmetry, reminders, framework drift, repository
   visibility, or memory simulation.
8. Keep everything tracked in Git safe to publish. Never put profile, memory,
   local settings, connections, or credentials in tracked files.
9. Inspect the resulting tree and exact diff. Confirm `AGENTS.md` is the only
   always-loaded persona authority and `CLAUDE.md` imports it.
10. Ask separately before plugin installation, repository creation, external
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

Read the finished folder as a user would: understandable, free of duplicated
doctrine, private state ignored, and equivalent Claude and Codex entry paths.
For each approved capability, run the `references/research-toolkit.md` Verify
controls. Run the framework test suite when changing the framework itself.
