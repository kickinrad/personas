# Migrating a persona

Ask `personas:persona-dev` to look over your existing folder and propose an
update. You don't need to start over or give up your customizations. Review
the changes before applying them.

1. Put the persona's identity, voice, role, and boundaries in `AGENTS.md`.
2. Point `CLAUDE.md` to the same definition with `@AGENTS.md`.
3. Keep recurring workflows in `skills/`, Claude settings in `.claude/`, and
   Codex settings in `.codex/`.
4. Keep your ignored `user/` files, connections, model choices, and other
   customizations intact.
5. Preview generated agent and profile files before writing them. Check
   [legacy ownership conflicts](troubleshooting.md#a-native-adapter-reports-drift-or-an-ownership-conflict)
   when updating an older generated profile.

If you're coming from before 6.0, use the `personas` plugin and its
`persona-dev` skill. Older folders may have framework stamps, hooks, Cloud
visibility guards, or management CLI files they no longer need. Review each
one before removing it; something you customized may still have a job.

Try the updated persona in every runtime you use. See [rollback](rollback.md)
if you need to recover, or the [changelog](../CHANGELOG.md) for version history.
