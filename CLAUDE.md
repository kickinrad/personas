---
title: personas
---

# Persona framework

This repository contains framework mechanics for persona lifecycle, an optional
read-only viewer, and persona-state transport. Persona homes are external,
independent repositories and are evidence—not normalization targets.

## Authorities

- Framework source owns lifecycle mechanics, triggers, templates, deterministic
  validation, runtime declarations, and generated-adapter contracts.
- Persona homes own identity, voice, local role procedure, configuration, and
  cache.
- Vault notes own durable Wils knowledge, topology, current state, decisions,
  and recovery.

Changing a framework procedure requires one source edit. Changing a durable fact
requires one vault edit. Never copy either into persona homes as shared doctrine.

## Release units

- `persona-manager` — create, extend, update, and validate personas. Its
  plugin-shipped `self-improve` skill is canonical.
- `persona-dashboard` — optional read-only HTML viewer. It creates no action or
  knowledge record.
- `personas-mesh` — sync mechanics, 1Password-backed configuration rendering,
  versioned launcher generation, hooks, and unit templates.

The units remain separate because their triggers, authority, dependencies, and
activation lifecycles differ.

## Development contract

1. Snapshot source and preserve unrelated work before editing.
2. Work in an isolated migration branch or worktree.
3. Keep plugin versions unchanged during source staging; bump once at approved
   finalization.
4. Declare runtime support in each plugin's `interop/capabilities.json`.
   Claude support is native only where proven. Missing adapters are
   `replacement` or `unsupported` with a reason.
5. Resolve plugin resources from `${CLAUDE_PLUGIN_ROOT}` or the executing
   script's plugin-relative path. Never assume an authored marketplace or cache
   location.
6. Run tests with fixture homes. Never mutate `~/.personas` during source
   validation.
7. Keep credentials in a caller-selected 1Password vault. Use `op` without
   printing values.
8. Treat installed plugins, caches, launchers, systemd units, vault notes, and
   persona homes as activation surfaces. Source readiness does not
   authorize their mutation.

## Commands

```bash
bash tests/run-tests.sh
```

The gate covers the exact three-plugin boundary, final release versions, trigger
isolation, deterministic persona validation, canonical self-improve ownership,
dashboard read-only behavior, mesh launcher provenance, 1Password rendering,
deep merge, export inventory, and stale paths.

Use `plugins/persona-manager/bin/validate-persona <persona-path>` for a read-only
persona health check. Use `plugins/personas-mesh/bin/install-launchers` only
during an approved activation.
