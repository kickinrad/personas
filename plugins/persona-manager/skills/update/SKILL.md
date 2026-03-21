---
name: update
description: Detect drift between an existing persona and the current framework version. Checks hooks, flags, settings, skills, and gitignore for missing or outdated entries. Proposes and applies fixes with approval. Use when a persona seems outdated, after framework updates, or for periodic maintenance.
triggers:
  - update persona
  - check for updates
  - persona drift
  - sync with framework
  - update hooks
  - persona maintenance
---

# Persona Update

Detects framework drift in an existing persona and proposes targeted fixes. Safe by design — only touches framework-provided files, never overwrites persona-specific content.

## What This Skill Does NOT Touch

These are persona-specific and must never be overwritten:
- `CLAUDE.md` personality, rules, skills table (only CHECK for missing framework sections)
- Custom skills in `skills/{domain}/`
- `user/profile.md`, `user/memory/`
- `.mcp.json`
- `.claude/output-styles/`
- Persona-specific `allowedDomains` in settings.json

---

## Version Manifest (Framework v1.5.0)

This is the canonical reference for what the current framework expects. Each check below compares the persona's files against these expectations.

### Required Hooks (hooks.json)

All 6 hooks must be present:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/public-repo-guard.sh",
            "timeout": 10000
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "type": "command",
        "command": "echo '{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\"Read user/profile.md now. If it contains unfilled template placeholders, use AskUserQuestion to interview the user section by section and populate each section (see Session Start in CLAUDE.md). If already filled out but incomplete, ask the user to fill in the gaps before proceeding. Then check MCP tool availability.\"}}'",
        "timeout": 5000
      }
    ],
    "Stop": [
      {
        "type": "prompt",
        "prompt": "Before ending: if anything meaningful happened this session (decisions, corrections, discoveries, preferences), update user/memory/ with relevant entries. Keep entries concise — one insight per memory file topic. Skip if nothing worth remembering occurred."
      }
    ],
    "StopFailure": [
      {
        "type": "command",
        "command": "date -Iseconds > user/memory/.last-crash 2>/dev/null; exit 0",
        "timeout": 3000
      }
    ],
    "PreCompact": [
      {
        "type": "prompt",
        "prompt": "Context is about to be compacted. Summarize any important session context that hasn't been written to user/memory/ yet. Write it now so it survives compaction."
      }
    ],
    "PostCompact": [
      {
        "type": "command",
        "command": "echo '{\"hookSpecificOutput\":{\"hookEventName\":\"PostCompact\",\"additionalContext\":\"Context was just compacted. Check user/memory/.last-crash — if it exists, a previous session ended unexpectedly. Read it, offer to review what was lost, then delete the marker.\"}}'",
        "timeout": 3000
      }
    ]
  }
}
```

**Hook content patterns to verify:**
- SessionStart: must use `echo` with JSON (not `cat | jq`), must mention `user/profile.md`, must mention `AskUserQuestion`
- StopFailure: must write to `user/memory/.last-crash`
- PostCompact: must check for `.last-crash`
- PreToolUse: must reference `public-repo-guard.sh`

### Required Flags (.claude-flags)

| Flag | Required? | Notes |
|------|-----------|-------|
| `--name {persona}` | Yes | Added in framework v1.4.0. Labels terminal title/prompt bar |
| `--setting-sources project,local` | Yes | Isolates persona settings |
| `--dangerously-skip-permissions` | Conditional | Only on macOS/Linux/WSL2 (never Windows native) |
| `--remote-control` | Optional | Recommended but persona's choice |
| `--chrome` | Optional | Only if persona uses browser |

### Required Settings Keys (.claude/settings.json)

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
      "allowedDomains": ["api.anthropic.com"]
    }
  },
  "extraKnownMarketplaces": {
    "personas": {
      "source": {
        "source": "github",
        "repo": "kickinrad/personas"
      }
    }
  },
  "enabledPlugins": {
    "persona-manager@personas": true
  }
}
```

**Settings checks:**
- `extraKnownMarketplaces` must exist (added in framework v1.4.0 — enables auto-install of persona-manager)
- `enabledPlugins` must include `persona-manager@personas`
- `enabledPlugins` must NOT contain `remote-deploy@personas` (renamed to `persona-remote@personas`)
- `sandbox.enabled` must be `true`
- `sandbox.autoAllowBashIfSandboxed` must be `true`
- `sandbox.filesystem.denyRead` must include `"../"` (sandbox escape prevention)

### Required Gitignore Patterns

These patterns must be present in `.gitignore`:

| Pattern | Purpose |
|---------|---------|
| `.mcp.json` | API keys and secrets |
| `.claude/settings.local.json` | Local overrides |
| `*.local.json` | Local config variants |
| `*.local.md` | Local config variants |
| `*.log` | Log files |
| `.DS_Store` | macOS metadata |
| `Thumbs.db` | Windows metadata |

### Required Files

| File | Must exist | Must be executable |
|------|-----------|-------------------|
| `.claude/hooks/public-repo-guard.sh` | Yes | Yes |
| `.claude/settings.local.json` | Yes | No |
| `skills/self-improve/SKILL.md` | Yes | No |
| `hooks.json` | Yes | No |
| `.claude/settings.json` | Yes | No |
| `.gitignore` | Yes | No |

### Settings.local.json

Must contain:
```json
{
  "autoMemoryDirectory": "user/memory"
}
```

---

## Execution Workflow

### Step 1: Identify the Persona

Determine which persona to update:

1. Check if CWD is inside `~/.personas/{name}/` — if so, update this persona (self-update mode)
2. If not, ask the user which persona to update: `ls ~/.personas/`
3. Store the persona path: `PERSONA_DIR=~/.personas/{name}`

### Step 2: Detection Phase

Read each file and compare against the version manifest. Build a list of drift points.

**Check order matters** — go from least invasive to most:

#### 2a. Check hooks.json

```
Read: $PERSONA_DIR/hooks.json
```

Check for:
- **Missing hooks**: Compare top-level keys against required set (PreToolUse, SessionStart, Stop, StopFailure, PreCompact, PostCompact). Most common drift: StopFailure and PostCompact missing
- **Outdated SessionStart**: If the command contains `cat user/profile.md` or `jq -Rs`, it's the old format. The new format uses a simple `echo` with JSON — it's dependency-free (no jq needed) and mentions MCP tool availability
- **Outdated Stop hook**: If the prompt is persona-customized (e.g., mentions domain-specific things like "contractor experiences, house quirks"), preserve those additions — only flag if the base structure is wrong
- **Missing PreToolUse matcher**: Must have `"matcher": "Bash"` — older personas might have it differently

#### 2b. Check .claude-flags

```
Read: $PERSONA_DIR/.claude-flags
```

Check for:
- **Missing `--name` flag**: Added in framework v1.4.0. The persona name should match the directory name
- **Missing `--setting-sources`**: Should be present for isolation
- **`--dangerously-skip-permissions` on Windows**: Check OS — if Windows, this flag must not be present

#### 2c. Check .claude/settings.json

```
Read: $PERSONA_DIR/.claude/settings.json
```

Check for:
- **Missing `extraKnownMarketplaces`**: Added in v1.4.0 for auto-install
- **Missing `enabledPlugins`**: Must include `persona-manager@personas`
- **Old plugin name `remote-deploy@personas`**: Renamed to `persona-remote@personas`
- **Missing sandbox keys**: Check for `enabled`, `autoAllowBashIfSandboxed`, `filesystem.denyRead` containing `"../"`
- **DO NOT touch `allowedDomains`**: These are persona-specific

#### 2d. Check .gitignore

```
Read: $PERSONA_DIR/.gitignore
```

Check for missing required patterns. Don't reorder or reformat existing entries — only add missing ones.

#### 2e. Check required files exist

- `.claude/hooks/public-repo-guard.sh` — must exist and be executable
- `.claude/settings.local.json` — must exist with `autoMemoryDirectory`
- `skills/self-improve/SKILL.md` — must exist

#### 2f. Check self-improve skill currency

```
Read: $PERSONA_DIR/skills/self-improve/SKILL.md
```

Compare against the current template at `plugins/persona-manager/skills/persona-dev/references/self-improve-skill.md`. Check for:
- Missing sections (e.g., scheduled tasks, expansion packs, agents)
- Outdated tool discovery table
- Missing workspace hygiene items

**Note:** The self-improve skill may have a persona-specific first line (e.g., "This persona lives at `~/.personas/bob/`"). Preserve that — only check for missing framework content.

#### 2g. Check CLAUDE.md framework sections

```
Read: $PERSONA_DIR/CLAUDE.md
```

**Only check for missing framework sections — NEVER rewrite personality or rules.** Look for:
- Missing "Session Start" section (or outdated version that doesn't mention AskUserQuestion)
- Missing "Workspace Hygiene" or workspace organization guidance
- Missing self-improve skill reference

### Step 3: Diff Display

For each drift point found, present a clear summary:

```
## Drift Report for {name}

### 1. Missing StopFailure hook
**Current:** Not present in hooks.json
**Expected:** StopFailure hook that writes crash marker to user/memory/.last-crash
**Why it matters:** Without this, crash recovery doesn't work. If a session dies from an
API error, the next session has no way to know context was lost. The StopFailure hook
writes a timestamp marker that PostCompact and SessionStart can detect.
**Change:** Add StopFailure entry to hooks.json

### 2. Missing PostCompact hook
**Current:** Not present in hooks.json
**Expected:** PostCompact hook that checks for crash marker
**Why it matters:** After context compaction, the persona loses track of what happened.
PostCompact checks for the crash marker from StopFailure and reminds the persona to
review what may have been lost — enabling crash recovery.
**Change:** Add PostCompact entry to hooks.json

### 3. Outdated SessionStart hook
**Current:** Uses `cat user/profile.md | jq -Rs` (depends on jq, doesn't mention MCP)
**Expected:** Simple `echo` with JSON instruction (dependency-free, mentions MCP check)
**Why it matters:** The old format breaks if jq isn't installed, and doesn't prompt the
persona to check MCP tool availability on session start.
**Change:** Replace SessionStart command with echo-based version

### 4. Missing --name flag in .claude-flags
**Current:** --setting-sources project,local --dangerously-skip-permissions --remote-control
**Expected:** --name {name} --setting-sources project,local ...
**Why it matters:** The --name flag labels the terminal title and prompt bar so you can
tell which persona is running. Added in framework v1.4.0.
**Change:** Prepend --name {name} to .claude-flags

### 5. Missing extraKnownMarketplaces in settings.json
**Current:** Not present
**Expected:** extraKnownMarketplaces pointing to kickinrad/personas
**Why it matters:** Without this, the persona can't auto-install persona-manager from the
marketplace. Users have to manually run /plugin marketplace add each time.
**Change:** Add extraKnownMarketplaces to settings.json

...
```

Present the full report before proposing changes. Give the user a complete picture.

### Step 4: Proposal Phase

After showing the full drift report, propose changes **one at a time**:

```
I found {N} drift points. Let me walk through each fix.

### Fix 1 of {N}: Add StopFailure hook

I'll add this to hooks.json:

  "StopFailure": [
    {
      "type": "command",
      "command": "date -Iseconds > user/memory/.last-crash 2>/dev/null; exit 0",
      "timeout": 3000
    }
  ]

This merges into your existing hooks — nothing else changes.

Apply this fix? (yes / skip / apply all remaining)
```

Use `AskUserQuestion` for each approval. Accept these responses:
- **yes / y / apply** — apply this fix, move to next
- **skip / no / n** — skip this fix, move to next
- **all / apply all / yes to all** — apply this and all remaining fixes without asking

### Step 5: Apply Phase

For each approved fix:

1. **Read the current file** (fresh read — don't rely on cached content)
2. **Apply the specific change:**
   - For hooks.json: parse JSON, merge the new hook, write back. Preserve existing hooks and any persona-specific customizations (like domain-specific Stop prompts)
   - For .claude-flags: prepend/append the missing flag. Preserve existing flags
   - For settings.json: parse JSON, deep-merge missing keys. NEVER touch `allowedDomains` or persona-specific `enabledPlugins`
   - For .gitignore: append missing patterns at the end, grouped under a comment
   - For missing files: copy from framework references
3. **Verify the change:** Re-read the file and confirm the change is present
4. **Report:** "Applied fix {N}: {description}"

**JSON editing safety:** When editing hooks.json or settings.json:
- Read the file fresh
- Parse with `jq` to validate before and after
- If the file has trailing commas or formatting issues, fix them
- Never manually construct JSON by string concatenation — use `jq` for merges

### Step 6: Verification Phase

After all changes are applied (or skipped):

1. **Validate JSON files:**
   ```bash
   jq . hooks.json > /dev/null 2>&1 && echo "hooks.json: valid" || echo "hooks.json: INVALID"
   jq . .claude/settings.json > /dev/null 2>&1 && echo "settings.json: valid" || echo "settings.json: INVALID"
   ```

2. **Check file permissions:**
   ```bash
   test -x .claude/hooks/public-repo-guard.sh && echo "guard: executable" || echo "guard: NOT executable"
   ```

3. **Verify no persona-specific content was lost:**
   - Check that custom `allowedDomains` are still present in settings.json
   - Check that custom `enabledPlugins` (like `persona-dashboard@personas`) are still present
   - Check that custom Stop hook prompt additions are preserved
   - Check that CLAUDE.md personality sections are unchanged

4. **Summary:**
   ```
   ## Update Complete

   Applied: {N} fixes
   Skipped: {M} fixes
   Errors: {E}

   ### Changes Applied
   - Added StopFailure hook (crash recovery)
   - Added PostCompact hook (compaction recovery)
   - Updated SessionStart hook (dependency-free, MCP check)
   - Added --name flag to .claude-flags
   - Added extraKnownMarketplaces to settings.json

   ### Skipped
   - Self-improve skill update (user chose to skip)

   ### Verification
   - hooks.json: valid JSON
   - settings.json: valid JSON
   - public-repo-guard.sh: executable
   - Custom allowedDomains: preserved (7 entries)
   - Custom enabledPlugins: preserved (3 entries)

   Commit these changes? (The persona should commit its own updates)
   ```

5. If the user approves a commit:
   ```bash
   git add hooks.json .claude-flags .claude/settings.json .gitignore
   git commit -m "chore({name}): update to framework v1.5.0"
   ```

---

## Common Drift Patterns

Based on real deployed personas, these are the most common issues:

| Drift | Affected | Fix |
|-------|----------|-----|
| Missing StopFailure hook | All pre-v1.3.0 personas | Add hook to hooks.json |
| Missing PostCompact hook | All pre-v1.3.0 personas | Add hook to hooks.json |
| Old SessionStart (cat\|jq) | All pre-v1.4.0 personas | Replace with echo-based command |
| Missing --name flag | All pre-v1.4.0 personas | Prepend to .claude-flags |
| Missing extraKnownMarketplaces | All pre-v1.4.0 personas | Add to settings.json |
| Old plugin name remote-deploy | Personas with remote deploy | Rename to persona-remote in enabledPlugins |
| Missing .DS_Store / Thumbs.db in gitignore | Some personas | Append to .gitignore |
| Stale self-improve skill | Personas created before v1.3.0 | Update from current template (preserve persona name) |

---

## Running This Skill

This skill can be invoked in two ways:

### Self-update (persona runs it on itself)
The persona is running in its own directory (`~/.personas/{name}/`). CWD is already the persona root. The persona detects drift in its own files and proposes fixes.

### Cross-update (from the framework repo or another context)
The user asks to update a specific persona or all personas. The skill asks which persona to target, then operates on `~/.personas/{name}/`.

### Batch mode
To update all personas:
1. List personas: `ls ~/.personas/`
2. Run detection on each
3. Present a combined drift report
4. Apply fixes per-persona with approval
