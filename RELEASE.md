# Personas 4.0.0 release preparation

Personas 4.0.0 keeps personas simple: readable folders with one
portable definition, shared role skills, and small native adapters for Claude
Code and Codex.

Highlights:

- `PERSONA.md` owns portable identity and behavior;
- Claude Code and Codex receive native project entry points and settings;
- optional explicit folder memory works without claiming native-memory sync;
- Cloud uses the same publishable folder with no GitHub token or visibility
  protocol;
- runtime support requires clean behavioral canary evidence;
- the CLI and enforcement-heavy transitional architecture are gone.

On 2026-07-31, Claude Code 2.1.220 and Codex CLI 0.146.0 independently passed
the same sanitized Atlas identity, voice, boundary, skill, profile, and
explicit-memory probes.

Read [MIGRATION.md](MIGRATION.md), [SUPPORT.md](SUPPORT.md), and
[ROLLBACK.md](ROLLBACK.md) before publishing.

## Recommended GitHub topics

`ai`, `agent-tools`, `ai-personas`, `claude-code`, `codex`, `developer-tools`,
`privacy`, `productivity`

## External release steps

1. Review the final diff and complete source gate.
2. Confirm the recorded Claude and Codex parity evidence remains current.
3. Commit and push only with explicit authorization.
4. Create tag `personas--v4.0.0` at the final green release commit.
5. Publish the release notes and observe hosted CI.
