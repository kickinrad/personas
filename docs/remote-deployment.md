# Remote Deployment

Personas can run on remote servers for scheduled, autonomous tasks — weekly financial reviews, daily meal plans, morning briefings. This guide covers setup, scheduling, and keeping local and remote in sync.

## Prerequisites

- SSH access to a remote server
- Claude Code installed and authenticated on the remote server
- `rsync` available on both local and remote machines
- Tailscale recommended for secure, zero-config networking

## Architecture

```
Local Machine                    Remote Server
┌──────────────────┐            ┌──────────────────┐
│ plugins/warren/  │   rsync    │ ~/.personas/     │
│   CLAUDE.md      │ ────────→  │   warren/        │
│   skills/        │            │     CLAUDE.md    │
│   profile.md     │            │     skills/      │
│   .mcp.json      │            │     profile.md   │
│                  │            │     .mcp.json    │
│                  │  ← rsync   │     .claude/     │
│   .claude/memory │ ←────────  │       memory/    │
└──────────────────┘            └──────────────────┘
                                      ↑
                                   scheduler MCP
                                   runs scheduled
                                   prompts
```

The remote server runs personas on a schedule via the home-scheduler MCP server (SQLite-backed, with execution history and concurrency control). Memory syncs back to your local machine so you can see what the persona learned.

## Using persona-manager:deploy

The easiest way to deploy:

```bash
persona-manager "deploy warren to my cloud server"
```

This interactive skill will:
1. Ask which persona and which host
2. Sync the workspace via rsync
3. Verify Claude Code works on the remote
4. Set up scheduled tasks via scheduler MCP (or crontab fallback)
5. Optionally configure memory sync back to local

## Manual Setup

### Step 1: Sync the Persona

```bash
rsync -avz \
  --exclude='.claude/memory/' \
  plugins/warren/ \
  remote-host:~/.personas/warren/
```

Memory is excluded by default — the remote instance builds its own context. Include it with `--include='.claude/memory/'` if you want continuity.

**Important:** Include `profile.md` and `.mcp.json` in the sync. These are gitignored but needed on the remote. Make sure API keys in `.mcp.json` are valid for the remote environment.

### Step 2: Verify Remote Setup

```bash
# Check Claude Code is installed
ssh remote-host 'which claude && claude --version'

# Check persona files landed
ssh remote-host 'ls ~/.personas/warren/CLAUDE.md'

# Test a session
ssh remote-host 'cd ~/.personas/warren && claude \
  --mcp-config .mcp.json \
  --strict-mcp-config \
  -p "confirm you can access your tools and profile"'
```

### Step 3: Set Up Scheduled Tasks

#### Option A: Scheduler MCP (Recommended)

The home-scheduler MCP server provides SQLite-backed execution history, concurrency control (max 3 parallel), and conversational schedule management. Ensure it's running on the remote server (`~/projects/personal/home-base/services/home-scheduler`).

Use `scheduler_add_claude_trigger` to create scheduled tasks:

```
Tool: scheduler_add_claude_trigger
Arguments:
  name: "warren-weekly-review"
  prompt: "weekly review"
  schedule: "0 9 * * 1"
  runtime_dir: "~/.personas/warren"
```

Manage schedules conversationally:

```
scheduler_list_triggers          # See all scheduled tasks
scheduler_get_executions         # View execution history
scheduler_update_trigger         # Modify schedule or prompt
scheduler_disable_trigger        # Pause without deleting
```

#### Option B: Raw Crontab (Fallback)

If the scheduler is not available, use crontab directly:

```bash
ssh remote-host 'crontab -l 2>/dev/null; echo "0 9 * * 1 cd ~/.personas/warren && claude --mcp-config .mcp.json --strict-mcp-config -p \"weekly review\""' | ssh remote-host 'crontab -'
```

#### Common Schedules

| Schedule | Cron Expression | Use Case |
|----------|----------------|----------|
| Weekday mornings 9 AM | `0 9 * * 1-5` | Daily briefings |
| Monday mornings 9 AM | `0 9 * * 1` | Weekly reviews |
| First of month 9 AM | `0 9 1 * *` | Monthly snapshots |
| Weekday evenings 5 PM | `0 17 * * 1-5` | End-of-day summaries |

### Step 4: Set Up Memory Sync (Optional)

Pull remote memory back to your local machine on a schedule:

```bash
# Add to local crontab
0 */6 * * * rsync -avz remote-host:~/.personas/warren/.claude/memory/ ~/personas/plugins/warren/.claude/memory/
```

This runs every 6 hours and pulls any new memory entries. You can review what the persona learned remotely by reading the memory files locally.

## Safety Model

Remote personas run with the same sandbox that protects local sessions:

### Sandbox Isolation

The `.claude/settings.json` file (committed to git, synced to remote) restricts:
- **Filesystem:** Write access only to the persona's own directory
- **Network:** Only whitelisted domains (defined per persona)
- **No access to:** `~/.aws`, `~/.ssh`, `~/.gnupg`, parent directories, other personas

### Autonomy Flags

Remote scheduled tasks run with:
- `--mcp-config .mcp.json` — only the persona's configured MCP servers
- `--strict-mcp-config` — blocks any global MCP servers

The persona operates within its sandbox even when running unattended. It can write to its own directory (memory, docs, scripts) but cannot escape its boundary.

### What Remote Personas Can Do

| Action | Allowed |
|--------|---------|
| Read own profile.md and CLAUDE.md | Yes |
| Write to own memory | Yes |
| Call whitelisted MCP servers | Yes |
| Write to own docs/ or scripts/ | Yes |
| Access other personas | No |
| Access system credentials | No |
| Make network calls to non-whitelisted domains | No |

## Monitoring

### Check Execution History (Scheduler)

If using the scheduler MCP, check execution history directly:

```
Tool: scheduler_get_executions
Arguments:
  trigger_name: "warren-weekly-review"
  limit: 10
```

This shows status, duration, and output for recent runs — no log scraping needed.

### Check Cron Logs (Fallback)

If using raw crontab:

```bash
ssh remote-host 'grep -i "personas\|claude" /var/log/syslog | tail -20'
```

### Check Memory for Activity

```bash
ssh remote-host 'cat ~/.personas/warren/.claude/memory/MEMORY.md | tail -30'
```

### Check for Errors

```bash
# Redirect cron output to a log file for debugging
ssh remote-host 'crontab -l'
# Modify to add logging:
# 0 9 * * 1 cd ~/.personas/warren && claude ... >> ~/.personas/warren/cron.log 2>&1
```

## Troubleshooting

### Claude Code not found on remote

Make sure Claude Code is in the remote user's PATH. If installed via npm:
```bash
ssh remote-host 'export PATH="$HOME/.local/bin:$PATH" && which claude'
```

Add the PATH export to the cron entry if needed:
```
0 9 * * 1 export PATH="$HOME/.local/bin:$PATH" && cd ~/.personas/warren && claude ...
```

### MCP server fails on remote

- Check that MCP server packages are installed on the remote: `ssh remote-host 'npx -y @package/name --version'`
- Verify API keys in `.mcp.json` are valid for the remote environment
- Check network access — some APIs restrict by IP

### Memory sync conflicts

If both local and remote write to the same memory file, rsync may overwrite entries. Options:
- Use `--append` flag for append-only sync
- Keep remote memory separate and review manually
- Sync one direction only (remote → local)

### Tailscale connection

If using Tailscale for SSH:
```bash
# Check Tailscale status on remote
ssh remote-host 'tailscale status'

# Use Tailscale hostname
rsync -avz plugins/warren/ cloud:~/.personas/warren/
```

## Next Steps

- [Getting Started](getting-started.md) — Set up personas locally first
- [Self-Improvement](self-improvement.md) — Understand how remote personas evolve autonomously
