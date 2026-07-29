# Support matrix

| Runtime | Status | Supported path |
|---|---|---|
| Claude Code local | Native | Root plugin, deterministic create, verification, hooks |
| Claude Code Cloud | Preview, private only | Exact-PRIVATE GitHub proof, bound repository marker, CI and native SessionStart guard; Cloud environment must provide authenticated visibility inspection |
| Codex | Native | Root Codex plugin, shared skills, deterministic create and verification |
| Gemini CLI / Kimi Code | Unsupported | No adapter is provided |

## Data boundary

Published persona definition contains role procedure, public settings, hooks,
and skills. Profile, memory, local settings, connection configuration, and
credentials are local-only and ignored by default. A private repository never
permits committing credentials.

Claude Code Cloud starts from a clean repository clone. Its Cloud environment
must install `gh` and provide a least-privilege `GH_TOKEN` capable of reading
the private repository's metadata, or provide an equivalent authenticated
`PERSONA_GITHUB_CLI` adapter. These credentials stay in the Cloud environment
and never enter the repository.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for recovery and exact failures.
