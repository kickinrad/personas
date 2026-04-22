# personas-mesh

Sync personas across WSL / Windows / Hetzner through a Tailscale-private git hub.

## What this plugin provides

| Area | Contents |
|---|---|
| `bin/` | `render-config`, `sync-persona`, `sync-all` — node-agnostic sync and template-render logic |
| `hooks/` | `session-start.sh`, `stop.sh` — injected into each persona's `hooks.json` during `personas-mesh:setup` |
| `skills/` | `setup`, `doctor`, `status` — human-invoked workflows |
| `systemd/` | User-unit files for WSL watchdog, WSL Windows-bridge (disabled until Phase 4), Hetzner host |
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

## Planning doc

`../../.claude/plans/personas-mesh-sync.md` in the framework repo is the source of truth for scope, phases, and decisions. Keep it in sync with what this plugin actually ships.
