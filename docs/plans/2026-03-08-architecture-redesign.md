# Architecture Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Separate the personas framework (persona-manager) from individual personas, moving personas to `~/.personas/` with independent git repos.

**Architecture:** The `kickinrad/personas` repo becomes framework-only (persona-manager plugin + docs). Each persona (warren, julia, mila) gets copied into `~/.personas/{name}/` with its own git repo. Shell aliases updated to scan the new location.

**Tech Stack:** bash, git, jq, zsh

---

### Task 1: Create `~/.personas/` and Migrate Warren

**Files:**
- Create: `~/.personas/warren/` (full directory copy)
- Create: `~/.personas/warren/.gitignore`

**Step 1: Create the personas home directory**

Run: `mkdir -p ~/.personas`

**Step 2: Copy warren files to new location**

Run:
```bash
cp -r ~/projects/personal/personas/plugins/warren/ ~/.personas/warren/
```

**Step 3: Create per-persona `.gitignore`**

Write `~/.personas/warren/.gitignore`:

```
# Private data — never commit
profile.md
.mcp.json
.claude/memory/
.claude/settings.local.json

# Local databases
*.db
*.db-shm
*.db-wal

# Generated files
*.log
dashboard.html
investments.md

# OS
.DS_Store
```

**Step 4: Initialize git repo and make initial commit**

Run:
```bash
cd ~/.personas/warren
git init
git add -A
git commit -m "feat(warren): initial commit — migrated from monorepo"
```

**Step 5: Verify the repo looks right**

Run: `cd ~/.personas/warren && git status && git log --oneline`
Expected: Clean working tree, one initial commit.

---

### Task 2: Migrate Julia

**Files:**
- Create: `~/.personas/julia/` (full directory copy)
- Create: `~/.personas/julia/.gitignore`

**Step 1: Copy julia files**

Run: `cp -r ~/projects/personal/personas/plugins/julia/ ~/.personas/julia/`

**Step 2: Create per-persona `.gitignore`**

Write `~/.personas/julia/.gitignore`:

```
# Private data — never commit
profile.md
.mcp.json
.claude/memory/
.claude/settings.local.json

# Local databases
*.db
*.db-shm
*.db-wal

# Generated files
*.log

# OS
.DS_Store
```

**Step 3: Initialize git repo and commit**

Run:
```bash
cd ~/.personas/julia
git init
git add -A
git commit -m "feat(julia): initial commit — migrated from monorepo"
```

**Step 4: Verify**

Run: `cd ~/.personas/julia && git status && git log --oneline`

---

### Task 3: Migrate Mila

**Files:**
- Create: `~/.personas/mila/` (full directory copy)
- Create: `~/.personas/mila/.gitignore`

**Step 1: Copy mila files**

Run: `cp -r ~/projects/personal/personas/plugins/mila/ ~/.personas/mila/`

**Step 2: Create per-persona `.gitignore`**

Write `~/.personas/mila/.gitignore`:

```
# Private data — never commit
profile.md
.mcp.json
.claude/memory/
.claude/settings.local.json

# Local databases
*.db
*.db-shm
*.db-wal

# Generated files
*.log

# OS
.DS_Store
```

**Step 3: Initialize git repo and commit**

Run:
```bash
cd ~/.personas/mila
git init
git add -A
git commit -m "feat(mila): initial commit — migrated from monorepo"
```

**Step 4: Verify**

Run: `cd ~/.personas/mila && git status && git log --oneline`

---

### Task 4: Update Self-Management Paths in Each Persona's CLAUDE.md

Each persona's CLAUDE.md references `~/projects/personal/personas/plugins/{name}/` as its home. These need updating to `~/.personas/{name}/`.

**Files:**
- Modify: `~/.personas/warren/CLAUDE.md` — replace old path references
- Modify: `~/.personas/julia/CLAUDE.md` — replace old path references
- Modify: `~/.personas/mila/CLAUDE.md` — replace old path references

**Step 1: Find and replace path references in warren's CLAUDE.md**

Search for `~/projects/personal/personas/plugins/warren` and replace with `~/.personas/warren`. Also search for generic `~/projects/personal/personas/plugins/{name}` patterns.

**Step 2: Repeat for julia and mila**

Same find-and-replace in each persona's CLAUDE.md.

**Step 3: Also update any `open.sh` scripts**

Warren has `scripts/` with shell scripts that may reference the old path. Check and update:
```bash
grep -r "projects/personal/personas" ~/.personas/warren/scripts/ 2>/dev/null
grep -r "projects/personal/personas" ~/.personas/julia/scripts/ 2>/dev/null
grep -r "projects/personal/personas" ~/.personas/mila/scripts/ 2>/dev/null
```

**Step 4: Commit in each persona repo**

Run in each `~/.personas/{name}/`:
```bash
git add -A
git commit -m "fix: update paths from monorepo to ~/.personas/"
```

---

### Task 5: Update Shell Aliases

**Files:**
- Modify: `~/.config/zsh/.personas.zsh`

**Step 1: Update the personas root path**

Change line 3 from:
```bash
_PERSONAS_ROOT="$HOME/projects/personal/personas/plugins"
```
to:
```bash
_PERSONAS_ROOT="$HOME/.personas"
```

**Step 2: Verify the alias file still works**

Run: `source ~/.config/zsh/.personas.zsh && type warren`
Expected: `warren is a shell function`

**Step 3: Add to chezmoi tracking**

Run:
```bash
chezmoi add ~/.config/zsh/.personas.zsh
```

**Step 4: Commit chezmoi change**

Run:
```bash
chezmoi cd && git add -A && git commit -m "fix(personas): update alias path to ~/.personas/" && popd
```

---

### Task 6: Strip Personas from Framework Repo

**Files:**
- Delete: `plugins/julia/` directory
- Delete: `plugins/warren/` directory
- Delete: `plugins/mila/` directory
- Modify: `.claude-plugin/marketplace.json` — remove persona entries
- Modify: `.gitignore` — simplify (no more `plugins/*` persona rules)

**Step 1: Remove persona directories**

Run from `~/projects/personal/personas/`:
```bash
git rm -r plugins/julia/ plugins/warren/ plugins/mila/
```

**Step 2: Update marketplace.json**

Replace contents of `.claude-plugin/marketplace.json` with:
```json
{
  "name": "personas",
  "owner": { "name": "kickinrad", "url": "https://github.com/kickinrad" },
  "metadata": {
    "description": "Framework for self-evolving AI personas on Claude Code",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "persona-manager",
      "source": "./plugins/persona-manager",
      "description": "Scaffolds and manages AI personas in ~/.personas/",
      "version": "1.0.4",
      "category": "management"
    }
  ]
}
```

**Step 3: Simplify `.gitignore`**

Replace contents with:
```
.DS_Store
.worktrees/
*.log
*.local.json
*.local.md
```

The persona-specific gitignore rules are no longer needed — each persona owns its own `.gitignore`.

**Step 4: Commit**

Run:
```bash
git add -A
git commit -m "refactor(framework): remove personas — they now live in ~/.personas/"
```

---

### Task 7: Update persona-manager Skills

**Files:**
- Modify: `plugins/persona-manager/skills/persona-dev/SKILL.md`
- Modify: `plugins/persona-manager/skills/deploy/SKILL.md`
- Modify: `plugins/persona-manager/skills/publish/SKILL.md`
- Modify: `plugins/persona-manager/skill-rules.json`

**Step 1: Update persona-dev skill**

Key changes:
- Scaffolding target: `~/.personas/{name}/` (not `plugins/{name}/`)
- Remove step "Add entry to marketplace.json" — personas are independent
- Remove "Bump version in both plugin.json AND marketplace.json" — just plugin.json
- Update the CLAUDE.md template's self-management section: path is `~/.personas/{name}/`
- Update CLI aliases section: `_PERSONAS_ROOT="$HOME/.personas"`
- The self-management path reference changes from `~/projects/personal/personas/plugins/{name}/` to `~/.personas/{name}/`
- Add step: "Initialize git repo in the new persona directory"
- Add step: "Create .gitignore from template"

**Step 2: Update deploy skill**

Change persona source path references from `plugins/{name}/` to `~/.personas/{name}/`.

**Step 3: Update publish skill**

This skill needs rethinking — personas are now independent repos, not part of the marketplace. Update to:
- Remove marketplace.json steps
- Add "push persona repo to remote" steps
- Update commit paths

**Step 4: Update skill-rules.json**

Change `fileTriggers.pathPatterns` from `["**/personas/plugins/**"]` to `["**/.personas/**"]`.

**Step 5: Commit**

Run:
```bash
git add -A
git commit -m "feat(persona-manager): update skills for ~/.personas/ architecture"
```

---

### Task 8: Update Framework CLAUDE.md and README.md

**Files:**
- Modify: `CLAUDE.md` (repo root)
- Modify: `README.md`

**Step 1: Update CLAUDE.md**

Key changes:
- Architecture diagram: remove persona directories, show `~/.personas/` as external
- Persona structure section: reference `~/.personas/{name}/` instead of `plugins/{name}/`
- CLI aliases section: update path
- Remove persona-specific gitignore documentation
- Update "Running Personas" — alias function points to `~/.personas/`
- Update lifecycle table — persona-dev scaffolds to `~/.personas/`
- Gitignored section: simplify to framework-only rules
- Remove luna references if any remain

**Step 2: Update README.md**

Key changes:
- Quick Start: clone is just the framework, personas are created via persona-manager
- Available Personas section: show only persona-manager as built-in; mention personas are scaffolded to `~/.personas/`
- Project Structure: show framework-only structure
- "Create Your Own" section: update to show `~/.personas/` output
- Contributing: update for new architecture

**Step 3: Commit**

Run:
```bash
git add -A
git commit -m "docs(framework): update docs for ~/.personas/ architecture"
```

---

### Task 9: Update Tests

**Files:**
- Modify: `tests/personas-test.sh`

**Step 1: Update test script**

The test currently scans `$REPO_ROOT/plugins/` for persona plugins. After migration, only persona-manager remains. Update:
- Remove version sync check against marketplace.json persona entries (only persona-manager remains)
- Keep persona-manager validation (plugin.json, skill frontmatter)
- Optionally add a new test that scans `~/.personas/*/` if the directory exists (validates migrated personas have proper structure)

**Step 2: Run the updated tests**

Run: `bash tests/personas-test.sh`
Expected: All checks pass with only persona-manager tested.

**Step 3: Commit**

Run:
```bash
git add -A
git commit -m "test(framework): adapt tests for framework-only repo"
```

---

### Task 10: Update Framework Docs

**Files:**
- Modify: `docs/getting-started.md`
- Modify: `docs/creating-personas.md`
- Modify: `docs/self-improvement.md`
- Modify: `docs/remote-deployment.md`

**Step 1: Update getting-started.md**

- Clone is just the framework
- `persona-manager` scaffolds personas into `~/.personas/`
- Profile setup happens in `~/.personas/{name}/profile.md`

**Step 2: Update creating-personas.md**

- Manual scaffolding target is `~/.personas/{name}/`
- Each persona gets its own `.gitignore` and `git init`
- No marketplace.json entry needed

**Step 3: Update self-improvement.md**

- Path references from `plugins/{name}/` to `~/.personas/{name}/`
- Commits go to persona's own repo

**Step 4: Update remote-deployment.md**

- Source path is `~/.personas/{name}/` (already mostly correct)
- Remove any `plugins/` path references

**Step 5: Commit**

Run:
```bash
git add -A
git commit -m "docs(framework): update all guides for ~/.personas/ architecture"
```

---

### Task 11: Final Verification

**Step 1: Run framework tests**

Run: `cd ~/projects/personal/personas && bash tests/personas-test.sh`
Expected: All pass (persona-manager only).

**Step 2: Verify shell aliases work**

Run:
```bash
source ~/.config/zsh/.personas.zsh
type warren && type julia && type mila
```
Expected: All three are shell functions.

**Step 3: Verify persona repos are clean**

Run:
```bash
for p in warren julia mila; do
  echo "=== $p ==="
  cd ~/.personas/$p && git status && git log --oneline
  cd -
done
```
Expected: Clean working trees, initial commits present.

**Step 4: Smoke test a persona**

Run: `cd ~/.personas/warren && ls CLAUDE.md .claude/settings.json skills/`
Expected: All core files present.

**Step 5: Verify no secrets leaked**

Run:
```bash
for p in warren julia mila; do
  echo "=== $p ==="
  cd ~/.personas/$p
  git log --all --diff-filter=A --name-only --pretty=format: | sort -u | grep -E '(profile\.md|\.mcp\.json|memory/)' || echo "clean"
  cd -
done
```
Expected: "clean" for all three — no secrets in git history.
