# Contributing

Keep Personas easy to understand and preserve persona-owned content.

## Development

Use Python 3.11 or newer, Bash, and Git. No Python packages are required.
Create a focused branch and run:

```bash
bash tests/run-tests.sh
```

The same offline gate runs in CI against a checkout and a source export.
Tests use temporary homes; never point them at a live persona or runtime home.

Keep lifecycle procedure and templates under their owning skill. Add behavior
tests for changed contracts, including a failing case. For runtime changes,
also run a synthetic Claude/Codex acceptance probe and record versions,
results, and limits in [runtime evidence](docs/runtime-evidence.md).

Pull requests explain the user outcome and verification. Include a DCO sign-off
with `git commit -s`.

## Release

1. Update the version in `.claude-plugin/plugin.json` and align the Codex
   manifest, marketplace metadata, and capability declaration. Check dependent
   pins and add the user-facing changes to `CHANGELOG.md`.
2. Run the gate, review the diff, scan for secrets, and verify affected runtime
   behavior. Merge the reviewed pull request after hosted CI passes.
3. Tag the tested merge commit as `personas--v<VERSION>` and publish its
   changelog entry as the release notes.
4. Install the release through the runtime's plugin flow and test a synthetic
   persona before separately reviewing any live-folder reconciliation.

Use the [rollback procedure](docs/rollback.md) if a release needs recovery.
