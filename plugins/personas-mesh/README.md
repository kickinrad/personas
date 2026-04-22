# personas-mesh

Keeps every persona's state in sync across WSL, Windows, and Hetzner without manual `git push` / `git pull`. Uses a Tailscale-private bare-repo hub on `cloud` as the source of truth; GitHub is an async public mirror.

## What it does

- **Per-session hook**: `git pull --rebase --autostash` on SessionStart; `git add -A && commit && push` (amend-if-recent) on Stop.
- **Per-node systemd watchdog**: catches dirty trees between sessions, runs the same pull/commit/push loop.
- **Template-and-render** for node-specific config (`.mcp.json`, `.claude/settings.local.json`): templates tracked in git, rendered output gitignored.
- **Conflict-safe by construction**: auto-memory files are one-file-per-memory (naturally mergeable); `MEMORY.md` + `user/profile.md` use `merge=union`.

## Skills

- **`setup`** — bootstrap personas-mesh on the current node (WSL / Hetzner host auto-detect).
- **`doctor`** — diagnose sync issues (remote reachability, divergent commits, conflict branches).
- **`status`** — show per-persona sync state across nodes.

## Topology

```
                           Hub (Hetzner `cloud`)
                   ssh://wils@cloud/srv/personas/*.git
                                │
       ┌────────────────────────┼───────────────────────────┐
       │                        │                           │
   WSL-native              Windows FS                 Hetzner host
   (~/.personas/{p})       (/mnt/c/...)               (/srv/personas-work/{p})
   interactive sessions    CoWork app                 bridgey-* containers
```

See `CLAUDE.md` for the full implementation plan.
