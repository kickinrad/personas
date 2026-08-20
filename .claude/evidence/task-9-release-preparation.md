# Historical Task 9 — Release preparation (3.0.0)

> Historical evidence only. It does not prove the current 5.0.0 contract,
> whose release metadata and validation live in the current source release
> surfaces and tests.

Date: 2026-07-30

## Version decision

Persona Manager is prepared as **3.0.0**. This is a truthful major release from
the historical 1.x/2.0.x line: the product changes from three units and a
nested manager path to one root plugin, retires Dashboard and Mesh from this
source, adds native Codex packaging, replaces creation/verification contracts,
and makes Cloud explicitly private-only with fail-closed identity binding.

The root LICENSE is Apache License 2.0 and is the legal authority. Both plugin
manifests now declare Apache-2.0. The Claude marketplace metadata and both
manifests declare 3.0.0; marketplace plugin entries intentionally carry no
duplicate version field.

## Prepared release surface

- CHANGELOG.md
- MIGRATION.md
- SUPPORT.md
- ROLLBACK.md
- RELEASE.md

Migration records the old nested layout, root layout, private user-data
defaults, runtime support, Cloud boundary, and deferred Mesh review/publication,
live fleet migration/security pass, and gallery. Public rollback uses the last
published pre-3.0 commit `d3a0ed1d155fe043e2f196b65b284d264cd247a0`.
The maintainer-local Mesh extraction recovery ref remains
`forge/personas-mesh-extraction` at
`e1f504222883b0fb5823f6cbec2b2305336dbdd4`.

## Isolated local-install evidence

Using fresh temporary HOME and CODEX_HOME only:

1. Codex local marketplace add and persona-manager install discovered version
   3.0.0 from the local root.
2. Claude local marketplace add and persona-manager install discovered version
   3.0.0 from the local root.
3. The installed Codex artifact created and verified a Codex persona.
4. The installed Claude artifact created and verified a Claude-local persona;
   Cloud creation passed with a local PRIVATE adapter stub and failed without
   writes with a PUBLIC stub.

The commands used only local paths and temporary directories. No live persona
or live Mesh runtime was used.

## Real private Claude Cloud canary

The dedicated canary repository was created and repeatedly verified as GitHub
visibility `PRIVATE`. Its generated CI was green, and no profile, memory, local
settings, MCP configuration, or credential was committed. Its repository and
session identifiers remain private and are intentionally omitted here.

A fresh Anthropic Cloud session cloned the private repository and reported:

- `CLAUDE_CODE_REMOTE=true`;
- `.persona-cloud-repository` tracked and unchanged from `HEAD`;
- binding marker and origin both identified the canary repository;
- `user/profile.md`, `user/memory`, and `.claude/memory` absent;
- `gh` absent and not required;
- native `SessionStart` and `PreToolUse` hooks completed without error;
- Bash emitted `cloud-pretool-ok`.

Final remote verdict: `CLOUD_CANARY_REMOTE_PASS`.

## Readiness

Claude local and Codex are native based on those disposable CLI installs.
Cloud is preview, private-only support backed by the real zero-token canary
above. Hosted public CI is green through the Cloud fixes. Tagging, release
publication, and setting recommended GitHub topics follow this evidence commit.
