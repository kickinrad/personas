# Changelog

## 4.0.0 — 2026-08-06

### Changed

- Renamed the public plugin from `persona-manager` to `personas`, matching the
  project and marketplace name.
- Kept the folder contract and the `persona-dev`, `persona-update`, and
  `self-improve` workflows unchanged.

## 3.0.0 — 2026-07-31

### Changed

- Restored the core model: a persona is a readable folder, not a managed
  runtime application.
- Added `PERSONA.md` as the portable authority with thin native `CLAUDE.md` and
  `AGENTS.md` entry points.
- Added minimal `.claude/settings.json` and `.codex/config.toml` project
  adapters around the same persona definition.
- Defined explicit ignored folder memory that both runtimes can read while
  keeping native auto-memory runtime-owned and unsynchronized.
- Made behavioral canaries—not file presence—the gate for runtime support.

### Removed

- The public creation and verification CLI.
- GitHub visibility checks, Cloud repository markers, generated private-only
  CI, publishing guards, and special Cloud profiles.
- Default persona lifecycle hooks for reminders, drift, crash markers,
  compaction, and repository binding.
- Framework version stamps and committed output-style duplication.

### Repository

- The persona plugin remains the single root plugin under Apache-2.0.
- Dashboard remains retired, and Mesh remains preserved separately for its own
  future review.
