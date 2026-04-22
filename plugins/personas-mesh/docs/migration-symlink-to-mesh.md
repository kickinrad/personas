# Migration: break the WSL → Windows symlink, switch to mesh sync

This is Phase 4 of the rollout. Run only after Phases 1–3 have proved the mesh is healthy for at least a week — a failing mesh during this migration is a path to lost memory files.

## Current state (pre-migration)

```
/home/wilst/.personas → /mnt/c/Users/wilst/.personas   (symlink)
```

Every read and write from WSL goes through the WSL 9P bridge to the Windows NTFS filesystem — source of the "personas feel slow in WSL" pain.

## Target state (post-migration)

```
/home/wilst/.personas/          — real directory, WSL-native ext4 (fast)
/mnt/c/Users/wilst/.personas/   — real directory, Windows-native (CoWork uses this)
```

Both are independent sync nodes, each pointed at `ssh://wils@cloud/srv/personas/*.git`. The `personas-mesh-wsl.timer` syncs the WSL-native copy every 10 minutes; `personas-mesh-windows-bridge.timer` syncs the Windows copy every 3 minutes.

## Pre-flight checks

1. `personas-mesh:status` → all personas green for every row, no `CONFLICT` anywhere.
2. `git -C ~/.personas/{p} status --porcelain` → empty for all 10 personas. Commit or stash anything dirty first.
3. Close CoWork on Windows. Close any open persona sessions in other terminals.
4. Verify hub reachability: `ssh wils@cloud ls /srv/personas/ | wc -l` → `10`.
5. Dry run: `ls ~/.personas/` should list all 10 dirs. If any are missing from the Windows side, migrate those separately or skip.

## The migration

```bash
set -eu

# Belt-and-suspenders: take a backup of the Windows-side tree before touching anything.
timestamp=$(date +%Y%m%d-%H%M%S)
sudo mkdir -p /var/backups/personas
sudo tar --exclude='*/node_modules/*' --exclude='*/.venv/*' \
  -cf /var/backups/personas/pre-unlink-${timestamp}.tar \
  -C /mnt/c/Users/wilst .personas
echo "backup: /var/backups/personas/pre-unlink-${timestamp}.tar"

# 1. Break the symlink — only removes the link, not the Windows data.
[ -L ~/.personas ] || { echo "ERROR: ~/.personas is not a symlink; aborting"; exit 1; }
rm ~/.personas

# 2. Fresh WSL-native root — clone from hub (NOT from the Windows copy).
#    Cloning from the hub avoids carrying any mid-sync state that might be
#    stale relative to the hub.
mkdir ~/.personas
for p in archer bob julia kai mila nara piper reed urza warren; do
  git clone ssh://wils@cloud/srv/personas/${p}.git ~/.personas/${p}
done

# 3. Restore the shared aliases.sh (it lives in ~/.personas/, not in any persona).
cp /mnt/c/Users/wilst/.personas/.aliases.sh ~/.personas/.aliases.sh

# 4. Re-render per-persona configs for WSL-native paths.
for p in archer bob julia kai mila nara piper reed urza warren; do
  cd ~/.personas/${p}
  personas-mesh-render-config \
    ~/projects/personal/personas/plugins/personas-mesh/templates/.mcp.json.template \
    .mcp.json \
    "${p}"
  mkdir -p .claude
  personas-mesh-render-config \
    ~/projects/personal/personas/plugins/personas-mesh/templates/settings.local.json.template \
    .claude/settings.local.json \
    "${p}"
done

# 5. Patch ~/.zshrc to source the WSL-native aliases file.
if ! grep -q '^\[ -f "$HOME/.personas/.aliases.sh" \]' ~/.zshrc; then
  cat >> ~/.zshrc <<'EOF'

# personas-mesh — source persona aliases from WSL-native path
[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"
EOF
fi

# 6. Activate the Windows-bridge timer (was installed disabled in Phase 1).
systemctl --user enable --now personas-mesh-windows-bridge.timer

# 7. Verify both paths sync to the hub.
personas-mesh-sync-all --verbose ~/.personas
personas-mesh-sync-all --verbose /mnt/c/Users/wilst/.personas

echo "MIGRATION COMPLETE. Open a new shell and test 'julia' — should be noticeably faster."
```

## Post-migration sanity

- `ls -ld ~/.personas` → `drwxr-xr-x … /home/wilst/.personas` (real dir, not a symlink).
- `ls ~/.personas/archer/user/memory/` and `ls /mnt/c/Users/wilst/.personas/archer/user/memory/` show the same files (both are at the hub's tip).
- Open CoWork on Windows, have it write a memory → within 3 min, `git -C ~/.personas/archer log` on WSL shows the commit.

## If something goes wrong

**The symlink was removed but clones failed.** Restore the symlink and retry:

```bash
rm -rf ~/.personas
ln -s /mnt/c/Users/wilst/.personas ~/.personas
```

**A persona's memory is missing in WSL but present on Windows.** It likely means the Windows copy had local uncommitted changes that were never on the hub. Recover from the backup tarball:

```bash
mkdir /tmp/recovery
tar -xf /var/backups/personas/pre-unlink-*.tar -C /tmp/recovery
diff -r /tmp/recovery/.personas/{persona}/user/memory ~/.personas/{persona}/user/memory
# cherry-pick the new files across, commit, push
```

**The Windows-bridge timer isn't firing.** Check `systemctl --user status personas-mesh-windows-bridge.timer`. Common issue: WSL user services need `loginctl enable-linger wils` to run without an active WSL shell (same as Hetzner). Since you're typically in a WSL shell when personas run, this is usually fine; enable lingering only if you leave WSL closed overnight and still expect sync.

## Rollback

Within the first few hours, if the new arrangement proves problematic, the symlink can be restored — the Windows-side tree was untouched:

```bash
rm -rf ~/.personas
ln -s /mnt/c/Users/wilst/.personas ~/.personas
systemctl --user disable --now personas-mesh-windows-bridge.timer
```

Commits made to the WSL-native copy between migration and rollback would be lost from the laptop — check the hub remote to retrieve them (`ssh wils@cloud git -C /srv/personas/{p}.git log`).
