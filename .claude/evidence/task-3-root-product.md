# Task 3 — Persona Manager root product

Date: 2026-07-28

## Canonical layout

Persona Manager is now the repository-root release unit:

```text
.claude-plugin/plugin.json
.codex-plugin/plugin.json
skills/
hooks/
bin/
scripts/
interop/capabilities.json
skill-rules.json
```

Both marketplace manifests resolve `persona-manager` at `.`. Claude and Codex
share the same root `skills/` tree; no generated skill copy remains.

## History-preserving moves and removals

`git mv` moved the nested manifest, skill tree, hooks, validator, public-repo
guard, capability declaration, and rule declaration into the root layout.
The nested `plugins/persona-manager/**` tree and the empty `plugins/` directory
were removed. The obsolete `interop/generate.py` and all `.generated/**` output
were removed rather than replaced: the sole retained Codex-specific artifact is
the small root `.codex-plugin/plugin.json` metadata manifest.

There are no forwarding manifests or scripts. The core test asserts that the
nested source, generator, and generated directories do not exist and that both
marketplace manifests contain no `plugins/` path.

## Validation

Executed on 2026-07-28:

```text
HOME=<fresh temporary directory> bash tests/run-tests.sh
jq . .claude-plugin/plugin.json
jq . .codex-plugin/plugin.json
jq . .claude-plugin/marketplace.json
jq . .agents/plugins/marketplace.json
git diff --check
git diff --cached --check
```

Results: the fresh-home gate passed (8 shell checks; 9 Python contract tests).
The contract test invokes `bin/personas verify` from the source root, a clean
installed-copy fixture, and a separately relocated-copy fixture; each resolves
its own plugin root and returns `PASS`. It also proves that the three shared
`SKILL.md` files are the only product skill bodies and that no generated skill
tree exists. All four manifests parse as JSON and both diff checks pass.

No live persona, installed runtime, cache, remote, commit, push, or tag was
changed. Mesh remains outside this task and was not modified.
