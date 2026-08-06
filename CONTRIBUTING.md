# Contributing

Help keep Personas understandable: a persona is a folder, portable
meaning has one owner, and runtime support requires evidence.

## Development

1. Fork and clone the repository, then create a focused branch.
2. Run the complete gate:

   ```bash
   bash tests/run-tests.sh
   ```

3. Keep shared workflows under `skills/`, runtime manifests at the root, and
   persona fixtures sanitized.
4. For a folder-contract change, add an observable fixture and test. For a
   runtime claim, add a native adapter and behavioral canary.
5. Keep tests offline unless a separately authorized canary explicitly tests a
   hosted runtime.
6. Never point tests at `~/.personas` or include real profiles, memories,
   credentials, repositories, or integrations.

## Pull requests

Explain the user outcome, affected folder surface, parity evidence, privacy
effect, and any unsupported capability. Prefer deletion to compatibility
machinery that users would need to understand.

All contributions need a DCO sign-off:

```text
Signed-off-by: Your Name <your@email.com>
```

Use `git commit -s` to add it.
