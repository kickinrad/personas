# Public Framework Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the private personas monorepo into a public, installable framework with native sandboxing, self-improvement, and zero custom tooling.

**Architecture:** Each persona is a Claude Code plugin distributed via marketplace. Isolation via `--setting-sources project` + native OS sandboxing. Self-improvement via CLAUDE.md behavioral instructions. Shell aliases for CLI access.

**Tech Stack:** Claude Code plugins, bubblewrap/Seatbelt sandbox, zsh, bash, git

---

## Pre-Flight

Before starting any task, back up all local data that won't survive a git history scrub:

```bash
# Create backup directory
mkdir -p ~/backups/personas-$(date +%Y%m%d)

# Back up all gitignored local data
for persona in julia warren mila; do
  dir="plugins/$persona"
  mkdir -p ~/backups/personas-$(date +%Y%m%d)/$persona

  # Profile (personal data)
  [[ -f "$dir/profile.md" ]] && cp "$dir/profile.md" ~/backups/personas-$(date +%Y%m%d)/$persona/

  # MCP config (API keys)
  [[ -f "$dir/.mcp.json" ]] && cp "$dir/.mcp.json" ~/backups/personas-$(date +%Y%m%d)/$persona/

  # Memory
  [[ -d "$dir/.claude/memory" ]] && cp -r "$dir/.claude/memory" ~/backups/personas-$(date +%Y%m%d)/$persona/

  # Local settings
  [[ -f "$dir/.claude/settings.local.json" ]] && cp "$dir/.claude/settings.local.json" ~/backups/personas-$(date +%Y%m%d)/$persona/
done

echo "Backup complete at ~/backups/personas-$(date +%Y%m%d)/"
```

Verify the backup before proceeding.

---

### Task 1: Fix .gitignore to Allow Sandbox Config

**Files:**
- Modify: `/.gitignore`

**Context:** Currently `.gitignore` has `plugins/*/.claude/` which blocks EVERYTHING in `.claude/` including the sandbox config we need committed. We need to be selective.

**Step 1: Read current .gitignore**

Run: `cat .gitignore`

**Step 2: Update .gitignore**

Replace the `plugins/*/.claude/` line with specific ignores:

```gitignore
# Per-persona local state (never commit)
plugins/*/.claude/memory/
plugins/*/.claude/settings.local.json
```

This allows `plugins/*/.claude/settings.json` (sandbox config) to be committed while keeping memory and local overrides gitignored.

**Step 3: Verify the change**

Run: `git status` — should now show `.claude/settings.json` files as trackable (once we create them).

**Step 4: Commit**

```bash
git add .gitignore
git commit -m "fix(framework): allow .claude/settings.json to be committed

Sandbox configs need to ship with personas. Only memory/ and
settings.local.json remain gitignored."
```

---

### Task 2: Create Sandbox Configs

**Files:**
- Create: `plugins/warren/.claude/settings.json`
- Create: `plugins/julia/.claude/settings.json`
- Create: `plugins/mila/.claude/settings.json`

**Context:** Each persona needs a committed `.claude/settings.json` with sandbox config. Network domains are persona-specific based on their MCP servers.

**Step 1: Create Warren's sandbox config**

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["."],
      "denyRead": ["~/.aws", "~/.ssh", "~/.gnupg", "../"]
    },
    "network": {
      "allowedDomains": [
        "api.anthropic.com",
        "*.googleapis.com",
        "*.monarchmoney.com",
        "*.finnhub.io",
        "*.alphavantage.co",
        "*.yahoo.com",
        "fc.yahoo.com"
      ]
    }
  }
}
```

**Step 2: Create Julia's sandbox config**

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["."],
      "denyRead": ["~/.aws", "~/.ssh", "~/.gnupg", "../"]
    },
    "network": {
      "allowedDomains": [
        "api.anthropic.com",
        "*.googleapis.com",
        "mealie.*.ts.net"
      ]
    }
  }
}
```

**Step 3: Create Mila's sandbox config**

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["."],
      "denyRead": ["~/.aws", "~/.ssh", "~/.gnupg", "../"]
    },
    "network": {
      "allowedDomains": [
        "api.anthropic.com",
        "*.googleapis.com"
      ]
    }
  }
}
```

**Step 4: Commit**

```bash
git add plugins/warren/.claude/settings.json plugins/julia/.claude/settings.json plugins/mila/.claude/settings.json
git commit -m "feat(framework): add native sandbox configs per persona

Each persona gets OS-level isolation (bubblewrap/Seatbelt):
- Full write to own directory only
- Blocked from parent dirs and sensitive system dirs
- Network whitelisted per persona's MCP server needs"
```

---

### Task 3: Update Shell Aliases

**Files:**
- Modify: `~/.config/zsh/.personas.zsh`

**Context:** Current aliases use `--mcp-config` and `--strict-mcp-config`. Replace with single `--setting-sources project` flag. Remove the auto-create `.mcp.json` stub logic (no longer needed — MCP loads from project scope automatically).

**Step 1: Read current file**

Run: `cat ~/.config/zsh/.personas.zsh`

**Step 2: Replace with simplified version**

```bash
# Persona aliases — auto-discover personas and create shell functions
# Each function cd's into the persona dir and runs claude with project-only settings
_PERSONAS_ROOT="$HOME/projects/personal/personas/plugins"

for _p_dir in "$_PERSONAS_ROOT"/*/; do
  [[ -d "$_p_dir" ]] || continue
  _p_name=$(basename "$_p_dir")
  [[ "$_p_name" == "persona-manager" ]] && continue
  [[ -f "${_p_dir}CLAUDE.md" ]] || continue

  eval "${_p_name}() {
    if [[ \$# -gt 0 ]]; then
      (cd \"${_p_dir}\" && claude --setting-sources project --dangerously-skip-permissions -p \"\$*\")
    else
      (cd \"${_p_dir}\" && claude --setting-sources project --dangerously-skip-permissions)
    fi
  }"
done
unset _PERSONAS_ROOT _p_dir _p_name
```

**Step 3: Reload and test**

```bash
source ~/.config/zsh/.personas.zsh
type warren  # Should show the function definition
```

**Step 4: No git commit** — this file lives in dotfiles repo, not personas repo. Just verify it works.

---

### Task 4: Fix Version Mismatches

**Files:**
- Modify: `plugins/warren/.claude-plugin/plugin.json`
- Modify: `plugins/julia/.claude-plugin/plugin.json`
- Modify: `plugins/mila/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Context:** plugin.json files say `0.0.0-dev` but marketplace says `1.1.0+`. Sync them. Also remove Luna from marketplace.

**Step 1: Read all plugin.json files to verify current state**

**Step 2: Update Warren's plugin.json version to `1.1.0`**

**Step 3: Update Julia's plugin.json version to `1.2.0`**

**Step 4: Update Mila's plugin.json version to `1.1.0`**

**Step 5: Update marketplace.json**

Remove Luna entry. Verify warren/julia/mila versions match their plugin.json files. Keep persona-manager at 1.0.4.

**Step 6: Run validation**

```bash
bash tests/personas-test.sh
```

Expected: All pass, no Luna references.

**Step 7: Commit**

```bash
git add plugins/warren/.claude-plugin/plugin.json plugins/julia/.claude-plugin/plugin.json plugins/mila/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "fix(framework): sync plugin versions and remove luna from marketplace

Warren: 1.1.0, Julia: 1.2.0, Mila: 1.1.0, Persona-manager: 1.0.4
Luna removed — persona was deleted."
```

---

### Task 5: Add Self-Improvement Instructions to Each Persona

**Files:**
- Modify: `plugins/warren/CLAUDE.md`
- Modify: `plugins/julia/CLAUDE.md`
- Modify: `plugins/mila/CLAUDE.md`

**Context:** Each persona's CLAUDE.md needs a standardized self-improvement section. This replaces hooks and custom machinery with behavioral instructions.

**Step 1: Read each persona's CLAUDE.md** to understand current structure.

**Step 2: Add Session Start section** (if not present) to each:

```markdown
## Session Start

If profile.md doesn't exist:
1. Copy profile.md.example to profile.md
2. Guide the user through filling it in
3. Do not proceed with other tasks until profile is set up
```

**Step 3: Add Self-Improvement section** to each:

```markdown
## Self-Improvement

You can and should evolve yourself across sessions. You have full write access to your own directory.

**After every session** — update .claude/memory/MEMORY.md with learnings.

**When you notice a pattern** (3+ corrections or repeated workflows):
1. Propose the change to the user (rule, skill, or tool)
2. On approval, create/edit the relevant files
3. Commit with: `git commit -m "improve(self): description"`

**What you can create:**
- `skills/{name}/SKILL.md` — new workflow skills
- `docs/{name}.md` — reference documentation
- `scripts/{name}.sh|.py` — utility scripts and tools
- Edits to your own `CLAUDE.md` — personality and rule updates
- Edits to `profile.md` — with user approval for personal data

**What requires user action:**
- Changes to `.mcp.json` (API keys, new services)
- `git push` / marketplace updates
- Version bumps in plugin.json
```

**Step 4: Review each file** — ensure no duplication with existing content, merge if overlapping sections exist.

**Step 5: Commit**

```bash
git add plugins/warren/CLAUDE.md plugins/julia/CLAUDE.md plugins/mila/CLAUDE.md
git commit -m "feat(framework): add self-improvement instructions to all personas

Standardized Session Start and Self-Improvement sections.
Personas can now create skills, tools, docs, and evolve their
own CLAUDE.md across sessions."
```

---

### Task 6: Scrub Personal Data from Committed Files

**Files:**
- Modify: `plugins/warren/CLAUDE.md` (remove financial specifics, account names, family details)
- Modify: `plugins/julia/CLAUDE.md` (remove household specifics)
- Modify: `plugins/mila/CLAUDE.md` (remove client names, project details, platform handles)
- Verify: all `profile.md` files are gitignored
- Verify: all `.mcp.json` files are gitignored
- Check: `plugins/warren/investments.md` — if committed, remove or gitignore
- Check: `plugins/warren/docs/` — scrub any financial specifics

**Context:** CLAUDE.md files define personality and rules (safe to commit) but currently contain references to specific people, accounts, and personal details that belong in profile.md.

**Step 1: Read each CLAUDE.md carefully**

Look for:
- Real names (family, fiancée, clients)
- Account numbers, policy numbers
- Specific financial figures
- Server URLs (internal Tailscale addresses)
- Client organization names
- Social media handles / platform stats

**Step 2: For each personal reference found:**

- If it's behavioral/personality → keep it (generic form)
- If it's factual/personal → replace with `[see profile.md]` reference
- If it's a client name → replace with generic description

Example:
```
BEFORE: "Sako's Vanguard IRA has $45k in VTSAX"
AFTER:  "Track all household investment accounts per profile.md"
```

**Step 3: Check warren/investments.md**

If committed, add to `.gitignore`:
```gitignore
plugins/warren/investments.md
```

**Step 4: Run `git status`** to verify no sensitive files are tracked.

**Step 5: Commit**

```bash
git add -A
git commit -m "security(framework): scrub personal data from committed files

Moved personal references to profile.md (gitignored).
CLAUDE.md files now contain only personality/behavioral rules."
```

---

### Task 7: Create persona-manager:deploy Skill

**Files:**
- Create: `plugins/persona-manager/skills/deploy/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: deploy
description: Deploy a persona to a remote server for scheduled autonomous execution. Use when user wants to run personas on a remote machine, set up cron jobs, or sync persona workspaces to a server.
---

# Deploy Persona to Remote Server

## Prerequisites

- Remote server accessible via SSH (ideally via Tailscale)
- Claude Code installed on remote server
- `rsync` available on both machines

## Workflow

### Step 1: Identify Target

Ask which persona and which remote host:
- Persona directory (e.g., `~/.personas/warren/` or `plugins/warren/`)
- Remote host (e.g., `cloud` via Tailscale, or full SSH address)

### Step 2: Sync Workspace

```bash
rsync -avz --exclude='.claude/memory/' {persona_dir}/ {host}:~/.personas/{name}/
```

Note: Exclude memory by default (remote builds its own). Include if user wants continuity.

### Step 3: Verify Remote Setup

```bash
ssh {host} 'which claude && claude --version'
ssh {host} 'ls ~/.personas/{name}/CLAUDE.md'
```

### Step 4: Set Up Scheduled Tasks

For each skill that should run on a schedule:

```bash
ssh {host} "crontab -l 2>/dev/null; echo '{schedule} cd ~/.personas/{name} && claude --setting-sources project --dangerously-skip-permissions -p \"{prompt}\"'" | ssh {host} 'crontab -'
```

Common schedules:
- `0 9 * * 1-5` — weekday mornings at 9 AM
- `0 9 * * 1` — Monday mornings at 9 AM
- `0 17 * * 1-5` — weekday evenings at 5 PM

### Step 5: Test Run

```bash
ssh {host} "cd ~/.personas/{name} && claude --setting-sources project --dangerously-skip-permissions -p 'confirm you can access your tools and profile'"
```

### Step 6: Set Up Memory Sync (Optional)

Add local cron to pull memory updates:

```bash
# Add to local crontab
0 */6 * * * rsync -avz {host}:~/.personas/{name}/.claude/memory/ {persona_dir}/.claude/memory/
```
```

**Step 2: Commit**

```bash
git add plugins/persona-manager/skills/deploy/SKILL.md
git commit -m "feat(persona-manager): add deploy skill for remote server setup"
```

---

### Task 8: Create persona-manager:publish Skill

**Files:**
- Create: `plugins/persona-manager/skills/publish/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: publish
description: Publish a private persona to the public marketplace. Use when user wants to share a persona, promote a private persona to public, or submit a persona to the marketplace.
---

# Publish Persona to Marketplace

## Prerequisites

- Persona must have all committed files ready (CLAUDE.md, plugin.json, skills/, profile.md.example)
- No personal data in committed files
- Working profile.md.example template

## Pre-Publish Checklist

Before publishing, verify:

1. **No secrets in committed files**
   ```bash
   grep -r "eyJ\|GOCSPX\|sk-\|password\|secret" plugins/{name}/ --include="*.md" --include="*.json" | grep -v node_modules | grep -v .mcp.json
   ```

2. **No personal data in CLAUDE.md** — should contain personality/rules only, not specific names/accounts/figures

3. **profile.md.example exists** with clear placeholder instructions

4. **plugin.json has correct version** — bump if needed:
   ```json
   { "version": "X.Y.Z" }
   ```

5. **Sandbox config exists** at `.claude/settings.json`

6. **.gitignore covers sensitive files** — profile.md, .mcp.json, .claude/memory/

## Publish Steps

### Step 1: Bump Version

Update version in `plugins/{name}/.claude-plugin/plugin.json`.

### Step 2: Add to Marketplace

Add entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "{name}",
  "description": "{one-line description}",
  "source": { "source": "relative", "path": "plugins/{name}" },
  "version": "{version}"
}
```

### Step 3: Commit and Push

```bash
git add plugins/{name}/ .claude-plugin/marketplace.json
git commit -m "feat(marketplace): publish {name} persona v{version}"
git push
```

### Step 4: Announce (Optional)

If publishing to a shared marketplace, consider opening a PR instead of pushing directly.

```bash
gh pr create --title "feat(marketplace): add {name} persona" --body "..."
```
```

**Step 2: Commit**

```bash
git add plugins/persona-manager/skills/publish/SKILL.md
git commit -m "feat(persona-manager): add publish skill for marketplace promotion"
```

---

### Task 9: Update Tests

**Files:**
- Modify: `tests/personas-test.sh`

**Context:** Update test script to also validate sandbox configs and version sync between plugin.json and marketplace.json.

**Step 1: Read current test script**

**Step 2: Add new validations**

Add these checks to the existing script:

```bash
# Check sandbox config exists for each persona
for dir in plugins/*/; do
  name=$(basename "$dir")
  [[ "$name" == "persona-manager" ]] && continue
  [[ ! -f "${dir}CLAUDE.md" ]] && continue

  if [[ -f "${dir}.claude/settings.json" ]]; then
    # Verify it contains sandbox config
    if grep -q '"sandbox"' "${dir}.claude/settings.json"; then
      pass "  $name: sandbox config present"
    else
      fail "  $name: .claude/settings.json missing sandbox key"
    fi
  else
    fail "  $name: missing .claude/settings.json (sandbox config)"
  fi
done

# Check version sync between plugin.json and marketplace.json
for dir in plugins/*/; do
  name=$(basename "$dir")
  plugin_version=$(jq -r '.version' "${dir}.claude-plugin/plugin.json" 2>/dev/null)
  marketplace_version=$(jq -r ".plugins[] | select(.name == \"$name\") | .version" .claude-plugin/marketplace.json 2>/dev/null)

  if [[ -n "$marketplace_version" && "$plugin_version" != "$marketplace_version" ]]; then
    fail "  $name: version mismatch — plugin.json=$plugin_version, marketplace=$marketplace_version"
  fi
done

# Check no secrets in committed files
for dir in plugins/*/; do
  name=$(basename "$dir")
  if grep -rq "eyJ\|GOCSPX\|sk-live\|BEGIN PRIVATE KEY" "$dir" --include="*.md" --include="*.json" 2>/dev/null | grep -v .mcp.json; then
    fail "  $name: possible secret in committed files!"
  else
    pass "  $name: no secrets detected in committed files"
  fi
done
```

**Step 3: Run tests**

```bash
bash tests/personas-test.sh
```

Expected: All pass (after previous tasks complete).

**Step 4: Commit**

```bash
git add tests/personas-test.sh
git commit -m "test(framework): add sandbox, version sync, and secret detection checks"
```

---

### Task 10: Scrub Git History

**Files:** None (git operation)

**Context:** Git history may contain accidentally committed secrets (OAuth tokens, JWT, API keys from when .mcp.json or profile.md were committed). This is the point of no return — force push required.

**Step 1: Check for secrets in history**

```bash
git log --all --diff-filter=A -- '*.json' '*.md' | head -30
git log --all -p -- plugins/*/.mcp.json | grep -i "eyJ\|GOCSPX\|secret\|token\|api.key" | head -20
git log --all -p -- plugins/*/profile.md | head -20
```

**Step 2: If secrets found, use git-filter-repo**

```bash
# Install if needed
pip install git-filter-repo

# Remove sensitive files from entire history
git filter-repo --path plugins/luna/ --invert-paths
git filter-repo --path-glob 'plugins/*/.mcp.json' --invert-paths
git filter-repo --path-glob 'plugins/*/profile.md' --invert-paths
```

**Step 3: Verify clean history**

```bash
git log --all -p | grep -i "GOCSPX\|eyJ.*\." | head -10
```

Expected: No matches.

**Step 4: Restore local files from backup**

```bash
for persona in julia warren mila; do
  cp ~/backups/personas-*/  $persona/profile.md plugins/$persona/ 2>/dev/null
  cp ~/backups/personas-*/$persona/.mcp.json plugins/$persona/ 2>/dev/null
  cp -r ~/backups/personas-*/$persona/memory plugins/$persona/.claude/ 2>/dev/null
done
```

**Step 5: Force push** (requires user confirmation)

```bash
git push --force-with-lease origin main
```

---

### Task 11: Write User-Facing Docs

**Files:**
- Modify: `README.md` (rewrite for public audience)
- Create: `docs/getting-started.md`
- Create: `docs/creating-personas.md`
- Create: `docs/self-improvement.md`
- Create: `docs/remote-deployment.md`

**Step 1: Rewrite README.md**

Public-facing README with:
- What personas are (1 paragraph)
- Quick start (5 steps)
- Available personas table
- Link to docs/ for details
- Contributing section

**Step 2: Write getting-started.md**

- Prerequisites (Claude Code installed, zsh)
- Install marketplace
- Install first persona
- Set up shell alias
- First session walkthrough
- Filling in profile.md

**Step 3: Write creating-personas.md**

- Using persona-manager skill
- Plugin structure explained
- Three-layer model
- Writing good CLAUDE.md personality docs
- Adding skills
- Adding MCP servers
- Testing your persona

**Step 4: Write self-improvement.md**

- How the 5-level system works
- Memory → Rules → Skills → Tools → Publish
- Examples of each level
- How to review persona evolution (`git log`)

**Step 5: Write remote-deployment.md**

- Prerequisites (SSH access, Claude Code on remote)
- Using persona-manager:deploy skill
- Manual setup guide
- Scheduled tasks with cron
- Memory sync
- Safety (sandbox + dangerously-skip-permissions)

**Step 6: Commit**

```bash
git add README.md docs/
git commit -m "docs(framework): add public documentation

Getting started, creating personas, self-improvement guide,
and remote deployment docs."
```

---

### Task 12: Final Validation and Go Public

**Step 1: Run full test suite**

```bash
bash tests/personas-test.sh
```

**Step 2: Verify no secrets in repo**

```bash
# Scan all committed files
git ls-files | xargs grep -l "eyJ\|GOCSPX\|sk-live\|BEGIN PRIVATE KEY\|password.*=" 2>/dev/null
```

Expected: No matches.

**Step 3: Verify gitignore coverage**

```bash
# These should NOT appear in git ls-files output
git ls-files | grep -E "profile\.md$|\.mcp\.json$|settings\.local\.json$|memory/"
```

Expected: No matches.

**Step 4: Test fresh clone experience**

```bash
cd /tmp
git clone ~/projects/personal/personas personas-test
cd personas-test
bash tests/personas-test.sh
```

**Step 5: Make repo public** (GitHub UI or CLI)

```bash
gh repo edit kickinrad/personas --visibility public
```

**Step 6: Celebrate** 🎉

---

## Task Dependency Graph

```
Task 1 (gitignore) ──→ Task 2 (sandbox configs)
                   ──→ Task 4 (version fix)
                   ──→ Task 6 (scrub data)

Task 3 (shell aliases) ── independent, do anytime

Task 5 (self-improvement) ── after reading CLAUDE.md files

Task 7 (deploy skill) ── independent
Task 8 (publish skill) ── independent

Task 9 (tests) ── after Tasks 2, 4

Task 10 (git history) ── after Task 6, LAST destructive step

Task 11 (docs) ── after all code changes

Task 12 (go public) ── after everything
```

**Parallelizable groups:**
- Group A: Tasks 1, 3, 7, 8 (independent)
- Group B: Tasks 2, 4, 5, 6 (after Task 1)
- Group C: Task 9 (after Group B)
- Group D: Task 10 (after Group C)
- Group E: Task 11 (after Group D)
- Group F: Task 12 (after everything)
