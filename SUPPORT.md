# Support matrix

| Runtime | Status | Supported path |
|---|---|---|
| Claude Code local | Native | Root plugin, deterministic create, verification, hooks |
| Claude Code Cloud | Preview, private only | Exact-PRIVATE creation/local verification, bound repository marker, private-only CI, and zero-token native SessionStart binding check |
| Codex | Native | Root Codex plugin, shared skills, deterministic create and verification |
| Gemini CLI / Kimi Code | Unsupported | No adapter is provided |

## Data boundary

Published persona definition contains role procedure, public settings, hooks,
and skills. Profile, memory, local settings, connection configuration, and
credentials are local-only and ignored by default. A private repository never
permits committing credentials.

Claude Code Cloud starts from a clean repository clone and needs no GitHub token
inside the VM. Persona Manager trusts the private repository selected at
creation, enforces private visibility in GitHub Actions, and checks at
SessionStart that the committed binding matches the cloned origin.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for recovery and exact failures.
