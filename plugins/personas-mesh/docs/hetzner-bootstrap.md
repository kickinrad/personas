# Hetzner hub bootstrap

Runbook for standing up `cloud:/srv/personas` as the mesh hub. Run interactively as `wils@cloud` — needs sudo (the `wils` user is in the sudo group; `sudo -n` fails, so you'll be prompted for a password).

## Pre-flight

From WSL:

```bash
ssh wils@cloud 'echo ok; hostname; uname -rm'
# expect: ok  ubuntu-4gb-ash-1  <kernel> x86_64

pass ls bridgey/     # must list token-{bob,julia,mila,nara,warren}
pass ls discord/     # must list {bob,julia,mila}-bot-token
```

If either `pass ls` fails with "gpg: decryption failed", unlock the GPG agent first: `gpg --list-secret-keys` or retry after typing your passphrase into `pass show anything`.

## Phase 0 steps

### 1. Create hub directories

```bash
ssh wils@cloud
# on cloud:
sudo mkdir -p /srv/personas /srv/personas-work
sudo chown wils:wils /srv/personas /srv/personas-work
```

### 2. Clone bare repos from GitHub

For each of the 10 personas:

```bash
cd /srv/personas
for p in archer bob julia kai mila nara piper reed urza warren; do
  git clone --bare https://github.com/kickinrad/$p.git $p.git
done
```

### 3. Install bin scripts to /usr/local/bin

From WSL (one-liner to copy from the plugin cache):

```bash
rsync -av --chmod=u+x \
  ~/projects/personal/personas/plugins/personas-mesh/bin/ \
  wils@cloud:/tmp/personas-mesh-bin/
ssh wils@cloud 'sudo install -m 755 -o root -g root \
  /tmp/personas-mesh-bin/sync-persona \
  /tmp/personas-mesh-bin/sync-all \
  /tmp/personas-mesh-bin/render-config \
  /usr/local/bin/personas-mesh-{sync-persona,sync-all,render-config}'
```

### 4. Clone working trees

```bash
ssh wils@cloud
# on cloud:
cd /srv/personas-work
for p in archer bob julia kai mila nara piper reed urza warren; do
  git clone /srv/personas/$p.git $p
done
```

### 5. Install the systemd user units

From WSL:

```bash
rsync -av \
  ~/projects/personal/personas/plugins/personas-mesh/systemd/personas-mesh-hetzner.{service,timer} \
  ~/projects/personal/personas/plugins/personas-mesh/systemd/personas-mesh-github-mirror.{service,timer} \
  wils@cloud:~/.config/systemd/user/
```

On cloud:

```bash
# The .service units reference %h/.local/bin/... — symlink the /usr/local/bin
# binaries into ~/.local/bin so the unit files don't need rewriting.
mkdir -p ~/.local/bin
for b in sync-persona sync-all render-config; do
  ln -sf /usr/local/bin/personas-mesh-$b ~/.local/bin/personas-mesh-$b
done

# Enable lingering so user units run without an active login session:
sudo loginctl enable-linger wils

systemctl --user daemon-reload
systemctl --user enable --now personas-mesh-hetzner.timer
systemctl --user enable --now personas-mesh-github-mirror.timer
systemctl --user list-timers | grep personas-mesh
```

### 6. Add GitHub mirror remote on each bare repo

On cloud:

```bash
for p in archer bob julia kai mila nara piper reed urza warren; do
  git -C /srv/personas/$p.git remote add github git@github.com:kickinrad/$p.git 2>/dev/null || true
done
```

This requires cloud's SSH key to be authorized for the `kickinrad` GitHub account. If not set up:

```bash
# on cloud:
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_kickinrad -N ''
cat ~/.ssh/id_ed25519_kickinrad.pub
# then: paste the pubkey into https://github.com/settings/keys
cat > ~/.ssh/config.d/kickinrad <<'EOF'
Host github.com
  IdentityFile ~/.ssh/id_ed25519_kickinrad
EOF
```

### 7. Smoke test

On cloud:

```bash
personas-mesh-sync-all --verbose /srv/personas-work
systemctl --user status personas-mesh-hetzner.timer
journalctl --user -u personas-mesh-hetzner.service --since '1 minute ago'
```

## Coolify stack edit (Phase 2 prep — do later, after Phase 1 pilot proves the laptop-side loop)

The `bridgey-personas` service compose currently mounts `/opt/bridgey/personas/{p}:/workspace:ro`. To flip to the mesh-tracked bind:

1. Open Coolify → Project `my-cloud` → Service `bridgey-personas` → compose tab.
2. For each `bridgey-{persona}` service, change:
   ```yaml
   - '/opt/bridgey/personas/julia:/workspace:ro'
   ```
   to one of:
   - **rw-workspace variant** (simpler, riskier — bot can write skills/): `- '/srv/personas-work/julia:/workspace:rw'`
   - **sidecar-rsync variant** (preferred — keeps `/workspace:ro`, only exposes memory dir as rw): add a second mount `- '/srv/personas-work/julia/user/memory:/data/bridgey/memory:rw'`
3. Redeploy (Coolify handles `pull_policy: never`; no image rebuild needed).
4. Verify: `ssh wils@cloud sudo -u root docker logs bridgey-julia-jgcko8w0o4gwoocs0cks8swo --tail 40`.

Decide between rw-workspace and sidecar-rsync during the Julia pilot; document which was picked in `docs/decisions.md` alongside this runbook.

## Rollback

If Phase 0 needs to be undone:

```bash
# on cloud:
systemctl --user disable --now personas-mesh-{hetzner,github-mirror}.timer
rm ~/.config/systemd/user/personas-mesh-*.{service,timer}
sudo rm -rf /srv/personas /srv/personas-work
sudo rm /usr/local/bin/personas-mesh-*
```

Persona repos on the laptop are unaffected by a rollback — they still have their GitHub origin as the primary remote until you re-point them (Phase 1).
