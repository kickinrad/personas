# Plan: Personas v5 as Folders, With Runtime Parity

_Created 2026-07-31 from the accepted simplification and parity direction._

## Execution status

Current contract: Personas `5.0.0`, with `AGENTS.md` as the sole portable
persona definition and an import-only `CLAUDE.md` adapter. The completed 3.0
work below is historical planning context, not current authority.

- Tasks 0–6 and 8–9 are complete in source.
- The current v5 canary is recorded in
  [personas-folder-parity.md](../evidence/personas-folder-parity.md): Codex
  and Claude Code loaded the synthetic Atlas fixture without runtime mutation.
- Codex also discovers the repository's local marketplace and Persona Manager
  package. The plugin was not installed into the maintainer's live Codex or
  Claude configuration during source validation.
- The prior real Claude Code Cloud canary established that a publishable
  persona repository opens in Cloud. The simplified folder adds no Cloud-only
  runtime dependency; a fresh hosted run of the exact new Atlas fixture remains
  a useful post-source confirmation, not a reason to restore Cloud machinery.
- Commit, push, tag, release publication, topic changes, and live persona
  migration remain separately authorized delivery actions.

## Goal

Restore the product's original idea: a persona is a readable folder that makes
an AI collaborator behave consistently. Claude Code and Codex are supported
only when each runtime natively discovers the folder, adopts the same persona,
can use its shared skills, and passes the same behavioral acceptance probes.

Runtime-specific files are adapters around one portable persona definition.
They must not turn the persona into an application, security system, or CLI
product.

## Product principles

1. **The folder is the product.** A user can understand a persona by opening
   it in an editor.
2. **Parity is observable behavior.** Runtime files may differ, but identity,
   working doctrine, skill availability, and explicit folder memory must behave
   equivalently.
3. **One portable authority.** `AGENTS.md` owns identity, voice, role,
   boundaries, and shared operating doctrine.
4. **Native adapters stay thin.** `CLAUDE.md`, `AGENTS.md`, `.claude/`, and
   `.codex/` contain only what their runtime needs to load the portable source.
5. **Portable memory is explicit.** `user/memory/` is ordinary ignored Markdown
   that either runtime can read. Claude or Codex native auto-memory remains
   optional runtime-owned state and is never presented as synchronized.
6. **Safe to publish.** Tracked persona files contain no profile, memory,
   credentials, or machine-local configuration. Repository visibility is a
   user choice, not a runtime security protocol.
7. **Support is earned.** If an installed-runtime canary cannot prove persona
   adoption, that runtime is marked unsupported until it can.

## Target persona folder

```text
atlas/
├── AGENTS.md                  # portable identity and operating doctrine
├── CLAUDE.md                  # Claude Code import of AGENTS.md
├── README.md                  # human orientation
├── skills/                    # shared role workflows
├── .claude/
│   ├── settings.json          # minimal native Claude project configuration
│   └── output-styles/         # Claude-native presentation adapter, if useful
├── .codex/
│   ├── config.toml            # minimal native Codex project configuration
│   └── hooks.json             # only behaviorally necessary native hooks
└── user/                      # ignored, local, optional
    ├── profile.md
    └── memory/MEMORY.md
```

No `.persona-cloud-repository`, generated private-repository workflow,
visibility adapter, framework version stamp, launch-flags file, or public
creation/verification CLI belongs in the minimum folder unless later evidence
proves it is required for persona behavior.

## Memory decision

Codex native memories are file-backed, but Codex owns their location under
`$CODEX_HOME/memories`; the current documented interface does not allow a
persona to select `user/memory/` as the native memory root. The native feature
is also experimental.

Therefore:

- `user/memory/` is the portable, user-controlled memory surface.
- Both runtime entry files explicitly load it when present.
- Runtime-native memory may be enabled separately, but generated persona files
  neither relocate it nor imply synchronization.
- A future documented Codex project-memory location may add an adapter without
  changing the portable folder contract.

## Acceptance criteria

1. A sanitized persona can be understood without running a command: its
   identity, instructions, skills, runtime adapters, and private-state boundary
   are visible in the folder.
2. A newly generated persona contains `AGENTS.md`, importing `CLAUDE.md`,
   shared `skills/`, minimal `.claude/` configuration, and minimal `.codex/`
   configuration.
3. Claude Code and Codex independently pass a clean-room identity probe that
   demonstrates they loaded the same name, role, voice constraint, boundary,
   and one role skill from the generated folder.
4. Both runtimes can read an explicitly seeded `user/profile.md` and
   `user/memory/MEMORY.md` locally. Neither claims that native auto-memory is
   portable or synchronized.
5. Removing either runtime adapter causes only that runtime's acceptance probe
   to fail; the portable persona definition remains intact.
6. No default persona hook exists solely to remind, report framework drift,
   manage repository visibility, or simulate memory recovery.
7. The public creation path is the `persona-dev` skill. Users do not need to
   learn `bin/personas`, staging directories, profiles, visibility adapters, or
   structured verifier output.
8. Claude Cloud can open the same publishable persona folder from a repository
   without a marker, GitHub token, visibility preflight, or special Cloud
   profile. Documentation recommends private repositories for personalized
   use without claiming to enforce visibility.
9. Codex is labeled supported only after its installed plugin, project config,
   hooks if retained, instructions, shared skills, and behavioral probe pass in
   a clean temporary environment.
10. The README explains the idea, installation, folder, first persona, runtime
    support, and memory distinction before any maintainer detail.

## Dependency graph

```text
0 Preserve and rebaseline current work
  -> 1 Specify the portable folder and behavioral probes
    -> 2 Remove enforcement and CLI product machinery
      -> 3 Rebuild shared persona templates
        -> 4 Build the minimal Claude adapter
        -> 5 Build the native Codex adapter
          -> 6 Prove memory behavior
            -> 7 Run installed-runtime canaries
              -> 8 Rewrite product documentation and migration
                -> 9 Remove residue and prepare release
```

Tasks 4 and 5 may be implemented in parallel only after Task 3 freezes the
portable contract. All other tasks are ordered.

## Task 0 — Preserve and rebaseline current work

**Behavior**

Start the simplification from a known state without mixing the existing
uncommitted `3.0.1` work, README rewrite, and new architectural changes.

**Ownership**

- current Git worktree and branch state
- `.claude/plans/personas-core-renewal.md` as historical record only
- this plan as the new execution authority

**Work**

1. Inventory and classify every current modification as existing `3.0.1`
   work, README work, or new parity work.
2. Preserve completed renewal evidence and the extracted Mesh repository.
3. Establish a green baseline before structural edits.
4. Do not mutate installed personas under `~/.personas`.

**Proof**

- Each pre-existing modification has an explicit disposition.
- `bash tests/run-tests.sh` passes at the chosen baseline.
- No Mesh or live-persona path changes.

## Task 1 — Specify the portable folder and parity probes

**Depends on:** Task 0.

**Behavior**

Replace file-presence parity with observable persona adoption.

**Ownership**

- `interop/capabilities.json`
- `tests/fixtures/runtimes/**`
- `tests/test_runtime_adapters.py`
- new focused persona-adoption fixtures under `tests/fixtures/`

**Work**

1. Define the portable authority as `AGENTS.md` and document what remains in
   `CLAUDE.md` and `AGENTS.md`.
2. Define one sanitized acceptance persona with a distinctive name, role,
   voice rule, refusal boundary, and role skill.
3. Define runtime-neutral probes for instruction loading, skill discovery,
   local profile reading, explicit folder-memory reading, and hook/config
   discovery where those mechanics are retained.
4. Mark Codex `experimental` until its real canary passes; stop claiming native
   support based only on manifest and file checks.
5. Remove Cloud privacy enforcement from the capability definition; describe
   Cloud as a deployment surface for the same publishable folder.

**Proof**

- Contract tests fail against the current Claude-centric fixture for the
  missing Codex adapter and behavioral evidence.
- Every future `supported` status maps to a named executable probe.

## Task 2 — Remove enforcement and CLI product machinery

**Depends on:** Task 1.

**Behavior**

Make creation and use folder-native again.

**Ownership**

- `bin/personas`
- `scripts/public-repo-guard.sh`
- `hooks/framework-version.sh`
- `hooks/hooks.json`
- Cloud-specific templates under `skills/persona-dev/assets/`
- related create, verify, privacy, release, and documentation tests

**Work**

1. Retire the public `create` and `verify` CLI interfaces.
2. Move framework correctness checks into repository tests rather than
   generated persona runtime behavior.
3. Remove GitHub visibility inspection, the visibility adapter,
   `.persona-cloud-repository`, generated privacy CI, and Cloud binding hooks.
4. Remove default advisory publishing, crash-marker, compaction-memory, and
   framework-drift hooks unless a later behavioral probe demonstrates a
   persona-critical need.
5. Keep a short static privacy rule: tracked files must be publishable;
   `user/`, local settings, and credentials stay ignored.
6. Delete obsolete profiles and structured-output contracts rather than
   preserving compatibility shims for unreleased complexity.

**Proof**

- No generated persona requires Git, GitHub CLI, a token, a repository marker,
  or a framework executable to start.
- Repository tests still reject tracked private fixtures and credential-like
  test values where useful, without installing runtime guards.
- Deleting the retired executables and hooks reduces both source and test
  surface.

## Task 3 — Rebuild the shared persona templates

**Depends on:** Task 2.

**Behavior**

Let `persona-dev` create the readable folder directly after showing a plan and
receiving approval.

**Ownership**

- `skills/persona-dev/SKILL.md`
- `skills/persona-dev/assets/**`
- `skills/persona-dev/references/**`
- `skills/persona-update/SKILL.md`
- `skills/self-improve/SKILL.md`
- sanitized example under `examples/`

**Work**

1. Add `AGENTS.md` as the single source for identity, voice, boundaries, and
   runtime-neutral procedure.
2. Make `CLAUDE.md` an explicit import of `AGENTS.md`, with shared
   skills, and optional ignored user context.
3. Have `persona-dev` write the approved folder directly with normal agent file
   operations; rely on plan review, diffs, and Git for recovery.
4. Keep role skills portable and free of Claude- or Codex-only vocabulary
   unless a skill is explicitly runtime-specific.
5. Make `persona-update` reconcile adapters while preserving persona-owned
   content, without a framework version stamp.
6. Make `self-improve` propose changes to the owning portable file or skill,
   never duplicate shared meaning into both adapters.

**Proof**

- The Atlas example contains no duplicated identity or doctrine.
- A reader can identify every portable and runtime-specific file from its
  contents alone.
- Creation requires no framework executable.

## Task 4 — Build the minimal Claude Code adapter

**Depends on:** Task 3.

**Behavior**

Preserve native Claude behavior without making Claude's file layout the shared
domain model.

**Ownership**

- `skills/persona-dev/assets/claude-md-template.md`
- Claude-specific templates under `skills/persona-dev/assets/.claude/` or their
  chosen flat template equivalents
- Claude-focused acceptance fixtures and tests

**Work**

1. Make `CLAUDE.md` import `AGENTS.md`; `AGENTS.md` routes optional user
   context.
2. Reduce `.claude/settings.json` to settings needed for persona behavior;
   remove repository-policy and plugin-installation management.
3. Retain an output-style adapter only if the Claude acceptance probe shows it
   materially improves persona adoption beyond `AGENTS.md`.
4. Add no default hook without a named behavior that instructions or skills
   cannot provide reliably.

**Proof**

- A clean Claude session passes the shared identity, boundary, voice, skill,
  profile, and explicit-memory probes.
- Removing `.claude/` demonstrates exactly which native enhancements are lost,
  without making the folder unreadable or unsafe.

## Task 5 — Build the native Codex adapter

**Depends on:** Task 3.

**Behavior**

Give Codex equivalent outcomes through its documented native surfaces.

**Ownership**

- `skills/persona-dev/assets/agents-template.md`
- new Codex project templates for `.codex/config.toml` and, only if required,
  `.codex/hooks.json`
- `.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json`
- Codex-focused acceptance fixtures and tests

**Work**

1. Make `AGENTS.md` the portable definition, route optional user context, and
   context without referring to Claude as the canonical runtime.
2. Generate minimal trusted-project `.codex/config.toml` settings only where
   they affect persona behavior.
3. Map any retained persona-critical Claude lifecycle behavior to documented
   Codex hook events. Do not create hooks merely for structural symmetry.
4. Express voice and response shape through `AGENTS.md`, since
   Codex has no documented first-class equivalent to Claude output styles.
5. Verify the installed Codex plugin exposes the same shared skills.

**Proof**

- A clean Codex session passes the same behavioral probes as Claude.
- Codex discovers project instructions, configuration, hooks if any, and the
  installed shared skill through documented native paths.
- The adapter contains no instruction to vaguely “translate Claude
  mechanisms.”

## Task 6 — Prove portable and native memory behavior

**Depends on:** Tasks 4 and 5.

**Behavior**

Make memory useful without promising impossible synchronization.

**Ownership**

- `skills/persona-dev/assets/profile-template.md`
- `skills/persona-dev/assets/memory-template.md`
- runtime entry templates
- memory-specific acceptance fixtures and documentation

**Work**

1. Seed a distinctive sanitized preference in ignored `user/memory/MEMORY.md`
   and prove both runtimes can retrieve it when launched from the persona.
2. Confirm both runtimes behave coherently when `user/` is absent, as in a
   fresh Cloud checkout.
3. Document Claude auto-memory and Codex `$CODEX_HOME/memories` as separate,
   optional runtime features.
4. Do not redirect `CODEX_HOME` into the persona: that would relocate auth,
   configuration, plugins, sessions, and other state—not just memory.
5. Add a future compatibility note for a documented project-scoped Codex
   memory root if OpenAI introduces one.

**Proof**

- Both runtimes answer the explicit folder-memory probe correctly.
- Neither runtime requires native memory for persona identity or correctness.
- Tests and docs make no cross-runtime native-memory claim.

## Task 7 — Run installed-runtime canaries

**Depends on:** Task 6.

**Behavior**

Earn support claims with real runtime execution rather than simulated parsing.

**Ownership**

- temporary clean Claude and Codex homes
- installed plugin fixtures
- `tests/test_runtime_adapters.py` orchestration where automatable
- private canary repositories only if a hosted runtime requires one

**Work**

1. Install the plugin into clean isolated Claude and Codex environments.
2. Create the same sanitized Atlas folder through `persona-dev` on each
   runtime.
3. Run the frozen identity, voice, boundary, skill, profile, and memory probes.
4. Test Claude Code Cloud against the same publishable folder without special
   privacy machinery.
5. Record exact product versions, commands/prompts, outputs, and limitations.
6. If Codex fails any persona-critical probe, mark it unsupported and stop the
   Codex release path; do not soften the acceptance criterion.

**Proof**

- Reproducible canary evidence exists for every supported runtime.
- Claude and Codex results satisfy the same behavioral rubric.
- No canary relies on a developer checkout path or live personal persona.

## Task 8 — Rewrite product documentation and migration

**Depends on:** Task 7.

**Behavior**

Explain the simple product that now exists.

**Ownership**

- `README.md`
- `SUPPORT.md`
- `TROUBLESHOOTING.md`
- `MIGRATION.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `ACTIVATION.md` if still needed

**Work**

1. Lead with “a persona is a folder” and show the folder immediately.
2. Show one plugin install and one guided creation request per supported
   runtime.
3. Explain `.claude/` and `.codex/` as native adapters around `AGENTS.md`.
4. Explain portable folder memory versus runtime-native memory in one short
   section.
5. Reduce Cloud guidance to publishability, private-repository recommendation,
   and absence of ignored local state in fresh checkouts.
6. Document removal of CLI, Cloud markers, visibility checks, generated CI,
   and old version stamps for existing 3.x persona folders.
7. State unsupported or experimental runtimes plainly based on canary results.

**Proof**

- A new user can explain the product after the first screen of the README.
- The documented first-use paths match clean installed-runtime tests.
- Local links resolve and no removed interface remains in active docs.

## Task 9 — Remove residue and prepare release

**Depends on:** Task 8.

**Behavior**

Ship a smaller, truthful framework with no retired machinery hiding behind the
new story.

**Ownership**

- manifests and marketplaces
- `interop/`
- tests and fixtures
- release and repository inventory checks
- obsolete evidence generated by superseded mechanics, preserving only useful
  historical records

**Work**

1. Apply the deletion test to every executable, hook, template, profile,
   capability declaration, and test retained from the enforcement design.
2. Ensure manifest descriptions and repository metadata say “folder” and match
   proven runtime support.
3. Run source, packaging, clean-install, privacy, and behavioral acceptance
   gates.
4. Confirm Mesh remains separately recoverable and live persona homes remain
   untouched.
5. Prepare migration and release notes; do not publish without separate
   authorization.

**Proof**

- Full repository tests pass from a clean checkout.
- Installed Claude and every declared supported runtime pass their canaries.
- No retired CLI, Cloud enforcement, marker, visibility adapter, or generated
  privacy workflow appears in active source or documentation.
- The release diff is smaller in concepts and user-facing interfaces than the
  current 3.x design.

## Execution guardrails

- Do not mutate, migrate, or regenerate live persona homes during framework
  work.
- Do not modify or publish the separately preserved Mesh project.
- Preserve unrelated user changes and resolve the current dirty worktree before
  structural edits.
- Do not create repositories, push commits, tags, or releases without separate
  authorization.
- Prefer deletion over compatibility layers for unreleased or short-lived
  enforcement machinery.
- Treat current official runtime documentation and executable canary evidence
  as higher authority than remembered capability claims.

## Definition of done

Persona Manager is done when a person can open a persona folder, understand it,
install the plugin, and receive the same recognizable collaborator in Claude
Code and every runtime we claim to support. Runtime-specific configuration is
present where it earns its keep, private state remains local, Cloud needs no
special protocol, and no public CLI or hook system is required to understand or
use the persona.
