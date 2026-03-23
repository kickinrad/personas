---
name: persona-update
description: This skill should be used when the user asks to "update persona", "check for updates", "sync with framework", "persona maintenance", or mentions "persona drift", "persona outdated", or "update hooks". Detects drift between an existing persona and the current framework version, diffs persona files against current templates, and applies changes intelligently.
---

# Persona Update

Diffs persona files against the current framework templates. You — the persona — are the merge engine. Read the diffs, understand what's framework vs custom, apply intelligently, and ask the user only when something is genuinely ambiguous.

## What This Skill Does NOT Touch

These are persona-specific and must never be overwritten:
- `CLAUDE.md` personality, rules, skills table (only CHECK for missing framework sections)
- Custom skills in `skills/{domain}/`
- `user/profile.md`, `user/memory/`
- `.mcp.json`
- `.claude/output-styles/`
- Persona-specific `allowedDomains` in settings.json
- Persona-specific `enabledPlugins` beyond `persona-manager@personas`
- Custom Stop hook prompt additions (domain-specific context)

## File-to-Template Mapping

Templates live in the `persona-dev` skill's `references/` directory (sibling skill in this plugin). Find them at `~/.claude/plugins/marketplaces/personas/plugins/persona-manager/skills/persona-dev/references/`.

| Persona File | Template |
|---|---|
| `hooks.json` | `references/hooks-template.json` |
| `.claude/settings.json` | `references/settings-template.json` |
| `.gitignore` | `references/gitignore-template` |
| `.claude/hooks/public-repo-guard.sh` | `references/public-repo-guard.sh` |
| `skills/self-improve/SKILL.md` | `references/self-improve-skill.md` |

`CLAUDE.md` and `.claude-flags` are too customized for template diffing — handle these conversationally (Step 5).

---

## Workflow

### Step 1: Version Check

1. Read `.framework-version` from persona root (treat missing as `0.0.0`)
2. Read plugin version: `jq -r '.version' ~/.claude/plugins/marketplaces/personas/plugins/persona-manager/.claude-plugin/plugin.json`
3. If versions match → report "Persona is up to date with framework v{version}" and stop
4. If behind → continue with the diff

### Step 2: Diff Each File Pair

For each row in the mapping table:

1. **Read both files** — the persona's file and the corresponding template
2. **Compare them** — you're an AI, you can see what's different
3. **Classify each difference:**
   - **Framework addition** — something the template has that the persona doesn't (e.g., a new hook, a new settings key). These should be merged in.
   - **Framework change** — something the template updated (e.g., SessionStart command format). These should be applied, preserving persona additions.
   - **Persona customization** — something the persona added that isn't in the template (e.g., custom allowedDomains, extra hooks, domain-specific Stop prompt). These must be preserved.
   - **Missing file** — persona doesn't have the file at all. Create from template.
4. **Note ambiguities** — if the persona customized something the framework also changed, flag it for Step 4

### Step 3: Present Drift Report

Show a grouped summary:

```
## Drift Report for {name} ({current_version} → {plugin_version})

### hooks.json
- Missing: PostCompact hook (crash recovery after compaction)
- Changed: SessionStart command updated (dependency-free format)
- Preserved: Custom Stop prompt additions

### .claude/settings.json
- Missing: extraKnownMarketplaces entry
- Preserved: 5 custom allowedDomains entries

### .gitignore
- Missing: .DS_Store, Thumbs.db patterns

### No drift: public-repo-guard.sh, self-improve skill
```

### Step 4: Apply Changes

Apply using your judgment:

- **JSON files** (hooks.json, settings.json): Merge missing keys and update changed values. Use `jq` for safe JSON manipulation. Always preserve persona-specific content.
- **Text files** (.gitignore): Append missing entries. Never reorder or remove existing ones.
- **Script files** (public-repo-guard.sh): Replace from template if outdated. Ensure executable: `chmod +x`.
- **Skill files** (self-improve): Update framework content, preserve persona-specific first line (persona name/path).
- **Ambiguous changes**: Use `AskUserQuestion` — show both versions, explain the conflict, let the user decide.

### Step 5: Conversational Checks

These files are too customized for diffing. Check them conversationally:

**CLAUDE.md** — Read the persona's CLAUDE.md and verify these framework sections exist:
- Session Start (mentions AskUserQuestion for interview)
- Self-Improvement (references self-improve skill)
- Workspace Hygiene (file organization, cleanup habits)
- Security (personal data handling, secret management)
- Built-in Tools (Claude Code native capabilities)

If any are missing, read `references/claude-md-template.md` for the canonical version and propose additions that fit the persona's style. Never rewrite personality or rules.

**.claude-flags** — Read and verify:
- `--name {persona}` is present (use directory name)
- `--setting-sources project,local` is present
- `--dangerously-skip-permissions` is NOT present on Windows native
- Don't add or remove optional flags (--remote-control, --chrome) — those are persona-specific

### Step 6: Finalize

1. **Validate JSON:** `jq . hooks.json && jq . .claude/settings.json`
2. **Check permissions:** `test -x .claude/hooks/public-repo-guard.sh`
3. **Stamp version:** Write the current plugin version to `.framework-version`
4. **Propose commit:** `chore({name}): update to framework v{version}`

---

## Running Modes

**Self-update:** CWD is inside `~/.personas/{name}/` — update this persona directly.

**Cross-update:** CWD is elsewhere — ask which persona: `ls ~/.personas/`, then operate on `~/.personas/{name}/`.

**Batch:** Update all personas — `ls ~/.personas/`, run on each sequentially, present a combined report.
