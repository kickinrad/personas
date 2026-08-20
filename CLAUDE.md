---
title: personas
---

# Persona framework

This repository contains Personas framework mechanics for persona
lifecycle. Persona homes are external, independent repositories and are
evidence—not normalization targets.

This repository-development file is not a generated persona adapter; the
persona `CLAUDE.md` import-only budget does not apply here.

## Authorities

- Framework source owns lifecycle procedure, templates, runtime declarations,
  repository tests, and adapter contracts.
- Persona homes own identity, voice, local role procedure, configuration, and
  cache.
- Vault notes own durable Wils knowledge, topology, current state, decisions,
  and recovery.

Changing a framework procedure requires one source edit. Changing a durable fact
requires one vault edit. Never copy either into persona homes as shared doctrine.

## Release unit

`personas` creates, extends, updates, and validates personas. Its
plugin-shipped `self-improve` skill is canonical.

## Development contract

1. Snapshot source and preserve unrelated work before editing.
2. Work in an isolated migration branch or worktree.
3. Keep this release aligned at `5.0.0`; do not create a documentation-only or
   staging version bump.
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

The gate covers the folder contract, release version, native runtime adapters,
canonical skill ownership, export inventory, documentation, and stale paths.
