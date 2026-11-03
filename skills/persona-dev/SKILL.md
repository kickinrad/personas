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
3. Read `references/writing.md` and the templates in `assets/`, and
   `references/environments.md` when choosing a home or launch mode.
4. Present a folder plan covering `AGENTS.md`, skills, settings, ignored
   context, approved capabilities, starter evals, and launch. Write nothing
   before approval.
5. After approval, create:
   - `AGENTS.md`: identity, role, craft, voice, and role-specific boundaries;
   - `PERSONAS.md`, the shared rules, written by the sync helper below;
   - minimal `.claude/settings.json` and `.codex/config.toml`;
   - `skills/` for portable role workflows;
   - `evals/` with one synthetic case graded by the Craft's Proof;
   - `user/` for profile, memory, and private evals, ignored by default.
6. Replace every placeholder with reviewed content. Add no hook for symmetry,
   reminders, drift, or memory simulation. Keep everything tracked safe to
   publish.
7. Inspect the tree and diff. No `CLAUDE.md` may exist in the folder or above
   it; it stops Claude Code from reading `AGENTS.md`.
8. Ask separately before plugin installation, repository creation, external
   connection, publishing, or changing an existing persona's private data.

## Evolve or reconcile

Inspect the folder first and edit only the owning surface, written per
`references/writing.md`; `self-improve`'s
"Route the change" list owns routing. Classify each difference from the
current contract as adapter drift, persona-owned customization, obsolete
machinery, or ambiguity, and show the plan before writing. Preserve
persona-owned meaning and `user/`; a re-included `user/` is persona-owned.

## Activate native adapters

`scripts/persona-native-sync.py --persona PATH --runtime claude|codex|all
[--color COLOR]` reports drift for `PERSONAS.md` and the native subagents;
add `--apply` only after approval. Each agent reads the live folder. Only servers named in
tracked `.agent-mcp.json` are projected from ignored `.mcp.json`. For Codex they
also set the `mcp_servers` tables of the tracked `.codex/config.toml`, minus
servers the global Codex config defines; hand-written Codex variants and
global overrides stay. Move a refused file aside only with approval.

## Evaluate

Evals are optional; run them when Wils asks or a change is risky. The Craft's
Proof is the outside judge; never grade the persona yourself. Prefer
deterministic graders (`regex`, `tool_used`) over noisy `llm` rubrics. Run
once, without a plain-Claude arm:

```bash
plugin=$(python3 scripts/persona-native-sync.py --persona PATH --eval-plugin)
claude plugin eval "$plugin" --no-publish --runs 1 --ablation none
```

Tracked `evals/` hold synthetic cases; mock allowlisted tools in
`evals/mocks/<server>/<tool>.md`. Replays of real conversations live in ignored
`user/evals/` and are costly; include them only on request with `--with-private`.

## Verify

Read the folder as a user would. Run `scripts/verify-fleet.py --root
PERSONAS_ROOT`, the Verify controls in `references/research-toolkit.md` for
each approved capability, and the framework tests when changing the framework.
