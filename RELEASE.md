# Persona Manager 3.0.0 release preparation

## Public release notes

Persona Manager 3.0.0 is a focused, privacy-first toolkit for creating one
durable AI collaborator. It replaces the old multi-plugin tree with one root
plugin for Claude Code local, preview private-only Claude Code Cloud, and Codex.

Highlights:

- deterministic, atomic persona creation and structured verification;
- native Codex packaging alongside Claude Code support;
- Cloud creation/local verification and CI require exact `PRIVATE` visibility;
  zero-token Cloud startup verifies the repository binding offline;
- local profile, memory, settings, connections, and credentials stay ignored;
- one source gate is the CI verdict.

Read [MIGRATION.md](MIGRATION.md), [SUPPORT.md](SUPPORT.md), and
[ROLLBACK.md](ROLLBACK.md) before publishing.

Cloud remains preview support until a separately authorized real private
GitHub/Claude Cloud canary has completed.

## Recommended GitHub topics

`ai`, `agent-tools`, `claude-code`, `codex`, `developer-tools`,
`privacy`, `productivity`

These are recommendations only; no GitHub metadata was changed.

## External release steps — not performed

1. Review the final diff and source gate.
2. Commit, tag `persona-manager--v3.0.0`, and push only with explicit
   authorization.
3. Publish release notes and set the recommended GitHub topics.
4. Observe hosted public CI after the authorized push.
