# Scenario 07: Update Migration

Verify that `persona-dev update` detects drift between an existing persona and the current framework, proposes fixes, and applies them correctly.

## Grader Type

LLM-judge + Code-based

## Setup

Create a deliberately outdated test persona with these drift points:
- `hooks.json` missing `PostCompact` and `PreCompact` hooks (only has 4 of 6)
- `.claude-flags` missing `--name` flag (old format without it)
- `.claude/settings.json` missing `enabledPlugins` entry (old format)
- `.claude/settings.json` using old plugin name format
- `skills/self-improve/SKILL.md` has outdated content (missing workspace hygiene section)
- `.gitignore` missing `*.local.json` pattern

## Prompt

```
Run persona-dev update to check this persona for drift against the latest framework.
```

## Assertions

### LLM-judge
- [ ] The update skill detected the missing `PostCompact` and `PreCompact` hooks
- [ ] The update skill detected the missing `--name` flag in `.claude-flags`
- [ ] The update skill detected the missing/outdated `enabledPlugins` in settings.json
- [ ] The update skill explained WHY each change matters (not just "this is missing")
- [ ] The update skill proposed changes one at a time (not a bulk "fix everything")
- [ ] The update skill waited for approval before applying each change

### Code-based (after applying all proposed changes)
- [ ] `hooks.json` now has all 6 hook types
- [ ] `.claude-flags` contains `--name` flag with persona name
- [ ] `.claude/settings.json` has `enabledPlugins["persona-manager@personas"]: true`
- [ ] `.gitignore` includes `*.local.json`
- [ ] All JSON files are still valid JSON after modifications
- [ ] No existing persona customizations were overwritten (custom skills, profile data, memory preserved)

## Critical constraint

The update must NEVER overwrite persona-specific content:
- Custom CLAUDE.md personality/rules (only add missing framework sections)
- Custom skills (only update self-improve)
- user/profile.md and user/memory/ (never touch)
- .mcp.json (never touch)
- Custom output styles (never touch)
