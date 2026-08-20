# Troubleshooting

## Creation was cancelled or stopped partway through

Decline the folder plan to stop before writing. If work stops after approval,
inspect the partial folder and exact diff. Finish it deliberately or move it
aside; never overwrite an existing persona blindly.

## The target directory already exists

Treat it as an existing persona and use `personas:persona-update`, or
choose another empty directory. Preserve its identity, skills, and `user/`
content until ownership is clear.

## The persona does not sound or behave right

Confirm the runtime loaded its native entry file, then read `AGENTS.md`.
Identity, voice, role, and boundaries belong there. Repeated multi-step
procedure belongs in a role skill. Avoid copying the same correction into both
`CLAUDE.md` and `AGENTS.md`.

## Codex does not load the persona

Start Codex from the persona folder and confirm `AGENTS.md` is discovered.
Trust the project if Codex asks before applying `.codex/config.toml`. Verify
that `AGENTS.md` contains the portable definition and the relevant `skills/`
directory.

Codex support was earned by the release canary. Do not describe a new loader or
setting as supported until it passes the same parity probes.

## Memory is missing

Explicit persona memory lives in ignored `user/memory/MEMORY.md`. A fresh clone
or Cloud checkout will not contain it. Restore it only from its intended local
source; do not commit it merely to make it travel.

Claude and Codex native auto-memory use separate runtime-owned locations. They
do not synchronize with each other or automatically write the explicit persona
memory file.

## Cloud cannot see local context

That is expected: ignored `user/` files are absent from a fresh checkout.
Provide session context explicitly or use the runtime's environment-owned
memory. Never solve the problem by committing a private profile, memory, or
credential.

## A capability is unsupported

Do not copy another runtime's settings and call it support. Add a native adapter
and pass the same behavioral canary used by supported runtimes.

## A skill cannot find its templates

Use an installed or source Personas plugin context. The skills resolve
their bundled `assets/` and `references/` relative to their own plugin package;
they do not require a management CLI.
