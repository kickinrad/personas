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

Keep each skill's procedures and templates together. When behavior changes,
add a test for what should happen and a case that should fail safely. For
runtime changes, also try the behavior with a disposable persona in Claude
or Codex, as appropriate. Record versions, results, and limits in
[runtime evidence](docs/runtime-evidence.md).

In your pull request, explain what improves for the user and how you checked
it. Include a DCO sign-off with `git commit -s`.

## Release

1. Update the version in `.claude-plugin/plugin.json` and align the Codex
   manifest, marketplace metadata, and capability declaration. Check dependent
   pins and add the user-facing changes to `CHANGELOG.md`.
2. Run the gate, review the diff, scan for secrets, and verify affected runtime
   behavior. Merge the reviewed pull request after hosted CI passes.
3. Tag the tested merge commit as `personas--v<VERSION>` and publish its
   changelog entry as the release notes.
4. Install the release through the runtime's plugin flow and test a disposable
   persona before reviewing updates to any real persona folders.

Use the [rollback procedure](docs/rollback.md) if a release needs recovery.
