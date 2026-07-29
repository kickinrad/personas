# Troubleshooting

## I want to cancel creation

For role refinement, say “stop” or decline the proposed plan before approval.
For deterministic creation, interrupt `bin/personas create`; it removes its
named sibling staging directory on a handled failure and reports whether
`stagingCleaned` is true. Never overwrite the final home to restart.

## Permission was denied

Do not retry with broader permissions by default. Read the denial, decide
whether the requested filesystem, plugin, repository, or connection access is
actually necessary, then grant the narrowest permission or choose an offline
path. Installation, GitHub repository creation, and external connections each
need separate approval.

## I am offline or plugin installation failed

Creation from an installed or source plugin is offline-capable; it uses bundled
templates and opens no listener. If marketplace installation is unavailable,
clone or otherwise obtain the framework source through an approved route, then
run the same skill from that source context. Do not download random copies of
persona templates. Retry plugin installation only after connectivity and
marketplace authorization are available.

## The persona name or directory collides

Choose a different empty directory, or treat the existing directory as an
existing persona and use `persona-manager:persona-update`. Do not overwrite an
existing `CLAUDE.md`, `AGENTS.md`, `user/`, or `.claude/` tree. A collision is a
stop-and-inspect event, not a merge instruction.

## Creation stopped after a partial write

Keep the partial directory out of Git while you inspect it. Compare it with the
approved plan, then either finish deliberately or move it aside as a recovery
copy. Before any commit, use the publishing guard at the staging seam:

```bash
.claude/hooks/public-repo-guard.sh --check-staged
```

`bin/personas create` stages at `.<name>.personas-staging` beside the final home
and atomically renames only on success. A handled failure removes that staging
directory; if cleanup itself fails, the JSON report gives the retained staging
path for inspection and explicit cleanup.

## Verification fails

Run the profile that matches the runtime:

```bash
bin/personas verify /path/to/persona --profile claude-local --json
bin/personas verify /path/to/persona --profile codex --json
```

The report names the missing or malformed path. `WARN` is inspection-only;
`FAIL` requires correction. A legacy `.claude/skills/self-improve/` copy is a
warning: review it and remove it only with explicit approval.

## Claude Cloud says private visibility is not proven

Stop before loading personalized context. Public, internal, unknown,
unavailable, unauthenticated, and ambiguous repository evidence are all unsafe.
Check that the repository identity is unambiguous, authenticated GitHub access
is available, and the reported visibility is exactly `PRIVATE`. Then rerun the
Cloud preflight and verification. Credentials remain forbidden from Git even in
a private repository.

The framework repository may be public. The personalized Cloud persona
repository is private. If you cannot prove that boundary, use Claude local or
Codex without publishing personal state.

## A capability is unsupported

Only Claude Code local, private-only Claude Cloud, and Codex are supported.
Gemini CLI and Kimi Code have no adapter. Do not copy Claude hooks or settings
into another runtime and call it supported; keep the persona’s role procedure
portable and add an adapter as separate framework work.

## Recovery after a failed update or session

Use the repository’s last known good commit, inspect the persona’s exact diff,
and rerun verification before resuming work. The framework hook reports version
drift but does not repair files. If a Cloud session fails, resolve private
visibility first; Cloud auto-memory is environment-local and is not a recovery
transport.

## A skill cannot find its templates

Run from an installed or source plugin context that provides
`${CLAUDE_PLUGIN_ROOT}`. Framework skills resolve sibling references from that
root; they do not search an assumed marketplace or cache directory.
