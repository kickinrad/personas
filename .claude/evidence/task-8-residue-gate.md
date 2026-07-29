# Task 8 — Residue and release-gate consolidation

Date: 2026-07-28

## Inventory decision

The tracked evaluation systems (`tests/evals/eval-a`, `tests/evals/eval-b`)
and scenario prose (`tests/scenarios`) had no current caller. Their assertions
depended on retired nested plugin paths, an installed Claude CLI, and mutable
live-style `~/.personas` state. Their durable behavior is now covered by the
deterministic creation, verification, privacy, runtime-adapter, documentation,
and framework contract tests, so the stale evaluator, scenario, and ignored run
outputs were removed rather than presented as an executable product promise.

Removed stale maintainer/session residue:

- `.claude/handoffs/archive/20260427T161546Z.md`
- `personas.md`
- `skill-rules.json` (test-only routing prose with no runtime caller)
- unused raster logo and social-preview assets

Retained:

- `assets/banner.svg`, called by README
- `.claude/plans/personas-core-renewal.md`
- Task evidence and all recovery/history references

Skill discovery is now evidenced by the canonical `skills/*/SKILL.md`
frontmatter and the two manifests that expose that one skills tree. No removed
routing table was a runtime input.

## One verdict

`bash tests/run-tests.sh` is the only CI verdict. It runs shell checks,
framework contracts, verification, privacy, runtime adapters, deterministic
creation, documentation, JSON parse checks, stale-path/inventory policy, and
secret hygiene. It also runs `bash -n` across shipped/test shell scripts and,
when Git metadata exists, both staged and unstaged `git diff --check` hygiene
checks. `.github/workflows/ci.yml` has one job that invokes that same command.

## Export validation

The worktree is intentionally uncommitted. Validation used:

```bash
export_root=$(mktemp -d)
tar --exclude=.git --exclude=.pytest_cache --exclude=__pycache__ -cf - . |
  tar -xf - -C "$export_root"
HOME=$(mktemp -d) bash "$export_root/tests/run-tests.sh"
```

This tests the exact current source tree, including uncommitted and ignored
source records, from a fresh temporary HOME without live `~/.personas`. It is
not a commit/archive proof: no Git metadata, commit, tag, or remote state is
included.

Executed successfully: current-tree central gate; exported-tree central gate;
Python YAML parse of CI; `git diff --check`; and `git diff --cached --check`.
No network, installation, live persona mutation, commit, push, or tag was
performed.
