---
name: persona-dev
description: Create, update, and evolve personas. Use this when the user asks to create a new persona, add a skill to an existing persona, update a persona's CLAUDE.md or profile, set up hooks or self-improvement, document a new MCP tool in a persona, or improve how a persona works over time. Also triggers when the user says things like "my persona should remember this", "this keeps happening, make it a skill", "create a persona for", or "build me a persona".
triggers:
  - create a persona
  - new persona
  - add a persona
  - build a persona
  - persona development
  - add a skill to
  - my persona should
  - make it a skill
  - persona self-improvement
  - persona evolution
---

# Persona Development

Personas live in `~/.personas/{name}/`, each as its own git-tracked directory with sandbox isolation.

## Persona Structure

Each persona contains:

```
~/.personas/{name}/
├── CLAUDE.md                    # Role, rules, skill refs (committed)
├── .claude/
│   ├── settings.json            # Sandbox + autoMemoryDirectory (committed)
│   ├── output-styles/           # Personality, tone, style (committed)
│   └── settings.local.json      # (always gitignored)
├── hooks.json                   # SessionStart hook (committed)
├── profile-template.md           # Interview template (committed)
├── .mcp.json                    # MCP server config (gitignored)
├── skills/
│   ├── {domain}/{skill}/SKILL.md # Domain skills
│   └── self-improve/SKILL.md    # Ships with every persona
├── tools/                       # Utilities, scripts, pipelines (committed)
├── docs/                        # Reference materials, plans (committed)
├── user/                        # Personal data silo (optionally gitignored)
│   ├── profile.md               # User's personal context (filled from interview)
│   └── memory/                  # Native auto-memory
│       ├── MEMORY.md            # Index (first 200 lines loaded)
│       └── *.md                 # Topic files (read on demand)
└── .gitignore
```

**Workspace organization:**
- `docs/` — domain knowledge, reference materials, plans. Use subdirs for categories (`docs/plans/`, `docs/reference/`)
- `tools/` — executable tools, utilities, data pipelines. Each tool gets its own subdir if non-trivial
- `skills/` — reusable multi-step workflows (SKILL.md files)
- `user/` — personal data silo (profile.md, memory/)
- Root — only framework files. Don't dump loose files here

---

## Creating a New Persona

### Phase 1: Discovery

**Environment detection (silent — no user questions):**

Before asking discovery questions, detect the runtime environment to set smart defaults:

1. Check if `/mnt/c/Users` exists → **Cowork on Windows** (WSL2 VM)
2. Check for no TTY and Lima process markers → **Cowork on macOS**
3. Otherwise → **CLI** (Linux/Mac native)

Set internal defaults based on detection:
- `offer_aliases`: `false` if Cowork detected, `true` if CLI detected

These defaults are used in Phase 7 — no user-facing questions here.

Before building anything, understand what this persona needs to be. Ask the user:

**Required:**
- What domain or role? (finance advisor, personal chef, brand strategist, etc.)
- What's the persona's expertise and voice? (casual vs formal, opinionated vs neutral, proactive vs reactive)
- What workflows will it handle? (weekly reviews, meal planning, code review, etc.)
- What does the user need the persona to know about them? (accounts, preferences, constraints — this shapes `profile-template.md`)

**Explore based on domain:**
- What external services or APIs does the persona need? (→ MCP server research in Phase 2)
- Are there recurring multi-step tasks? (→ skill planning)
- What kind of data does it work with? (→ tool needs)
- What should the persona push back on? (→ anti-patterns in output style)

Don't rush this. A well-understood persona is easier to build and evolves better. Ask follow-up questions — domain expertise matters.

### Phase 2: Research

Before writing a single file, research what tools and integrations could enhance this persona:

1. **MCP servers** — search for community or official MCP servers relevant to the domain (recipe APIs, financial data, calendar, etc.). Existing MCP servers beat custom scripts
2. **CLI tools** — identify useful CLI tools already installed or easily available (`gh`, `jq`, domain-specific CLIs)
3. **Expansion packs** — check if any persona-manager expansion packs fit:
   - `persona-dashboard:install` — visual dashboard with task tracking (good for personas with ongoing work, reviews, or regular check-ins)
4. **Reference material** — find domain-specific best practices, checklists, or frameworks that should live in `docs/`

Present findings to the user: "Here's what I found that could enhance this persona: [list]. Which of these should we include?"

### Phase 3: Scaffold

**First, check if the persona already exists:**
- If `~/.personas/{name}/CLAUDE.md` exists, stop and ask: "A persona named `{name}` already exists. Update it, or pick a different name?"
- Don't proceed with scaffolding if it would overwrite an existing persona

Create the directory structure:

```bash
mkdir -p ~/.personas/{name}/{.claude/output-styles,skills,docs,tools,user/memory}
```

### Phase 4: Build core files

**4a. Write CLAUDE.md**

Use the template from `references/claude-md-template.md`. Key decisions:

- **Role and rules**: Be specific about what this persona does and its boundaries
- **Workspace Hygiene section**: Include it — every persona must maintain its own workspace
- **Self-Improvement**: Point to the self-improve skill (one line, not inline)

**4b. Create profile-template.md**

Copy `references/profile-template.md` and customize it for this persona's domain:
- Rename/add/remove sections to fit the domain (e.g., a finance persona needs "Accounts & Assets", a chef persona needs "Dietary Restrictions")
- Update placeholders to be domain-specific
- Update the interview instructions comment with persona-specific guidance on what to ask and how to probe deeper

This file is committed — it's the spec for how `user/profile.md` should look when filled out.

**4c. Copy profile-template.md → user/profile.md**

Copy the customized `profile-template.md` to `user/profile.md`. On first session, the SessionStart hook reads this, sees the unfilled placeholders, and interviews the user to populate it. `user/profile.md` is optionally gitignored (via the `user/` line in `.gitignore`) — the template stays as the committed reference.

**4d. Create first domain skill(s)**

Write at least one skill under `skills/{domain}/{skill-name}/SKILL.md` with:
- YAML frontmatter (name, description, triggers)
- Step-by-step workflow
- Expected output format

**4e. Copy self-improve skill**

Copy `references/self-improve-skill.md` to `skills/self-improve/SKILL.md`. Replace `{name}` with the persona name. This ships with every persona — it handles rule promotion, skill creation, tool discovery, and periodic audits.

**4f. Set up hooks**

Copy `references/hooks-template.json` to `hooks.json` in the persona root. The hook:
- **SessionStart** (command): Reads `user/profile.md` contents into session context via `additionalContext` — the persona then interviews if unfilled or checks completeness. Must be `type: "command"` (SessionStart only supports command hooks)

**4g. Create .gitignore**

Copy `references/gitignore-template` to `.gitignore`.

**4h. Configure sandbox**

Copy `references/settings-template.json` to `.claude/settings.json`. This includes `autoMemoryDirectory: "user/memory"` for native auto-memory. Add any persona-specific network domains for MCP servers to `allowedDomains`.

**4i. Create output style**

Copy `references/output-style-template.md` to `.claude/output-styles/{name}.md`. Fill in the persona's personality, tone, and communication style from the Discovery phase. Set `keep-coding-instructions: false` for non-coding personas.

**4j. Validate scaffold**

Before proceeding, verify all required files exist:
- [ ] `CLAUDE.md`
- [ ] `profile-template.md`
- [ ] `user/profile.md` (copy of template, ready for first-session interview)
- [ ] `.claude/output-styles/{name}.md`
- [ ] `hooks.json`
- [ ] `.gitignore`
- [ ] `.claude/settings.json` (with `autoMemoryDirectory`)
- [ ] `user/memory/` directory exists
- [ ] `skills/self-improve/SKILL.md`
- [ ] At least one domain skill in `skills/`

If anything is missing, fix it now — don't proceed with gaps.

### Phase 5: Configure integrations

If Phase 2 identified useful MCP servers or tools:

1. Document tools in CLAUDE.md under "MCP Tools Available"
2. Add domains to `.claude/settings.json` → `network.allowedDomains`
3. Tell the user how to configure each server in `.mcp.json` (gitignored — secrets go here)
4. For CLI tools: add usage instructions to relevant skills or CLAUDE.md
5. For expansion packs: ask the user if they want to install them now

### Phase 6: Initialize git + optional GitHub

```bash
cd ~/.personas/{name}
git init
git add -A
git commit -m "feat({name}): initial scaffold"
```

Ask the user: "Want to set up a GitHub repo for this persona?"
- If yes: `gh repo create {github-username}/{name} --private --source=. --push`
- If no: Skip — can always add a remote later

### Phase 7: Configure invocation + verify

**If CLI detected:**

Set up the alias system so the persona is callable by name:

1. **Create `~/.personas/.aliases.sh`** if it doesn't exist (see [CLI Aliases](#cli-aliases) below for the template)
2. **Add source line to the user's shell config** if not already present:
   - Detect the user's shell from `$SHELL`
   - For zsh: append to `~/.zshrc`
   - For bash: append to `~/.bashrc`
   - The line to add: `[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"`
   - **Check first** — only add if the line isn't already there
3. **Tell the user** to restart their shell or run `source ~/.personas/.aliases.sh` to activate immediately

**If Cowork detected:**

Ask: "Do you also use Claude Code from the terminal? I can set up shell aliases so you can launch this persona from the command line too."

- If yes → follow the CLI alias setup above
- If no → skip aliases and tell the user: "To use this persona in Cowork, open `~/.personas/{name}/` as a project folder."

**Then verify** — run through the [Testing a Persona](#testing-a-persona) checklist regardless of environment.

---

## What Is a Persona?

**A persona is a self-contained AI assistant.** It combines standard Claude Code features — identity (CLAUDE.md), user context (`user/profile.md`), output style (`.claude/output-styles/`), skills, hooks, MCP tools, sandbox settings, and native auto-memory (`user/memory/`) — into a specialized agent that evolves over time. The persona maintains all of these itself; identity changes require human approval, everything else evolves automatically.

---

## Profile vs Memory vs Rules — Canonical Definitions

| Question | Answer | File |
|----------|--------|------|
| Will this be true next month without action? | Yes | `user/profile.md` |
| Did Claude discover or decide this? | Yes | `user/memory/` |
| Should this always happen, every session? | Yes | `CLAUDE.md` rule |

**user/profile.md** = WHO you are, WHAT you have, HOW you like to work. Stable facts.
**user/memory/** = WHAT HAPPENED, WHAT WAS DECIDED, WHAT WORKED. Dynamic learnings.
**CLAUDE.md rules** = HOW THE PERSONA BEHAVES. Permanent, promoted from patterns.

---

## CLI Aliases

Personas are invoked by name from any directory via shell functions that auto-discover `~/.personas/*/`.

### Setup

Create `~/.personas/.aliases.sh`:

```bash
#!/usr/bin/env bash
# Auto-discover personas and create shell functions
# Source this from your .bashrc, .zshrc, or equivalent

for _persona_dir in "$HOME/.personas"/*/; do
  [ -d "$_persona_dir" ] || continue
  _persona_name=$(basename "$_persona_dir")
  [ -f "${_persona_dir}CLAUDE.md" ] || continue

  eval "${_persona_name}() {
    if [ \$# -gt 0 ]; then
      (cd \"${_persona_dir}\" && claude --setting-sources project --dangerously-skip-permissions -p \"\$*\")
    else
      (cd \"${_persona_dir}\" && claude --setting-sources project --dangerously-skip-permissions)
    fi
  }"
done
unset _persona_dir _persona_name
```

**Source from your shell config** (add to `~/.zshrc` or `~/.bashrc`):

```bash
[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"
```

After creating or updating a persona: `source ~/.personas/.aliases.sh` or restart your shell.

**Usage:**
- `{name}` — interactive session
- `{name} "do weekly review"` — one-shot prompt

**What the flags do:**
- `--setting-sources project` — loads only the persona's CLAUDE.md and .claude/settings.json (ignores global config)
- `--dangerously-skip-permissions` — safe because the sandbox restricts filesystem and network access

---

## First Session Flow

On first session, `user/profile.md` exists as an unfilled copy of `profile-template.md`. The SessionStart hook reads it, sees the template placeholders, and interviews the user to populate each section. The persona follows the interview instructions embedded in the template to ask the right questions and fill out the profile to spec.

On subsequent sessions, the SessionStart hook reads `user/profile.md` automatically. If any sections are still incomplete, the persona prompts the user to fill in the gaps before proceeding.

---

## MCP Availability Check

Always embed this pattern in every persona's Session Start (already in the CLAUDE.md template):

```
After reading user/profile.md: Check which MCP tools are available.
For any disconnected server, tell the user what's unavailable
and ask: skip for now, or help set it up?
Offer text-only mode if all MCPs are unavailable.
```

When adding MCP servers:
1. Document tools in CLAUDE.md under "MCP Tools Available"
2. Add domains to `.claude/settings.json` → `network.allowedDomains`
3. Configure the server in `.mcp.json` (gitignored)

---

## Expansion Packs

Optional capabilities that can be installed into personas after creation:

| Pack | Skill | What it adds | Good for |
|------|-------|-------------|----------|
| Dashboard | `persona-dashboard:install` | Visual dashboard (HTML), task tracking, open.sh | Personas with ongoing work, reviews, regular check-ins |

These are separate skills in persona-manager — invoke them when the user asks for the capability, or suggest them during Phase 2 (Research) when creating a persona.

During self-audits, personas can also discover expansion packs that would help with recurring needs.

---

## Testing a Persona

After creation, verify:

- [ ] Run `{name}` — does the SessionStart hook read `user/profile.md` (or trigger the interview if unfilled)?
- [ ] Try each skill trigger — does the right skill activate?
- [ ] Ask something outside its domain — does it redirect gracefully?
- [ ] Check that `autoMemoryDirectory` is set in `.claude/settings.json`
- [ ] Check sandbox — `ls ../` from within the persona should fail

Test with adversarial prompts too — ask the persona to do something it shouldn't. A good persona redirects gracefully rather than blindly complying.

---

## Troubleshooting

**"command not found" when typing a persona name:**
- Shell aliases not loaded — run `source ~/.personas/.aliases.sh`
- Check that `~/.personas/{name}/CLAUDE.md` exists (the alias script requires it)

**Persona doesn't pick up profile:**
- Verify the file exists: `ls ~/.personas/{name}/user/profile.md`
- Check that hooks.json includes the SessionStart hook (reads `user/profile.md` automatically)

**MCP server not connecting:**
- Check `.mcp.json` syntax: `jq . ~/.personas/{name}/.mcp.json`
- Check the persona's `.claude/settings.json` for `allowedDomains` — MCP servers need network access

**Sandbox errors (Linux):**
- Bubblewrap must be installed: `which bwrap || sudo apt install bubblewrap`

---

## Guiding Persona Growth

Tips for users to get the most out of persona evolution:

**Do:**
- Correct the persona explicitly — "no, always do X instead" creates clear memory entries that can be promoted to rules
- Review memory periodically — read `user/memory/MEMORY.md`, delete entries that are wrong
- Approve good promotions — when the persona proposes a rule or skill that fits, approve it
- Use trigger phrases consistently — this trains both you and the persona

**Avoid:**
- Vague feedback — "be better at this" gives the persona nothing actionable
- Editing persona files directly — tell the persona to make changes so it creates proper memory/commits
- Skipping the approval step — the propose/approve pattern exists to prevent drift
