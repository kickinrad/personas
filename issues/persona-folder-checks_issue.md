---
slug: persona-folder-checks
status: idea
---

# Persona folder checks

## Outcome

One check covers every persona folder, replacing 20 per-repo stack adoptions. Persona folders are not stack projects: kickinrad/stacks has no base-only choice, and prose folders give `/stack check` and `mise run check test` nothing to run.

## Approach

- `doctor.py` stays the persona folder contract. Run it against `~/.personas` from the plugin's checks, not only `examples/`.
- Tools stay plain scripts in `tools/`. Where a persona has tests, the doctor runs them (today: julia `tools/recipe-import` and `tools/meal-spinner`).
- A tool that outgrows a script (its own package, deploys, CI) moves to `~/projects/<area>/<name>` and adopts the `python` or `bun-lib` stack there, as Otto's dashboards did with Porchlight.
- This repo adopts no stack; its CI already runs its tests and the doctor.

## Acceptance

- `python3 skills/persona-dev/scripts/doctor.py --root ~/.personas` exits 0.
- julia's tool tests run through that check and pass.
- No persona repo has an `issues/stack-adoption_issue.md` or `issues/adopt-base-stack_issue.md`.

## Run

- 2026-11-02: Replaces the 20 per-persona stack issues filed from the Stacks Plan's Phase 3 and this repo's generic stack-adoption issue. The persona copies were removed the same day.

## Related

- [Stacks Plan](https://github.com/kickinrad/workflows/blob/main/plans/stacks_plan.md)
