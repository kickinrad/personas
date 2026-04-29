---
name: status
description: Show the per-persona sync state across all nodes. This skill should be used when the user asks "are my personas in sync", "show mesh status", "personas-mesh status", "is the mesh healthy", "which personas are drifting", or just wants a one-screen dashboard of the mesh. Reads from the local node directly and optionally SSHes to cloud for the Hetzner column.
---

# personas-mesh:status

One-screen dashboard of per-persona sync health.

## What to show

For each of the 10 personas (Archer, Bob, Julia, Kai, Mila, Nara, Piper, Reed, Urza, Warren), a row with:

- **Persona** — name
- **WSL** — last commit ts (relative), `✓` clean or `●` dirty-count
- **Windows** — same for `/mnt/c/…` copy (or `—` if still symlinked)
- **Hetzner** — last commit ts from `ssh wils@cloud git -C /srv/personas-work/{p} log -1 --format=%ct` (or `—` if persona not deployed there)
- **Hub** — last commit ts from `ssh wils@cloud git -C /srv/personas/{p}.git log -1 --format=%ct`
- **Status** — `in sync` / `N ahead` / `N behind` / `DIVERGED` / `CONFLICT`

## Source of truth per column

| Column | Source |
|---|---|
| WSL | `git -C ~/.personas/{p} log -1 --format=%ct`; `git status --porcelain` |
| Windows | `git -C /mnt/c/Users/wilst/.personas/{p} ...` (or symlink-resolved) |
| Hetzner | `ssh wils@cloud git -C /srv/personas-work/{p} ...` |
| Hub | `ssh wils@cloud git -C /srv/personas/{p}.git ...` |

## Bot-only check (laptop-only personas skip)

Archer, Kai, Piper, Reed, Urza are not deployed on Hetzner — mark their Hetzner column `—`.

## Conflict badge

If `git branch --list 'sync-conflict/*'` returns anything on any node for that persona, mark Status as `CONFLICT` and point the user at `personas-mesh:mesh-doctor`.

## Output style

```
Persona  WSL        Windows    Hetzner     Hub         Status
archer   2m ago ✓   —          —           2m ago      in sync
bob      12m ago ✓  —          4m ago      3m ago      1 behind
julia    ●3 dirty   —          1m ago ✓    1m ago      CONFLICT
…
```

## Fast path

Run `ssh wils@cloud 'for r in /srv/personas/*.git; do echo "$(basename "$r") $(git -C "$r" log -1 --format=%ct 2>/dev/null)"; done'` once, parse, combine with local reads — one ssh round trip for all personas.
