---
name: self-improve
description: This skill should be used when a persona wants to evolve itself — the user says "self-improve", "self-audit", "time for a self-audit", "promote this to a rule", "this should be a skill", "update my rules", or "improve yourself", or the persona notices a recurring pattern worth promoting. Covers rule promotion, skill creation, tool & integration discovery, workspace hygiene, and periodic audits. Ships with the persona-manager plugin so every persona shares one canonical workflow.
---

# Self-Improvement

Your persona home is your working directory (`~/.personas/<name>/`). All persona files are immediately live — no reinstall needed.

## When to Update What

| File | Update when | How |
|------|------------|-----|
| `user/memory/` | Something worth remembering happened | Native auto-memory handles this |
| `user/profile.md` | Stable facts change (new account, preference shift) | Propose, write with approval |
| `CLAUDE.md` (rules) | A behavioral pattern should become permanent | Propose, write with approval |
| New skill file | A 3+ step workflow recurs with no existing skill | Draft, propose to user |
| New tool | A capability gap needs automation (research first!) | Draft, propose to user |
| `docs/*.md` | Stable domain context too long for profile.md | Write with approval |
| Remove files | Stale docs, unused tools, dead skills | Propose removal in audit |

## Level 1: Memory (Native Auto-Memory — Hands Off)

Memory is handled **entirely** by Claude Code's native auto-memory system via `autoMemoryDirectory` in `settings.local.json` — never write to `user/memory/` manually (the canonical rule lives in each persona's CLAUDE.md Memory section). The Stop and PreCompact hooks prompt you to *reflect* on session insights — auto-memory captures them automatically from your reflection.

**Memory vs knowledge docs:** `user/memory/` is auto-memory's alone; `docs/` is for knowledge and reference documents you create deliberately (domain context, plans, research, checklists).

During self-audits, review `user/memory/MEMORY.md` and topic files for:
- Recurring patterns worth promoting to rules
- Outdated entries worth cleaning up
- Gaps in what's being captured

## Level 2: Rule Promotion (Propose to User)

When you notice the same correction or preference **3+ times** across sessions (visible in memory):

1. Cite the evidence: "I've seen this in sessions on [dates]"
2. Propose the rule: "Want me to add this to my CLAUDE.md?"
3. Wait for approval
4. Write the change directly to CLAUDE.md
5. Commit: `improve(self): {description}`

**What makes a good rule:**
- Specific and actionable ("always group by store section", not "be more organized")
- Based on repeated evidence, not a single occurrence
- Fills a gap — doesn't duplicate an existing rule

## Level 3: Skill Creation (Propose to User)

When handling a request that involves **3+ steps** with no existing skill, and it has happened **3+ times**:

1. Note it in memory as a potential skill gap on first occurrence
2. After 3 occurrences, draft a `SKILL.md` with:
   - YAML frontmatter (name, description, triggers)
   - Clear step-by-step workflow
   - Expected output format
3. Propose the skill with a preview
4. On approval, write to `.claude/skills/{domain}/{skill-name}/SKILL.md`
5. Update the Skills table in CLAUDE.md
6. Commit: `feat(self): add {skill-name} skill`

## Level 4: Tool & Integration Discovery (Propose to User)

When a capability gap needs automation beyond conversation:

### Step 1: Research before building

Before creating anything custom, investigate what already exists. Work through the discovery categories in the shared research toolkit — MCP servers, CLI tools, APIs, skills, agents, hooks, scripts, reference material, scheduled tasks, and expansion packs (e.g., `persona-dashboard:install`). The canonical list lives in the persona-dev sibling skill: `~/.claude/plugins/marketplaces/personas/plugins/persona-manager/skills/persona-dev/references/research-toolkit.md`.

Present findings: "Here's what I found that could help: [options]. Want to use an existing solution, or should I build something?"

### Step 2: Identify what's needed

Use the where-it-lives table in the same `research-toolkit.md` reference to place each capability (`.mcp.json`, skill, agent, hook, `tools/` script, `docs/`, expansion pack).

### Step 3: Keep custom builds simple

- If it would take more than ~100 lines or needs ongoing maintenance, prefer an existing tool
- Custom tools should do one thing well — no Swiss Army knives
- Always include a brief comment header explaining what the tool does and when to use it
- A skill that documents how to use an existing CLI tool is better than a wrapper script that reimplements it

### Step 4: Propose, build, integrate

1. Propose with a preview of what you'll create or install
2. On approval, write the files (or guide setup)
3. For MCP changes: remind user to update `.mcp.json` and `.claude/settings.json` network allowlist
4. For tools/scripts: make executable (`chmod +x`), add to `tools/` with its own subdir if non-trivial
5. For skills: write SKILL.md, add trigger phrase to CLAUDE.md skills table
6. For agents: create `.claude/agents/{name}.md` with system prompt and tool access
7. For hooks: add entries to `hooks.json`, document what triggers them
8. Update CLAUDE.md if the new integration changes workflows
9. Commit: `feat(self): add {tool-name}`

## Periodic Audit

Run monthly, or when the user says "time for a self-audit":

1. **Read memory** — scan `user/memory/MEMORY.md` and topic files for recurring themes, friction points, repeated questions
2. **Check for promotable patterns:**
   - Recurring correction (3+ sessions) → propose CLAUDE.md rule
   - Recurring multi-step workflow → propose new SKILL.md
   - Outdated `user/profile.md` fact → flag for user update
3. **Review existing rules** — any that no longer apply? Propose removal
4. **Review existing skills** — any that need updating based on recent sessions?
5. **Workspace hygiene sweep:**
   - Scan `docs/` and `tools/` for stale or outdated files — propose removal or update
   - Check MCP servers — any unused or disconnected for 3+ sessions? Flag for removal
   - Check skills — any that wrap tools no longer installed, or workflows that have changed?
   - Check agents — any in `.claude/agents/` that aren't being triggered?
   - Check hooks — any domain-specific hooks in `hooks.json` that are no longer useful?
   - Check scripts in `tools/` — any that duplicate what a skill or MCP server now handles?
   - Check for loose files in the root that should be in `docs/` or `tools/`
   - Check for recurring manual checks or reminders the user keeps requesting — could any be automated with scheduled tasks?
   - Verify `.gitignore` is up to date with any new generated files
   - **Vault integration health** — does the persona have a current MOC at its declared vault home? Are notes accruing or is the persona avoiding the vault? Are wikilinks resolving? Dispatch the `vault:curator` agent to lint if drift suspected
6. **Present all proposals** clearly in a single summary:

```
## Self-Audit Results

### Proposed Rule Changes
- **Add:** "{rule}" — seen in [dates], evidence: {summary}
- **Remove:** "{rule}" — no longer relevant because {reason}

### Proposed New Skills
- **{skill-name}** — handles {workflow}, triggered {N} times ad-hoc

### Profile Updates
- **Flag:** {fact} may be outdated — please verify

### Workspace Cleanup
- **Remove:** `docs/old-thing.md` — not referenced in 5+ sessions
- **Move:** `root-file.md` → `docs/reference/` — misplaced
- **Flag:** MCP server `{name}` unused for 3+ sessions — remove?
- **Flag:** Script `tools/{name}` duplicates skill `{skill}` — consolidate?
- **Flag:** Agent `{name}` not triggered in 3+ sessions — still needed?

### No Action Needed
- Memory is clean, rules are current, workspace is tidy, no skill gaps detected
```

7. Wait for approval on each proposal before writing anything

## The Key Distinction

**Memory stores what happened. Rules define what always happens.**

Don't promote a one-off to a rule — look for the pattern first. Three occurrences is the threshold, not one strong opinion.
