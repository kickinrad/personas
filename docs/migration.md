# Migrating a persona

Ask `personas:persona-dev` to inspect the existing folder and propose a
migration. Review the exact changes before applying them.

1. Keep shared identity, voice, role, and boundaries in `AGENTS.md`.
2. Make `CLAUDE.md` import that definition with `@AGENTS.md`.
3. Keep recurring procedures in `skills/` and native settings in the matching
   runtime directory.
4. Preserve ignored `user/` context, integrations, model preferences, and
   persona-owned customizations.
5. Preview native adapter generation before applying it. Review
   [legacy ownership conflicts](troubleshooting.md#a-native-adapter-reports-drift-or-an-ownership-conflict)
   when updating an older generated profile.

For pre-6.0 installations, use the `personas` root plugin and `persona-dev`
lifecycle skill. Review obsolete framework stamps, hooks, Cloud visibility
guards, and management CLI files individually before retiring them; preserve
anything independently owned by the persona.

Verify the resulting folder in every runtime it uses. See
[rollback](rollback.md) for recovery and the [changelog](../CHANGELOG.md) for
version history.
