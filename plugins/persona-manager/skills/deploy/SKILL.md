---
name: deploy
description: Deploy a persona to a remote server for scheduled autonomous execution. Use when user wants to run personas on a remote machine, set up cron jobs, or sync persona workspaces to a server.
---

# Deploy Persona to Remote Server

## Prerequisites

- Remote server accessible via SSH (ideally via Tailscale)
- Claude Code installed on remote server
- rsync available on both machines

## Workflow

### Step 1: Identify Target

Ask which persona and which remote host:
- Persona directory (e.g., plugins/warren/ or ~/.personas/warren/)
- Remote host (e.g., cloud via Tailscale, or full SSH address)

### Step 2: Sync Workspace

```bash
rsync -avz --exclude='.claude/memory/' {persona_dir}/ {host}:~/.personas/{name}/
```

Note: Exclude memory by default (remote builds its own). Include if user wants continuity.

### Step 3: Verify Remote Setup

```bash
ssh {host} 'which claude && claude --version'
ssh {host} 'ls ~/.personas/{name}/CLAUDE.md'
```

### Step 4: Set Up Scheduled Tasks

For each skill that should run on a schedule:

```bash
ssh {host} "crontab -l 2>/dev/null; echo '{schedule} cd ~/.personas/{name} && claude --setting-sources project --dangerously-skip-permissions -p \"{prompt}\"'" | ssh {host} 'crontab -'
```

Common schedules:
- `0 9 * * 1-5` — weekday mornings at 9 AM
- `0 9 * * 1` — Monday mornings at 9 AM
- `0 17 * * 1-5` — weekday evenings at 5 PM

### Step 5: Test Run

```bash
ssh {host} "cd ~/.personas/{name} && claude --setting-sources project --dangerously-skip-permissions -p 'confirm you can access your tools and profile'"
```

### Step 6: Set Up Memory Sync (Optional)

Add local cron to pull memory updates:

```bash
0 */6 * * * rsync -avz {host}:~/.personas/{name}/.claude/memory/ {persona_dir}/.claude/memory/
```
