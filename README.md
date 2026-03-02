# kickinrad/personas

> Private monorepo for persistent, personal AI assistants built on Claude Code. Each persona lives directly in this repo — edit and go.

```
$ luna "good morning"

🌙 Good morning! Let me pull your day together...

🌤  Weather   — 62°F, partly cloudy. Light jacket weather.
📅  Calendar  — 10am standup, 2pm 1:1 with Marco
✅  Tasks     — 3 due today: Review PR #47, Call insurance, Groceries
📝  Big 3     — From last night: ship auth refactor, gym, newsletter draft

Energy check: how are you feeling today?
```

---

## How It Works

Personas are Claude Code plugins. Each one is three layers stacked together:

| Layer | File | What it is |
|-------|------|------------|
| **Personality** | `plugins/{name}/CLAUDE.md` | Role, skills, rules — committed |
| **Context** | `plugins/{name}/profile.md` | Your personal data — gitignored |
| **Memory** | `plugins/{name}/.claude/memory/` | Auto-written by Claude across sessions — gitignored |

Each persona activates only when its working directory is `plugins/{name}/` — no global state bleed, no shared context.

---

## Structure

```
personas/
├── .gitignore                    ← covers profile.md, .mcp.json, .claude/, *.db, *.log
├── plugins/
│   ├── persona-manager/          ← scaffolding tool (user-scoped install)
│   ├── luna/                     ← life assistant
│   │   ├── CLAUDE.md             ← committed
│   │   ├── skills/               ← committed
│   │   ├── profile.md.example    ← committed template
│   │   ├── profile.md            ← gitignored (your personal data)
│   │   ├── .mcp.json             ← gitignored (MCP server config)
│   │   └── .claude/              ← gitignored (settings + memory)
│   ├── julia/   (same structure)
│   ├── warren/  (same structure)
│   └── mila/    (same structure)
└── tests/
    └── personas-test.sh
```

---

## Setup (new machine)

### 1. Clone

```bash
git clone git@github.com:kickinrad/personas.git ~/projects/personal/personas
```

### 2. Add shell functions

Add to `~/.config/zsh/.personas.zsh` (or equivalent):

```bash
_PERSONAS_ROOT="$HOME/projects/personal/personas/plugins"

for _p_dir in "$_PERSONAS_ROOT"/*/; do
  [[ -d "$_p_dir" ]] || continue
  _p_name=$(basename "$_p_dir")
  [[ "$_p_name" == "persona-manager" ]] && continue
  [[ -f "${_p_dir}CLAUDE.md" ]] || continue

  if [[ ! -f "${_p_dir}.mcp.json" ]]; then
    printf '{\n  "mcpServers": {}\n}\n' > "${_p_dir}.mcp.json"
  fi

  eval "${_p_name}() {
    if [[ \$# -gt 0 ]]; then
      (cd \"${_p_dir}\" && claude \
        --mcp-config \"${_p_dir}.mcp.json\" \
        --strict-mcp-config \
        -p \"\$*\")
    else
      (cd \"${_p_dir}\" && claude \
        --mcp-config \"${_p_dir}.mcp.json\" \
        --strict-mcp-config)
    fi
  }"
done
unset _PERSONAS_ROOT _p_dir _p_name
```

Then `source ~/.config/zsh/.personas.zsh` (or open a new terminal).

### 3. Register plugins

Update `~/.claude/plugins/installed_plugins.json` — each persona needs a local entry pointing to its plugin dir. Example for luna:

```json
"luna@personas": [{
  "scope": "local",
  "projectPath": "/home/wilst/projects/personal/personas/plugins/luna",
  "installPath": "/home/wilst/projects/personal/personas/plugins/luna",
  "version": "local",
  "installedAt": "2026-02-25T19:44:33.119Z",
  "lastUpdated": "2026-03-02T00:00:00.000Z"
}]
```

### 4. Create private data files

Copy the example and fill in your details:

```bash
cp plugins/luna/profile.md.example plugins/luna/profile.md
# Edit profile.md — add your name, location, and context
```

Create `.claude/settings.local.json` per persona (controls which MCP servers and plugin are active):

```json
{
  "enabledPlugins": { "luna@personas": true },
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["calendar", "tasks"]
}
```

### 5. Use

```bash
luna          # open interactive session
luna "hi"     # one-shot prompt
```

---

## Day-to-Day

**Edit and immediately use** — no install, no update, no cache. Just:

```bash
# Edit a persona
code ~/projects/personal/personas/plugins/luna/CLAUDE.md

# Use it (picks up changes immediately)
luna
```

**Add a new skill:**

```bash
mkdir -p plugins/luna/skills/my-skill
# Create SKILL.md with YAML frontmatter
git add plugins/luna/skills/my-skill/SKILL.md
git commit -m "feat(luna): add my-skill"
```

---

## Included Personas

| Persona | Role | Skills |
|---------|------|--------|
| **luna** 🌙 | Life assistant | morning briefing, brain dump, evening shutdown, stuck mode |
| **julia** 👩‍🍳 | Personal chef | meal planning, pantry, grocery lists |
| **warren** 📊 | Personal CFO | weekly review, budget health, net worth, trading review |
| **mila** ✨ | Brand strategist | content planning, agency growth, music career, writing, quarterly goals |
