# Troubleshooting

## Creation stopped or the folder already exists

Inspect the folder and diff before continuing. Use `personas:persona-dev` to
review an existing persona or choose an empty destination. Preserve identity,
skills, settings, and ignored `user/` content.

## The persona is not loading or behaving as expected

Start the runtime from the persona folder. Check `AGENTS.md` and the
`@AGENTS.md` import in `CLAUDE.md`. Trust the project if the runtime asks before
loading project settings. Keep recurring procedures in the relevant role skill.

## A native adapter reports drift or an ownership conflict

Run the [sync helper](usage.md#native-agents-and-codex-profiles) without
`--apply` to inspect drift. Confirm that the destination belongs to the selected
persona before applying changes.

Older generated profiles may lack a source path. Review and move the conflicting
file to a backup outside the runtime's discovery directory, then rerun the
helper to generate an owned replacement. Keep the backup until verification
passes. Do not overwrite a different persona or manually maintained agent.

If a filesystem error interrupts application, inspect the reported completed
and remaining paths, correct the access problem, and rerun the preview. Claude
also needs permission to read the persona's absolute source path.

## Memory or local context is missing

A clone or Cloud checkout omits ignored `user/` files. Restore them from their
intended local source or provide context in the session. Keep private profile
and memory files out of Git. Native runtime memory has its own location and
lifecycle; Personas does not synchronize it.

## A skill cannot find its resources

Use an installed Personas plugin or load the source plugin in the runtime.
Bundled templates and references resolve relative to their owning skill.
