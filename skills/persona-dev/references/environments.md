# Environments — personas root, Cowork, WSL2 symlink

Read when `persona-dev` must choose a persona home across native, WSL, Windows,
Desktop, or Cowork environments, or configure a Claude launcher.

## Personas root by environment

| Environment | Personas root | Why |
|-------------|--------------|-----|
| macOS / Linux (native) | `~/.personas/` | Standard home directory |
| WSL2 (CLI only) | `~/.personas/` (WSL side) | Better I/O performance |
| WSL2 (CLI + Desktop) | `/mnt/c/Users/{WINUSER}/.personas/` + symlink from WSL `~/.personas/` | Both environments see the same files |
| Windows native (CLI or Desktop) | `%USERPROFILE%\.personas\` | Native Windows home |
| Cowork / Desktop session | **Workspace folder** — detect with `pwd` or workspace path, NOT `~` | `~` resolves to temp session filesystem that vanishes |

## Cowork detection

If `$HOME` starts with `/sessions/` or the CWD is inside a temp path, you're in a Cowork session. Cowork runs in an isolated Linux VM — it can only access explicitly mounted folders and resolves symlinks to real paths (blocking escape). Find the actual workspace/mounted folder and write there instead.

## WSL2 + Desktop symlink

When the user wants both CLI and Desktop, personas should live on the Windows side (`/mnt/c/Users/{WINUSER}/.personas/`) with a symlink from WSL's `~/.personas/`. **Important:** This symlink must be created from the WSL terminal, not from Cowork — Cowork cannot create symlinks to paths outside its mounted folders. Tell the user to run:

```bash
ln -s /mnt/c/Users/{WINUSER}/.personas ~/.personas
```

## Claude launcher

Pass caller arguments through unchanged. Add persona defaults only when neither
the caller nor `.claude-flags` supplies them; always isolate project and local
settings with `--setting-sources project,local`. Discover supported flags from
the installed CLI and store one approved line in `.claude-flags`. Verify the
launcher starts at the persona root, loads `CLAUDE.md`, and leaves Codex alone.
