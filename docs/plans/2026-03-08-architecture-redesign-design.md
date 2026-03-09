# Architecture Redesign: Separate Framework from Personas

**Date:** 2026-03-08
**Status:** Approved

## Problem

The current monorepo (`kickinrad/personas`) serves too many roles: framework, marketplace, plugin manager, and personal personas. This creates:
- Shared git history across unrelated personas
- Framework changes tangled with persona content
- Awkward nesting (`plugins/{name}/`)
- Distribution concerns — can't cleanly share the framework without exposing personal personas

## Design

### Separation of Concerns

**`kickinrad/personas` (GitHub)** — framework only:
- persona-manager plugin (skills: persona-dev, deploy, publish)
- Framework documentation, tests, marketplace.json
- No persona directories

**`~/.personas/` (local)** — persona runtime home:
- Not a git repo itself, just a directory
- Each persona is its own subdirectory with its own git repo
- Personas can optionally be pushed to any remote (or stay local-only)

### Framework Repo Structure

```
kickinrad/personas/
├── .claude-plugin/
│   └── marketplace.json               # Only lists persona-manager
├── plugins/
│   └── persona-manager/
│       ├── .claude-plugin/plugin.json
│       ├── skill-rules.json
│       └── skills/
│           ├── persona-dev/SKILL.md   # Scaffolds into ~/.personas/
│           ├── deploy/SKILL.md
│           └── publish/SKILL.md
├── CLAUDE.md
├── README.md
├── docs/
└── tests/
```

### Individual Persona Structure

Each persona at `~/.personas/{name}/`:

```
~/.personas/{name}/
├── .git/                              # Own git repo
├── .gitignore                         # Own ignore rules
├── .claude-plugin/plugin.json
├── CLAUDE.md                          # Personality + rules (committed)
├── profile.md.example                 # Template (committed)
├── profile.md                         # User data (gitignored)
├── .mcp.json                          # Secrets (gitignored)
├── .claude/
│   ├── settings.json                  # Sandbox (committed)
│   └── memory/                        # Auto-memory (gitignored)
├── skills/
├── docs/
└── scripts/
```

### Shell Integration

Update `~/.config/zsh/.personas.zsh`:

```bash
_PERSONAS_ROOT="$HOME/.personas"    # was ~/projects/personal/personas/plugins
```

Auto-discovery logic stays the same — scans for directories containing `CLAUDE.md`.

### What Changes

| Aspect | Before | After |
|--------|--------|-------|
| Framework + personas | One monorepo | `kickinrad/personas` = framework only |
| Persona location | `~/projects/personal/personas/plugins/{name}/` | `~/.personas/{name}/` |
| Persona git | Shared history in monorepo | Each has own git repo |
| persona-manager | Bundled with personas | Standalone plugin, own marketplace |
| Shell aliases | Same approach | Same, just new path |

### What Stays the Same

- How you invoke personas (`warren`, `julia "plan meals"`)
- Three-layer model (personality / context / memory)
- Sandboxing via `.claude/settings.json`
- MCP config pattern (`.mcp.json`, gitignored)
- Self-improvement model (5 levels)
- Remote deployment (rsync source path changes)
- `--setting-sources project --dangerously-skip-permissions` flags

## Migration

1. Create `~/.personas/` directory
2. Copy warren, julia, mila files into `~/.personas/{name}/`
3. Each gets `git init`, proper `.gitignore`, initial commit
4. Remove persona directories from `kickinrad/personas`
5. Trim `marketplace.json` to persona-manager only
6. Update framework `CLAUDE.md` and `README.md`
7. Update persona-manager skills to target `~/.personas/`
8. Update tests for new structure
9. Update `~/.config/zsh/.personas.zsh` path
