---
name: sync
description: Sync persona files between local and remote server. Use when the user says "sync", "push to remote", "pull from remote", "sync persona", or runs /sync.
triggers:
  - sync
  - sync push
  - sync pull
  - push to remote
  - pull from remote
  - sync persona
---

# Remote Sync

Bidirectional rsync between local persona and remote deployment at `{tailscale_host}:{remote_path}`.

## Usage

- `/sync push` — local → remote (config, skills, CLAUDE.md changes)
- `/sync pull` — remote → local (memory, outputs, learnings)
- `/sync` — bidirectional (push then pull)

## Commands

### Push (local → remote)

Push local config/skills/rules to the remote server. Excludes runtime data.

```bash
rsync -avz --delete \
  --exclude='.git/' \
  --exclude='.mcp.json' \
  --exclude='*.log' \
  --exclude='*.db' \
  --exclude='*.db-journal' \
  --exclude='user/memory/' \
  ~/.personas/{name}/ {tailscale_host}:{remote_path}/
```

After pushing, restart the container to pick up changes:

```bash
ssh {tailscale_host} "cd /opt/personas && docker compose restart persona-{name}"
```

### Pull (remote → local)

Pull memory and outputs from the remote server. Only syncs `user/memory/`.

```bash
rsync -avz \
  {tailscale_host}:{remote_path}/user/memory/ \
  ~/.personas/{name}/user/memory/
```

### Bidirectional

Run push then pull in sequence.

## Important

- `.mcp.json` is NEVER synced (contains API keys, differs per environment)
- `.git/` is never synced
- Push excludes `user/memory/` (remote writes there, local pulls it)
- After push, container restart is needed for the persona to see changes
