---
name: persona-update
description: This skill should be used when the user asks to "update persona", "check for updates", "sync with framework", "persona maintenance", or mentions "persona drift", "persona outdated", or "update hooks". Detects drift between an existing persona and the current framework version, diffs persona files against current templates, and applies changes intelligently.
---

# Persona Update

Diffs persona files against the current framework templates. You — the persona — are the merge engine. Read the diffs, understand what's framework vs custom, apply intelligently, and ask the user only when something is genuinely ambiguous.

## What This Skill Does NOT Touch

These are persona-specific and must never be overwritten:
- `CLAUDE.md` personality, rules, skills table (only CHECK for missing framework sections)
- Custom skills in `.claude/skills/{domain}/`
- `user/profile.md`, `user/memory/`
- `.mcp.json`
- `.claude/output-styles/`
- Persona-specific `allowedDomains` in settings.json
- Persona-specific `enabledPlugins` beyond `persona-manager@personas`
- Custom Stop hook prompt additions (domain-specific context)
- Persona-specific vault notes anywhere in the vault — user content, never modified by drift fix

## Propagating a Shared Rule Across Personas

When a rule or principle changes for every persona — a framework behavioral standard, a shared operating rule — split it into two parts before touching any files:

- **Core** — the invariant rule text: what the rule requires. Identical in meaning across all personas.
- **Warmth** — each persona's expression of that rule: the voice, framing, and examples it wears in that persona's CLAUDE.md or output-style.

Propagate the core by editing each persona's surface independently. Read how the persona expresses the current rule, then rewrite that passage so it carries the new core in the persona's existing voice. Never paste identical text into every persona, and never flatten or homogenize the warmth to make the edit easier — a rule that arrives in the wrong voice erodes the personality the persona was built around. If a persona's existing expression conflicts with the new core in a way that can't be resolved without changing the voice, surface it with `AskUserQuestion` instead of averaging the two.

This governs Step 4 merges, the Step 5 conversational checks (CLAUDE.md and output-style), and especially Batch mode, where the temptation to copy one merged result across all personas is strongest.

## File-to-Template Mapping

Templates live in the `persona-dev` skill's `references/` directory (sibling skill in this plugin). Find them at `~/.claude/plugins/marketplaces/personas/plugins/persona-manager/skills/persona-dev/references/`.

| Persona File | Template |
|---|---|
| `hooks.json` | `references/hooks-template.json` |
| `.claude/settings.json` | `references/settings-template.json` |
| `.gitignore` | `references/gitignore-template` |
| `.claude/hooks/public-repo-guard.sh` | `references/public-repo-guard.sh` |
| `.claude/output-styles/*.md` | `references/output-style-template.md` |

**Self-improve is not diffed** — it ships via the persona-manager plugin (every persona enables `persona-manager@personas`), so the plugin's `skills/self-improve/SKILL.md` is always current. If the persona still has a legacy local copy at `.claude/skills/self-improve/`, flag it in the drift report and propose deleting it — the local copy duplicates the plugin skill and drifts.

`CLAUDE.md` and `.claude-flags` are too customized for template diffing — handle these conversationally (Step 5).

**Output-style diffs:** The output-style template provides structural guidance (sections, boundary rule). Persona customization in output-style files (personality, voice, specific opinions) must always be preserved — personality is unique to each persona. Only check for missing structural sections, not content alignment.

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

### Legacy
- Local self-improve copy at .claude/skills/self-improve/ — plugin ships it now; propose removal

### No drift: public-repo-guard.sh
```

### Step 4: Apply Changes

Apply using your judgment:

- **JSON files** (hooks.json, settings.json): Merge missing keys and update changed values. Use `jq` for safe JSON manipulation. Always preserve persona-specific content.
- **Text files** (.gitignore): Append missing entries. Never reorder or remove existing ones.
- **Script files** (public-repo-guard.sh): Replace from template if outdated. Ensure executable: `chmod +x`.
- **Legacy self-improve copies**: If `.claude/skills/self-improve/` exists, propose deleting it — the plugin-shipped skill supersedes it. Never update the local copy in place.
- **Ambiguous changes**: Use `AskUserQuestion` — show both versions, explain the conflict, let the user decide.

### Step 5: Conversational Checks

These files are too customized for diffing. Check them conversationally:

**CLAUDE.md** — Read the persona's CLAUDE.md and verify these framework sections exist:
- Session Start (mentions AskUserQuestion for interview)
- Self-Improvement (references self-improve skill)
- Workspace Hygiene (file organization, cleanup habits)
- Security (personal data handling, secret management)
- Built-in Tools (Claude Code native capabilities)
- `## Vault — Our Shared Brain` section (or equivalent vault-aware section)
- Important Rules contains the "Query the vault before fresh research" bullet
- Skills/Tools section references at least `vault:knowledge` + `obsidian:obsidian-cli`
- **Capture-on-mention** paragraph in the Vault section (save-at-mention pattern, `captured_auto: true` for unattended runs, the Discord confirmation-message carve-out). If missing, apply the core/warmth split above — the invariant is the rule text in `references/claude-md-template.md`; the persona's existing voice carries it

If any are missing, read `references/claude-md-template.md` for the canonical version and propose additions that fit the persona's style. Never rewrite personality or rules.

**`.claude/settings.json`** — Read and verify:
- `enabledPlugins` contains `vault@core` (not `vault@toolbox` — that's stale; propose a rewrite if found)
- `enabledPlugins` contains `obsidian@obsidian-skills`
- `extraKnownMarketplaces` contains `core` (directory source pointing at `/home/wilst/projects/markets/core`)

If any are missing, merge from `references/settings-template.json` while preserving persona-specific `allowedDomains` and any extra plugins the persona enabled beyond the framework baseline.

**Output-style** — Read `.claude/output-styles/` files and verify:
- Has "Who I Am", "How I'll Be", "What I Won't Do" sections
- `keep-coding-instructions: false` in frontmatter
- No operational content that belongs in CLAUDE.md (skills, tools, security rules)
- Boundary rule: voice/personality here, operational content in CLAUDE.md

**.claude-flags** — Read and verify:
- `--setting-sources project,local` is present
- `--dangerously-skip-permissions` is NOT present on Windows native
- Don't add or remove optional flags (--remote-control, --chrome) — those are persona-specific

### Step 6: After applying drift fixes

Once all merges and conversational adjustments have landed, dispatch the `@persona-validator` agent against the persona directory before stamping the version. The validator is the structural counterpart to this skill — it checks scaffold completeness and framework compliance (file presence, frontmatter shape, hook wiring, settings keys) so drift fixes don't silently leave the persona in a half-updated state.

```
Agent('persona-validator', 'validate ~/.personas/{name}/')
```

If the validator surfaces failures, treat them as part of this update cycle: fix in place, re-run the validator, only stamp the version once it returns clean. Don't paper over a validator concern by stamping the version anyway — the next `persona-update` run will see the version match and skip the diff entirely.

### Step 7: Finalize

1. **Validate JSON:** `jq . hooks.json && jq . .claude/settings.json`
2. **Check permissions:** `test -x .claude/hooks/public-repo-guard.sh`
3. **Stamp version:** Write the current plugin version to `.framework-version`
4. **Propose commit:** `chore({name}): update to framework v{version}`

---

## Running Modes

**Self-update:** CWD is inside `~/.personas/{name}/` — update this persona directly.

**Cross-update:** CWD is elsewhere — ask which persona: `ls ~/.personas/`, then operate on `~/.personas/{name}/`.

**Batch:** Update all personas — `ls ~/.personas/`, run on each sequentially, present a combined report. When the batch carries a shared rule change, apply the core/warmth split above: one core, per-persona expression, no copy-pasted merged text.
