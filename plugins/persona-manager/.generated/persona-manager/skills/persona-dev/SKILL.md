---
name: persona-dev
description: Use when the user asks to create or design a persona, extend an existing persona with a local role workflow, or wire an approved plugin or tool into a persona home. NOT for framework drift or upgrades; use persona-update.
---

# Develop a persona

Treat the persona framework, persona home, and vault as separate authorities:

- Framework source owns lifecycle mechanics, templates, validation, runtime
  declarations, and generated-adapter contracts.
- A persona home owns identity, voice, local role procedure, configuration, and
  cache.
- The vault owns durable Wils knowledge, decisions, topology, current state, and
  recovery.

Do not normalize existing persona homes from framework defaults.

## Create

1. Discover the role, name, voice, workflows, user context, environment,
   integrations, and inheritance posture. Use structured questions and finish
   with an explicit build approval.
2. Read [environments](references/environments.md) for placement and
   [research-toolkit](references/research-toolkit.md) for capability discovery.
3. Present the complete identity, integration, skill, hook, sandbox, file, and
   access plan. Write nothing before approval.
4. Scaffold literal files from `assets/`. Create both `CLAUDE.md` and
   `AGENTS.md`; the former owns shared role procedure and the latter is a thin
   Codex loader. Read
   [lifecycle-meta](references/lifecycle-meta.md) for authority and growth,
   [launch-flags](references/launch-flags.md) for Claude launch configuration, and the
   matching template immediately before creating each file.
5. Preserve every existing file under `user/`. A populated profile or memory
   store is user data, never template output.
6. Enable the runtime's `persona-manager` plugin; the canonical `self-improve`
   skill ships with it. A local `.claude/skills/self-improve/` copy is invalid.
7. Route durable knowledge placement and vault writes through `vault:curator`.
   Keep identity and role procedure in the persona home.
8. Run `the installed plugin root/bin/validate-persona <persona-path>`. Resolve every
   error before stamping `.framework-version`.
9. Ask separately before repository creation, plugin installation, external
   connection, mesh activation, or publishing.

## Extend

For an existing persona, snapshot its status first and edit only the requested
surface. Put voice in its output style, role procedure in local instructions or
skills, executable helpers in `tools/`, and durable knowledge in the vault.
Research an existing capability before creating one. Install or connect only
with explicit approval.

## Verify

Re-run deterministic validation, inspect the exact diff, and confirm no
framework template, local skill, or vault note duplicated another authority.
Runtime support is truthful only as declared in
`../../interop/capabilities.json`; missing generated adapters remain
unsupported.
