---
name: self-improve
description: Self-improvement workflow for evolving this persona — rule promotion, skill creation, tool & integration discovery, workspace hygiene, and periodic audits. Triggers when you notice recurring patterns, want to propose a new rule or skill, need a new tool, or it's time for a self-audit.
triggers:
  - self-improve
  - self-audit
  - time for a self-audit
  - promote this to a rule
  - this should be a skill
  - update my rules
  - improve yourself
---

# Self-Improvement

This persona lives at `~/.personas/{name}/`. All files are immediately live — no reinstall needed.

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

## Level 1: Memory Management (Native Auto-Memory)

Memory is handled natively by Claude Code via `user/memory/`. The system automatically creates topic-based memory files and reads them when relevant.

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
4. On approval, write to `skills/{domain}/{skill-name}/SKILL.md`
5. Update the Skills table in CLAUDE.md
6. Commit: `feat(self): add {skill-name} skill`

## Level 4: Tool & Integration Discovery (Propose to User)

When a capability gap needs automation beyond conversation:

### Step 1: Research before building

Before creating anything custom, investigate what already exists:

- **MCP servers** — search for community or official MCP servers that solve the problem. A well-maintained server beats a custom script every time
- **CLI tools** — check if there's an existing tool (`gh`, `jq`, `fzf`, etc.) that handles it. Many problems have mature solutions
- **Expansion packs** — check if a persona expansion pack covers it (e.g., `persona-dashboard:install` for task tracking and visual status)
- **Reference docs** — sometimes the "tool" you need is just good documentation in `docs/`

Present findings: "Here's what I found that could help: [options]. Want to use an existing tool, or should I build something?"

### Step 2: Identify what's needed

| Need | Where it goes | Example |
|------|--------------|---------|
| Script or utility | `tools/{tool-name}/` | Data pipeline, API wrapper, setup script |
| Reference doc | `docs/` | Domain knowledge, checklists, templates |
| MCP server (existing) | `.mcp.json` + sandbox allowlist | Community server for a service |
| MCP server (custom) | Propose — user configures | Only if nothing exists |
| CLI tool integration | `tools/` or CLAUDE.md instructions | Wrapping an external CLI |
| Expansion pack | Invoke the persona-manager skill | Dashboard, future packs |

### Step 3: Keep custom builds simple

- If it would take more than ~100 lines or needs ongoing maintenance, prefer an existing tool
- Custom tools should do one thing well — no Swiss Army knives
- Always include a brief comment header explaining what the tool does and when to use it

### Step 4: Propose, build, integrate

1. Propose with a preview of what you'll create or install
2. On approval, write the files (or guide MCP setup)
3. For MCP changes: remind user to update `.mcp.json` and `.claude/settings.json` network allowlist
4. For tools: make executable (`chmod +x`), add to `tools/` with its own subdir if non-trivial
5. Update CLAUDE.md if the new tool changes workflows
6. Commit: `feat(self): add {tool-name}`

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
   - Check for loose files in the root that should be in `docs/` or `tools/`
   - Verify `.gitignore` is up to date with any new generated files
7. **Present all proposals** clearly in a single summary:

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

### No Action Needed
- Memory is clean, rules are current, workspace is tidy, no skill gaps detected
```

8. Wait for approval on each proposal before writing anything

## The Key Distinction

**Memory stores what happened. Rules define what always happens.**

Don't promote a one-off to a rule — look for the pattern first. Three occurrences is the threshold, not one strong opinion.
