# Persona lifecycle

Read this reference when creating a persona or reconciling what belongs in its
home.

## Authorities

| Subject | Authority |
|---|---|
| Shared role, rules, and operating procedure | `CLAUDE.md` |
| Codex loading and mechanism translation | `AGENTS.md` |
| Identity, voice, and response shape | `.claude/output-styles/<name>.md` |
| Minimum stable role-local user context | `user/profile.md` |
| Runtime-managed learned preferences | `user/memory/` |
| Reusable role-local procedure | the runtime's project skill directory |
| Durable shared knowledge and current state | the vault through Curator |
| Framework mechanics and validation | `persona-manager` |

A persona home specializes the global contract; it does not copy it. A runtime
loader points to shared authority instead of becoming another instruction
source.

## First session

An unfilled profile triggers a section-by-section interview. Confirm the
captured section before writing it. Later sessions read the profile and memory
index before relying on personal context. Missing tools or connections are
reported as capability gaps, never silently treated as complete coverage.

## Growth

Repeated friction earns a proposed rule, skill, tool, or deletion only after
real evidence. Identity changes, connections, plugin installation, external
services, and framework mutations require separate approval. Shared durable
facts route to Curator; framework drift routes to `persona-update`.

## Verification

Run `bin/personas verify <persona-path> --profile claude-local`, inspect the exact diff, and verify:

- both harness loaders resolve their canonical files;
- framework templates did not overwrite persona-owned material;
- one meaning has one authority;
- secrets and local provider configuration remain external and gitignored;
- runtime support matches the plugin capability declaration.
