---
name: doctor
description: Diagnose and resolve personas-mesh sync problems. This skill should be used when the user asks to "why isn't my persona syncing", "fix the mesh", "mesh is broken", "sync conflict", "personas-mesh not working", "check why memory isn't propagating", or when personas-mesh:status flagged an issue. Walks through remote reachability, divergent commits, stash-branch resolution for conflicts, and the rarer cases (hub disk full, GitHub token expired).
---

# personas-mesh:doctor

Interactive diagnostic for one persona (or all).

## Diagnostic sequence

Run each check in order; bail on first failure so the user can fix it before moving on.

### 1. Hub reachability

```bash
ssh -o ConnectTimeout=3 wils@cloud 'ls /srv/personas/*.git 2>/dev/null | wc -l'
```

- Zero output or ssh error → hub unreachable. Common causes: Tailscale down on WSL, Tailscale down on `cloud`, ssh key missing.
- Non-zero repo count → hub is up.

### 2. Origin remote points at the hub

For each persona under the node's root:

```bash
git -C "$dir" remote get-url origin
```

- Must match `ssh://wils@cloud/srv/personas/{name}.git`. If it's a GitHub URL, the persona was never set up — route to `personas-mesh:setup`.

### 3. Local state clean

```bash
git -C "$dir" status --porcelain
```

- Empty → clean.
- Non-empty → show the dirty files. Ask whether to commit (auto-sync) or whether the user wants to review first.

### 4. Divergence

```bash
git -C "$dir" rev-list --left-right --count HEAD...@{upstream}
```

- `0 0` → in sync. Done.
- `N 0` → local ahead. Offer to `sync-persona` (push).
- `0 N` → remote ahead. Offer `sync-persona` (pull).
- `N M` → divergent. Real conflict case — go to step 5.

### 5. Conflict branches

```bash
git -C "$dir" branch --list 'sync-conflict/*'
```

- If present: display each with `git log sync-conflict/... --not main --oneline`.
- For each: offer
  - Merge the stash back in via `git cherry-pick` of the salient commits
  - Drop the stash branch (after user confirms)
- Also check `~/.personas/.sync-conflicts/{persona}.log` and prune resolved entries.

### 6. Systemd timer health (non-Hetzner)

```bash
systemctl --user status personas-mesh-*.timer
```

- Not running → `systemctl --user enable --now personas-mesh-wsl.timer`.
- Running but last run failed → `journalctl --user -u personas-mesh-wsl.service --since -1h`.

### 7. Per-node env sanity

- `cat ~/.personas-node.env` should define `AUTO_MEMORY_DIR`.
- `pass show bridgey/token-{persona}` should succeed for bot personas.
- GPG agent unlocked? `pass ls` non-error.

## Conflict resolution recipe

When a conflict is surfaced (branch `sync-conflict/HOST-TIMESTAMP`):

1. `git diff main..sync-conflict/HOST-TS` — see what the other node had that didn't merge.
2. If the diff is a memory append (almost always): `git checkout sync-conflict/...` then `git diff main`, manually reconcile the `MEMORY.md` / `user/profile.md` lines, commit on `main`, delete the stash branch.
3. If the diff is code (rare): treat like a normal merge, ask the user to pick.

## Outputs

End with a short status line: `personas-mesh is healthy` OR `personas-mesh has N issues — here's what's next`.
