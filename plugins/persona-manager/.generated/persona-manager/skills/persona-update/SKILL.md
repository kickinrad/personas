---
name: persona-update
description: Use when the user asks to update a persona, inspect framework drift, reconcile hooks or settings with current templates, or check whether a persona is outdated. NOT for creating a new persona; use persona-dev.
---

# Update a persona

Reconcile framework mechanics without normalizing the persona.

1. Snapshot the persona repository and confirm the target. Preserve identity,
   voice, user data, local role procedure, integrations, and vault knowledge.
2. Resolve framework source from `the installed plugin root`. Read the current
   version from its `.claude-plugin/plugin.json`, templates from the sibling
   `persona-dev/assets/` directory, and procedure depth from `references/`.
   Stop if the plugin root is unavailable;
   never guess a marketplace or cache path.
3. Compare `.framework-version`, `CLAUDE.md`, `AGENTS.md`, hooks, settings,
   gitignore, guard script, and required structural sections. Classify each difference as framework
   addition, framework change, persona customization, or ambiguity.
4. Present the drift report before writing. Merge framework mechanics while
   preserving persona-owned content; ask only where both authorities changed
   the same meaning.
5. Reject `.claude/skills/self-improve/`. The plugin-shipped
   `the `persona-manager:self-improve` skill` skill is canonical; retire a legacy local copy
   only with explicit approval.
6. Run
   `the installed plugin root/bin/validate-persona <persona-path> --plugin-root "the installed plugin root"`.
   Fix every error. Use a fresh internal reviewer for judgment-heavy changes;
   the runtime selects its model and profile.
7. Stamp `.framework-version` only after deterministic validation passes, then
   show the exact diff and propose the persona-local commit.

Batch updates repeat this procedure independently per persona. Shared meaning
may be consistent, but identity and voice are never copied across homes.
