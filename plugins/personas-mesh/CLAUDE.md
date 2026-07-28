---
title: personas-mesh
---

# personas-mesh

Portable sync mechanics for persona repositories and profile-local configuration.
The plugin does not own the current deployment roster, hostnames, endpoints, deployed
personas, or recovery state; those belong in canonical operational knowledge and
external profile configuration.

## Mechanics

- `bin/sync-persona` performs pull, commit-if-dirty, and push for one repository.
- `bin/sync-all` iterates an externally configured persona root and skips
  redirect stubs.
- `bin/sync-user-*` reconciles gitignored `user/` directories between two
  explicitly configured local roots.
- `bin/render-config` resolves caller-supplied 1Password references
  through `op`, substitutes templates, and deep-merges JSON without printing
  secret values.
- `bin/install-launchers` copies executables into an immutable versioned
  snapshot and generates stable provenance-bearing launchers.
- `bin/mirror-all` pushes configured bare repositories to an asynchronous mirror
  remote.

## Profile configuration

Local paths and topology are read from
`~/.config/personas-mesh/profile.env`, based on `templates/profile-env.example`.
Source defaults may identify mechanics; they may not encode Wils-specific
hostnames, users, roots, or persona rosters.

## Activation

Source edits do not mutate installed launchers or units. An approved activation
generates launchers, installs the appropriate unit templates, reloads user
systemd, and verifies provenance and behavior. No unit may execute a mutable
repository worktree.

## Security

Credential values live only in 1Password. Probe `op` with output redirected to
`/dev/null`. Rendered files remain local and gitignored. Missing configuration,
credentials, remotes, or roots fail closed.

Runtime support and launcher provenance are declared in
`interop/capabilities.json`.
