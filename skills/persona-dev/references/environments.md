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
starts at the persona root and loads `CLAUDE.md`.
