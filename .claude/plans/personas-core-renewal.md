# Plan: Personas Core Renewal

_Created 2026-07-28 from the accepted product shape and framework audit._

## Goal

Turn `kickinrad/personas-framework` into a focused, privacy-first kit for
creating one durable AI collaborator.

The public repository will contain one product: Persona Manager. Claude Code
local and Claude Code Cloud remain native runtime profiles, and Codex becomes a
proven adapter. Cloud personas are private-repository-only. Persona Dashboard is
retired. Personas Mesh is preserved as a separate local project before its
source is removed from the core repository.

Reorganization, regeneration, rewriting, and deletion are allowed when they
reduce interface complexity without losing accepted behavior or authority.

## Product boundary

### In scope

- Persona creation, extension, update, self-improvement, and validation.
- A shared persona-home contract with explicit Claude and Codex adapters.
- A fail-closed Claude Cloud profile for private GitHub repositories.
- Privacy-safe defaults and deterministic publishing checks.
- One supported verification command.
- A first-use path that creates a useful persona in under ten minutes.
- History-preserving extraction of the working Mesh source.
- Retirement of Dashboard and removal of unowned residue.
- A tagged, documented public release.

### Out of scope

- Mutating or migrating live homes under `~/.personas`.
- Activating, reinstalling, or changing live Mesh launchers, timers, units, or
  configuration.
- Reviewing or redesigning extracted Mesh behavior.
- Creating or publishing a new Mesh remote without separate approval.
- A universal persona schema or compiler for runtimes beyond Claude and Codex.
- Public-repository execution of a personalized Claude Cloud persona.
- A persona gallery beyond one sanitized example.
- Folder Bridge, autonomous messaging, task management, or agent orchestration.

## Authority and target layout

- This repository owns framework procedure, validation, manifests, and runtime
  adapter contracts.
- Persona homes own identity, voice, role procedure, local configuration, and
  private state.
- Durable user knowledge remains in its canonical knowledge system.
- Shared procedure has one source. Runtime parity means equivalent observable
  behavior, not identical files.

Target core:

```text
personas-framework/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── .agents/plugins/marketplace.json
├── skills/
│   ├── persona-dev/
│   ├── persona-update/
│   └── self-improve/
├── hooks/
├── bin/
├── scripts/
├── interop/
├── examples/
└── tests/
```

The repository root becomes the canonical Persona Manager plugin. Generated
runtime output is retained only where a runtime requires a mechanical adapter;
shared skill trees are not copied.

## Acceptance criteria

1. The core repository contains only Persona Manager and makes no current
   Dashboard or Mesh product claim.
2. Mesh exists at `~/projects/markets/personas-mesh` as an
   independently testable local repository with relevant history, source
   inventory and digest parity, contract evidence, and a recorded recovery ref
   before its core source is removed.
3. Persona Manager is canonical at the repository root. Shared skills, hooks,
   executables, and assets have one implementation; runtime-specific manifests
   and adapters are minimal.
4. Private profile, memory, credentials, and runtime configuration are
   untracked by default. Core creation is offline-capable and opens no network
   listener.
5. Clean installed Claude and Codex flows both discover the plugin, create a
   persona, load its instructions, and validate it.
6. One documented verification command produces structured results, stable exit
   codes, and the same local and CI verdict. Public CI is green.
7. A stranger can create and use a persona from the README in under ten
   minutes, with expected output, failure messages, and recovery documented.
8. Dormant evaluations, prose scenarios, generated duplicates, stale paths,
   maintainer state, and unused assets are either integrated with a named owner
   or removed from product source.
9. The release has a changelog, migration note, support matrix, rollback
   procedure, and Git tag. Live personas remain unchanged.
10. Claude Cloud readiness is granted only when authenticated GitHub evidence
    reports repository visibility `PRIVATE`. Creation, verification, CI, and
    cloud startup fail closed when visibility is public or cannot be proven.
    Credentials remain forbidden from Git regardless of visibility.

## Rollout and dependency graph

```text
0 Baseline and recovery
  → 1 Extract Mesh
    → 2 Retire non-core modules
      → 3 Flatten Persona Manager
        → 4 Contract validation ─┐
        → 5 Privacy and safety ──┴→ 6 Runtime adapters
                                  → 7 First-success experience
                                    → 8 Cruft and release gate
                                      → 9 Release and handoff
```

Tasks 4 and 5 may run in parallel only after their exact file ownership is
separated. All other tasks are ordered.

## Task 0 — Establish a green, recoverable baseline

**Behavior**

Produce trustworthy pre-change evidence and restore the currently broken public
CI without changing framework behavior.

**Ownership**

- `.github/workflows/ci.yml`
- `tests/run-tests.sh`
- `tests/personas-test.sh`
- `tests/framework-contract-test.py`
- read-only inventory of both marketplace files and `plugins/*`

**Work**

1. Record `HEAD`, branch, working-tree state, tracked source inventory, plugin
   versions, and digests for `plugins/personas-mesh`.
2. Run the current local gate from a clean temporary home.
3. Fix CI references to the moved hook and settings templates.
4. Ensure CI invokes paths that exist and does not depend on live
   `~/.personas`.
5. Preserve an extraction/recovery ref before structural work.

**Proof**

- `bash tests/run-tests.sh` passes.
- The current GitHub Actions workflow passes on the baseline structure.
- Recorded inventory can identify every Mesh source file later.
- No persona home or installed runtime path changes.

## Task 1 — Extract Personas Mesh without changing it

**Depends on:** Task 0.

**Behavior**

Preserve working Mesh source and relevant history in an independent local
repository before deleting anything from core.

**Ownership**

- Source: `plugins/personas-mesh/**`
- Destination: `~/projects/markets/personas-mesh`
- Mesh-specific cases currently embedded in
  `tests/framework-contract-test.py`

**Work**

1. Create a non-destructive history split rooted at
   `plugins/personas-mesh`; retain the split ref in the original repository.
2. Initialize the sibling from that history rather than copying only the
   current tree.
3. Add only the shell needed for independent ownership: README, license and
   attribution, source instructions, `AGENTS.md`, CI entrypoint, and extracted
   contract tests.
4. Keep all launchers, hooks, scripts, templates, and systemd files
   behavior-identical during extraction.
5. Record source commit, split ref, file inventory, digests, test results, and
   restoration procedure.
6. Stop before remote creation or live activation.

**Proof**

- Source and extracted inventories match, excluding the new repository shell.
- Original Mesh files match destination digests.
- Extracted Mesh contract tests pass without importing core source.
- `git log` in the sibling contains relevant Mesh history.
- Installed launchers and live systemd state are untouched.

## Task 2 — Retire Dashboard and remove Mesh from core

**Depends on:** Task 1 evidence passing.

**Behavior**

Make the public source and product inventory describe only Persona Manager.

**Ownership**

- `plugins/persona-dashboard/**`
- `plugins/personas-mesh/**`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `README.md`
- `ACTIVATION.md`
- `TROUBLESHOOTING.md`
- `CLAUDE.md`
- `personas.md`
- `.github/**`
- affected tests

**Work**

1. Remove Dashboard source and generated output.
2. Remove Mesh source only after Task 1 recovery evidence is cold-read.
3. Reduce both marketplaces to Persona Manager.
4. Remove activation and troubleshooting paths that exist only for Dashboard
   or Mesh.
5. Retain historical references only in the changelog/migration record.
6. Add a stale-path check for retired names and plugin paths.

**Proof**

- No current manifest or README advertises Dashboard or Mesh.
- No core test imports a retired module.
- Stale-path scan passes.
- The retained split ref and extracted Mesh repository still reproduce the
  removed source.

## Task 3 — Flatten and deepen Persona Manager

**Depends on:** Task 2.

**Behavior**

Make the repository itself the installable product and eliminate duplicate
generated skill implementations.

**Ownership**

- Move from `plugins/persona-manager/**` to root:
  `.claude-plugin/plugin.json`, `skills/`, `hooks/`, `bin/`, `scripts/`,
  `interop/`, license/README content as appropriate
- Add `.codex-plugin/plugin.json`
- Replace or retire `interop/generate.py`
- Remove `plugins/persona-manager/.generated/**`
- Update both marketplace sources and all path callers

**Work**

1. Move authoritative source with history-preserving Git operations.
2. Resolve scripts through the installed plugin root, not authored repository
   or cache paths.
3. Share skill bodies directly across runtimes.
4. Generate only runtime-specific metadata or adapters that cannot be shared.
5. Make generated-output drift a deterministic check.
6. Apply the deletion test to every retained forwarding script or manifest.

**Proof**

- Claude and Codex marketplaces resolve the root plugin.
- No duplicated `SKILL.md` implementation exists in generated trees.
- Executables work from source, an installed copy, and a relocated fixture.
- Regeneration is deterministic or has been deleted as unnecessary.

## Task 4 — Rebuild the persona contract and verification interface

**Depends on:** Task 3.

**Behavior**

Expose one verification command while keeping shared, Claude, and Codex
requirements distinct and observable.

**Ownership**

- `bin/personas`
- existing `bin/validate-persona` migration or retirement
- `interop/capabilities.json`
- `tests/fixtures/**`
- contract tests under `tests/`

**Interface**

```text
bin/personas verify <persona-path> [--json]
```

The command is read-only, returns stable exit codes, distinguishes errors from
drift warnings, and reports which shared and runtime contracts were evaluated.
An inspection mode may report 1.x migration requirements but must not mutate
the home. Cloud verification additionally requires authenticated GitHub
visibility evidence; an absent client, unavailable authentication, ambiguous
remote, API failure, or any value other than `PRIVATE` is a failure rather than
an assumed-safe state.

**Work**

1. Separate the shared persona-home contract from Claude-only settings and
   Codex-only loader/runtime checks.
2. Preserve causes and exact paths in errors.
3. Define stable `PASS`, `WARN`, and `FAIL` output and exit behavior.
4. Cover valid, absent, malformed, stale, unsupported, unsafe-to-publish, and
   legacy homes with fixtures.
5. Make the same command the CI contract front door.
6. Add `verify --profile claude-cloud` (or an equivalent explicit selector)
   that resolves the GitHub repository and proves `visibility == PRIVATE`
   through an authenticated adapter.

**Proof**

- Fixture matrix produces expected structured output and exit codes.
- A Codex-valid home is not failed for an irrelevant Claude setting.
- A legacy home receives an actionable migration report without modification.
- CI and a local invocation return the same verdict.
- Cloud verification refuses public, internal, unknown, unauthenticated, and
  unreachable repository states.

## Task 5 — Make privacy and publishing safety structural

**Depends on:** Task 3. May proceed alongside Task 4 with non-overlapping
ownership.

**Behavior**

Private user state is untracked by default. A personalized cloud persona runs
only from a proven-private GitHub repository, and repository safety does not
depend on parsing one form of a shell command.

**Ownership**

- `skills/persona-dev/assets/gitignore-template`
- profile, memory, settings, and README templates under
  `skills/persona-dev/assets/`
- `scripts/public-repo-guard.sh` replacement or retirement
- security/publishing fixtures and tests

**Work**

1. Separate publishable persona definition and role procedure from local user
   profile, memory, credentials, and runtime settings.
2. Ignore private state by default.
3. Implement deterministic staged-tree/repository checks at a real Git or
   release seam.
4. Treat runtime hooks as early warnings, not the security guarantee.
5. Fail closed when repository visibility or required inspection is unknown.
6. Keep persona creation functional offline and free of listeners or telemetry.
7. Document exactly what is read, written, ignored, or transmitted.
8. When the user explicitly chooses Claude Cloud, create the GitHub repository
   as private or validate an existing private repository before adding
   personalized context. Repository creation and GitHub connection remain
   separately authorized external actions.
9. Install a repository CI guard that fails when
   `github.event.repository.private` is not true, and a cloud SessionStart
   preflight that independently proves private visibility before loading or
   operating on personalized context.
10. Never describe private visibility as a substitute for secret management:
    credentials, tokens, and signing keys remain outside Git.

**Proof**

- Generated homes do not track private fixtures.
- Alternate Git forms and non-agent Git clients cannot bypass the release gate.
- Visibility lookup failure cannot silently become “private.”
- Secret, PII-like, tracked-user-state, and clean-public fixtures behave as
  specified.
- Offline creation and verification pass.
- A public visibility fixture and every unknown-evidence fixture fail closed.
- The private-repository creation path verifies the resulting GitHub state
  before personalized files are written or committed.

## Task 6 — Prove Claude and Codex runtime adapters

**Depends on:** Tasks 4 and 5.

**Behavior**

Claude local, Claude Cloud, and Codex install and exercise the supported persona
outcome through their native mechanisms.

**Ownership**

- `.claude-plugin/**`
- `.codex-plugin/**`
- `hooks/**`
- `skills/**`
- `interop/capabilities.json`
- runtime acceptance harness under `tests/`

**Work**

1. Keep `CLAUDE.md` and persona role doctrine canonical.
2. Generate `AGENTS.md` as a thin Codex loader for shared doctrine, voice, and
   relevant private context.
3. Classify each lifecycle behavior as `native`, `generated`, `replacement`, or
   `unsupported` per runtime.
4. Port only hooks that have a real Codex lifecycle need; do not claim Claude
   auto-memory or compaction semantics where they do not exist.
5. Use `${PLUGIN_ROOT}` for Codex-native paths and compatibility variables only
   deliberately.
6. Test installation, discovery, hook trust/execution, persona creation, and
   verification from clean temporary homes.
7. Test Claude Cloud from a private GitHub fixture repository: fresh clone,
   committed `CLAUDE.md`, project settings/hooks/skills, private-visibility
   preflight, persona behavior, verification, branch push, and recovery.
8. Keep private profile/memory transport explicit. Cloud auto-memory is
   environment-local and is not claimed as cross-session portable memory.

**Proof**

- Claude local marketplace install and golden path pass.
- Claude Cloud private-repository golden path passes and the corresponding
  public-repository path stops before persona work.
- Codex local marketplace install and golden path pass.
- Positive and negative skill-routing cases pass.
- Capability declarations cite executable evidence.
- Unsupported behavior fails explicitly rather than silently degrading.

## Task 7 — Rewrite the first-success experience

**Depends on:** Task 6.

**Behavior**

A new user understands the promise immediately and reaches one useful persona
without learning internal release architecture first.

**Ownership**

- `README.md`
- `CONTRIBUTING.md`
- `TROUBLESHOOTING.md`
- `examples/`
- public assets and architecture diagram
- documentation validation

**Work**

1. Lead with the re-explaining/continuity problem and the durable-collaborator
   outcome.
2. Provide separate Claude and Codex quickstarts.
   Split Claude into local and private-repository Cloud paths.
3. Document a five-to-ten-minute guided creation with exact expected output.
4. Ship one sanitized example with no user data or private integration.
5. Explain the privacy contract and authority model in plain language.
6. Cover cancellation, permission denial, offline/install failure,
   existing-home collision, partial-write cleanup, validation failure,
   unsupported capability, and recovery.
7. Use clear terminal prompts, labels, ordering, and descriptive errors.
8. Move internal architecture after the golden path.
9. State prominently that Claude Cloud personas require a private GitHub
   repository, how privacy is checked, what private visibility cannot protect,
   and why credentials remain prohibited.

**Proof**

- A clean-room doc test completes without undocumented knowledge.
- Links, paths, commands, and expected output validate automatically.
- Partial creation leaves either a complete valid home or a recoverable
  explicitly named staging path.
- The first README screen states problem, outcome, supported runtimes, and
  installation.
- The Cloud quickstart cannot proceed without a verified-private repository and
  shows the exact remediation for public or unverifiable visibility.

## Task 8 — Remove residue and consolidate the release gate

**Depends on:** Task 7.

**Behavior**

Every tracked artifact has a current caller and owner, and one gate establishes
release readiness.

**Ownership**

- `tests/evals/eval-a/**`
- `tests/evals/eval-b/**`
- `tests/scenarios/**`
- tracked `.claude/plans/**` and `.claude/handoffs/**`
- `personas.md`
- generated artifacts
- unused assets and trigger rules
- `.github/workflows/ci.yml`
- `tests/run-tests.sh`

**Work**

1. Inventory callers and current value for every candidate.
2. Integrate useful evaluations and scenarios into the supported gate, or
   archive them outside product source/delete them.
3. Remove maintainer session residue that is not current project authority.
4. Retain the current plan until project closeout; archive it according to the
   project convention afterward.
5. Consolidate shell, Python, JSON, manifest, adapter, link, security, and stale
   path checks behind one local command used by CI.
6. Verify the gate from a fresh clone and temporary home.

**Proof**

- No tracked artifact lacks a named caller or release purpose.
- Fresh-clone gate passes.
- CI calls the same gate users and maintainers run locally.
- The gate does not read or mutate live persona homes.
- Repository inventory is materially smaller or every retained file has
  documented leverage.

## Task 9 — Release and hand off deferred work

**Depends on:** Task 8.

**Behavior**

Publish a coherent, recoverable Persona Manager release and create explicit
follow-up boundaries.

**Ownership**

- `CHANGELOG.md`
- migration and rollback documentation
- runtime support matrix
- plugin versions and marketplace metadata
- GitHub topics, social preview, release notes
- project closeout references

**Work**

1. Choose the truthful breaking version under the component versioning policy.
2. Document the old three-unit layout, new root layout, user-data default, and
   runtime support changes.
3. Install and test the release artifact through both runtime marketplaces.
4. Confirm rollback from the release tag and retained pre-renewal ref.
5. Tag only after public CI passes.
6. Record deferred projects:
   - extracted Mesh review and possible publication;
   - live persona fleet migration and security pass;
   - additional examples/gallery.
7. Ask separately before creating a Mesh remote, pushing a release, changing
   installed plugins, or touching live personas.

**Proof**

- Release artifact installs and completes both golden paths.
- Public CI and release checks are green.
- Changelog, support matrix, migration, and rollback paths are complete.
- Tag points to the exact tested source.
- No live persona or Mesh runtime state changed during this project.

## Design review conditions

Before implementation crosses Tasks 5–7, verify:

| State | Required behavior |
|---|---|
| Happy path | Preview, explicit approval, atomic creation, verification |
| Cancellation | No final home or a clearly identified recoverable staging path |
| Existing home | Refuse overwrite; offer inspect, extend, or choose another name |
| Permission denied | Name the path and required user-controlled remedy |
| Offline/install failure | Preserve local work; distinguish network from package failure |
| Partial write | Clean rollback or deterministic resume |
| Validation failure | Name shared or runtime seam and preserve the underlying cause |
| Unsupported runtime behavior | Explicit capability status and safe alternative |
| Public or unknown GitHub visibility | Stop before personalized context; require authenticated `PRIVATE` evidence |
| Recovery | Exact command/path; no destructive default |

Rollout is staged: fixtures, clean temporary installs, then the release
artifact. Piper or another live persona may be a later fleet-migration canary,
not part of this project.

## Recovery

- Keep the pre-renewal tag/ref until release acceptance.
- Keep the Mesh split ref and extraction manifest after core removal.
- Never use live installed plugins, caches, launchers, or persona homes as
  source.
- Revert structural tasks by commit boundary; do not mix extraction, deletion,
  flattening, and behavioral change in one commit.
- If extracted Mesh parity cannot be proven, stop before Task 2.
- If either runtime cannot pass the installed golden path, declare it
  unsupported rather than releasing an aspirational capability claim.
