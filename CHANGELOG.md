# Changelog

## 0.7.0 — 2026-09-23

- Summon any persona as a native subagent from Claude Code or Codex. The sync
  helper writes one agent per runtime that reads the live `AGENTS.md` and
  resolves the persona's `skills/` and `user/` paths from its folder.
- Choose a Claude agent color with `--color`; later runs keep it.
- Give subagents the persona's tools: servers named in `.mcp.json`
  `agentMcpServers` are projected into both the Claude and Codex agents.
- **Breaking:** rename `codexMcpServers` to `agentMcpServers`; the
  `mcp_servers` alias is no longer read.
- **Breaking:** remove the generated Codex profile and the `--codex-artifact`
  and `--codex-mcp` options. Move older generated profiles and agents aside,
  then regenerate.
- Flag tracked private context (`user/`, local settings, `.mcp.json`, `.env`)
  in the fleet verifier, and drop checks for pre-0.6 folder layouts.
- Consolidate documentation into usage and troubleshooting guides.

## 0.6.0 — 2026-09-11

- Reset the public version from 6.2.2 as a one-time early-development
  correction; history and existing tags are unchanged.
- Keep focused launch as a Claude Code option. Codex remains integrated until
  it offers a supported user-configuration exclusion control.
- Reject HTTP MCP URLs with embedded credentials before projecting them to a
  Codex profile.

## 6.2.2 — 2026-09-09

- Ask during persona creation whether normal user configuration should remain
  integrated or be excluded with each runtime's native focused-launch option.
- Introduce Personas through practical chef, market-research, and code-review
  workflows, with a compact map of skills, private context, and optional tools.

## 6.2.1 — 2026-09-09

- Prevent generated adapters from replacing another persona's files and check
  all selected destinations before applying changes.
- Correct MCP key and description quoting; isolate Claude generation from
  Codex configuration and preserve independent profile and agent modes.
- Replace content-hash drift with explicit source ownership. Legacy profiles
  without ownership need reviewed regeneration.
- Inherit runtime model choices for new personas and preserve existing
  persona settings.
- Simplify offline testing, support source exports, and remove the `jq`
  requirement and personal fleet policy from public validation.
- Consolidate usage documentation and retain completed task records in Git
  history.

## 6.2.0 — 2026-09-01

### Changed

- Added independent Codex profile and native-agent generation.
- Limited Codex MCP validation and projection to explicitly selected bindings,
  preserving Claude-only transports without weakening profile validation.

## 6.0.0 — 2026-08-20

### Changed

- Folded persona creation, evolution, reconciliation, and optional native
  activation into `persona-dev`; retired `persona-update`.
- Added on-demand, marked and collision-safe Claude/Codex native-agent sync
  from the live `AGENTS.md`, including narrow local MCP translation.
- Removed public host-specific identity, credential-manager, and local-path
  coupling.

## 5.0.0 — 2026-08-17

### Changed

- Made `AGENTS.md` the single portable persona definition.
- Reduced `CLAUDE.md` to a native import of that definition.

## 4.0.0 — 2026-08-06

### Changed

- Renamed the public plugin from `persona-manager` to `personas`, matching the
  project and marketplace name.
- Kept the folder contract and its original portable workflows unchanged.

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
