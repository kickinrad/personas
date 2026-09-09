# Troubleshooting

## Creation stopped or the folder already exists

Look at what's already there before trying again. Ask `personas:persona-dev`
to review the existing persona, or choose an empty folder for a new one. Keep
your existing role, skills, settings, and private `user/` files.

## The persona is not loading or behaving as expected

Start Claude Code or Codex from the persona folder. Check that `AGENTS.md`
contains the role and `CLAUDE.md` contains `@AGENTS.md`. If the runtime asks
you to trust the project, review the files before accepting.

Ask the agent to explain its role and name the local skill it would use for
your task. If it gives an unexpected answer, check whether global instructions
or settings are also being loaded. See [settings and tools](usage.md#settings-and-tools).

## A native adapter reports drift or an ownership conflict

Run the [sync helper](usage.md#native-agents-and-codex-profiles) without
`--apply` to see what differs. Check that the existing file really belongs to
the persona you're updating before applying changes.

Older generated profiles may not record which persona they came from. Review
the conflicting file and move it to a backup outside the directory where the
runtime looks for agents or profiles. Then rerun the helper. Keep the backup
until the replacement works. Don't overwrite another persona or an agent you
maintain by hand.

If a file error interrupts an update, check the completed and remaining paths
in the output. Fix the access problem and run the preview again. Claude also
needs permission to read the persona at its original location.

## Memory or local context is missing

A clone or Cloud checkout doesn't include ignored `user/` files. Restore them
from your private backup or provide the context in the conversation. Keep
private profile and memory files out of Git. The runtime's own memory is
separate; Personas doesn't copy it between Claude Code and Codex.

## A skill cannot find its resources

Use an installed Personas plugin or load this repository as a source plugin
in the runtime. Keep each skill's templates and references beside it; copying
only `SKILL.md` can leave those files behind.
