# Troubleshooting

## Creation stopped or the folder already exists

Look at what's already there before trying again. Ask `personas:persona-dev`
to review the existing persona, or choose an empty folder for a new one. Keep
your existing role, skills, settings, and private `user/` files.

## The persona is not loading or behaving as expected

Start Claude Code or Codex from the persona folder. Check that `AGENTS.md`
contains the role, and that no `CLAUDE.md` exists in the folder or above it;
one stops Claude Code from reading `AGENTS.md`. Claude Code needs version
2.1.281 or later. If the runtime asks you to trust the project, review the
files before accepting.

Ask the agent to explain its role and name the local skill it would use for
your task. If it gives an unexpected answer, check whether global instructions
or settings are also being loaded. See [settings and tools](usage.md#settings-and-tools).

## A new server is missing from the agents

Add it to the `mcpServers` list in the persona's `.claude/agents/<slug>.md`,
the one place its servers live, then rerun the
[sync helper](usage.md#call-a-persona-from-any-session) for Codex in the
folder. A remote server that
uses OAuth signs in once through `/mcp` inside the runtime; its client ID and
callback port are the only OAuth settings the helper accepts.

## Updating an older persona

Ask `personas:persona-dev` to review the folder and propose an update. You
don't need to start over: identity, voice, role, and boundaries belong in
`AGENTS.md`; workflows live in `skills/`; delete an old `CLAUDE.md`. Keep
your ignored `user/` files, connections, model choices, and other
customizations. Review leftover hooks, framework stamps, or management files
before removing them; something you customized may still have a job.

## Memory or local context is missing

A clone or Cloud checkout doesn't include ignored `user/` files. Restore them
from your private backup or provide the context in the conversation. Keep
private profile and memory files out of Git. The runtime's own memory is
separate; Personas doesn't copy it between Claude Code and Codex.

## A skill cannot find its resources

Use an installed Personas plugin or load this repository as a source plugin
in the runtime. Keep each skill's templates and references beside it; copying
only `SKILL.md` can leave those files behind.
