# Task 2 — Retire non-core modules

Date: 2026-07-28

## Retirement inventory

- Removed the 10 tracked `plugins/persona-dashboard/**` files, including its
  generated Codex projection.
- Removed the 51 tracked `plugins/personas-mesh/**` files, including its
  generated Codex projection, launchers, hooks, unit templates, and skills.
- Removed the obsolete core Mesh plan
  `.claude/plans/personas-mesh-sync.md`; it described retired product source
  and live topology rather than a supported core path.
- Reduced both marketplace manifests to `persona-manager`.
- Regenerated the remaining Persona Manager Codex projection so new personas do
  not enable the retired Mesh plugin.

## Recovery retained before removal

- Original repository ref: `forge/personas-mesh-extraction`
- Ref commit: `e1f504222883b0fb5823f6cbec2b2305336dbdd4`
- Sibling repository: `~/projects/markets/personas-mesh`
- Task 1 established 51-file byte and digest parity between the original Mesh
  source and the sibling source, excluding the sibling ownership shell.
- The sibling has no configured remote. No launcher, systemd unit, cache,
  persona home, installation, activation, commit, push, or tag was changed.

## Validation

Executed on 2026-07-28:

```text
HOME=<fresh temporary directory> bash tests/run-tests.sh
python3 interop/generate.py --check
jq . .claude-plugin/marketplace.json
jq . .agents/plugins/marketplace.json
git diff --check
HOME=<fresh temporary directory> bash ~/projects/markets/personas-mesh/tests/run-tests.sh
```

Results: core gate passed (8 shell checks; 7 Python contract tests), remaining
Codex projection matched generation, both manifests parsed, diff check passed,
and the read-only Mesh sibling gate passed (3 contract tests).

`tests/framework-contract-test.py` now scans active Markdown, JSON, Python,
shell, TOML, and YAML source for retired Dashboard or Mesh paths and plugin IDs.
It intentionally excludes the assertion itself plus historical migration,
changelog, evidence, and plan records.
