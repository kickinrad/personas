---
name: setup
description: Bootstrap personas-mesh on the current node (WSL / Hetzner host). This skill should be used when the user asks to "install personas-mesh", "set up persona sync", "bootstrap the mesh", "wire up sync on this machine", or after pulling personas-mesh for the first time on any node. Installs bin/ scripts to ~/.local/bin, copies systemd units, renders the per-node env file, wires each persona's hooks.json with the sync hooks, adds .gitattributes, and verifies by running one sync loop. Does not modify persona-manager or any persona CLAUDE.md.
---

# personas-mesh:setup

One-shot bootstrap per node. Run after installing the plugin on a fresh machine.

## What this does

1. **Detect node type** — `wsl`, `windows` (WSL process driving `/mnt/c/`), or `hetzner`. Ask the user to confirm.
2. **Install binaries** — copy `${CLAUDE_PLUGIN_ROOT}/bin/{render-config,sync-persona,sync-all}` to `~/.local/bin/personas-mesh-*` (stable path referenced by systemd units).
3. **Render `~/.personas-node.env`** — interactive on first install: asks for the persona-memory path template (default is the node-appropriate absolute path from `templates/node-env.example`).
4. **Install systemd units** — copy the node-appropriate `.service` + `.timer` files to `~/.config/systemd/user/`; `systemctl --user daemon-reload`; enable + start the main timer. On WSL, install both `personas-mesh-wsl.timer` AND `personas-mesh-windows-bridge.timer` but only enable the WSL one (the bridge goes live in Phase 4 after the symlink is broken).
5. **Per-persona wiring** — for each persona under `~/.personas/` (or `/srv/personas-work/` on Hetzner):
   - Confirm the remote `origin` points at `ssh://wils@cloud/srv/personas/{name}.git` (migrate from `https://github.com/...` if needed; keep GitHub as `github` remote).
   - Copy `${CLAUDE_PLUGIN_ROOT}/templates/.gitattributes` into the persona (merge only — don't clobber existing rules).
   - Append the entries from `templates/.gitignore.additions` to the persona's `.gitignore`, dedup.
   - Patch the persona's `hooks.json` to add SessionStart + Stop command hooks pointing at `${CLAUDE_PLUGIN_ROOT}/hooks/{session-start,stop}.sh`. Do not replace existing hooks; append to the existing arrays.
   - Render `.mcp.json` and `.claude/settings.local.json` from templates via `render-config`.
6. **Smoke test** — run `personas-mesh-sync-all` once with `--verbose`; show result.
7. **Summary** — print what was installed and the one remaining action (Hetzner host bootstrap or symlink break) if applicable.

## Safety rails

- **Never delete a persona's existing hook.** Only append command hooks and a new matcher entry.
- **Never write a rendered `.mcp.json` that still contains `${…}`** — `render-config` already errors; the skill must verify by grepping the output.
- **Never push** a persona repo that has uncommitted changes the user hasn't seen. If the setup run finds dirty work, show it via `git status` and ask before the first `sync-persona` pushes.
- **Refuse to run on Hetzner host without sudo access** for `/srv/personas-work/` creation — direct the user to the runbook instead (`docs/hetzner-bootstrap.md`).

## Invocation

```
Skill('personas-mesh:setup')
# or specific node:
Skill('personas-mesh:setup', '--node=wsl')
Skill('personas-mesh:setup', '--node=hetzner')
```

## Depends on

- `${CLAUDE_PLUGIN_ROOT}/bin/*` — executable
- `${CLAUDE_PLUGIN_ROOT}/templates/*`
- `${CLAUDE_PLUGIN_ROOT}/systemd/*`
- `${CLAUDE_PLUGIN_ROOT}/hooks/*.sh`

## Reversal

The setup is idempotent — re-running it updates paths and re-syncs templates. To uninstall from a node:

```
systemctl --user disable --now personas-mesh-*.timer
rm ~/.config/systemd/user/personas-mesh-*.{service,timer}
rm ~/.local/bin/personas-mesh-*
# Revert each persona's hooks.json by removing the added command entries
# (hooks.json lives per-persona under ~/.personas/{name}/hooks.json)
```
