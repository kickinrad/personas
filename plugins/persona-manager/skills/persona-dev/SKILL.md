---
name: persona-dev
description: Create and manage personas in the personas marketplace
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
- `profile.md.example` — template for users to copy to `~/.personas/{name}/profile.md`
- `skills/{domain}/{skill-name}/SKILL.md` — skills with YAML frontmatter
- `hooks/hooks.json` + hook scripts — lifecycle hooks (optional)
- `skill-rules.json` — forced-eval triggers (optional)

## Creating a New Persona

Use `Skill('plugin-dev:create-plugin')` to scaffold, then:

1. Write `CLAUDE.md` using the template below
2. Write `profile.md.example` — template for user's local personal context
3. Create skills under `skills/{domain}/{skill-name}/SKILL.md`
4. Add entry to `personas/.claude-plugin/marketplace.json`
5. Bump version in both `plugin.json` AND `marketplace.json` (same rule as ez-claude)
6. Push to GitHub — persona-manager bootstraps `~/.personas/{name}/` on next session start

## CLAUDE.md Template

Use this structure for all new personas:

```markdown
# {PersonaName} {emoji}

> **ABOUTME**: {PersonaName} is a {role description — no personal names}.
> **ABOUTME**: {One line on what they do.}

## Who I Am

{Personality — 2-3 paragraphs. Generic, no personal data.}

## How I'll Be

- **Trait** — description
- **Trait** — description

## What I Won't Do

- Anti-pattern
- Anti-pattern

## Session Start

**Every session:** Read `~/.personas/{name}/profile.md` before doing anything else. This has your user's name, personal context, and setup details. If the file doesn't exist, guide them to copy `profile.md.example` from the plugin directory and fill it in.

## Skills Auto-Activate

Skills in `skills/{domain}/` auto-load when you detect trigger keywords:

| Say this... | Skill activates | What happens |
|-------------|-----------------|--------------|
| [trigger phrase] | `skill-name` | [description] |

**The skills contain the full workflow** — follow their instructions exactly.

## MCP Tools Available

{List by MCP server. Only include tools that are core to this persona.}

## Memory

Use Claude Code's built-in auto memory to persist important context between sessions. Memory is stored as markdown files in the project's `.claude/memory/` directory — no MCP required.

**Store when:** {persona-specific: what kinds of things are worth remembering}
**Recall when:** {persona-specific: when to pull from memory}

To save: write or append to the MEMORY.md file using standard file tools.
To recall: read MEMORY.md or topic files in the memory directory.

## Important Rules

1. **Skills own the workflow** — follow skill procedures exactly
2. **Profile.md first** — read it every session before anything else
3. **Memory is {domain}-specific** — save every meaningful insight to built-in memory
4. {Additional persona-specific rules}
```

## profile.md.example Template

Every persona should ship a `profile.md.example` in its plugin directory. This is the template users copy to `~/.personas/{name}/profile.md` and fill in.

**Key principles:**
- Include all sections the persona needs to function (name, location, preferences, account details, etc.)
- Use `[placeholder]` syntax for values to fill in
- Never include real personal data — this file IS committed to the repo
- Add comments explaining what each section is for

## First Session vs. Subsequent Sessions

Each persona should handle the "no profile.md yet" case gracefully:

**If profile.md doesn't exist:**
1. Tell the user it's missing
2. Guide them to copy `profile.md.example` from the plugin directory: `cp ~/.claude/plugins/cache/*/plugins/{name}/profile.md.example ~/.personas/{name}/profile.md`
3. Walk through the key fields together and help fill them in
4. Don't fail silently or try to continue without profile context

**Mila (self-configuring):** On first session, Mila actively interviews the user to discover their focus areas and WRITES the profile.md herself. Other personas guide the user to fill in the template.

## Runtime Model

Skills activate via **local-scope plugin install** — no `--plugin-dir` needed:

```bash
# One-time setup per persona workspace
mkdir -p ~/.personas/luna
cd ~/.personas/luna
claude plugin install luna@personas --scope local
# Writes: ~/.personas/luna/.claude/settings.local.json
```

Skills only activate when CWD is `~/.personas/{name}/` — native isolation, no bleed.

Workspace layout (auto-bootstrapped by .zshrc on shell reload after plugin install/update):
- `~/.personas/{name}/CLAUDE.md` → symlink → plugin cache (auto-updates on `/plugin update`)
- `~/.personas/{name}/skills/` → symlink → plugin cache skills/
- `~/.personas/{name}/.mcp.json` → local only, fill in credentials, never committed
- `~/.personas/{name}/.claude/settings.local.json` → written by `plugin install --scope local`

If previously installed at user scope: `claude plugin uninstall {name}@personas` first.

## CLI Aliases

Persona aliases are auto-discovered from `~/.personas/*/` via a single `.zshrc` loop. Add this once to `.zshrc`:

```bash
# Persona aliases — auto-discovered from ~/.personas/*/
for _persona_dir in "$HOME/.personas"/*/; do
  _persona_name=$(basename "$_persona_dir")
  eval "${_persona_name}() { (cd \"$_persona_dir\" && claude --mcp-config \"${_persona_dir}.mcp.json\" --strict-mcp-config \"\$@\") }"
done
unset _persona_dir _persona_name
```

After installing a new persona, run `source ~/.zshrc` (or open a new shell) — the alias is auto-created. No manual alias setup needed.

Usage:
- `luna` → interactive session with Luna's MCP only
- `luna "good morning"` → one-shot
- `--strict-mcp-config` blocks global MCP servers from leaking into persona sessions

## Profile.md vs Memory — Canonical Definitions

| Layer | What goes here | Who writes it | When read |
|-------|---------------|---------------|-----------|
| **profile.md** | WHO you are, WHAT you have, HOW you like to work. Stable facts: name, location, accounts, preferences. Doesn't change session to session. | User (manually, with guidance) | Every session start |
| **memory (MEMORY.md)** | WHAT HAPPENED, WHAT WAS DECIDED, WHAT WORKED. Dynamic learnings: strategy results, insights, financial snapshots, session outcomes. | Claude (automatically during sessions) | When past context is needed |

**Rule of thumb:**
- If it would be the same next month without any action → `profile.md`
- If Claude discovered or decided it during a session → `memory`

## Version Bumping

Bump in BOTH `plugin.json` AND `marketplace.json` before every commit.
Patch for skill/doc changes, minor for new skills, major for breaking changes.
