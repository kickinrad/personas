---
name: persona-dev
description: Use when the user asks to create or design a persona, extend an existing persona with a role workflow, or connect an approved capability to a persona folder. NOT for framework reconciliation; use persona-update.
---

# Develop a persona

A persona is a readable folder. Keep its portable definition, runtime adapters,
private local context, and external knowledge sources distinct.

## Create

1. Discover the desired name, role, outcomes, voice, boundaries, workflows,
   local context, and target runtimes. Ask only questions that materially
   change the folder.
2. Read the templates in `assets/`. Read `references/environments.md` when
   choosing a home across native, WSL, Windows, Desktop, or Cowork. Read
   `references/launch-flags.md` when configuring a Claude launcher. Read
   `references/research-toolkit.md` when the persona needs a new capability.
3. Present one complete folder plan. Include the portable `AGENTS.md`, importing
   `CLAUDE.md`, shared skills, minimal native settings, ignored local context,
   and any requested integration. Write nothing before approval.
4. After approval, create the folder directly with normal file operations:
   - `AGENTS.md` owns identity, voice, role, boundaries, and shared doctrine;
   - `CLAUDE.md` imports `AGENTS.md` for Claude Code;
   - `.claude/settings.json` and `.codex/config.toml` contain minimal native
     project settings;
   - `skills/` contains portable role workflows;
   - `user/` contains optional ignored profile and explicit memory.
5. Replace every template placeholder with reviewed persona-specific content.
   Do not leave generic role filler in a finished persona.
6. Create no hook merely for symmetry, reminders, framework drift, repository
   visibility, or memory simulation.
7. Keep everything tracked in Git safe to publish. Never put profile, memory,
   local settings, connections, or credentials in tracked files.
8. Inspect the resulting tree and exact diff. Confirm `AGENTS.md` is the only
   resident persona authority and `CLAUDE.md` imports it.
9. Ask separately before plugin installation, repository creation, external
   connection, publishing, or changes to an existing persona's private data.

## Extend

For an existing persona, inspect its folder first and edit only the owning
surface; `self-improve`'s "Route the change" list owns content routing. Prefer
an existing capability over a new wrapper. Read `references/lifecycle-meta.md`
when ownership between those surfaces is unclear.

## Verify

Read the finished folder as a user would. Check that it is understandable,
contains no duplicated doctrine, keeps private state ignored, and provides
equivalent Claude and Codex entry paths. Run the framework test suite only when
changing the framework itself.
