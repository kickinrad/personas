# Support

| Runtime | Status | Supported path |
|---|---|---|
| Claude Code local | Supported | `CLAUDE.md`, `.claude/settings.json`, shared skills, and optional explicit folder memory |
| Claude Code Cloud | Supported folder model | The same publishable Claude folder in a repository; ignored local context is normally absent |
| Codex | Supported | `AGENTS.md`, `.codex/config.toml`, shared skills, and optional explicit folder memory |
| Gemini CLI / Kimi Code | Unsupported | No native adapter has passed the parity gate |

## Parity gate

A runtime is supported only when a clean installed behavioral canary proves that it loads
the persona's identity, voice, boundary, role skill, optional local profile, and
explicit folder memory. File presence alone is insufficient.

## Memory boundary

`user/memory/MEMORY.md` is optional ignored Markdown that either supported
runtime can read. Claude and Codex native auto-memory are separate runtime-owned
features and are not synchronized. Codex currently stores native local memories
under `$CODEX_HOME/memories`, not in a persona-selected folder.

## Publishing boundary

Everything tracked in a persona repository should be safe to publish. Keep
`user/`, runtime-local settings, connections, and credentials out of Git. A
private repository is recommended for personalized Cloud use, but Persona
Manager leaves visibility user-managed and requires no GitHub credentials.
