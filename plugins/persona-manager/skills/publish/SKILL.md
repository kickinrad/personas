---
name: publish
description: Publish a persona to a remote git repository. Use when user wants to share a persona, push a persona to GitHub, or make a persona available publicly.
---

# Publish Persona

## Prerequisites

- Persona must have all committed files ready (CLAUDE.md, plugin.json, skills/, profile.md.example)
- No personal data in committed files
- Working profile.md.example template
- Persona has its own git repo at `~/.personas/{name}/`

## Pre-Publish Checklist

Before publishing, verify:

1. **No secrets in committed files**
   ```bash
   grep -r "eyJ\|GOCSPX\|sk-\|password\|secret" ~/.personas/{name}/ --include="*.md" --include="*.json" | grep -v node_modules | grep -v .mcp.json
   ```

2. **No personal data in CLAUDE.md** — should contain personality/rules only, not specific names/accounts/figures

3. **profile.md.example exists** with clear placeholder instructions

4. **plugin.json has correct version** — bump if needed

5. **Sandbox config exists** at `.claude/settings.json`

6. **.gitignore covers sensitive files** — profile.md, .mcp.json, .claude/memory/

## Publish Steps

### Step 1: Bump Version

Update version in `~/.personas/{name}/.claude-plugin/plugin.json`.

### Step 2: Commit Changes

```bash
cd ~/.personas/{name}
git add -A
git commit -m "chore({name}): bump to v{version}"
```

### Step 3: Push to Remote

If no remote exists yet, create a GitHub repo and add the remote:

```bash
cd ~/.personas/{name}
gh repo create {owner}/{name}-persona --public --source=. --push
```

If remote already exists:

```bash
cd ~/.personas/{name}
git push
```

### Step 4: Announce (Optional)

Share the repo URL. Users can clone directly:

```bash
git clone https://github.com/{owner}/{name}-persona ~/.personas/{name}
```
