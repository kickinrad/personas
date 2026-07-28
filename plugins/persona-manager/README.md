# Persona Manager

Claude-native lifecycle procedures plus a portable deterministic validator for
persona homes.

## Skills

- `persona-dev` — discover, plan, create, or deliberately extend one persona.
- `persona-update` — reconcile framework mechanics while preserving persona
  identity, voice, local role procedure, configuration, and user data.
- `self-improve` — canonical persona-local improvement procedure served by this
  plugin. A copied `.claude/skills/self-improve/` is invalid.

## Validation

```bash
${CLAUDE_PLUGIN_ROOT}/bin/validate-persona /path/to/persona
```

The validator performs read-only structural, JSON, sandbox, memory-path,
gitignore, hook, version, duplicate-skill, and secret-pattern checks. It is a
deterministic command, not a durable model-pinned agent identity. A runtime may
add a fresh internal reviewer when judgment is needed.

## Source resolution

Skills use `${CLAUDE_PLUGIN_ROOT}` and sibling references. The framework update
notice is a plugin hook at `hooks/framework-version.sh`, which resolves its
manifest relative to its own executable path.

## Ownership

This plugin owns lifecycle mechanics, templates, validation, and runtime
declarations. It does not own persona identity or voice, user knowledge, system
topology, or vault current state. Runtime support and gaps are declared in
`interop/capabilities.json`.
