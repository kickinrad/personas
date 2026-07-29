# Migration notes

## 3.0.0 layout and user-data migration

The supported source layout is now one root plugin:

```text
.claude-plugin/  .codex-plugin/  skills/  hooks/  bin/  scripts/  interop/
```

Do not use the former `plugins/persona-manager/` path or generated nested
copies. Recreate or extend a sanitized persona with `bin/personas create`,
then verify it with `bin/personas verify`. Existing persona identity, voice,
`user/profile.md`, `user/memory/`, local settings, and connection
configuration are user-owned; do not bulk-copy or commit them during migration.
The new defaults ignore them. Credentials must never enter Git.

Claude Code local and Codex are supported. Claude Code Cloud is preview-only
until a separately authorized private GitHub/Cloud canary is run, and is usable only
for a bound GitHub repository whose authenticated visibility is exactly
`PRIVATE`; public, internal, unavailable, or ambiguous evidence fails closed.
Cloud creation initializes a new empty local Git repository with the approved
origin but never creates, clones, or pushes a remote. Adopting an existing
nonempty repository requires separately approved migration work.
Use [ROLLBACK.md](ROLLBACK.md) instead of modifying live homes if source rollback
is needed.

## 2026-07-28 — Persona Manager becomes the core product

The core repository now distributes only `persona-manager`. Persona Dashboard
and Personas Mesh were retired from this repository; they are not installable
or activatable from this marketplace.

Before the Mesh source was removed, it was extracted unchanged to a separately
owned sibling repository with history, file digest parity, independent tests,
and recovery evidence. The maintainer-local retained source ref is
`forge/personas-mesh-extraction` at
`e1f504222883b0fb5823f6cbec2b2305336dbdd4`. It is deliberately unpublished
pending the separate Mesh review. This is a recovery record, not a Mesh
installation or runtime instruction.

Existing installed Dashboard or Mesh components, launchers, units, caches, and
persona homes are deliberately untouched. Their maintenance and any migration
remain separate, explicitly approved work.

## Deferred work

- Separate Mesh review and any publication.
- Live fleet migration and a live-persona security pass.
- A persona gallery beyond the sanitized example.
