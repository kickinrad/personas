---
name: persona-update
description: Use when the user asks to update a persona, reconcile its folder with the current framework, or inspect whether its runtime adapters are outdated. NOT for creating a new persona; use persona-dev.
---

# Update a persona

Reconcile framework mechanics without normalizing the persona.

1. Snapshot the persona folder and confirm the target. Preserve identity,
   voice, user data, role procedure, integrations, and external knowledge.
2. Resolve the installed Personas root and read the current templates
   under `skills/persona-dev/assets/`. Stop if the plugin root is unavailable.
3. Compare the folder with the portable contract: `PERSONA.md`, `CLAUDE.md`,
   `AGENTS.md`, shared skills, `.claude/settings.json`, `.codex/config.toml`,
   `.gitignore`, and optional ignored `user/` context.
4. Classify each difference as a framework adapter change, persona-owned
   customization, obsolete machinery, or ambiguity.
5. Present the reconciliation plan before writing. Preserve persona-owned
   meaning and ask where ownership is ambiguous.
6. Remove retired Cloud markers, visibility workflows, publishing guards,
   framework stamps, and generated hooks only after showing their exact paths
   and receiving approval for the persona-local change.
7. Inspect the final tree and diff. Confirm both runtime entry files load the
   same `PERSONA.md`, optional user context, and shared skills.

Batch updates repeat this procedure independently for each persona.
