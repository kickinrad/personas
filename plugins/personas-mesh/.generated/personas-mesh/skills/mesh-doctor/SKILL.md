---
name: mesh-doctor
description: Use when persona sync is broken, mesh status is red, repositories diverge, conflict branches exist, a configured remote is unreachable, or rendered profile configuration fails. NOT for first installation; use setup.
---

# Diagnose personas-mesh

Read canonical topology/current state and the configured profile before probing. Stop
at the first failed layer so later symptoms do not hide the cause.

1. Verify configured roots, required executables, stable launcher provenance,
   and unit `ExecStart` targets.
2. Probe SSH or the configured transport, then confirm each `origin` matches the
   approved topology.
3. Inspect repository status, upstream counts, rebase state, and
   `sync-conflict/*` branches without mutating.
4. Inspect user-unit status and recent logs for the exact failed service.
5. Verify nonsecret profile configuration. Probe required 1Password items with
   `op read "op://<vault>/<item>/<field>" >/dev/null`; never print values.
6. Present the cause, evidence, proposed repair, and rollback. Ask before
   commits, pushes, branch deletion, config writes, launcher installation, or
   unit changes.
7. Apply only the approved repair, rerun the failed probe, then run
   `personas-mesh:status`.

For a conflict branch, compare it with the active branch and reconcile the
salient commits. Delete the conflict branch only after the result is committed,
verified, and approved. Return observed topology or recovery drift to its vault
owner instead of copying it into plugin source.
