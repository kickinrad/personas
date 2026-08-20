# {PersonaName}

{PersonaName} is a portable AI persona for {role description without personal facts}.

## Use

Open this folder in Claude Code or Codex. Codex loads the portable definition in
`AGENTS.md`; Claude Code imports that same definition through `CLAUDE.md`.

## Folder map

- `AGENTS.md` — portable identity, role, voice, boundaries, and Codex entry.
- `CLAUDE.md` — Claude Code import of `AGENTS.md`.
- `.claude/settings.json` — native Claude project settings.
- `.codex/config.toml` — native Codex project settings.
- `skills/` — portable role workflows.
- `user/` — optional ignored profile and explicit memory.

## Privacy

Everything tracked in Git should be safe to publish. Keep personal context,
runtime-local settings, connections, and credentials out of Git. A private
repository is recommended for personalized Cloud use, but privacy starts with
what the folder contains—not with a repository visibility check.
