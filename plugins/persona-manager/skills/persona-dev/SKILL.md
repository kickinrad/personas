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
│   ├── settings.local.json        # autoMemoryDirectory (gitignored, created during setup)
│   ├── output-styles/             # Personality, tone, style (committed)
│   └── hooks/
│       └── public-repo-guard.sh   # Blocks personal data in public repos (committed)
├── .gitignore                     # Secrets exclusion
├── hooks.json                     # SessionStart + Stop + StopFailure + PreCompact + PostCompact + PreToolUse hooks
├── CLAUDE.md                      # Personality + rules
├── docs/                          # Reference materials, plans
├── .mcp.json                      # MCP server config (gitignored)
├── skills/
│   ├── {domain}/{skill}/SKILL.md  # Domain skills
│   └── self-improve/SKILL.md      # Ships with every persona
├── tools/                         # Utilities, scripts, pipelines (committed)
├── docs/                          # Reference materials, plans (committed)
└── user/                          # Personal data silo (gitignored for public sharing)
    ├── profile.md                 # User context (filled from interview)
    └── memory/                    # Native auto-memory
        ├── MEMORY.md              # Index (first 200 lines loaded)
        └── *.md                   # Topic files (read on demand)
```

**Workspace organization:**
- `docs/` — domain knowledge, reference materials, plans. Use subdirs for categories (`docs/reference/`)
- `tools/` — executable tools, utilities, data pipelines. Each tool gets its own subdir if non-trivial
- `skills/` — reusable multi-step workflows (SKILL.md files)
- `user/` — personal data silo, ensure ALL personal data lands here: profile.md and auto-memory. Gitignored for public sharing
- Root — only framework files. Don't dump loose files here

---

## Creating a New Persona

### Phase 1: Discovery

Before building anything, understand what this persona needs to be. Ask the user:

**Required:**
- What domain or role? (finance advisor, personal chef, brand strategist, etc.)
- What's the persona's expertise, personality, and voice? (casual vs formal, opinionated vs neutral, proactive vs reactive, present fun and effective personalities that fit the role and ask for preferences)
- What workflows will it handle? (weekly reviews, meal planning, code review, etc.)
- What does the user need the persona to know about them? (info, accounts, preferences, constraints — this shapes `user/profile.md`)
- What is the personas name? (suggest a selection of fun, memorable first names that fits the role, and ask the user if they have any preferences or want to choose their own)

**Explore based on domain:**
- What external services or APIs does the persona need? (→ MCP server research in Phase 2)
- Are there recurring multi-step tasks? (→ skill planning)
- What kind of data does it work with? (→ tool/script needs)
- What should the persona push back on? (→ anti-patterns in CLAUDE.md)

**Environment detection (ask early):**
- What environment? (CLI only, Desktop only, or both)
- What OS? Detect automatically when possible (`uname`, check for WSL, check for Windows paths)
- This determines Phase 7 setup (aliases, Desktop config, or both)

Don't rush this. A well-understood persona is easier to build and evolves better. Ask follow-up questions — domain expertise matters.

### Phase 2: Research

Before writing a single file, research what tools and integrations could enhance this persona. Think broadly — personas have a rich toolkit beyond MCP servers:

1. **MCP servers** — search for community or official MCP servers relevant to the domain (recipe APIs, financial data, calendar, etc.). Existing servers beat custom solutions
2. **CLI tools** — identify useful CLI tools already installed or easily available (`gh`, `jq`, domain-specific CLIs)
3. **APIs** — identify REST/GraphQL APIs the persona could call directly via `curl` or scripts in `tools/`. Not everything needs an MCP server — sometimes a simple API call in a bash script is the right tool
4. **Skills** — plan domain skills that wrap CLI tools, API workflows, or multi-step processes into reusable SKILL.md files. Skills are the persona's playbooks — they turn "I know how to use this tool" into "here's the complete workflow"
5. **Agents** — consider whether the persona needs specialized subagents (in `.claude/agents/`) for complex autonomous tasks like research, analysis, or multi-step operations
6. **Hooks** — beyond the standard SessionStart/Stop/PreCompact, consider domain-specific hooks (e.g., a PreToolUse hook that validates data before writes, a Stop hook that generates a summary)
7. **Scripts** — bash or python scripts in `tools/` for data pipelines, API wrappers, formatters, or anything the persona does repeatedly
8. **Reference material** — domain-specific best practices, checklists, templates, or frameworks that should live in `docs/`
9. **Scheduled tasks** — identify workflows that benefit from timed reminders or delayed checks. Any persona can schedule tasks using natural language ("remind me at 3pm to...", "in 45 minutes, check whether..."). These are session-scoped — they vanish on exit. Suggest domain-specific scheduling patterns during persona setup and document them in the CLAUDE.md template
10. **Expansion packs** — check if any persona-manager expansion packs fit:
   - `persona-manager:persona-dashboard` — visual dashboard with task tracking (good for personas with ongoing work, reviews, or regular check-ins)

| Discovery | Where it lives | When to choose it |
|-----------|---------------|-------------------|
| MCP server | `.mcp.json` + sandbox allowlist | Persistent connection to an external service |
| CLI tool | Document in CLAUDE.md or wrap in a skill | Mature tool already exists for the job |
| API (direct) | `tools/` script or skill instructions | Simple HTTP calls, no persistent connection needed |
| Skill | `skills/{domain}/{name}/SKILL.md` | Multi-step workflow the persona will repeat |
| Agent | `.claude/agents/{name}.md` | Autonomous subtask needing its own context |
| Hook | `hooks.json` | Behavioral automation tied to session events |
| Script | `tools/{name}` | Data processing, automation, one-off utilities |
| Scheduled task | Scheduling patterns in CLAUDE.md | Timed reminders, delayed checks |
| Reference doc | `docs/` | Domain knowledge the persona should internalize |

Present findings to the user: "Here's what I found that could enhance this persona: [list]. Which of these should we include?"

### Phase 3: Scaffold

**First, check if the persona already exists:**
- If `~/.personas/{name}/CLAUDE.md` exists, stop and ask: "A persona named `{name}` already exists. Update it, or pick a different name?"
- Don't proceed with scaffolding if it would overwrite an existing persona

**Determine the personas root directory:**

| Environment | Personas root | Why |
|-------------|--------------|-----|
| macOS / Linux (native) | `~/.personas/` | Standard home directory |
| WSL2 (CLI only) | `~/.personas/` (WSL side) | Better I/O performance |
| WSL2 (CLI + Desktop) | `/mnt/c/Users/{WINUSER}/.personas/` + symlink from WSL `~/.personas/` | Both environments see the same files |
| Windows native (CLI or Desktop) | `%USERPROFILE%\.personas\` | Native Windows home |
| Cowork / Desktop session | **Workspace folder** — detect with `pwd` or workspace path, NOT `~` | `~` resolves to temp session filesystem that vanishes |

**Cowork detection:** If `$HOME` starts with `/sessions/` or the CWD is inside a temp path, you're in a Cowork session. Cowork runs in an isolated Linux VM — it can only access explicitly mounted folders and resolves symlinks to real paths (blocking escape). Find the actual workspace/mounted folder and write there instead.

**WSL2 + Desktop symlink:** When the user wants both CLI and Desktop, personas should live on the Windows side (`/mnt/c/Users/{WINUSER}/.personas/`) with a symlink from WSL's `~/.personas/`. **Important:** This symlink must be created from the WSL terminal, not from Cowork — Cowork cannot create symlinks to paths outside its mounted folders. Tell the user to run:
```bash
ln -s /mnt/c/Users/{WINUSER}/.personas ~/.personas
```

Create the directory structure:

```bash
mkdir -p ~/.personas/{name}/{.claude/output-styles,.claude/hooks,skills,tools,docs,user/memory}
```

### Phase 4: Build core files

**4a. Write CLAUDE.md**

Use the template from `references/claude-md-template.md`. Key decisions:

- **Personality**: Be specific about traits and anti-patterns. Give it opinions
- **Workspace Hygiene section**: Include it — every persona must maintain its own workspace
- **Self-Improvement**: Point to the self-improve skill (one line, not inline)

**4b. Create user/profile.md**

Use `references/profile-template.md` as a starting point and customize it for this persona's domain:
- Rename/add/remove sections to fit the domain (e.g., a finance persona needs "Accounts & Assets", a chef persona needs "Dietary Restrictions")
- Update placeholders to be domain-specific
- Update the interview instructions comment with persona-specific guidance on what to ask and how to probe deeper

Write directly to `user/profile.md`. On first session, the SessionStart hook reads this, sees the unfilled placeholders, and interviews the user to populate each section in place. No separate template file needed — the profile IS the template until it's filled out.

**Important: Use AskUserQuestion for the profile interview.** The persona should use the `AskUserQuestion` tool (not just conversation) when interviewing the user to fill out their profile. This provides a structured input experience — the user sees a clear question with context, rather than a wall of conversational text. Add this to the interview instructions in the template:
```
Use AskUserQuestion to ask each section's questions — one section at a time.
Present what you're asking about and why, then let the user respond.
```

**4d. Create first domain skill(s)**

Write at least one skill under `skills/{domain}/{skill-name}/SKILL.md` with:
- YAML frontmatter (name, description, triggers)
- Step-by-step workflow
- Expected output format

**4e. Copy self-improve skill**

Copy `references/self-improve-skill.md` to `skills/self-improve/SKILL.md`. Replace `{name}` with the persona name. This ships with every persona — it handles memory management, rule promotion, skill creation, tool discovery, and periodic audits.

**4f. Set up hooks**

Copy `references/hooks-template.json` to `hooks.json` in the persona root. Copy `references/public-repo-guard.sh` to `.claude/hooks/public-repo-guard.sh` and make it executable (`chmod +x`). These hooks:
- **PreToolUse** (command, matcher: Bash): Runs `public-repo-guard.sh` before git commit/push — checks if the repo is public and blocks if personal data (`user/`, `.mcp.json`, secrets) would be exposed. Every persona gets this by default
- **SessionStart** (command): Injects instruction to read `user/profile.md` and interview the user if unfilled. No dependencies — just echoes a JSON instruction for Claude to act on. Must be `type: "command"` (SessionStart only supports command hooks)
- **Stop** (prompt): Reminds the persona to update memory before ending
- **StopFailure** (command): Writes a crash marker to `user/memory/.last-crash` when a session dies from an API error. PostCompact and the next SessionStart can detect this and offer to recover lost context
- **PreCompact** (prompt): Saves session context to memory before compaction
- **PostCompact** (command): After compaction, checks for the crash marker and reminds the persona to review what may have been lost

**4g. Create .gitignore**

Copy `references/gitignore-template` to `.gitignore`.

**4h. Configure sandbox**

Copy `references/settings-template.json` to `.claude/settings.json`. Add any persona-specific network domains for MCP servers to `allowedDomains`. The template includes `extraKnownMarketplaces` and `enabledPlugins` to auto-install persona-manager — this gives every persona access to persona-dev for self-evolution without manual plugin installation.

Also create `.claude/settings.local.json` with the memory directory setting:
```json
{
  "autoMemoryDirectory": "user/memory"
}
```
**Important:** `autoMemoryDirectory` must be in `settings.local.json`, not `settings.json`. Claude Code ignores this setting in project settings (`.claude/settings.json`) as a security measure — it only works from local or user settings. The `settings.local.json` file is gitignored, so persona-dev must create it during setup on each machine.

**4i. Create README.md**

Every persona repo gets a short README. Keep it minimal — this isn't a library, it's a personal assistant:

```markdown
# {PersonaName} {emoji}

> {One-line role description}

A self-evolving AI persona built on [Claude Code](https://claude.com/claude-code) using the [personas](https://github.com/kickinrad/personas) framework.

## Usage

```bash
{name}              # interactive session
{name} "do weekly"  # one-shot prompt
```

## Setup

See the [personas framework](https://github.com/kickinrad/personas) for installation and setup.
```

For **public repos**, consider adding a brief "What it does" section describing the persona's domain and skills.

**4j. Validate scaffold**

Before proceeding, verify all required files exist:
- [ ] `README.md`
- [ ] `CLAUDE.md`
- [ ] `user/profile.md` (template with placeholders, ready for first-session interview)
- [ ] `hooks.json`
- [ ] `.claude/hooks/public-repo-guard.sh` (executable)
- [ ] `.gitignore`
- [ ] `.claude/settings.json`
- [ ] `skills/self-improve/SKILL.md`
- [ ] At least one domain skill in `skills/`

If anything is missing, fix it now — don't proceed with gaps.

### Phase 5: Configure integrations

If Phase 2 identified useful tools and integrations:

1. Document everything in CLAUDE.md under "Tools & Integrations" — organized by type (MCP servers, CLI tools, APIs, scripts)
2. For MCP servers: add domains to `.claude/settings.json` → `network.allowedDomains`, tell the user how to configure `.mcp.json` (gitignored — secrets go here)
3. For CLI tools: add usage instructions to relevant skills or CLAUDE.md
4. For APIs: create wrapper scripts in `tools/` or document usage patterns in skills
5. For skills: write the SKILL.md files that wrap tool usage into complete workflows
6. For agents: create agent definitions in `.claude/agents/` with appropriate system prompts and tool access
7. For hooks: add entries to `hooks.json` for domain-specific behavioral automation
8. For scripts: write to `tools/`, make executable, add brief comment header
9. For expansion packs: ask the user if they want to install them now

### Phase 6: Initialize git + GitHub sync

```bash
cd ~/.personas/{name}
git init
git add -A
git commit -m "feat({name}): initial scaffold"
```

**Always ask about GitHub sync** — don't skip this step:
- "Want to set up a GitHub repo so this persona syncs across machines?"
- If yes: `gh repo create {github-username}/{name} --private --source=. --push`
- If no: Skip — can always add a remote later
- Explain the benefit: backup, version history, sharing between CLI/Desktop/machines

**After creating the repo, set description and topics:**
```bash
gh repo edit --description "{PersonaName} — {one-line role description}. A self-evolving AI persona on Claude Code."
gh repo edit --add-topic claude-code --add-topic persona
```
Add 1-2 domain-specific topics too (e.g., `finance`, `cooking`, `fitness`).

**Public vs private — the persona handles this, not the user:**
- **Private repo (default):** Safe to commit everything including `user/` (profile, memories). Good for personal backup and cross-machine sync
- **Public repo:** If the user chooses public (or says "make it public"), the persona MUST immediately:
  1. Uncomment `user/` in `.gitignore`
  2. Remove `user/` from git tracking: `git rm -r --cached user/`
  3. Commit the change: `git commit -m "fix({name}): gitignore user/ for public repo"`
  4. Create a fresh remote (don't push existing history that may contain personal data)
- **Going public later:** If the self-improve skill or the user detects the repo has gone public, the persona handles the same steps automatically — don't ask the user to do it manually, they'll forget. The `public-repo-guard.sh` hook is the safety net, but the persona should proactively fix the gitignore rather than waiting for the hook to block

**Never commit these to any repo (public or private):**
- `.mcp.json` — contains API keys and secrets (always gitignored)
- Files matching `*.env`, `*.secret`, `*.key`, `*.pem` — credential files

### Phase 7: Configure launch flags

Before setting up aliases or Desktop access, determine the right CLI flags for this persona. Autodetect the environment, present defaults, and walk the user through customization.

**Step 1: Autodetect environment**

```bash
# Detect OS and sandbox support
if [[ "$(uname -s)" == "Darwin" ]]; then
  OS="macOS"         # Seatbelt built-in, sandbox always available
  SANDBOX_OK=true
elif grep -qi microsoft /proc/version 2>/dev/null; then
  OS="WSL2"          # bubblewrap needed
  SANDBOX_OK=$(command -v bwrap &>/dev/null && echo true || echo false)
elif [[ "$(uname -s)" == "Linux" ]]; then
  OS="Linux"         # bubblewrap needed
  SANDBOX_OK=$(command -v bwrap &>/dev/null && echo true || echo false)
elif [[ "$OS" == "Windows_NT" ]] || command -v cmd.exe &>/dev/null; then
  OS="Windows"       # No sandbox support
  SANDBOX_OK=false
fi
```

If sandbox prerequisites are missing on Linux/WSL2, tell the user:
```bash
sudo apt-get install bubblewrap socat  # Ubuntu/Debian
sudo dnf install bubblewrap socat      # Fedora
```

**Step 2: Present default flags and walk through customization**

Present the detected config and walk the user through each flag using `AskUserQuestion`. Explain what each one does, why it matters, and the tradeoff. **All flags are optional** — the user decides:

| Flag | What it does | Ask the user |
|------|-------------|--------------|
| `--name {name}` | Sets the session display name in the terminal title and prompt bar. Makes it easy to identify which persona is running | Always include — uses the persona name. No need to ask |
| `--setting-sources project,local` | Loads only this persona's settings.json, ignoring global `~/.claude/settings.json`. Keeps permissions, sandbox, and MCP config isolated to this persona | "This keeps your persona isolated from your global Claude config. Recommended ON unless you want global settings to merge in. Enable?" |
| `--dangerously-skip-permissions` | Skips permission prompts for every tool use. **Only safe when OS-level sandbox is active** (macOS/Linux/WSL2) — the sandbox restricts filesystem + network even without prompts. **NEVER on Windows** | "This lets the persona work without asking permission for every action. It's safe because the sandbox restricts what it can access. Want autonomous mode, or prefer to approve actions manually?" |
| `--remote-control` | Enables browser extension integration and external tool connections | "This allows tools like the Chrome extension to connect to your persona. Enable?" |
| `--chrome` | Enables Claude in Chrome browser automation. Gives the persona access to your Chrome browser for web interaction, form filling, screenshots, and debugging | "This lets the persona interact with your Chrome browser (requires the Claude in Chrome extension). Does this persona need browser access?" |

**Resulting flag sets by environment (defaults, all customizable):**

| Environment | Sandbox? | Default flags |
|-------------|----------|---------------|
| macOS | Yes (Seatbelt) | `--name {name} --setting-sources project,local --dangerously-skip-permissions --remote-control` |
| Linux | Yes (bubblewrap) | `--name {name} --setting-sources project,local --dangerously-skip-permissions --remote-control` |
| WSL2 | Yes (bubblewrap) | `--name {name} --setting-sources project,local --dangerously-skip-permissions --remote-control` |
| Windows native | **No** | `--name {name} --setting-sources project,local --remote-control` |

`--name` is always included with the persona's name — it labels the session in the terminal title and prompt bar. `--chrome` is not in the defaults but is always offered as an optional addition during the walkthrough.

---

**⚠ WINDOWS NATIVE — CRITICAL SAFETY WARNING ⚠**

**NEVER use `--dangerously-skip-permissions` on Windows native.** Windows does not have OS-level sandboxing (no Seatbelt, no bubblewrap). This flag would give the persona **completely unrestricted access** to the entire filesystem and network — it could read any file, delete anything, and make arbitrary network requests with zero guardrails.

On macOS/Linux/WSL2, `--dangerously-skip-permissions` is safe because the sandbox blocks dangerous operations at the OS level even when permissions are skipped. On Windows, there is no such safety net.

**If the user asks to enable it on Windows, refuse and explain why.** Even if they insist. This is not a preference — it's a safety boundary. The persona-dev skill must enforce this by never writing `--dangerously-skip-permissions` to `.claude-flags` on Windows native, regardless of user request.

---

Present defaults first, then offer customization via `AskUserQuestion`:
1. Show the recommended flag set for the detected OS environment (from the table above)
2. Briefly explain what each flag does in plain language
3. Ask: "These are the recommended defaults for your {OS} setup. Look good, or want to customize?"
4. If the user wants to customize, walk through each flag individually using `AskUserQuestion` — use the "Ask the user" column from the table above
5. `--chrome` is always presented as an optional addition: "Want to add Chrome browser automation? This lets the persona interact with web pages in your Chrome browser (requires the Claude in Chrome extension)."
6. On Windows, explain why `--dangerously-skip-permissions` is not available before moving on
7. Summarize the final chosen flags before writing to `.claude-flags`

**Step 3: Store the flags**

Write the chosen flags into `~/.personas/{name}/.claude-flags` (a single line, sourced by the alias):

```bash
echo '--name {name} --setting-sources project,local --dangerously-skip-permissions --remote-control' > ~/.personas/{name}/.claude-flags
```

This file is read by `.aliases.sh` so each persona can have its own flag configuration.

### Phase 8: Configure access + verify

Setup depends on the environment detected in Phase 1:

**CLI (macOS / Linux / WSL2) — shell aliases:**

1. **Create `~/.personas/.aliases.sh`** if it doesn't exist (see [CLI Aliases](#cli-aliases) below for the template)
2. **Add source line to the user's shell config** if not already present:
   - Detect the user's shell from `$SHELL`
   - For zsh: append to `~/.zshrc`
   - For bash: append to `~/.bashrc`
   - The line to add: `[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"`
   - **Check first** — only add if the line isn't already there
3. **Tell the user** to restart their shell or run `source ~/.personas/.aliases.sh` to activate immediately

**Windows native (no WSL) — PowerShell function:**

Windows users without WSL can't use bash aliases. Create a PowerShell function instead:

```powershell
# Add to $PROFILE (e.g., ~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1)
function {name} {
    param([Parameter(ValueFromRemainingArguments)]$args)
    Push-Location "$env:USERPROFILE\.personas\{name}"
    if ($args) {
        claude --name {name} --setting-sources project,local --remote-control -p ($args -join ' ')
    } else {
        claude --name {name} --setting-sources project,local --remote-control
    }
    Pop-Location
}
```

Note: no `--dangerously-skip-permissions` — Windows has no sandbox.

**Desktop (macOS + Windows only):**

Desktop is not available on Linux — Linux users are CLI-only.

1. Tell the user to select `~/.personas/{name}/` as their project folder in Claude Desktop
2. If MCP servers were configured in `.mcp.json`, offer to merge them into `claude_desktop_config.json`:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
3. Remind user to restart Claude Desktop after config changes
4. Note: Desktop Code tab reads `.mcp.json` (same as CLI), but Desktop Chat and Cowork read only `claude_desktop_config.json` — MCP servers need to be in both for full coverage

**Important environment limitations:**
- **Cowork** runs in an isolated Linux VM (Apple Silicon only) — can only access explicitly mounted folders, blocks symlinks outside scope. Reads MCP from `claude_desktop_config.json` (global), not `.mcp.json`. Cross-environment setup (WSL symlinks, Desktop config merges) must be done from a terminal, not Cowork.
- **Desktop Chat** is NOT sandboxed (server-side processing) — no direct filesystem access. MCP servers must be in `claude_desktop_config.json`.
- **Desktop Code tab** IS sandboxed (OS-level: Seatbelt on macOS, bubblewrap on Linux/WSL2) — reads `.mcp.json` from the project.
- **Windows native** does NOT support sandboxing — never use `--dangerously-skip-permissions`.

Then verify the persona works — run through the [Testing a Persona](#testing-a-persona) checklist.

---

## Three-Layer Model

Every persona uses three layers — never mix them:

| Layer | File | Who Writes | Content |
|-------|------|-----------|---------|
| **Personality** | `CLAUDE.md` | Human (Claude proposes) | Role, rules, skills, communication style |
| **Context** | `user/profile.md` | Claude (from user interview, via AskUserQuestion) | Personal data, accounts, preferences |
| **Memory** | `user/memory/` | Claude (automatic via autoMemoryDirectory in settings.local.json) + Stop/PreCompact hooks | Session outcomes, learnings, patterns |

---

## Profile.md vs Memory — Canonical Definitions

| Question | Answer | File |
|----------|--------|------|
| Will this be true next month without action? | Yes | `user/profile.md` |
| Did Claude discover or decide this? | Yes | `user/memory/MEMORY.md` |
| Should this always happen, every session? | Yes | `CLAUDE.md` rule |

**user/profile.md** = WHO you are, WHAT you have, HOW you like to work. Stable facts.
**user/memory/MEMORY.md** = WHAT HAPPENED, WHAT WAS DECIDED, WHAT WORKED. Dynamic learnings.
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

  # Read per-persona flags, or fall back to safe defaults
  if [ -f "${_persona_dir}.claude-flags" ]; then
    _flags=$(cat "${_persona_dir}.claude-flags")
  else
    _flags="--setting-sources project,local --remote-control"
  fi

  eval "${_persona_name}() {
    local _f=\"${_flags}\"
    if [ \$# -gt 0 ]; then
      (cd \"${_persona_dir}\" && claude \$_f -p \"\$*\")
    else
      (cd \"${_persona_dir}\" && claude \$_f)
    fi
  }"
done
unset _persona_dir _persona_name _flags
```

**Source from your shell config** (add to `~/.zshrc` or `~/.bashrc`):

```bash
[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"
```

After creating or updating a persona: `source ~/.personas/.aliases.sh` or restart your shell.

**Usage:**
- `{name}` — interactive session
- `{name} "do weekly review"` — one-shot prompt

**Per-persona flags:** Each persona stores its flags in `.claude-flags` (a single line). This is configured during Phase 7 (flag setup). If the file is missing, the alias falls back to safe defaults (no `--dangerously-skip-permissions`).

**What the flags do:**
- `--name {name}` — labels the session in the terminal title and prompt bar so you know which persona is running
- `--setting-sources project,local` — loads only the persona's CLAUDE.md and .claude/settings.json (ignores global config)
- `--dangerously-skip-permissions` — skips permission prompts. **Only safe when sandbox is enabled** (macOS/Linux/WSL2). Never use on Windows native
- `--remote-control` — enables browser extension and external tool integration (Claude in Chrome, etc.)

---

## First Session Flow

On first session, `user/profile.md` contains an unfilled template with placeholders and interview instructions. The SessionStart hook reads it, sees the placeholders, and uses `AskUserQuestion` to interview the user section by section. The persona follows the interview instructions embedded in the file to ask the right questions and fill out the profile in place.

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
| Dashboard | `persona-manager:persona-dashboard` | Visual dashboard (HTML), task tracking, open.sh | Personas with ongoing work, reviews, regular check-ins |

These are separate skills in persona-manager — invoke them when the user asks for the capability, or suggest them during Phase 2 (Research) when creating a persona.

During self-audits, personas can also discover expansion packs that would help with recurring needs.

---

## Testing a Persona

After creation, verify:

- [ ] Run `{name}` — does the SessionStart hook read `user/profile.md` (or trigger the interview if unfilled)?
- [ ] Try each skill trigger — does the right skill activate?
- [ ] Ask something outside its domain — does it redirect gracefully?
- [ ] End a session — does it write meaningful learnings to `user/memory/`?
- [ ] Check sandbox — `ls ../` from within the persona should fail

Test with adversarial prompts too — ask the persona to do something it shouldn't. A good persona redirects gracefully rather than blindly complying.

---

## Troubleshooting

**"command not found" when typing a persona name:**
- Shell aliases not loaded — run `source ~/.personas/.aliases.sh`
- Check that `~/.personas/{name}/CLAUDE.md` exists (the alias script requires it)

**Persona doesn't pick up profile:**
- Verify the file exists: `ls ~/.personas/{name}/user/profile.md`
- Check that hooks.json includes the SessionStart hook (reads user/profile.md automatically)

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
