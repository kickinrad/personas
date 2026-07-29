# Support matrix

| Runtime | Status | Supported path |
|---|---|---|
| Claude Code local | Native | Root plugin, deterministic create, verification, hooks |
| Claude Code Cloud | Preview, private only | Exact-PRIVATE GitHub proof, bound repository marker, CI and SessionStart guard; real private Cloud canary pending |
| Codex | Native | Root Codex plugin, shared skills, deterministic create and verification |
| Gemini CLI / Kimi Code | Unsupported | No adapter is provided |

## Data boundary

Published persona definition contains role procedure, public settings, hooks,
and skills. Profile, memory, local settings, connection configuration, and
credentials are local-only and ignored by default. A private repository never
permits committing credentials.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for recovery and exact failures.
