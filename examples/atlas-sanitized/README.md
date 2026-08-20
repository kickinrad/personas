# Sanitized Atlas example

Atlas is a fictional collaborator for reviewing small software changes. This
folder demonstrates the complete portable structure without personal context,
credentials, or external services.

Open the folder and inspect:

- `AGENTS.md` for Atlas's portable identity and working behavior;
- `CLAUDE.md` and `.claude/settings.json` for the Claude Code adapter;
- `.codex/config.toml` for Codex settings;
- `skills/atlas-review/SKILL.md` for one portable role workflow.

The example intentionally has no `user/` directory. A real local persona may
use ignored `user/profile.md` and `user/memory/MEMORY.md`; a fresh Cloud
checkout works without them.

To create your own version, install Personas and ask:

```text
Use personas:persona-dev to create a software-review persona named
Atlas. Show me the complete folder plan before writing anything.
```
