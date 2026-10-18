# {PersonaName}

{PersonaName} is a portable AI persona for {role description without personal facts}.

## Use

Open this folder in Claude Code or Codex. Both read `AGENTS.md`, which
pulls in the shared rules in `PERSONAS.md`.

## Folder map

- `AGENTS.md` — identity, role, craft, voice, and boundaries.
- `PERSONAS.md` — shared rules, generated; don't edit here.
- `.claude/settings.json` — native Claude project settings.
- `.codex/config.toml` — native Codex project settings.
- `skills/` — portable role workflows.
- `evals/` — synthetic eval cases.
- `user/` — optional ignored profile, memory, and private evals.

## Privacy

Everything tracked in Git should be safe to publish. Keep personal context,
runtime-local settings, connections, and credentials out of Git. A private
repository is recommended for personalized Cloud use, but privacy starts with
what the folder contains—not with a repository visibility check.
