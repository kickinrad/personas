---
name: setup
description: Use when the user asks to install personas-mesh, bootstrap persona sync, configure a mesh profile, or wire approved persona repositories into the mesh. NOT for diagnosing an existing failure; use mesh-doctor.
---

# Set up personas-mesh

Treat setup as activation. Confirm authority before mutating launchers, units,
remotes, hooks, or persona homes.

1. Read canonical topology/current-state knowledge and
   `templates/profile-env.example`. Collect the primary persona root, optional peer
   root, hub root, and mirror remote. Store only nonsecret paths in
   `~/.config/personas-mesh/profile.env`.
2. Confirm `git`, `jq`, `rsync`, `op`, SSH transport, and the 1Password
   service-account lane. Probe secret items by exit status with output discarded.
3. Run `the installed plugin root/bin/install-launchers`. Verify each launcher
   records the current manifest version, SHA-256, and immutable installed
   artifact.
4. Copy only the unit templates required for the profile to
   `~/.config/systemd/user/`. Every `ExecStart` must target a generated stable
   launcher; reload systemd after the complete unit set is present.
5. For each explicitly approved persona, inspect dirty state and remotes before
   any mutation. Merge `.gitattributes` and gitignore additions. Append mesh
   hooks using `the installed plugin root` without replacing persona-owned hooks.
6. Render local JSON from templates. Rendered keys win; unrelated existing keys
   remain. Reject unresolved placeholders and keep rendered files gitignored.
7. Run one verbose sync, inspect status, and reconcile the observed result back
   to the owner of current topology.

Stop on missing configuration, credentials, approval, dirty work, or remote
ambiguity. The plugin source is not a topology fallback.
