---
name: install
description: Add a visual dashboard to a persona — HTML dashboard, task tracking, and browser launcher. Use when the user asks to add a dashboard, set up a dashboard, create a task board, or wants visual status for a persona.
disable-model-invocation: true
triggers:
  - dashboard
  - add a dashboard
  - set up dashboard
  - create a dashboard
  - persona dashboard
  - task board
  - visual status
---

# Persona Dashboard (Expansion Pack)

An optional expansion pack that adds a visual HTML dashboard to any persona. Install this into a persona when the user asks for it — it's not included by default.

## When to Use a Dashboard

Good candidates: personas with rich ongoing data, task tracking, or regular review cycles.
Skip for: simple personas (one-off advice, single-skill tools).

## Files to Create

### 1. TASKS.md

Create in the persona root. This is the task tracking file the dashboard reads:

```markdown
# Tasks

## Active
- [ ] **Task title** — context, due [date]

## Waiting On
- [ ] **Waiting on X** — since [date]

## Someday

## Done
- [x] ~~Completed task~~ ([date])
```

### 2. dashboard.html

Copy the template from `assets/dashboard.html` in this skill's directory to the persona root. Then customize:

- Update the page title to match the persona name
- Adjust tab labels if needed (default: Tasks, Profile, Memory, System)
- The template reads: `TASKS.md`, `profile.md`, `MEMORY.md`, `CLAUDE.md`

The dashboard is a single-file HTML app served by a local Python HTTP server. It uses `fetch()` to load markdown files and renders them as formatted cards.

### 3. open.sh

Create in the persona root:

```bash
#!/bin/bash
PERSONA_DIR="$HOME/.personas/{name}"
PORT={unique-port}

cd "$PERSONA_DIR"
pkill -f "python3 -m http.server $PORT" 2>/dev/null
python3 -m http.server "$PORT" &
sleep 0.5

# WSL-compatible browser open
if command -v explorer.exe &>/dev/null; then
  explorer.exe "http://localhost:$PORT/dashboard.html"
elif command -v xdg-open &>/dev/null; then
  xdg-open "http://localhost:$PORT/dashboard.html"
elif command -v open &>/dev/null; then
  open "http://localhost:$PORT/dashboard.html"
fi
```

Make it executable: `chmod +x open.sh`

Use a unique port per persona to avoid collisions (pick from 7300-7399 range).

## Dashboard Design Principles

- **Single HTML file** — no build tools, no dependencies
- **Reads markdown files** via `fetch()` from the local HTTP server
- **Tabs**: Tasks (parses TASKS.md into cards), Profile, Memory, System
- **Clean, readable design** — prioritize scannability over decoration
- **Responsive** — works in any browser window size
- **Tasks tab**: Parse TASKS.md sections into card grids with status indicators

## Suggested Tab Customization

Adapt tabs to the persona's domain:

| Domain | Suggested tabs |
|--------|---------------|
| Finance | Priorities, Profile, Memory, System |
| Life system | Today, Briefing, Profile, Memory |
| Creative | Priorities, Content, Profile, Memory |
| Health | Today, Progress, Profile, Memory |

## CLAUDE.md Updates

After installing the dashboard, update the persona's CLAUDE.md:

1. Add a note about `TASKS.md` under the Skills or Important Rules section (e.g., "Update TASKS.md when tasks change")
2. Add `open.sh` reference to Session Start (optional — "run `bash open.sh` to launch dashboard")

## After Adding

Commit the new files: `feat({name}): add dashboard expansion pack`
