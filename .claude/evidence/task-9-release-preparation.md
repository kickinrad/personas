# Task 9 — Release preparation

Date: 2026-07-28

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
live fleet migration/security pass, and gallery. Rollback names
archive/pre-linear-renewal-main at
424237a2597b95ddc59a34443e32d6351e80d4fb and the Mesh extraction recovery
ref. Both refs resolve locally.

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

The commands used only local paths and temporary directories. No network,
GitHub, live cache, real home, commit, tag, push, or release was used.

## Readiness

Claude local and Codex are native based on those disposable CLI installs.
Cloud is preview, private-only support pending a separately authorized real
private GitHub/Claude Cloud canary. Hosted public CI, committing,
tagging, pushing, release publication, and setting recommended GitHub topics
remain deliberately blocked pending separate authorization.
