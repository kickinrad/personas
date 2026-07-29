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
4. After explicit approval, use the canonical deterministic creator for a
   sanitized initial home:
   `${CLAUDE_PLUGIN_ROOT}/bin/personas create <name> --destination <parent> --profile claude-local --json`.
   It stages beside the final home and atomically renames only on success. For
   Cloud, add `--profile claude-cloud --repository OWNER/REPO`; it refuses to
   write even staging files until authenticated `gh` evidence is exactly
   `PRIVATE`, then records a repository-binding marker for SessionStart and
   later verification. It never creates the GitHub repository.
5. The command scaffolds literal files from `assets/`. It creates both
   `CLAUDE.md` and `AGENTS.md`; the former owns shared role procedure and the latter is a thin
   Codex loader. Read
   [lifecycle-meta](references/lifecycle-meta.md) for authority and growth,
   [launch-flags](references/launch-flags.md) for Claude launch configuration, and the
   matching template immediately before creating each file.
6. Preserve every existing file under `user/`. A populated profile or memory
   store is user data, never template output.
7. Enable the runtime's `persona-manager` plugin; the canonical `self-improve`
   skill ships with it. A local `.claude/skills/self-improve/` copy is invalid.
8. Route durable knowledge placement and vault writes through `vault:curator`.
   Keep identity and role procedure in the persona home.
9. Run `${CLAUDE_PLUGIN_ROOT}/bin/personas verify <persona-path> --profile claude-local`.
   Resolve every `FAIL` before stamping `.framework-version`.
10. Ask separately before repository creation, plugin installation, external
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
