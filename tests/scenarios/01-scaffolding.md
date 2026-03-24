# Scenario 01: Scaffolding Validation

Verify that persona-dev creates a complete, valid persona directory structure.

## Grader Type

Code-based (file existence, JSON validity, content checks)

## Setup

- Clean `~/.personas/test-eval-persona/` directory (delete if exists)
- persona-dev skill available via persona-manager plugin

## Prompt

```
Create a persona named "test-eval-persona" with these specs:
- Role: Test evaluation assistant
- Personality: Friendly, concise, helpful
- Domain: Software testing
- Skills: One domain skill called "run-checks" that validates test outputs
- Environment: Linux CLI only
- No MCP servers needed
- Private repo, no GitHub sync
- Accept all default flags
```

## Assertions

### Structure (code-checkable)
- [ ] `~/.personas/test-eval-persona/` directory exists
- [ ] `CLAUDE.md` exists and is non-empty
- [ ] `README.md` exists
- [ ] `user/profile.md` exists with template placeholders
- [ ] `user/memory/` directory exists
- [ ] `user/memory/MEMORY.md` exists
- [ ] `.gitignore` exists
- [ ] `.claude/settings.json` exists and contains valid JSON
- [ ] `.claude/settings.local.json` exists with `autoMemoryDirectory` key
- [ ] `.claude/output-styles/` directory exists
- [ ] `.claude/hooks/public-repo-guard.sh` exists and is executable
- [ ] `hooks.json` exists and contains valid JSON
- [ ] `skills/self-improve/SKILL.md` exists with YAML frontmatter
- [ ] `skills/testing/run-checks/SKILL.md` exists with YAML frontmatter (or similar domain path)
- [ ] `docs/` directory exists
- [ ] `tools/` directory exists

### Content (code-checkable)
- [ ] `hooks.json` has exactly 6 hook types: PreToolUse, SessionStart, Stop, StopFailure, PreCompact, PostCompact
- [ ] `hooks.json` PreToolUse has matcher "Bash" and references `public-repo-guard.sh`
- [ ] `hooks.json` SessionStart is type "command" and mentions `user/profile.md`
- [ ] `.claude/settings.json` has `sandbox.enabled: true`
- [ ] `.claude/settings.json` has `extraKnownMarketplaces.personas` entry
- [ ] `.claude/settings.json` has `enabledPlugins["persona-manager@personas"]: true`
- [ ] `.claude/settings.local.json` has `autoMemoryDirectory` set to an absolute path ending in `/user/memory`
- [ ] `.claude-flags` exists and contains `--name test-eval-persona`
- [ ] `.claude-flags` contains `--setting-sources project,local`
- [ ] `.gitignore` includes `.mcp.json`
- [ ] `.gitignore` includes `.claude/settings.local.json`
- [ ] Git repo is initialized (`~/.personas/test-eval-persona/.git/` exists)

## Teardown

Remove `~/.personas/test-eval-persona/` after eval completes.
