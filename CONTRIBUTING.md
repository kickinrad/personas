# Contributing

Help make Persona Manager easier to trust and easier to use.

## Requirements

Use Python 3, Bash, and `jq`. Keep tests offline and use temporary persona
homes; never point a test at `~/.personas` or a real repository.

## Development procedure

1. Fork and clone the repository, then create a focused branch.
2. Run the full gate:

   ```bash
   bash tests/run-tests.sh
   ```

3. Keep shared skills at `skills/`, runtime manifests at the root, and persona
   fixtures sanitized. Do not add a generated skill copy or a forwarding
   manifest.
4. For a contract change, add an observable fixture and test. For a Cloud
   change, use an injectable local visibility adapter; never call a real GitHub
   repository from the test suite.
5. Update the public quickstart and troubleshooting path when a user-visible
   command or recovery step changes.

## Pull requests

Explain the user outcome, privacy effect, verification evidence, and any
unsupported capability. Do not include profiles, memory, local settings,
credentials, or real integrations in examples, fixtures, commits, or issue
text. Use clear commit messages and open a PR against `main`.

## DCO sign-off

All contributions need a sign-off line in the commit message:

```text
Signed-off-by: Your Name <your@email.com>
```

Use `git commit -s` to add it. This certifies that you wrote or are authorized
to submit the contribution under the project license.
