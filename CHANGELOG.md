# Changelog

## 3.0.0 — 2026-07-28

### Breaking

- Persona Manager is now the single root plugin. The former
  `plugins/persona-manager/` layout, Dashboard, and Mesh are not current
  product paths.
- The previous test-only routing table and dormant evaluator suites are gone.
- Claude Cloud is private-repository-only: creation, verification, CI, and
  SessionStart require authenticated evidence of exactly `PRIVATE` and a
  repository binding marker.

### Added

- Deterministic `bin/personas create` with atomic staging and profile-aware
  Claude local, Cloud, and Codex homes.
- Structured `bin/personas verify`, native Codex packaging, a private
  publishing guard, and one CI-equivalent release gate.
- Native project hooks in `.claude/settings.json` and a committed output-style
  identity for clean Claude local and Cloud clones.

### Changed

- Private profile, memory, local settings, connection configuration, and
  credentials remain local and are ignored by default.
- Repository-only Cloud doctrine no longer assumes local profile or memory
  files exist, and lifecycle hooks cannot replace the user's final answer.
- The project license authority is Apache-2.0.
