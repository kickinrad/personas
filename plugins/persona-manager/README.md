# Persona Manager

Meta-tool for creating and evolving self-improving AI personas built on Claude Code. Scaffolds `~/.personas/{name}/` directories with identity, sandbox, hooks, skills, memory, and MCP config — then keeps them in sync as the framework evolves.

## Quick Start

```
# First time: install from marketplace
/plugin marketplace add kickinrad/personas
/plugin install persona-manager@personas

# Create a persona
/persona-manager:persona-dev

# Update an existing persona
/persona-manager:persona-update
```

Every persona auto-installs persona-manager via `enabledPlugins` in its settings.json, so the skills are always available from within a persona session too.

## Skills

### persona-dev

Guided 8-phase persona creation workflow:

1. **Discovery** — role, personality, voice, workflows, environment
2. **Research** — MCP servers, CLI tools, APIs, integrations
3. **Scaffold** — directory structure with cross-platform detection
4. **Build Core Files** — CLAUDE.md, profile, hooks, sandbox, skills
5. **Configure Integrations** — MCP, tools, expansion packs
6. **Initialize Git** — repo setup, optional GitHub sync
7. **Configure Launch Flags** — OS-aware flag selection (sandbox safety)
8. **Configure Access** — shell aliases, Desktop setup, verification

**Trigger examples:** "create a persona", "build me a persona for finance", "add a skill to my persona", "my persona should remember this"

### persona-update

Template-diffing update system that detects drift between a persona and the current framework version:

- Compares hooks, settings, gitignore, guard script, and self-improve skill against templates
- Classifies differences as framework additions, changes, or persona customizations
- Merges intelligently — never overwrites personality, custom skills, or user data
- Stamps `.framework-version` after applying changes

**Trigger examples:** "update persona", "check for updates", "persona drift", "sync with framework"

## Agents

### persona-validator

Autonomous health checker that validates persona directories. Runs three categories of checks:

- **Structure** — all required files/dirs exist, JSON parses cleanly, hooks.json has all 6 events, settings.json has correct sandbox config
- **Drift** — `.framework-version` matches current plugin version
- **Security** — `.mcp.json` gitignored, `user/` handling correct for repo visibility, no secrets in tracked files

Triggers proactively after persona-dev scaffolds a new persona, or on demand.

**Trigger examples:** "validate my persona", "check persona health", "is my persona set up correctly"

## What Gets Scaffolded

Each persona is a self-contained directory with:

| Component | Purpose |
|-----------|---------|
| `CLAUDE.md` | Identity, personality, rules |
| `.claude/settings.json` | OS-level sandbox config |
| `.claude/output-styles/` | Voice and tone |
| `user/profile.md` | User context (filled via interview) |
| `user/memory/` | Native auto-memory |
| `skills/self-improve/` | 4-level evolution workflow |
| `hooks.json` | SessionStart, Stop, crash recovery, public repo guard |
| `.mcp.json` | External service integrations |
| `.claude-flags` | Per-persona CLI launch flags |

## Key Patterns

- **Template-based scaffolding** — all persona files generated from `references/` templates
- **Three-layer model** — Personality (CLAUDE.md) + Context (profile.md) + Memory (auto)
- **Four-level evolution** — Memory → Rule promotion → Skill creation → Tool discovery
- **Platform-aware** — handles macOS, Linux, WSL2, Windows native, and Cowork
- **Safety-first** — `--dangerously-skip-permissions` never used on Windows native; public repo guard blocks personal data exposure

## Reference Templates

Located in `skills/persona-dev/references/`:

| Template | Generates |
|----------|-----------|
| `claude-md-template.md` | Persona identity file |
| `profile-template.md` | User interview template |
| `hooks-template.json` | 6 lifecycle hooks |
| `settings-template.json` | Sandbox + marketplace config |
| `output-style-template.md` | Voice/personality style |
| `self-improve-skill.md` | Self-improvement workflow |
| `public-repo-guard.sh` | Git commit/push safety hook |
| `gitignore-template` | Standard .gitignore entries |
