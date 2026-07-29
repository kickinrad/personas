---
title: personas
---

# Persona framework

This repository contains Persona Manager framework mechanics for persona
lifecycle. Persona homes are external, independent repositories and are
evidence—not normalization targets.

## Authorities

- Framework source owns lifecycle mechanics, triggers, templates, deterministic
  validation, runtime declarations, and generated-adapter contracts.
- Persona homes own identity, voice, local role procedure, configuration, and
  cache.
- Vault notes own durable Wils knowledge, topology, current state, decisions,
  and recovery.

Changing a framework procedure requires one source edit. Changing a durable fact
requires one vault edit. Never copy either into persona homes as shared doctrine.

## Release unit

`persona-manager` creates, extends, updates, and validates personas. Its
plugin-shipped `self-improve` skill is canonical.

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

The gate covers the Persona Manager boundary, release version, trigger
isolation, deterministic persona validation, canonical self-improve ownership,
export inventory, and stale paths.

Use `bin/personas verify <persona-path> --profile shared` for a read-only
persona health check.
