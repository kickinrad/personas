# Sanitized Atlas example

Atlas is a fictional collaborator for reviewing small software projects. This
example demonstrates a safe creation conversation without personal context,
credentials, or external services.

Create Atlas in an existing empty parent directory:

```bash
bin/personas create atlas --destination /path/to/personas --profile codex --json
```

Then ask the installed `persona-manager:persona-dev` skill to add a role brief:
“Review a small change, explain the risk in plain language, and suggest the next
verification step.” The skill shows a plan and waits for approval.

After approval, expect public role files such as `CLAUDE.md`, `AGENTS.md`, a
README, and a role-local `skills/` directory. Local state belongs under `user/`
and local runtime configuration; it is intentionally absent from this example.

From a source checkout, inspect the result without changing it:

```bash
bin/personas verify /path/to/atlas --profile shared
```

Expected output starts with `PASS: atlas` for a complete sanitized home. For
Cloud, do not reuse this example as a repository recipe: prove the target
repository is exactly `PRIVATE` before adding any personalized context.
