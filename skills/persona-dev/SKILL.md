---
name: persona-dev
description: Develop and reconcile portable persona folders. Use when creating or evolving a persona, connecting an approved capability, or activating native adapters. Not for persona-local self-improvement (use self-improve).
---

# Develop a persona

A persona is a readable folder. Keep its portable definition, runtime adapters,
private local context, and external knowledge sources distinct.

## Create

1. Interview the user with `references/interview.md` until the outcome,
   craft, character, boundaries, workflows, runtimes, color, and launch are
   clear. Integrated use is the default.
2. Once the craft is clear, research capabilities with
   `references/research-toolkit.md` and recommend a small starting set.
3. Read the templates in `assets/`, and `references/environments.md` when
   choosing a home or launch mode.
4. Present a folder plan covering `AGENTS.md`, skills, settings, ignored
   context, approved capabilities, starter evals, and launch. Write nothing
   before approval.
5. After approval, create:
   - `AGENTS.md`: identity, role, craft, voice, and role-specific boundaries;
   - `PERSONAS.md`, the shared rules, written by the sync helper below;
   - minimal `.claude/settings.json` and `.codex/config.toml`;
   - `skills/` for portable role workflows;
   - `evals/` with two or three synthetic cases graded by the Craft's Proof;
   - ignored `user/` for profile, memory, and private evals.
6. Replace every placeholder with reviewed content. Add no hook for symmetry,
   reminders, drift, or memory simulation. Keep everything tracked safe to
   publish.
7. Inspect the tree and diff. No `CLAUDE.md` may exist in the folder or above
   it; it stops Claude Code from reading `AGENTS.md`.
8. Ask separately before plugin installation, repository creation, external
   connection, publishing, or changing an existing persona's private data.

## Evolve or reconcile

Inspect the folder first and edit only the owning surface; `self-improve`'s
"Route the change" list owns routing. Classify each difference from the
current contract as adapter drift, persona-owned customization, obsolete
machinery, or ambiguity, and show the plan before writing. Preserve
persona-owned meaning and `user/`.

## Activate native adapters

`scripts/persona-native-sync.py --persona PATH --runtime claude|codex|all
[--color COLOR]` reports drift for `PERSONAS.md` and the native subagents;
add `--apply` only after approval. Each agent reads the live folder. Only servers named in
tracked `.agent-mcp.json` are projected from ignored `.mcp.json`. Move a
refused file aside only with approval.

## Evaluate

The Craft's Proof is the outside judge; never grade the persona yourself.
Grade checkable facts with deterministic graders (`regex`, `tool_used`); keep
`llm` rubrics for judgment, where they are noisy.
Wrap it as a plugin whose main agent it is, then compare it with plain Claude:

```bash
plugin=$(python3 scripts/persona-native-sync.py --persona PATH --eval-plugin)
claude plugin eval "$plugin" --no-publish
```

Tracked `evals/` hold synthetic cases only. Cases from real conversations,
including `context.history_file` replays, go in ignored `user/evals/`; the
wrapper copies them to `evals/private/`. Mock the persona's allowlisted tools in
`evals/mocks/<server>/<tool>.md`; real servers never start. Run
evals before changing a persona; afterward it must match or beat the old
version on cases tagged `holdout`.

## Verify

Read the folder as a user would. Run `scripts/verify-fleet.py --root
PERSONAS_ROOT`, the Verify controls in `references/research-toolkit.md` for
each approved capability, and the framework tests when changing the framework.
