# Personas 6.0.0 release preparation

Personas 6.0.0 keeps personas simple: readable folders with one
portable definition, shared role skills, and small native adapters for Claude
Code and Codex.

Highlights:

- `AGENTS.md` owns portable identity and behavior;
- Claude Code imports `AGENTS.md`; Codex receives it natively;
- optional explicit folder memory works without claiming native-memory sync;
- Cloud uses the same publishable folder with no GitHub token or visibility
  protocol;
- `persona-dev` now owns create, evolve, reconcile, and optional activation;
- a narrow on-demand sync helper produces marked, collision-safe Claude and
  Codex adapters from the live portable source;
- `.mcp.json` remains ignored local configuration and supports stdio and
  streamable HTTP translation without credential literals.

The underlying atomic folder contract retains its 2026-07-31 Claude Code and
Codex CLI behavioral evidence. Personas 6.0.0 separately gates the new native
sync helper with generated-adapter, MCP translation, collision, credential,
Unicode, and MCP-free profile tests.

Read [MIGRATION.md](MIGRATION.md), [SUPPORT.md](SUPPORT.md), and
[ROLLBACK.md](ROLLBACK.md) before publishing.

## Recommended GitHub topics

`ai`, `agent-tools`, `ai-personas`, `claude-code`, `codex`, `developer-tools`,
`privacy`, `productivity`

## External release steps

1. Review the final diff and complete source gate.
2. Confirm the folder-contract evidence and native-sync test suite remain current.
3. Commit and push only with explicit authorization.
4. Create tag `personas--v6.0.0` at the final green release commit.
5. Publish the release notes and observe hosted CI.
