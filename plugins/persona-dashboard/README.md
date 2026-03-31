# Persona Dashboard

Expansion pack that adds a visual HTML dashboard to any persona.

## What It Does

Installs a self-contained HTML dashboard into a persona's workspace with:
- **Task tracking** — manage ongoing work and goals
- **Profile viewer** — quick reference to user context from `user/profile.md`
- **Memory browser** — browse session learnings from `user/memory/`
- **System overview** — persona config, hooks status, MCP connections

The dashboard is a single HTML file — no build step, no dependencies. Open it in any browser.

## Installation

From within any persona session:

```
install the dashboard expansion pack
```

Or invoke the skill directly:

```
Skill('persona-dashboard:install')
```

This copies the dashboard HTML and an `open.sh` launcher into the persona's workspace.

## Usage

After installation:

```bash
# From the persona directory
bash open.sh          # Opens dashboard in default browser
```

Or open `dashboard.html` directly in any browser.

## Requirements

- An existing persona created with persona-dev
- A web browser (for viewing the dashboard)
