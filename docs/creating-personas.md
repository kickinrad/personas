# Creating Personas

This guide covers how to build a custom persona from scratch, from scaffolding to publishing.

## Option 1: Using persona-manager

The fastest way to create a persona:

```bash
persona-manager "create a fitness coach persona"
```

The persona-manager skill will:
1. Scaffold the directory structure
2. Generate a `CLAUDE.md` with your described personality
3. Create a `profile.md.example` template
4. Set up `plugin.json` and sandbox config
5. Add it to the marketplace registry

## Option 2: Manual Scaffolding

### Directory Structure

Create the following under `plugins/`:

```
plugins/your-persona/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── .claude/
│   └── settings.json        # Sandbox configuration
├── CLAUDE.md                # Personality and rules
├── profile.md.example       # Profile template for users
└── skills/
    └── {domain}/            # Skill files go here
```

### plugin.json

```json
{
  "name": "your-persona",
  "description": "One-line description of what this persona does.",
  "version": "1.0.0",
  "author": {
    "name": "your-github-username",
    "url": "https://github.com/your-github-username"
  }
}
```

### Sandbox Configuration (.claude/settings.json)

Every persona ships with a sandbox config that restricts filesystem and network access:

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
  }
}
```

Key settings:
- `allowWrite: ["."]` — the persona can only write to its own directory
- `denyRead: ["../"]` — it cannot read parent directories or other personas
- `allowedDomains` — whitelist network access per persona (add domains for your MCP servers)

## Writing a Good CLAUDE.md

The `CLAUDE.md` file defines your persona's personality, rules, and behavior. This is the most important file — it is loaded into context every session.

### Template

```markdown
# PersonaName

> **ABOUTME**: PersonaName is a {role} — {one-line personality}.
> **ABOUTME**: {What they do in one sentence.}

## Who I Am

{2-3 paragraphs establishing personality, expertise, and approach.
Keep it generic — no personal data about any specific user.}

## How I'll Be

- **Trait** — description
- **Trait** — description
- **Trait** — description

## What I Won't Do

- Anti-pattern this persona avoids
- Anti-pattern this persona avoids

## Session Start

If profile.md doesn't exist:
1. Copy profile.md.example to profile.md
2. Guide the user through filling it in
3. Do not proceed until profile is set up

**Every session:** Read `profile.md` before doing anything else.

**After reading profile.md:** Check which MCP tools are available.
For any disconnected server, tell the user what's unavailable
and ask: skip for now, or help set it up?

## Skills Auto-Activate

Skills in `skills/{domain}/` auto-load on trigger keywords:

| Say this... | Skill activates | What happens |
|-------------|-----------------|--------------|
| "trigger phrase" | `skill-name` | Description |

## MCP Tools Available

{List MCP servers this persona uses, grouped by server.}

## Memory

**Store when:** {What's worth remembering}
**Recall when:** {When to pull from memory}

## Self-Management

{See the Self-Management section below.}

## Important Rules

1. **Skills own the workflow** — follow skill procedures exactly
2. **Profile.md first** — read it every session
3. **Memory is domain-specific** — save meaningful insights
```

### Personality Design Tips

- **Be specific about traits.** "Warm and encouraging" is weaker than "Celebrates small wins, never judges kitchen mishaps."
- **Include anti-patterns.** "What I Won't Do" prevents the persona from drifting into generic assistant behavior.
- **Give it opinions.** The best personas push back on bad ideas rather than blindly agreeing.
- **Keep personality separate from data.** `CLAUDE.md` describes who the persona is. `profile.md` describes who the user is. Never mix them.
- **Test with adversarial prompts.** Ask the persona to do something outside its domain — it should redirect gracefully.

## The Three-Layer Model

Every persona uses three layers. Keeping them separate is critical:

| Layer | File | Who Writes | What Goes Here |
|-------|------|------------|----------------|
| **Personality** | `CLAUDE.md` | Human (Claude proposes) | Role, rules, skills, communication style |
| **Context** | `profile.md` | Human (guided by Claude) | Personal data, accounts, preferences |
| **Memory** | `.claude/memory/` | Claude (automatic) | Session outcomes, learnings, patterns |

**Rules of thumb:**
- Will this be true next month without any action? Put it in `profile.md`.
- Did Claude discover or decide this? Put it in `memory`.
- Should this always happen, every session? Make it a `CLAUDE.md` rule.

## Adding Skills

Skills are markdown files with YAML frontmatter that define multi-step workflows. They live under `skills/{domain}/{skill-name}/SKILL.md`.

### SKILL.md Format

```markdown
---
name: weekly-review
description: Weekly financial review — budget, cashflow, balances, action items.
triggers:
  - weekly review
  - how did we do
  - financial check-in
---

# Weekly Review

## Steps

1. Pull transaction data from the last 7 days
2. Compare spending to budget categories
3. Calculate savings rate
4. Identify anomalies or trends
5. Generate action items

## Output Format

{Describe the expected output structure.}
```

**Trigger keywords** in the YAML frontmatter tell the persona when to activate a skill. When a user says something matching a trigger, the persona loads and follows the skill's instructions.

### Skill Design Guidelines

- Each skill should be a complete, repeatable workflow
- Include specific steps, not vague guidance
- Define the expected output format
- Keep skills focused — one skill per workflow, not one mega-skill

## Adding MCP Servers

MCP servers give personas access to external services. Configure them in `.mcp.json` (gitignored):

```json
{
  "mcpServers": {
    "service-name": {
      "command": "npx",
      "args": ["-y", "@org/mcp-server-package"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

Then reference the MCP server's tools in your `CLAUDE.md` under "MCP Tools Available" so the persona knows what it can access.

Remember to add the MCP server's domains to `.claude/settings.json` under `network.allowedDomains`.

## Self-Management Section

Add this to every persona's `CLAUDE.md` to enable self-improvement:

```markdown
## Self-Management

### When to update what

| File | Update when | How |
|------|------------|-----|
| `profile.md` | Stable facts change | Propose, write with approval |
| `MEMORY.md` | Something worth remembering | Write directly |
| `CLAUDE.md` | A pattern should become permanent | Propose, write with approval |
| New skill file | A workflow recurs with no existing skill | Draft, propose to user |

### Pattern promotion

When you notice the same correction 3+ times across sessions,
propose making it a permanent rule in CLAUDE.md.
```

See [Self-Improvement](self-improvement.md) for the full model.

## Testing Your Persona

Run the included test suite to verify structure:

```bash
bash tests/personas-test.sh
```

This checks:
- `plugin.json` exists and has a version
- `CLAUDE.md` exists
- `profile.md.example` exists
- `.claude/settings.json` has sandbox enabled
- No `profile.md` or `.mcp.json` committed (these should be gitignored)

Manual testing checklist:
- [ ] Run an interactive session — does the persona read `profile.md`?
- [ ] Try each skill trigger — does the right skill activate?
- [ ] Ask something outside its domain — does it redirect gracefully?
- [ ] Check memory after a session — did it write meaningful learnings?
- [ ] Verify sandbox — can it access files outside its directory? (It should not.)

## Publishing to the Marketplace

To make your persona available to others:

1. Add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-persona",
  "source": "./plugins/your-persona",
  "description": "One-line description.",
  "version": "1.0.0",
  "category": "persona"
}
```

2. Make sure versions match in both `plugin.json` and `marketplace.json`.

3. Commit and push:

```bash
git add plugins/your-persona/ .claude-plugin/marketplace.json
git commit -m "feat(your-persona): add to marketplace"
git push
```

4. Others can then install it:

```bash
claude plugin install your-persona@personas
```

## Next Steps

- [Self-Improvement](self-improvement.md) — How the evolution engine works
- [Remote Deployment](remote-deployment.md) — Run personas on servers
