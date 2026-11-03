# Contributing

Thanks for helping make Personas better. Aim for changes that make it easier
to use and understand, while keeping people's existing personas intact.

## Development

Use Python 3.11 or newer, Bash, and Git. No Python packages are required.
Create a focused branch and run:

```bash
bash tests/run-tests.sh
```

CI runs the same tests against both a Git checkout and an exported copy of
the source. Tests use temporary folders; never point them at a real persona
or your normal Claude/Codex home.

Edit source, not installed plugins or generated agent files. Keep the
framework free of personal host configuration, and preserve people's existing
persona customizations. Keep each skill's procedures and templates together. When behavior changes,
add a test for what should happen and a case that should fail safely. For
persona behavior, add or update a case in `evals/` (see
[Evaluate a persona](README.md#evaluate-a-persona)). For
runtime changes, also try the behavior with a disposable persona in Claude
or Codex, as appropriate, and note the runtime versions and results in your
pull request.

In your pull request, explain what improves for the user and how you checked
it. Include a DCO sign-off with `git commit -s`.

## Release

The plugin carries no version: the merged commit is the release. Old
`personas--v*` tags and `CHANGELOG.md` remain as history.

1. Run the gate, review the diff, scan for secrets, and verify affected runtime
   behavior. Merge the reviewed pull request after hosted CI passes.
2. Update the plugin through the runtime's plugin flow and test a disposable
   persona before reviewing updates to any real persona folders.

If a release causes trouble, revert its pull request and update the plugin
again.
