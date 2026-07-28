---
name: status
description: Use when the user asks whether personas are in sync, requests mesh status or health, or wants to know which configured persona repositories are ahead, behind, dirty, divergent, or conflicted. Read-only; use mesh-doctor for repair.
---

# Report mesh status

Read current topology and `~/.config/personas-mesh/profile.env`; fail closed if the
configured roots or transport are unavailable.

1. Derive the roster from configured repository roots and remotes. Never use a
   hardcoded persona list.
2. For each repository, collect last commit time, dirty count, upstream
   ahead/behind counts, and `sync-conflict/*` branches.
3. Query each configured remote endpoint once, then combine results locally.
4. Mark missing deployments as absent rather than unhealthy. Mark dirty,
   divergent, conflict, and unreachable states explicitly.
5. Return one compact table with persona, endpoint observations, and status.

Status performs no pull, commit, push, branch, unit, or config mutation. Route
any red state to `personas-mesh:mesh-doctor` with the exact evidence already
collected.
