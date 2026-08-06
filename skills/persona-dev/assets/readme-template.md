# {PersonaName}

{PersonaName} is a portable AI persona for {role description without personal facts}.

## Use

Open this folder in Claude Code or Codex. Each runtime loads its native entry
file, then reads the shared definition in `PERSONA.md` and relevant workflows
under `skills/`.

## Folder map

- `PERSONA.md` — portable identity, role, voice, and boundaries.
- `CLAUDE.md` — Claude Code entry point.
- `AGENTS.md` — Codex entry point.
- `.claude/settings.json` — native Claude project settings.
- `.codex/config.toml` — native Codex project settings.
- `skills/` — portable role workflows.
- `user/` — optional ignored profile and explicit memory.

## Privacy

Everything tracked in Git should be safe to publish. Keep personal context,
runtime-local settings, connections, and credentials out of Git. A private
repository is recommended for personalized Cloud use, but privacy starts with
what the folder contains—not with a repository visibility check.
