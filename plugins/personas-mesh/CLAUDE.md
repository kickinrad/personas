---
title: personas-mesh
---

# personas-mesh

Sync personas across WSL / Windows / Hetzner through a Tailscale-private git hub.

## What this plugin provides

| Area | Contents |
|---|---|
| `bin/` | `render-config`, `sync-persona`, `sync-all` — git mesh (cross-host sync via the hub). `sync-user-persona`, `sync-user-all` — local user/ rsync (WSL ↔ Windows reconciliation for gitignored personal data) |
| `hooks/` | `session-start.sh`, `stop.sh` — injected into each persona's `hooks.json` during `personas-mesh:setup` |
| `skills/` | `setup`, `mesh-doctor`, `status` — human-invoked workflows |
| `systemd/` | User-unit files for WSL watchdog, WSL Windows-bridge (disabled until Phase 4), Hetzner host, plus `personas-mesh-user-sync` (local user/ rsync, no install required — points at repo path directly) |
| `templates/` | `.gitattributes` (merge=union rules), `.gitignore.additions`, `.mcp.json.template`, `settings.local.json.template` |
| `docs/` | `hetzner-bootstrap.md`, `migration-symlink-to-mesh.md` — runbooks for steps requiring interactive sudo |

## Node detection

`bin/` scripts and the `setup` skill detect the current node via a precedence:

1. Explicit `PERSONAS_MESH_NODE` env (`wsl` / `windows` / `hetzner`) — override for edge cases
2. `/srv/personas` exists AND `hostname` is `ubuntu-4gb-ash-1` → `hetzner`
3. `/proc/sys/fs/binfmt_misc/WSLInterop` exists AND CWD starts with `/home/` → `wsl`
4. `/proc/sys/fs/binfmt_misc/WSLInterop` exists AND CWD starts with `/mnt/c/` → `windows` (WSL process driving the Windows-native dir)
5. Otherwise → fail loudly, print what was checked.

## Secrets

Never commit. Templates reference names only; rendering resolves via `pass`. If a referenced secret is missing, `render-config` fails loudly (non-zero exit, error to stderr, no partial file written).

## Hub endpoint

`ssh://wils@cloud/srv/personas/{p}.git` — Tailscale MagicDNS, not a public hostname. All mesh-origin URLs use `wils@cloud` literally; changing the hostname happens in one place (`bin/sync-persona`) if ever needed.

## Two layers of sync

The plugin handles two distinct sync problems with two separate mechanisms:

**Layer 1 — git mesh (cross-host).** `sync-persona` + `sync-all` push committed persona state through the Tailscale-private hub. Carries everything in git: `CLAUDE.md`, `hooks.json`, `.claude/skills/`, `tools/`, etc. Skips `user/` (gitignored for privacy).

**Layer 2 — user/ rsync (intra-host).** `sync-user-persona` + `sync-user-all` reconcile `~/.personas/{p}/user/` with `/mnt/c/Users/${WIN_USER}/.personas/{p}/user/` on a WSL+Windows machine. Uses two passes of `rsync -a --update` (mtime newer-wins, no delete propagation by design). The systemd timer points directly at the repo path — no install/copy step, edit-and-go.

Why split the layers: `user/` must stay out of git for public personas, but on a single dual-filesystem machine the WSL and Windows persona dirs would silently drift if not reconciled. The git mesh can't carry it; rsync can.

## Planning doc

`../../.claude/plans/personas-mesh-sync.md` in the framework repo is the source of truth for scope, phases, and decisions. Keep it in sync with what this plugin actually ships.
