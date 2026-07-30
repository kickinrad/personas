# Task 7 — First-success experience

Date: 2026-07-28

## Public path

The README now leads with the continuity problem, the durable collaborator
outcome, supported Claude local / private-only Claude Cloud / Codex surfaces,
and the Claude install path. It then separates three quickstarts and uses a
sanitized Atlas role with the actual skill-driven creation interface. The
verification command is the current `bin/personas verify` interface; retired
validator and nested-plugin paths were removed from owned public documents.

`examples/atlas-sanitized/README.md` provides a data-free role brief and
expected verification result. It contains no personal profile, credential, or
external-service instruction.

## Cloud boundary and deterministic creation

The README states that authenticated GitHub visibility must be exactly `PRIVATE`
at creation and local verification and is enforced by CI. Cloud SessionStart
uses a zero-token offline repository-binding check. It also distinguishes the
public framework repository from the private personalized Cloud repository and
states that credentials are forbidden from Git regardless of visibility.

Task-7 extension closed the creation and rollback gap with
`bin/personas create <name> --destination <parent> --profile … [--repository
OWNER/REPO] [--json]`. It validates the final path, creates an explicitly named
sibling staging directory, and atomically renames it only on success. Handled
failure cleans staging or reports the retained path and cleanup result. Local
and Codex paths are offline and make no external request.

Cloud creation proves authenticated `gh` visibility is exactly `PRIVATE`
before creating either staging or final files (an explicit adapter remains
available for controlled environments). It initializes a new empty local Git
repository with the approved GitHub origin and records a
`.persona-cloud-repository` binding, so immediate Cloud verification passes.
SessionStart keys its preflight from that marker and verification rejects a home
whose normalized GitHub `origin` differs. It also creates a
per-persona CI workflow that rejects a non-private repository and runs the tree
publishing guard. Public and unknown fixtures prove no target or staging write
occurs. GitHub repository creation remains a separately authorized operator
action and is never attempted.

## Support and validation

Troubleshooting now covers cancellation, denied permission, offline or install
failure, name collision, partial writes and staging cleanup, verification,
unsupported runtimes, Cloud private-visibility remediation, and recovery.

`tests/test_documentation.py` validates first-screen content, current commands,
Cloud remediation, closed creation guarantees, support boundaries, sanitized
example safety, and local Markdown links. `tests/test_persona_create.py`
covers success, collision, forced partial failure, destination cause, Cloud
private/public/unknown behavior, offline local creation, and stable JSON exits.

Executed on 2026-07-28:

```text
HOME=<fresh temporary directory> python3 tests/test_documentation.py
HOME=<fresh temporary directory> python3 tests/test_persona_create.py
HOME=<fresh temporary directory> bash tests/run-tests.sh
rg retired paths across README.md CONTRIBUTING.md TROUBLESHOOTING.md examples/
git diff --check
git diff --cached --check
```

Results: documentation checks passed (6 tests); creation checks passed (7
tests); Cloud verification (6 tests), publishing safety (10 tests), and runtime
adapters (4 tests) passed; the full fresh-home gate passed; retired owned-doc
paths were absent; both diff checks passed. No network, live persona, GitHub,
installation, activation, commit, push, or tag was used.
