# Persona framework activation

Source staging is intentionally separate from live activation.

Before activation:

1. Run the repository gate and independent Forge review.
2. Reconcile the installed `persona-manager` version against this source.
3. Generate runtime adapters only after their declarations are accepted.
4. Run `bin/personas verify <persona-path> --profile shared` against each intended persona
   home, then reconcile local legacy `.claude/skills/self-improve/` copies with
   explicit user approval.
5. Have Curator reconcile the accepted framework inventory with its exact
   vault knowledge counterparts and verify parent edges, links, and residue.

Do not infer activation from source readiness. Installed plugins, caches,
launchers, systemd units, persona homes, and vault notes remain unchanged until
their activation step is explicitly approved.
