# personas-mesh — next session pickup

Last session stood up personas-mesh end-to-end across WSL, Windows, and Hetzner `cloud`. Phases 0–4 complete; mesh is live and round-tripping writes through the hub in all 3 directions. Validate soak and wire up deferred items.

## Mesh status at session end (2026-04-22)

- Hub: `ssh://wils@cloud/srv/personas/*.git` (10 bare repos), systemd `personas-mesh-hetzner.timer` 2-min cadence.
- WSL: real ext4 `~/.personas/` (symlink broken), `personas-mesh-wsl.timer` 10-min cadence.
- Windows: `/mnt/c/Users/wilst/.personas/` independent, `personas-mesh-windows-bridge.timer` 3-min cadence.
- Hetzner containers (julia, mila, bob, nara, warren): bind-mount `/srv/personas-work/{p}:/workspace:rw`, `autoMemoryDirectory=/workspace/user/memory`, image `bridgey-persona:latest` rebuilt on cloud.
- Backup: `~/personas-backups/pre-unlink-20260422-211243.tar` (124 MB, pre-symlink-break snapshot).

## What to do next session

### 1. Verify 24h soak (start here)

```bash
# Any sync-conflict branches anywhere?
ls ~/.personas/.sync-conflicts/ 2>/dev/null

# All three timers healthy + recent successful runs?
systemctl --user status personas-mesh-wsl.service personas-mesh-windows-bridge.service --no-pager | grep -E "Active|Result"
ssh wils@cloud 'systemctl --user status personas-mesh-hetzner.service --no-pager | grep -E "Active|Result"'

# Per-persona: laptop WSL == laptop Windows == hub?
for p in archer bob julia kai mila nara piper reed urza warren; do
  wsl=$(git -C ~/.personas/$p rev-parse --short HEAD)
  win=$(git -C /mnt/c/Users/wilst/.personas/$p rev-parse --short HEAD)
  hub=$(ssh wils@cloud "git -C /srv/personas/$p.git log -1 --format=%h")
  echo "  $p: wsl=$wsl win=$win hub=$hub"
done
```

If anything's divergent, run `personas-mesh:doctor` (skill shipped in this session's plugin).

### 2. Wire up GitHub async mirror (deferred in Phase 0)

Currently `cloud` has no SSH key authorized for the `kickinrad` GitHub account, so `github` remote on bare repos isn't set up and `personas-mesh-github-mirror.timer` isn't enabled. Steps:

```bash
ssh wils@cloud '
  ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_kickinrad -N ""
  cat ~/.ssh/id_ed25519_kickinrad.pub
'
# Paste that pubkey into https://github.com/settings/keys
ssh wils@cloud '
  mkdir -p ~/.ssh/config.d
  cat > ~/.ssh/config.d/kickinrad <<EOF
Host github.com
  IdentityFile ~/.ssh/id_ed25519_kickinrad
EOF
  ssh-keyscan github.com >> ~/.ssh/known_hosts
  for p in archer bob julia kai mila nara piper reed urza warren; do
    git -C /srv/personas/$p.git remote add github git@github.com:kickinrad/$p.git 2>/dev/null || true
  done
  systemctl --user enable --now personas-mesh-github-mirror.timer
'
```

### 3. Deployment expansion — 5 missing personas + 7 missing Discord bots

Goal (stated mid-session): all 10 personas × all 3 locations × Discord. Currently:
- Hetzner has bridgey-* for **5**: julia, mila, bob, nara, warren. Missing: archer, kai, piper, reed, urza.
- Discord bots in `pass discord/`: **3** tokens (julia, bob, mila). Missing: archer, kai, piper, reed, urza, nara, warren.

This is out-of-scope for personas-mesh; it's home-base / bridgey stack expansion. Requires the Discord Developer Portal (only Wils can do OAuth) to create 7 bot applications, then:

- `pass insert discord/{name}-bot-token` for each new bot
- `pass insert bridgey/token-{name}` for 5 missing (archer, kai, piper, reed, urza)
- Edit `/data/coolify/services/jgcko8w0o4gwoocs0cks8swo/docker-compose.yml` on cloud — add 5 `bridgey-{name}` services + 7 `bridgey-discord-{name}` services (follow existing pattern; ports 8097+). Update `BRIDGEY_AGENTS` JSON on each bridgey-{name} to include the new peers.
- `docker compose up -d` from that dir (Coolify `/restart` is unreliable for local images — use direct compose).

### 4. Coolify API notes (surprise cost)

The Coolify v4 API has two quirks hit this session:
- `PATCH /api/v1/services/{uuid}` rejects raw string in `docker_compose_raw`; must be **base64-encoded**.
- `POST /api/v1/services/{uuid}/restart` does NOT reliably recreate containers when images have `pull_policy: never`. Use `docker compose up -d` from `/data/coolify/services/{uuid}/` instead (documented in `~/projects/personal/bridgey/CLAUDE.md`).

### 5. Housekeeping

- Stage all `/mnt/c/Users/wilst/.personas/{p}/.mcp.json` copies into WSL — only 7/10 had them; check whether archer/kai need MCP servers added.
- Consider pruning `~/personas-backups/pre-unlink-20260422-211243.tar` after a week of confirmed healthy mesh.
- Bump `framework-version` in any persona still at 1.9.0 (archer has `1.9.0`) — run `persona-update`.

## Don't re-do

- Phase 0 (Hetzner hub) — complete, don't re-clone bare repos.
- Phase 1–3 (persona migrations) — complete, don't rewrite remotes.
- Phase 4 (symlink break) — complete, don't re-symlink (would undo the WSL-native speedup).
- Coolify stack flip — complete, the 5 bot bind-mounts are at `/srv/personas-work/{p}:rw`.

## Key files shipped this session

- `plugins/personas-mesh/` — the plugin (scaffold, scripts, hooks, systemd, skills, docs).
- `.claude/plans/personas-mesh-sync.md` — revised plan (source of truth for what the plugin does).
- Commits on `main`: `e106805`, `00f249d`, `1225957`, `43a606b`.

Pick up by running the soak-verify commands above first.
