# Plan: `personas-mesh` — persona state sync across WSL / Windows / Hetzner

_Revised 2026-04-22 after orientation found the initial plan was written against a stale filesystem model. Key corrections: Hetzner hostname (`cloud`, not `homelab.ts.net`); `~/.personas` on WSL is currently a symlink to `/mnt/c/Users/wilst/.personas` and WSL-native separation is a target, not a premise; the Coolify `bridgey-personas` stack mounts `/opt/bridgey/personas/{p}:/workspace:ro`, which must be edited for bots to participate in memory sync; Bridgey is live._

## Goal

Make every persona (Archer, Bob, Julia, Kai, Mila, Nara, Piper, Reed, Urza, Warren — 10 total) stay automatically in sync across three node types without manual intervention:

- **WSL** (`/home/wilst/.personas/`) — primary interactive dev environment, WSL-native (fast) after Phase 4
- **Windows** (`/mnt/c/Users/wilst/.personas/`) — accessed by the CoWork native Windows app (read + write); an independent sync node after Phase 4
- **Hetzner** (`cloud`, Coolify-managed Docker containers) — always-on personas (Julia, Mila, Bob, Nara, Warren run bridgey-persona + bridgey-discord containers 24/7)

Sync must be foolproof under three failure modes: laptop sleep/travel, concurrent writes (bot + interactive session), and per-node configuration differences (paths, secrets).

A secondary goal of the WSL-native split (Phase 4) is to eliminate the 9P performance penalty WSL incurs today reading/writing the Windows NTFS mount through the symlink.

## Current state

Each persona is already a standalone git repo (`github.com/kickinrad/{name}`, private, remote currently `https://github.com/kickinrad/{name}.git`).

**Critical current state — the "two copies" are actually one.** `~/.personas` is a symlink to `/mnt/c/Users/wilst/.personas`. Every WSL session is reading and writing the Windows NTFS filesystem through the WSL 9P bridge — that's the source of the slowness. There is no WSL↔Windows drift today because there's no WSL copy; everything lives on the Windows side. CoWork on Windows and `claude` on WSL hit the same inodes.

**What we actually want**: two *real* copies — a WSL-native `~/.personas/` (fast local filesystem) and a Windows-native `C:\Users\wilst\.personas\` (so CoWork keeps working) — kept in sync via the mesh. Breaking the symlink and standing up a real WSL-native copy is an explicit migration step in Phase 4.

Hetzner is a third independent location. Discord-bot personas (Julia, Mila, Bob, Nara, Warren) run there as Coolify-managed docker containers that bind-mount a host directory. Those writes happen 24/7 regardless of laptop state — the main reason Hetzner becomes the hub.

`.gitignore` already excludes runtime state (databases, logs, `.mcp.json`, `settings.local.json`). Memory is per-file (auto-memory writes one `.md` per memory), which is naturally merge-friendly. The `MEMORY.md` index and `user/profile.md` are the only concurrent-write hot spots and can be handled with git's union merge driver.

`autoMemoryDirectory` in several WSL-side `.claude/settings.local.json` files points at `/mnt/c/Users/wilst/.personas/{persona}/user/memory`. Today that's cosmetically odd but functionally fine (symlink resolves to the same inode). *After* the symlink is broken it becomes wrong — every WSL-side `settings.local.json` must point at `/home/wilst/.personas/{persona}/user/memory`. The Phase 4 cleanup script fixes this in bulk.

## Target topology

```
            Hub: ssh://wils@cloud/srv/personas/*.git  (bare repos; always-on)
                              ▲
                ┌─────────────┼─────────────┐
                │             │             │
            WSL origin    Windows FS     Hetzner host systemd
            (direct push) (WSL systemd   pulls bares into
                           timer, per-   /srv/personas-work/{p};
                           /mnt/c copy)  Coolify stack bind-mounts
                                         these into bridgey-{p} containers

          ─────────────────────────────────────────────────────
          GitHub mirror (async hourly push from Hetzner host)
          Purpose: public backup, not in sync critical path
```

Hetzner tailnet name: `cloud` (MagicDNS) → `100.105.101.128` → host `ubuntu-4gb-ash-1`. All plan references use `cloud`.

**Why Hetzner is the hub**: Discord-bot personas will write memory continuously (see "Hetzner integration" below) and need a reachable push target even when the laptop is asleep. WSL-as-hub would queue divergent commits whenever the laptop is offline. GitHub is retained as an async mirror for public backup but is not on the sync hot path.

**Why Tailscale transport**: keeps all persona traffic on the private tailnet (no GitHub tokens in containers; no public internet dependency for normal sync; MagicDNS gives stable addressing). The mesh sync work happens on the Hetzner host (not inside containers).

### Hetzner integration — current reality vs target

Current state (from Coolify service `bridgey-personas` / uuid `jgcko8w0o4gwoocs0cks8swo`):

- Per-persona container `bridgey-{julia,mila,bob,nara,warren}` mounts `/opt/bridgey/personas/{p}:/workspace:ro` — **read-only**
- Writable agent state lives in named docker volume `jgcko…_{p}-data` at `/data/bridgey` inside the container
- Memory written during bot interactions stays in that docker volume; it is not git-tracked and not synced anywhere
- Shared auth at `/opt/bridgey/auth:/home/node/.claude:rw` (Claude CLI credentials)

Target state:

- `/opt/bridgey/personas/{p}` is replaced by (or aliased to) `/srv/personas-work/{p}` — a git-tracked working tree the Hetzner host-side sync timer keeps fresh from the hub. Keep `:ro` for the container's `/workspace` (prevents accidental container-side rewrites of skills/config).
- Bot memory writes need to land in the git-tracked tree. The bridgey-persona image's entrypoint (or a small wrapper) is adjusted so `AUTO_MEMORY_DIR` points at `/workspace/user/memory` AND the mount for `/workspace` is switched to `:rw`. Alternatively, a sidecar writes memory to `/data/bridgey/memory/` and an hourly on-host script rsyncs → `/srv/personas-work/{p}/user/memory/` and commits.
- Decision between "rw workspace" and "sidecar rsync" is deferred to the Phase 2 Julia pilot. The first is architecturally cleaner; the second preserves the existing read-only guarantee.

**Coolify stack modifications required** (Phase 2) — the current `docker_compose_raw` for `bridgey-personas` must be edited in place: bind-mount path changes from `/opt/bridgey/personas/{p}` → `/srv/personas-work/{p}`, and possibly `:ro` → `:rw`. Coolify's `pull_policy: never` constraint applies; image stays local.

## Data taxonomy

| Path | Synced? | Mechanism |
|---|---|---|
| `CLAUDE.md`, `hooks.json`, `skills/`, `tools/`, `.claude/hooks/` | Yes | Normal git |
| `user/memory/*.md` | Yes | Normal git — per-file pages merge cleanly |
| `user/memory/MEMORY.md` | Yes | `merge=union` (index appends don't conflict) |
| `user/profile.md` | Yes | `merge=union` (append-safe growth) |
| `.mcp.json` | Template-and-render | `.mcp.json.template` in git; output gitignored |
| `.claude/settings.local.json` | Template-and-render | `.local.json.template` in git; output gitignored |
| `.mcp.json`, `*.db`, `*.log`, `scheduler.*` | No (gitignored) | Runtime-only, per-node state |

### Template-and-render for config

Files that contain node-specific paths or secrets are never synced literally. Instead:

```
{persona}/
├── .mcp.json.template                    # committed; uses ${VARS}
├── .claude/settings.local.json.template  # committed
└── (rendered files)                      # node-local, gitignored
```

`bin/render-config` (shipped with the plugin) reads templates, substitutes variables from:

- `pass show bridgey/token-{persona}` — bridgey auth tokens
- `pass show discord/{persona}-bot-token` — Discord tokens
- `~/.personas-node.env` — per-node paths (e.g. `AUTO_MEMORY_DIR=/home/wilst/.personas/{p}/user/memory` on WSL, `.../mnt/c/...` on Windows, `/workspace/user/memory` in containers)

**Rendering timing**: must happen *before* `claude` launches so MCP servers start with correct config. Render is called from the `.aliases.sh` wrapper immediately before the `claude` invocation, avoiding any SessionStart-vs-MCP-init ordering risk. The rendered `.mcp.json` and `settings.local.json` are produced fresh on every invocation; they stay in `.gitignore`.

**Secret rotation**: changing a token means editing `pass` once. Next `claude {persona}` invocation picks up the new value. No per-repo secret commits ever.

## Sync triggers per node

| Node | Mechanism | Cadence |
|---|---|---|
| WSL working tree (`/home/wilst/.personas/{p}`) | Persona SessionStart hook: `git pull --rebase --autostash`; Stop hook: `git add -A && commit && push` | Per-session + 10-min watchdog for dirty trees |
| Windows FS (`/mnt/c/Users/wilst/.personas/{p}`, accessed from WSL — post-symlink-break) | WSL user systemd timer iterates `/mnt/c/Users/wilst/.personas/*/` — pull, commit-if-dirty, push | Every 3 minutes |
| Hetzner bind-mounts (`/srv/personas-work/{p}`) | Hetzner host systemd timer iterates `/srv/personas-work/*/` — pull, commit-if-dirty, push | Every 2 minutes (bots write often) |
| GitHub mirror | Hetzner host cron: for each bare repo, `git push github main` | Hourly |

All triggers use the same core script (`bin/sync-persona`) — different invokers, same logic. The Windows-FS trigger is disabled until the symlink is broken (Phase 4) — until then, the WSL working-tree trigger covers both, because they are the same inode.

## Conflict handling

**Preventive layout** — most conflicts never happen:
- Auto-memory's per-file pages are independently mergeable.
- `user/memory/MEMORY.md` and `user/profile.md` use `merge=union` via `.gitattributes`. Concurrent appends produce a union of both sides, which is the correct semantics for an index or an append-only journal.

**When a real conflict occurs** (rare — e.g. same line edited by two nodes):
- The sync script does not silently fail. It stashes the conflicting state into a `sync-conflict/{hostname}-{timestamp}` branch, surfaces a marker file at `~/.personas/.sync-conflicts/{persona}.log`, and continues.
- A `personas-mesh:mesh-doctor` skill walks the user through `git diff sync-conflict/...` and helps resolve.

## Commit noise control

Stop hook behavior:
- If the last commit is `auto-sync: {same hostname}` within the last 10 minutes → `git commit --amend --no-edit`
- Otherwise → new commit

Result: interactive sessions produce one commit per ~10 minutes of active work per node, not one per session stop. Log stays readable; session boundaries are still visible; no rebase gymnastics needed.

## Plugin structure

```
personas/plugins/personas-mesh/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── CLAUDE.md
├── bin/
│   ├── render-config           # template → file using pass + node env
│   ├── sync-persona            # single-persona pull/commit/push
│   └── sync-all                # iterate N persona dirs
├── hooks/
│   ├── session-start.sh        # git pull for the invoked persona
│   └── stop.sh                 # commit + push with amend-if-recent logic
├── skills/
│   ├── setup/                  # one-shot bootstrap for a new node
│   ├── mesh-doctor/            # diagnose + resolve sync conflicts
│   └── status/                 # show per-persona sync state across nodes
├── systemd/
│   ├── personas-mesh-wsl.service
│   ├── personas-mesh-wsl.timer
│   ├── personas-mesh-windows-bridge.service
│   ├── personas-mesh-windows-bridge.timer
│   ├── personas-mesh-hetzner.service      # installed on Hetzner host
│   └── personas-mesh-hetzner.timer
└── templates/
    ├── .gitattributes          # merge=union rules applied to every persona
    ├── .gitignore.additions    # entries added to each persona's .gitignore
    ├── .mcp.json.template      # default template (personas can override)
    └── settings.local.json.template
```

Skills overview:
- **`setup`** — install personas-mesh on the current node. WSL/Windows-bridge/Hetzner-host variants detected automatically. Sets origin remotes, installs hooks into each persona, installs systemd units, renders configs first time.
- **`mesh-doctor`** — diagnose a sync issue: check remote reachability, show divergent commits, walk through conflict resolution. (Namespaced to avoid collision with Claude Code's built-in `/doctor`.)
- **`status`** — quick table: per-persona, last-sync-ts from WSL / Windows / Hetzner, pending commits, dirty files.

## Prerequisites (verify before step 1)

- Tailscale active on WSL and on `cloud` (verified: `tailscale status` lists cloud; `ssh wils@cloud echo ok` returns `ubuntu-4gb-ash-1`).
- `pass` contains all per-persona tokens. Verified present: `bridgey/token-{bob,julia,mila,nara,warren}`, `discord/{bob,julia,mila}-bot-token`. Templates must fail loudly if a referenced secret is missing.
- GitHub repos `kickinrad/{persona}` are confirmed private (re-verify before pushing templates that reference secret *names*).
- Hetzner sudo access for `wils` is interactive-only (user in `sudo` group; `sudo -n` fails). Phase 0 bootstrap steps that need sudo (mkdir under `/srv`, install systemd units, install `bin/` scripts into `/usr/local/bin`) must be run by Wils interactively on the host. Document the exact commands; do not attempt to execute them from this session.
- Non-interactive checks possible from this session: `ssh wils@cloud` for user-owned files and reads; Coolify API (`http://cloud:8000/api/v1/*`) for stack state; `pass` once GPG is unlocked.

## Rollout phases

### Phase 0 — Bootstrap Hetzner hub

User-driven on `cloud` (requires interactive sudo). A runbook is shipped at `plugins/personas-mesh/docs/hetzner-bootstrap.md`.

1. SSH to Hetzner: `ssh wils@cloud`.
2. `sudo mkdir -p /srv/personas /srv/personas-work && sudo chown wils:wils /srv/personas /srv/personas-work`.
3. For each of the 10 personas, `git clone --bare https://github.com/kickinrad/{p}.git /srv/personas/{p}.git`.
4. Install `sync-persona` + `sync-all` to `/usr/local/bin/` (copied from `plugins/personas-mesh/bin/` via rsync-over-ssh from WSL).
5. Install `personas-mesh-hetzner.{service,timer}` user units; `systemctl --user enable --now personas-mesh-hetzner.timer`.
6. For each persona, `git clone /srv/personas/{p}.git /srv/personas-work/{p}`.
7. Add GitHub mirror remote to each bare repo and install the hourly mirror cron.
8. Permission check: confirm the docker user that runs `bridgey-{p}` containers can read `/srv/personas-work/{p}` (Coolify runs as root → no issue; note anyway).

### Phase 1 — Pilot with `archer` (laptop-only sync)

Chosen because Archer is not deployed to Hetzner → safest blast radius; validates the laptop-side mesh in isolation from the Coolify stack. Also: the laptop is currently a single symlinked directory, so Phase 1 exercises only WSL↔hub sync (CoWork sees the same files for free until the symlink is broken in Phase 4).

1. On WSL: `git -C ~/.personas/archer remote set-url origin ssh://wils@cloud/srv/personas/archer.git` (also add `github` as a second remote pointing at the original GitHub URL).
2. Push current working tree to the new origin.
3. Install hooks + `.gitattributes` + templates in the Archer repo. Commit.
4. Run `personas-mesh:setup` on WSL — installs the hook references, the `.zshrc` source line (if missing), and the WSL watchdog systemd timer. Verifies with a test write + sync round trip.
5. Exercise: make a memory edit from a WSL session, confirm it lands in the Hetzner bare repo within 10 minutes. Leave the pilot running 24h.

### Phase 2 — Add the Hetzner dimension with `julia`

Chosen because Julia is a live Discord bot — exercises the always-on write path. The Coolify stack must be edited.

1. Bootstrap Julia on the hub: `/srv/personas/julia.git` + `/srv/personas-work/julia` (from Phase 0).
2. Migrate Julia's laptop remote to `ssh://wils@cloud/srv/personas/julia.git`; push.
3. **Coolify stack edit (via API or UI)** — modify `bridgey-personas` compose for the `bridgey-julia` service:
   - `volumes: - '/opt/bridgey/personas/julia:/workspace:ro'` → `- '/srv/personas-work/julia:/workspace:rw'`
   - If taking the sidecar-rsync path instead: keep `:ro`, add a second mount `/srv/personas-work/julia/user/memory:/data/bridgey/memory:rw`, and leave the rest alone.
4. Redeploy the service (Coolify handles `pull_policy: never` — no image rebuild).
5. Verify: have Julia converse in Discord, confirm a new memory file appears in `/srv/personas-work/julia/user/memory/` within 2 min, and propagates to laptop on next session pull.
6. Choose between "rw workspace" and "sidecar rsync" based on whether any bot write accidentally mutates `CLAUDE.md` / `skills/`. Sidecar is safer; rw is simpler. Decide and document.
7. Monitor 24h.

### Phase 3 — Fleet roll

Batch-apply Phase 1/2 logic to the remaining 8 personas:
- Laptop-only (Phase 1 pattern): Archer, Kai, Piper, Reed, Urza.
- Laptop + Hetzner (Phase 2 pattern): Bob, Mila, Nara, Warren — all bridgey-deployed, same stack edit needed.

Can be semi-automated with `personas-mesh:setup --all` once Phases 1–2 validate the pattern.

### Phase 4 — Cleanup and symlink break

The WSL↔Windows separation is deliberate and happens LAST, after mesh sync is proven. This is the destructive step and should only run when the hub + WSL sync loop has run clean for a full week.

1. **Quiesce**: ensure all personas are at a clean commit on `cloud` (`personas-mesh:status` shows all green). Stop the CoWork Windows app.
2. **Break the symlink**:
   - `rm ~/.personas` (symlink pointer, not the data on `/mnt/c/`)
   - `mkdir ~/.personas`
   - `touch ~/.personas/.aliases.sh`  (or restore from git)
   - For each persona: `git clone ssh://wils@cloud/srv/personas/{p}.git ~/.personas/{p}` → fresh WSL-native copy pulled from the hub, not the old Windows copy (avoids carrying any mid-sync state).
   - Source `~/.personas/.aliases.sh` from `~/.zshrc` if not already.
3. **Rebuild settings.local.json**: run a migration script that writes `autoMemoryDirectory: /home/wilst/.personas/{p}/user/memory` to each WSL-side `settings.local.json`. (Currently 6 of 10 point at `/mnt/c/...` — Bob, Julia, Kai, Mila, Nara, Warren. 4 already correct — Archer, Piper, Reed, Urza.)
4. **Windows-side bridge on**: enable the `personas-mesh-windows-bridge.timer` systemd unit (previously shipped disabled). Now `/mnt/c/Users/wilst/.personas/*/` — the old Windows-native copy — becomes an independent node syncing to the hub on the 3-min cadence. CoWork continues reading and writing Windows-side; its writes reach the hub within 3 min and the laptop within 10 min of the next WSL session pull.
5. Deprecate any ad-hoc manual sync docs that are now superseded.

## Out of scope

- Replacing GitHub as the public backup target. GitHub stays as async mirror; switching to a different git host is a separate decision.
- Syncing persona *code* (this plugin's own source) — that belongs to normal development of the `personas` repo.
- Multi-user personas. The design assumes one user (Wils) across N nodes. Extending to shared ownership would need ACLs and identity on the hub.
- Encrypting the tailnet traffic further. Tailscale already provides WireGuard-level encryption end-to-end; no additional layer needed.

## Open questions to resolve at implementation time

1. **Systemd vs cron on WSL**: WSL2 has systemd running (verified — `--user` timers exist for `launchpadlib-cache-clean` and `weekly-audit`). Systemd user timers are the default; fall back to `~/.config/cron` only if they prove flaky.
2. **Tailscale SSH auth for the Hetzner host user**: `ssh wils@cloud echo ok` works today (verified). Need to confirm whether a persona's SessionStart hook invoking `git pull ssh://wils@cloud/...` will use the same ssh auth path without an interactive prompt — likely yes (ssh-agent forwarding via Tailscale), but test before wiring the hook.
3. **Hetzner memory-write path for Phase 2** — "rw workspace" vs "sidecar rsync":
   - rw workspace: bot writes auto-memory directly into `/srv/personas-work/{p}/user/memory/`; simple, single source of truth, but risks accidental mutations to `CLAUDE.md` / `skills/` / `tools/`.
   - sidecar rsync: bot writes to `/data/bridgey/memory/` (docker volume); host cron rsyncs → git-tracked tree; preserves read-only guarantee; adds one moving part.
   - Decide during Phase 2 pilot. Default lean: sidecar (safer for long-running bots).
4. **Coolify API stack edit vs UI edit**: the `docker_compose_raw` can be patched via `PATCH /api/v1/services/{uuid}` in theory, but redeployment is what activates changes. Verify whether API redeploy works without UI interaction, otherwise script+copy-paste into UI.
5. **Private-repo confirmation**: re-verify `gh repo view kickinrad/{p} --json visibility` returns `PRIVATE` for all 10 before pushing `.mcp.json.template` / `settings.local.json.template` that reference secret *names* (`pass show bridgey/token-{p}` etc).

## Success criteria

- Making a memory edit on any node is visible on every other node within 3 minutes (2 min for bot personas).
- Zero manual `git push` / `git pull` commands during normal use.
- A lost laptop connection does not cause any data loss or unrecoverable conflict — reconnect just resumes sync.
- No secret ever committed to a repo; rotating a secret is a single `pass` edit that propagates on next persona invocation.
- A persona running concurrently on Hetzner (bot) and WSL (interactive) merges cleanly; only `user/memory/MEMORY.md` and `user/profile.md` ever need union-merge, and those merges happen automatically.
