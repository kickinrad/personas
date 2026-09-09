# Personas framework development

This repository owns the portable persona contract, lifecycle skills,
templates, native adapters, and validation. Persona folders own their identity,
workflows, settings, and private context.

- Work in an isolated task branch or worktree and open a pull request to `main`.
- Edit native source; installed plugins and generated runtime files are evidence.
- Resolve bundled resources relative to the skill or executing script.
- Keep the public framework independent of personal host configuration.
- Preserve existing persona customizations and every supported artifact mode.
- Run `bash tests/run-tests.sh` with fixture homes. Never mutate live personas
  or installed runtime homes during validation.
- Treat runtime acceptance separately from file parsing; record the tested
  versions and limits in `docs/runtime-evidence.md`.

The Claude plugin manifest owns the release version; native declarations must
agree with it. See `CONTRIBUTING.md` for contribution and release procedure.
