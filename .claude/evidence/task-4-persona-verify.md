# Task 4 — Declarative persona contract and verification

Date: 2026-07-28

## Interface

`bin/personas verify <persona-path> [--profile PROFILE] [--json]` is read-only.
Profiles separate `shared`, `claude-local`, `codex`, and `claude-cloud`
requirements. The JSON report has stable `schemaVersion`, `status`, `profile`,
path-bearing errors/warnings, aggregate lists, and per-contract `checks`.

- Exit `0`: `PASS` or `WARN`.
- Exit `1`: contract `FAIL`.
- Exit `2`: unsupported profile or invocation failure.

The legacy `bin/validate-persona` executable is retired rather than retained as
a forwarding shim. The root contract test asserts its absence.

## Cloud boundary

The `claude-cloud` profile resolves only a GitHub `origin` remote, then calls
the executable named by `PERSONAS_GITHUB_VISIBILITY_ADAPTER` with `owner/repo`.
It accepts JSON evidence only when `authenticated` is exactly `true` and
`visibility` is exactly `PRIVATE`. Missing/ambiguous repository, unavailable
or unreachable adapter, malformed evidence, unauthenticated evidence, and all
other visibility values fail closed. Tests use a temporary local adapter; no
network request is made.

## Fixture coverage and validation

`tests/fixtures/contracts/matrix.json` declares the contract matrix. The public
interface tests cover valid, absent, malformed, stale, unsafe, legacy,
unsupported, public/internal/unknown, unauthenticated, ambiguous, unavailable,
and unreachable cases. Legacy inspection returns `WARN` and proves the fixture
bytes remain unchanged.

Executed on 2026-07-28:

```text
HOME=<fresh temporary directory> python3 tests/test_persona_verify.py
HOME=<fresh temporary directory> bash tests/run-tests.sh
jq . interop/capabilities.json
git diff --check
git diff --cached --check
```

Results: focused verification suite passed (6 tests); existing fresh-home gate
passed (8 shell checks; 9 Python contract tests); JSON and both diff checks
passed. Runner and CI integration are intentionally deferred to the owning
follow-up task.
