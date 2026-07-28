---
name: install
description: Use when the user asks to install a read-only visual dashboard for a persona or browse its profile, memory index, and operating instructions in a browser. NOT for tasks, calendars, project tracking, or action capture; those remain in their canonical systems.
---

# Install the persona dashboard

Install this optional, read-only viewer into one persona home.

1. Confirm the target contains `CLAUDE.md` and `user/profile.md`.
2. Copy `assets/dashboard.html` to the persona root and replace
   `{PersonaName}` with the display name.
3. Create `open-dashboard.sh` with the persona's resolved absolute path and a
   free port from 7300–7399:

```bash
#!/bin/bash
set -euo pipefail
PERSONA_DIR="/resolved/persona/path"
PORT={unique-port}
cd "$PERSONA_DIR"
python3 -m http.server "$PORT" &
if command -v explorer.exe &>/dev/null; then
  explorer.exe "http://localhost:$PORT/dashboard.html"
elif command -v xdg-open &>/dev/null; then
  xdg-open "http://localhost:$PORT/dashboard.html"
elif command -v open &>/dev/null; then
  open "http://localhost:$PORT/dashboard.html"
fi
```

4. Make the launcher executable and open the dashboard once.
5. Verify every tab is a read-only fetch of `user/profile.md`,
   `user/memory/MEMORY.md`, or `CLAUDE.md`.

The plugin creates no action record and writes no persona knowledge. Google
Tasks owns actions, Google Calendar owns time, and Obsidian owns projects and
durable knowledge. A dashboard request that needs any of those sources must
read them through their canonical service rather than mirror them locally.
