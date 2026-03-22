# bridgey-deploy Migration Design

> Merge remote persona deployment into Bridgey's marketplace. Deprecate and remove `persona-remote` from the personas framework.

## Problem

Two plugins compete for "remote persona deployment":

- **persona-remote** (personas framework) — fully designed but never deployed. Handles server setup, Docker, file sync, container lifecycle.
- **bridgey** (standalone repo) — designed for A2A communication but ended up building its own deployment pipeline on Coolify because it needed running remote agents.

The result: Coolify runs Bridgey containers that mount persona workspaces, but there's no sync mechanism, no update path, and no clear ownership of the deployment layer.

## Decision

**Merge persona-remote into Bridgey as `bridgey-deploy`.** Rationale:

1. Remote personas and Bridgey are almost always used together. Users who deploy personas remotely want A2A communication; users who want A2A need remote agents running.
2. Bridgey is general-purpose A2A for Claude Code. Non-persona users install just `bridgey`. Persona users who want remote deployment install `bridgey-deploy` alongside it.
3. The existing Coolify deployment already follows this pattern — containers run Bridgey daemons with persona workspaces mounted.

## New Bridgey Marketplace Structure

```
kickinrad/bridgey/
├── plugins/
│   ├── bridgey/              # Core A2A — daemon, MCP tools, discovery, Tailscale mesh
│   │   └── v0.5.0
│   ├── bridgey-deploy/       # Remote deployment — Docker, sync, Coolify integration
│   │   └── v0.1.0
│   └── bridgey-discord/      # Discord transport adapter
│       └── v0.1.0
└── .claude-plugin/marketplace.json
```

| Plugin | Responsibility | Depends on |
|--------|---------------|------------|
| `bridgey` | A2A protocol, daemon, MCP tools, agent discovery, Tailscale mesh | Nothing |
| `bridgey-deploy` | Remote deployment, file sync, container lifecycle, Coolify API | `bridgey` (peer) |
| `bridgey-discord` | Discord bot transport | `bridgey` (peer) |

## bridgey-deploy Plugin Design

### Skills

```
plugins/bridgey-deploy/
├── .claude-plugin/plugin.json
├── skill-rules.json
├── skills/
│   ├── deploy/
│   │   ├── SKILL.md                    # Adaptive deployment walkthrough
│   │   └── references/
│   │       ├── Dockerfile              # Claude Code + Bridgey daemon
│   │       ├── docker-compose.yml      # Template with bridgey env vars
│   │       └── entrypoint.sh           # Starts bridgey daemon as main process
│   ├── sync/
│   │   └── SKILL.md                    # /sync push|pull|both over Tailscale SSH
│   ├── remote-status/
│   │   └── SKILL.md                    # Health checks, disk, logs, last activity
│   └── coolify/
│       └── SKILL.md                    # Coolify API: create service, env vars, deploy, logs
└── hooks/
    └── sync-reminder.json              # SessionEnd hook snippet
```

### Deployment Targets (v1)

| Target | Detection | Support |
|--------|-----------|---------|
| **Docker Compose** | `docker --version` on remote | Baseline — generate docker-compose.yml, user runs `docker compose up` |
| **Coolify** | Ask user for URL + API token | First-class — create/update services, manage env vars, view logs via API |
| **Raw VPS** | SSH access | Walk through Docker install, then Docker Compose path |

Future targets (v2+): Fly.io, Railway, container registries.

The deploy skill detects what's available on the target server and adapts. All Coolify details (URL, API token) are stored in a gitignored config file, nothing hardcoded.

### Container Model

One container per remote agent:

```
┌─────────────────────────────────────────────┐
│  Container: bridgey-{name}                  │
│                                              │
│  entrypoint.sh                               │
│  ├── Generate bridgey.config.json from env  │
│  ├── Start bridgey daemon (main process)    │
│  └── Daemon executes claude -p on messages  │
│                                              │
│  Mounts:                                     │
│  ├── /workspace (ro) ← persona files        │
│  ├── /workspace/user/memory (rw) ← memory   │
│  ├── /home/node/.claude (ro) ← auth         │
│  └── /data/bridgey (rw) ← daemon state     │
└─────────────────────────────────────────────┘
```

Environment variables configure the Bridgey daemon:
- `BRIDGEY_NAME` — agent name
- `BRIDGEY_PORT` — daemon listen port
- `BRIDGEY_TOKEN` — bearer auth token
- `BRIDGEY_AGENTS` — JSON array of known remote agents
- `BRIDGEY_DESCRIPTION` — agent description
- `BRIDGEY_MAX_TURNS` — max agentic turns per inbound message

### Sync Model

rsync over Tailscale SSH (same as original persona-remote design):

| Command | Direction | What |
|---------|-----------|------|
| `/sync push` | local → remote | CLAUDE.md, hooks.json, skills/, .claude-flags, settings |
| `/sync pull` | remote → local | user/memory/, outputs, learnings |
| `/sync` | bidirectional | push then pull |

**Always excluded:** `.git/`, `.mcp.json`, `*.log`, `*.db`, `.credentials.json`

### Coolify Integration

Generic, not tied to any specific instance:

1. `/deploy` skill asks for Coolify URL and API token on first use
2. Stores connection details in `bridgey-deploy.config.json` (gitignored)
3. Uses Coolify API v1 to:
   - Create Docker Compose services
   - Set environment variables
   - Trigger deployments
   - View container logs
   - Check service health
4. Falls back to manual Docker Compose if Coolify is unavailable

### 7-Phase Deploy Walkthrough

Adapted from persona-remote's original design, enhanced with Bridgey integration:

1. **Server Connection** — detect existing or help provision
2. **SSH Access** — key-based auth setup
3. **Server Hardening** — disable password auth, UFW firewall (Tailscale-only)
4. **Tailscale** — install, enable SSH, verify MagicDNS
5. **Docker + Container** — install Docker, build persona+bridgey image
6. **Deploy** — sync files, transfer auth, start container (via Coolify API or docker-compose)
7. **Post-Install** — install /sync + /remote-status skills, create remote alias, store config

## Migration

### In kickinrad/bridgey (Bridgey repo):
- Create `plugins/bridgey-deploy/` with all skills and references
- Move current Coolify entrypoint logic into deploy references
- Update marketplace.json to register bridgey-deploy
- Bump bridgey core to v0.5.0 if headless mode changes needed

### In kickinrad/personas (personas framework):
- Delete `plugins/persona-remote/` entirely
- Remove from `.claude-plugin/marketplace.json`
- Update CLAUDE.md — all references to persona-remote → bridgey-deploy
- Update persona-dev skill — remove persona-remote references, add bridgey-deploy guidance
- Bump persona-manager version (patch)

### In deployed personas:
- Warren: remove `persona-remote@personas` from enabledPlugins, add `bridgey-deploy@bridgey`
- Nara: same
- Bob: add `bridgey-deploy@bridgey` (already has bridgey core)
- Commit + push all affected personas

### On cloud server (existing Coolify deployment):
- Current containers keep running (no disruption)
- Run `/sync push` from each local persona to update remote files to v1.5.0
- Fix bridgey-discord crash (missing DISCORD_BOT_MILA env var)

## Security

Inherits from both projects:

| Layer | Protection |
|-------|-----------|
| Network | Tailscale-only — UFW allows only tailscale0 interface |
| SSH | Key-only auth, password auth disabled |
| Container | Non-root (node:1000), read-only workspace, explicit writable paths |
| Credentials | .credentials.json mounted read-only, never in image, never synced |
| Secrets | .mcp.json excluded from sync, Coolify API token in gitignored config |
| A2A | Bearer tokens, rate limiting, localhost bind by default |

## Open Questions

1. **Bridgey marketplace access from personas:** Personas currently use `extraKnownMarketplaces` for the personas marketplace. They'll need a second entry for `kickinrad/bridgey` to auto-install bridgey-deploy. Should this go in the persona-dev scaffolding (for new personas) and a manual update for existing ones?
2. **Auth token refresh:** Claude Code OAuth tokens expire. Should bridgey-deploy include a reminder/skill to re-sync `.credentials.json`?
3. **Container updates:** When Claude CLI updates, containers need rebuilding. Should `/remote-status` detect outdated versions?

## Supersedes

This design supersedes:
- `2026-03-16-remote-deploy-design.md` — original persona-remote design (absorbed into bridgey-deploy)
- `2026-03-16-remote-deploy.md` — original implementation plan (no longer applicable)
