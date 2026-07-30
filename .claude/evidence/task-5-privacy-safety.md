# Task 5 — Privacy and publishing safety evidence

Date: 2026-07-28

## Structural boundary

- Publishable persona definition: `CLAUDE.md`, `AGENTS.md`, output style,
  role-local skills, tools, and README.
- Local-only state: `user/profile.md`, `user/memory/`, `.mcp.json`, and
  `.claude/settings.local.json`. The shipped `.gitignore` excludes each.
- Credentials, tokens, signing keys, and passwords are forbidden from Git for
  every repository visibility. The publishing guard rejects private paths and
  credential-like staged/tracked/tree content.
- Creation remains offline: template scaffolding makes no network request,
  opens no listener, and emits no telemetry. Runtime-provider requests occur
  only when the user starts that runtime.

## Guard contract

`scripts/public-repo-guard.sh` is deterministic and does not parse a user shell
command. Invoke it at a Git/release seam:

```bash
scripts/public-repo-guard.sh --check-staged
scripts/public-repo-guard.sh --check-tree "$GITHUB_SHA"
scripts/public-repo-guard.sh --check-repository
```

The generated PreToolUse hook is advisory only. It is deliberately not the
security boundary.

## Claude Cloud contract

The Cloud creation flow is separately authorized: obtain/validate the GitHub
repository first, then run:

```bash
.claude/hooks/public-repo-guard.sh --cloud-preflight OWNER/REPO
```

The interface uses authenticated `gh repo view … --json visibility --jq
.visibility` (or an injected `PERSONA_GITHUB_CLI` test double) and accepts only
the exact result `PRIVATE`. Public, internal, lower-case/ambiguous, unavailable,
unauthenticated, or empty evidence exits 2 before profile or memory context is
loaded, written, or committed. This task did not contact GitHub or create a
repository.

## Required integration owned by Task 6/root

Add these checks to the repository CI/release workflow before artifact creation
or publish:

```yaml
- run: test "${{ github.event.repository.private }}" = true
- run: scripts/public-repo-guard.sh --check-tree "${{ github.sha }}"
```

The generated SessionStart hook treats the committed
`.persona-cloud-repository` marker as the Cloud signal and executes the offline
`--check-cloud-binding` before it supplies Cloud context. Exact private
visibility remains enforced at creation, local verification, and CI. Cloud
startup deliberately requires no GitHub token.

## Validation

```text
python3 -m unittest -v tests/test_privacy_safety.py
Ran 7 tests — OK
bash -n scripts/public-repo-guard.sh — OK
git diff --check — OK
```

The focused fixture matrix covers clean publishable definition, PII-like profile,
tracked memory, local runtime settings, credential-like content, staged/tree
checks independent of Git command form, offline behavior, and PRIVATE/PUBLIC/
INTERNAL/unknown/ambiguous visibility results.
