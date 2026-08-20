# Historical Task 6 — Runtime adapter acceptance

> Historical evidence only. It predates the 5.0.0 `AGENTS.md` authority and
> import-only Claude adapter, so it is not current runtime proof.

Date: 2026-07-28

## Declared adapter surface

- Claude local and Claude Cloud are native profiles. Cloud is explicitly
  private-repository-only.
- Codex is a native plugin, not a generated projection. Its marketplace source
  path is `./`, resolved relative to the marketplace root.
- The root `.codex-plugin/plugin.json` uses `./skills/`; Claude and Codex use
  the one shared root skill tree.
- The default `hooks/hooks.json` hook command accepts `PLUGIN_ROOT` and the
  Claude compatibility `CLAUDE_PLUGIN_ROOT`. Capabilities declare Codex hook
  trust as required and document `PLUGIN_ROOT`, `PLUGIN_DATA`, and the
  compatibility variable.
- Persona `AGENTS.md` remains a thin loader for shared `CLAUDE.md` doctrine;
  it does not copy the role section.

## Official Codex manual facts applied

The locally fetched official Codex manual states that a skills-only plugin has
the required root `.codex-plugin/plugin.json`, a `skills/` directory, and a
`./skills/` manifest path (Plugins / “Create a skills-only plugin”, manual
lines 17663–17728). Its “Custom instructions with AGENTS.md” section describes
automatic project guidance at lines 18597–18749. The plugin hooks section
documents separate hook trust (around lines 22480–22482) and the installed
plugin `PLUGIN_ROOT`/`PLUGIN_DATA` plus Claude compatibility variables (lines
22521–22523). These facts support the native root plugin, direct skill sharing,
thin loader, and trusted-hook declarations above.

## Acceptance harness

`tests/test_runtime_adapters.py` uses only clean temporary directories:

1. Copies the packaged root product as an installed plugin and scaffolds a
   persona from packaged templates and instructions.
2. Verifies Claude local and Codex profiles, instruction loading, positive
   persona-creation routing, and negative retired-Mesh routing.
3. Executes the declared trusted SessionStart hook command with `PLUGIN_ROOT`,
   `PLUGIN_DATA`, and `CLAUDE_PLUGIN_ROOT` set.
4. Builds a local bare Git fixture, commits cloneable public doctrine/settings/
   hooks plus a role-local `skills/atlas-brief/SKILL.md`, simulates a GitHub
   `origin` with an injectable adapter, proves `PRIVATE` preflight, performs a
   local branch push/recovery, then proves the `PUBLIC` path fails before
   behavior changes. The fresh clone discovers that role-local skill and still
   contains no forbidden `.claude/skills/self-improve` duplicate.

The clone deliberately excludes `user/profile.md`, `user/memory/`, and
`.claude/settings.local.json`: Cloud auto-memory is environment-local and
private profile/memory transport is never silently claimed.

## Validation

Executed on 2026-07-28:

```text
HOME=<fresh temporary directory> python3 tests/test_runtime_adapters.py
HOME=<fresh temporary directory> bash tests/run-tests.sh
jq . .codex-plugin/plugin.json
jq . .agents/plugins/marketplace.json
jq . hooks/hooks.json
jq . interop/capabilities.json
git diff --check
git diff --cached --check
```

Results: runtime acceptance passed (4 tests); the full fresh-home gate passed
(8 shell checks, 9 framework checks, 6 verification checks, and 7 privacy
checks); all declared JSON and diff checks passed. No real network, GitHub,
live persona, installed cache, or external remote was used or changed.
