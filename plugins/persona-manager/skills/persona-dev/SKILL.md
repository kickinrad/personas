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
├── .claude/
│   ├── settings.json              # Sandbox config (committed)
│   └── memory/                    # Auto-memory (gitignored)
├── .gitignore                     # Secrets exclusion
├── hooks.json                     # Stop + PreCompact hooks
├── CLAUDE.md                      # Personality + rules
├── profile.md.example             # Profile template (committed)
├── profile.md                     # User's personal context (gitignored)
├── .mcp.json                      # MCP server config (gitignored)
├── skills/
│   ├── {domain}/{skill}/SKILL.md  # Domain skills
│   └── self-improve/SKILL.md      # Ships with every persona
├── docs/                          # Reference materials, plans (committed)
└── scripts/                       # Tools and utilities (committed)
```

**Workspace organization:**
- `docs/` — domain knowledge, reference materials, plans. Use subdirs for categories (`docs/plans/`, `docs/reference/`)
- `scripts/` — executable tools, utilities, data pipelines. Each tool gets its own subdir if non-trivial
- `skills/` — reusable multi-step workflows (SKILL.md files)
- Root — only framework files. Don't dump loose files here

---

## Creating a New Persona

### Phase 1: Discovery

Before building anything, understand what this persona needs to be. Ask the user:

**Required:**
- What domain or role? (finance advisor, personal chef, brand strategist, etc.)
- What's the persona's expertise and voice? (casual vs formal, opinionated vs neutral, proactive vs reactive)
- What workflows will it handle? (weekly reviews, meal planning, code review, etc.)
- What does the user need the persona to know about them? (accounts, preferences, constraints — this shapes `profile.md.example`)

**Explore based on domain:**
- What external services or APIs does the persona need? (→ MCP server research in Phase 2)
- Are there recurring multi-step tasks? (→ skill planning)
- What kind of data does it work with? (→ tool/script needs)
- What should the persona push back on? (→ anti-patterns in CLAUDE.md)

Don't rush this. A well-understood persona is easier to build and evolves better. Ask follow-up questions — domain expertise matters.

### Phase 2: Research

Before writing a single file, research what tools and integrations could enhance this persona:

1. **MCP servers** — search for community or official MCP servers relevant to the domain (recipe APIs, financial data, calendar, etc.). Existing MCP servers beat custom scripts
2. **CLI tools** — identify useful CLI tools already installed or easily available (`gh`, `jq`, domain-specific CLIs)
3. **Expansion packs** — check if any persona-manager expansion packs fit:
   - `persona-manager:persona-dashboard` — visual dashboard with task tracking (good for personas with ongoing work, reviews, or regular check-ins)
4. **Reference material** — find domain-specific best practices, checklists, or frameworks that should live in `docs/`

Present findings to the user: "Here's what I found that could enhance this persona: [list]. Which of these should we include?"

### Phase 3: Scaffold

Create the directory structure directly:

```bash
mkdir -p ~/.personas/{name}/{.claude/memory,skills,docs,scripts}
```

No external dependencies — this skill handles everything.

### Phase 4: Build core files

**4a. Write CLAUDE.md**

Use the template from `references/claude-md-template.md`. Key decisions:

- **Session Start pattern**: Guide (user fills template) vs Interview (persona writes directly)
- **Personality**: Be specific about traits and anti-patterns. Give it opinions
- **Workspace Hygiene section**: Include it — every persona must maintain its own workspace
- **Self-Improvement**: Point to the self-improve skill (one line, not inline)

**4b. Write profile.md.example**

Create a template with sections relevant to the persona's domain. Include:
- Personal info placeholders relevant to this domain
- Account/service connections
- Preferences and constraints
- Anything the persona needs to know about the user

**4c. Create first domain skill(s)**

Write at least one skill under `skills/{domain}/{skill-name}/SKILL.md` with:
- YAML frontmatter (name, description, triggers)
- Step-by-step workflow
- Expected output format

**4d. Copy self-improve skill**

Copy `references/self-improve-skill.md` to `skills/self-improve/SKILL.md`. Replace `{name}` with the persona name. This ships with every persona — it handles memory management, rule promotion, skill creation, tool discovery, and periodic audits.

**4e. Set up hooks**

Copy `references/hooks-template.json` to `hooks.json` in the persona root. These hooks:
- **Stop**: Reminds the persona to update memory before ending
- **PreCompact**: Saves session context before compaction

**4f. Create .gitignore**

Copy `references/gitignore-template` to `.gitignore`.

**4g. Configure sandbox**

Copy `references/settings-template.json` to `.claude/settings.json`. Add any persona-specific network domains for MCP servers to `allowedDomains`.

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

### Phase 7: Set up shell alias + verify

Tell the user how to set up the CLI alias for their shell (see [CLI Aliases](#cli-aliases) below), then verify the persona works:

```bash
source ~/.personas/.aliases.sh   # or their shell's equivalent
{name}                           # should start an interactive session
```

Run through the [Testing a Persona](#testing-a-persona) checklist to confirm everything works.

---

## Three-Layer Model

Every persona uses three layers — never mix them:

| Layer | File | Who Writes | Content |
|-------|------|-----------|---------|
| **Personality** | `CLAUDE.md` | Human (Claude proposes) | Role, rules, skills, communication style |
| **Context** | `profile.md` | Human (guided by Claude) | Personal data, accounts, preferences |
| **Memory** | `.claude/memory/` | Claude (automatic) | Session outcomes, learnings, patterns |

---

## Profile.md vs Memory — Canonical Definitions

| Question | Answer | File |
|----------|--------|------|
| Will this be true next month without action? | Yes | `profile.md` |
| Did Claude discover or decide this? | Yes | `MEMORY.md` |
| Should this always happen, every session? | Yes | `CLAUDE.md` rule |

**profile.md** = WHO you are, WHAT you have, HOW you like to work. Stable facts.
**MEMORY.md** = WHAT HAPPENED, WHAT WAS DECIDED, WHAT WORKED. Dynamic learnings.
**CLAUDE.md rules** = HOW THE PERSONA BEHAVES. Permanent, promoted from patterns.

---

## CLI Aliases

Personas are invoked by name from any directory via shell functions that auto-discover `~/.personas/*/`.

### Setup

Create `~/.personas/.aliases.sh` (works in both bash and zsh):

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

**Source from your shell config:**

| Shell | Add to |
|-------|--------|
| **zsh** | `~/.zshrc`: `[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"` |
| **bash** | `~/.bashrc`: `[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"` |
| **fish** | `~/.config/fish/conf.d/personas.fish` — see fish snippet below |

**Fish shell** (different syntax — create `~/.config/fish/conf.d/personas.fish`):

```fish
# Auto-discover personas for fish shell
for persona_dir in $HOME/.personas/*/
    set persona_name (basename $persona_dir)
    test -f "$persona_dir/CLAUDE.md"; or continue

    function $persona_name --description "Launch $persona_name persona" --wraps=claude
        if test (count $argv) -gt 0
            cd $persona_dir; and claude --setting-sources project --dangerously-skip-permissions -p "$argv"
        else
            cd $persona_dir; and claude --setting-sources project --dangerously-skip-permissions
        end
    end
end
```

After creating or updating a persona: `source ~/.personas/.aliases.sh` (or restart your shell).

**Usage:**
- `{name}` — interactive session
- `{name} "do weekly review"` — one-shot prompt

**What the flags do:**
- `--setting-sources project` — loads only the persona's CLAUDE.md and .claude/settings.json (ignores global config)
- `--dangerously-skip-permissions` — safe because the sandbox restricts filesystem and network access

---

## First Session Patterns

**Pattern A — Guide** (default): The persona tells the user to copy `profile.md.example` to `profile.md` and walks through each section together. Best for personas where the user knows their own context well.

**Pattern B — Interview**: The persona actively interviews the user and writes `profile.md` directly from answers. Best for personas where the user needs help articulating their context (e.g., financial goals, health history).

Choose the pattern in `CLAUDE.md` Session Start. See `references/claude-md-template.md` for both patterns.

---

## MCP Availability Check

Always embed this pattern in every persona's Session Start (already in the CLAUDE.md template):

```
After reading profile.md: Check which MCP tools are available.
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
| Dashboard | `persona-manager:persona-dashboard` | Visual dashboard (HTML), task tracking, open.sh | Personas with ongoing work, reviews, regular check-ins |

These are separate skills in persona-manager — invoke them when the user asks for the capability, or suggest them during Phase 2 (Research) when creating a persona.

During self-audits, personas can also discover expansion packs that would help with recurring needs.

---

## Testing a Persona

After creation, verify:

- [ ] Run `{name}` — does the persona greet you and check for `profile.md`?
- [ ] Try each skill trigger — does the right skill activate?
- [ ] Ask something outside its domain — does it redirect gracefully?
- [ ] End a session — does it write meaningful learnings to MEMORY.md?
- [ ] Check sandbox — `ls ../` from within the persona should fail

Test with adversarial prompts too — ask the persona to do something it shouldn't. A good persona redirects gracefully rather than blindly complying.

---

## Troubleshooting

**"command not found" when typing a persona name:**
- Shell aliases not loaded — run `source ~/.personas/.aliases.sh`
- Check that `~/.personas/{name}/CLAUDE.md` exists (the alias script requires it)

**Persona doesn't pick up profile.md:**
- Verify the file exists: `ls ~/.personas/{name}/profile.md`
- Make sure you copied from `profile.md.example`, not renamed it

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
- Review memory periodically — read MEMORY.md, delete entries that are wrong
- Approve good promotions — when the persona proposes a rule or skill that fits, approve it
- Use trigger phrases consistently — this trains both you and the persona

**Avoid:**
- Vague feedback — "be better at this" gives the persona nothing actionable
- Editing persona files directly — tell the persona to make changes so it creates proper memory/commits
- Skipping the approval step — the propose/approve pattern exists to prevent drift
