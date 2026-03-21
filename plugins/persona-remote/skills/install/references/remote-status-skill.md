---
name: remote-status
description: Check the health and status of the remote persona deployment. Use when the user says "remote status", "check remote", "is my persona running", "server status", or runs /remote-status.
triggers:
  - remote status
  - check remote
  - is my persona running
  - server status
  - remote health
---

# Remote Status

Check the health of the remote persona deployment at `{tailscale_host}`.

## What to Check

Run these commands via SSH and report results:

### 1. Container status

```bash
ssh {tailscale_host} "docker ps --filter name=persona-{name} --format '{{.Status}}'"
```

Report: running/stopped, uptime.

### 2. Disk usage

```bash
ssh {tailscale_host} "df -h /opt/personas/{name} | tail -1"
```

Report: used/available space.

### 3. Last activity

```bash
ssh {tailscale_host} "find {remote_path}/user/memory -name '*.md' -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1"
```

Report: last memory file modification time (proxy for last persona activity).

### 4. Container logs (recent)

```bash
ssh {tailscale_host} "docker logs persona-{name} --tail 10 2>&1"
```

Report: last 10 lines of container output.

## Output Format

Present as a concise status report:
- Container: running/stopped (uptime)
- Disk: X used / Y available
- Last activity: timestamp
- Recent logs: summary of last entries
