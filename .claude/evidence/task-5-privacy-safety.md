# Historical Task 5 — Privacy and publishing safety evidence

> Historical evidence only. It documents superseded guards and Cloud machinery;
> it is not current v5 privacy or runtime proof.

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

## Retired guard evidence

At Task 5, `scripts/public-repo-guard.sh` was the deterministic guard. The
commands below record that retired implementation; they are not v5 procedures
and must not be invoked as current release checks.

```bash
scripts/public-repo-guard.sh --check-staged
scripts/public-repo-guard.sh --check-tree "$GITHUB_SHA"
scripts/public-repo-guard.sh --check-repository
```

The generated PreToolUse hook is advisory only. It is deliberately not the
security boundary.

## Retired Claude Cloud evidence

Task 5's Cloud flow required a separately authorized GitHub repository and the
following now-retired preflight:

```bash
.claude/hooks/public-repo-guard.sh --cloud-preflight OWNER/REPO
```

The interface uses authenticated `gh repo view … --json visibility --jq
.visibility` (or an injected `PERSONA_GITHUB_CLI` test double) and accepts only
the exact result `PRIVATE`. Public, internal, lower-case/ambiguous, unavailable,
unauthenticated, or empty evidence exits 2 before profile or memory context is
loaded, written, or committed. This task did not contact GitHub or create a
repository.

## Superseded integration handoff

Task 5 handed the following checks to Task 6. The v5 contract retired that
machinery; this block is historical evidence, not an outstanding requirement:

```yaml
- run: test "${{ github.event.repository.private }}" = true
- run: scripts/public-repo-guard.sh --check-tree "${{ github.sha }}"
```

The then-generated SessionStart hook treated the committed
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
