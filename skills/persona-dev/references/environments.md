# Environments

Read when `persona-dev` must choose a persona home or a Claude launch mode.

## Personas root

| Environment | Personas root |
|-------------|---------------|
| macOS, Linux, or WSL | `~/.personas/` |
| Windows | `%USERPROFILE%\.personas\` |
| Cowork or Desktop session | the mounted workspace folder, not `~` |

In Cowork, `$HOME` often starts with `/sessions/` and vanishes with the
session. Detect the mounted workspace with `pwd` and write there instead.

## Integrated or focused launch

Integrated is the default: start `claude` or `codex` normally from the persona
folder and keep user-level configuration. Claude Code also supports focused
use with fewer user-level customizations:

```bash
claude --setting-sources project,local
```

Codex has no supported equivalent, so it remains integrated. Managed policy,
authentication, and explicit CLI flags remain runtime-owned. Verify a launch
starts at the persona root and loads `AGENTS.md`.

## Instruction loading

Claude Code 2.1.281 or later reads `AGENTS.md` directly when no `CLAUDE.md`
exists in the folder or above it, and expands its `@PERSONAS.md` import.
Codex reads the same line and opens the file. Keep `CLAUDE.md` and other
`AGENTS.md` files out of the personas root; Claude Code would load them too.
