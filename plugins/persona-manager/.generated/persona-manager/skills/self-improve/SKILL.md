---
name: self-improve
description: Use when a persona is asked to self-improve, self-audit, promote a repeated correction into a rule, turn a recurring workflow into a skill, or review its local tools and procedures. NOT for framework upgrades; use persona-update.
---

# Self-improve

Evolve the persona home without copying framework or vault authority.

## Route the change

- Native auto-memory owns `user/memory/`; do not write it manually.
- Stable user facts belong in the vault through `vault:curator`, with only the
  minimum role-local pointer in the persona.
- Identity and voice belong in the output style.
- Local role procedure belongs in persona instructions or a local skill.
- Framework mechanics belong in `persona-manager` source and route to
  `persona-update`.

## Promote evidence

After three real occurrences, cite the evidence and propose one of:

1. a concise operational rule;
2. a reusable local skill for a recurring multi-step procedure;
3. an existing integration discovered through
   [research-toolkit](../persona-dev/references/research-toolkit.md);
4. removal or consolidation of stale local material.

Wait for approval before changing identity, rules, tools, skills, hooks,
connections, or external services. Prefer an existing capability over a custom
wrapper. A fresh internal reviewer may inspect a bounded change, but do not
create a durable model-pinned task agent or maintain a long-lived agent roster.

## Audit

Review memory for repeated friction, then inspect profile pointers, rules,
skills, tools, hooks, integrations, and loose files. Report proposed additions,
updates, and removals with evidence. Check that local
`.claude/skills/self-improve/` is absent; this plugin copy is the single source.

Apply approved changes, run
`the installed plugin root/bin/validate-persona <persona-path>`, inspect the diff,
and propose a persona-local commit. One edit should change one authority.
