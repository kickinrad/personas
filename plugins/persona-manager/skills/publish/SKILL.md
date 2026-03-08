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

4. **plugin.json has correct version** — bump if needed

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
