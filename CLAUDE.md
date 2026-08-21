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
- Persona folders own their durable, portable role definition.

Changing a framework procedure requires one source edit. Keep persona-owned
meaning in its folder rather than duplicating it into framework documentation.

## Release unit

`personas` creates, extends, updates, and validates personas. Its
plugin-shipped `self-improve` skill is canonical.

## Development contract

1. Snapshot source and preserve unrelated work before editing.
2. Work in an isolated migration branch or worktree.
3. Keep this release aligned at `6.0.0`; do not create a documentation-only or
   staging version bump.
4. Declare runtime support in each plugin's `interop/capabilities.json`.
   Claude support is native only where proven. Missing adapters are
   `replacement` or `unsupported` with a reason.
5. Resolve plugin resources from `${CLAUDE_PLUGIN_ROOT}` or the executing
   script's plugin-relative path. Never assume an authored marketplace or cache
   location.
6. Run tests with fixture homes. Never mutate `~/.personas` during source
   validation.
7. Keep credentials out of tracked source and generated adapters.
8. Treat installed plugins, caches, launchers, and persona homes as activation
   surfaces. Source readiness does not
   authorize their mutation.

## Commands

```bash
bash tests/run-tests.sh
```

The gate covers the folder contract, release version, native runtime adapters,
canonical skill ownership, export inventory, documentation, and stale paths.
