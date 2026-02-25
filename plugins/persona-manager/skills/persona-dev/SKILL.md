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

Skills activate via **local-scope plugin install** — no `--plugin-dir` needed:

```bash
# One-time setup per persona workspace
mkdir -p ~/.personas/luna
cd ~/.personas/luna
claude plugin install luna@kickinrad/personas --scope local
# Writes: ~/.personas/luna/.claude/settings.local.json
```

Skills only activate when CWD is `~/.personas/{name}/` — native isolation, no bleed.

Workspace layout (auto-bootstrapped by .zshrc on shell reload after plugin install/update):
- `~/.personas/{name}/CLAUDE.md` → symlink → plugin cache (auto-updates on `/plugin update`)
- `~/.personas/{name}/skills/` → symlink → plugin cache skills/
- `~/.personas/{name}/.mcp.json` → local only, fill in credentials, never committed
- `~/.personas/{name}/.claude/settings.local.json` → written by `plugin install --scope local`

If previously installed at user scope: `claude plugin uninstall {name}@kickinrad/personas` first.

## CLI Aliases

Auto-discovered from plugin cache via `.zshrc` loop. Shell function per persona:

```bash
luna() {
  (cd "$HOME/.personas/luna" && claude \
    --mcp-config "$HOME/.personas/luna/.mcp.json" \
    --strict-mcp-config \
    "$@")
}
```

`luna` → interactive session with Luna's MCP only. `luna "good morning"` → one-shot.
`--strict-mcp-config` blocks global MCP servers from leaking into persona sessions.

## Version Bumping

Bump in BOTH `plugin.json` AND `marketplace.json` before every commit.
Patch for skill/doc changes, minor for new skills, major for breaking changes.
