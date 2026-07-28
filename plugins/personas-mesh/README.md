# personas-mesh

Synchronizes persona repositories across configured profiles and reconciles
gitignored user data between explicitly paired local roots.

## Layers

- Git mesh carries committed persona state through each repository's configured
  `origin`.
- User-data sync uses bidirectional `rsync -a --update` between configured local
  roots. It never propagates deletions.
- Profile-local configuration is rendered from templates with 1Password `op`.

## Skills

- `setup` — prepare configuration, versioned launchers, hooks, and unit
  templates for one profile.
- `status` — report read-only health from configured roots and remotes.
- `mesh-doctor` — diagnose and reconcile a failed sync.

## Installed executable contract

`bin/install-launchers` snapshots the plugin executables under
`~/.local/lib/personas-mesh/<version>/` and generates stable launchers under
`~/.local/bin/`. Every launcher records its source version, SHA-256, and
installed artifact. Systemd templates invoke only those stable launchers.

Current topology, hostnames, endpoints, deployed persona roster, and recovery
state are external knowledge—not plugin source. See `interop/capabilities.json`
for runtime support and `templates/profile-env.example` for the nonsecret
profile shape.
