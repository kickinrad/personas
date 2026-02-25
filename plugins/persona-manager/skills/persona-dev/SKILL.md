---
name: persona-dev
description: Create and manage personas in the kickinrad/personas marketplace
triggers:
  - create a persona
  - new persona
  - add a persona
  - persona development
---

# Persona Development

Personas are Claude Code plugins in `~/projects/personal/personas/plugins/{name}/`.

## Plugin Structure

Each persona contains:
- `.claude-plugin/plugin.json` — metadata (name, version, author, description)
- `CLAUDE.md` — personality, capabilities, MCP tools, communication style, trigger phrases
- `skills/{domain}/{skill-name}/SKILL.md` — skills with YAML frontmatter
- `hooks/hooks.json` + hook scripts — lifecycle hooks (optional)
- `skill-rules.json` — forced-eval triggers (optional)

## Creating a New Persona

Use `Skill('plugin-dev:create-plugin')` to scaffold, then:

1. Write `CLAUDE.md` with: personality, capabilities, MCP tools, communication style
2. Create skills under `skills/{domain}/{skill-name}/SKILL.md`
3. Add entry to `personas/.claude-plugin/marketplace.json`
4. Bump version in both `plugin.json` AND `marketplace.json` (same rule as ez-claude)
5. Push to GitHub — persona-manager bootstraps `~/.personas/{name}/` on next session start

## Runtime Model

- `~/.personas/{name}/CLAUDE.md` → symlink to plugin cache (auto-updates on version bump)
- `~/.personas/{name}/.mcp.json` → local only, fill in once, never committed
- `~/.personas/{name}/.claude/settings.json` → auto-managed by persona-manager

## CLI Aliases

Auto-discovered from `~/.personas/*/` via `.zshrc` loop. No manual alias management.
`luna` → interactive session. `luna "good morning"` → one-shot.

## Version Bumping

Bump in BOTH `plugin.json` AND `marketplace.json` before every commit.
Patch for skill/doc changes, minor for new skills, major for breaking changes.
