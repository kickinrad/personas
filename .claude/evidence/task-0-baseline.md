# Task 0 baseline and recovery evidence

## Snapshot

- Repository: `personas-framework`
- Baseline commit: `d3a0ed1d29177f85df9cdc28f4e51378ed0da8d9`
- Branch: `main`
- Baseline working tree: only untracked `.claude/plans/personas-core-renewal.md` (preserved; not part of this work).
- Recovery ref: `refs/forge/personas-core-renewal-baseline-d3a0ed1d2917` → `d3a0ed1d29177f85df9cdc28f4e51378ed0da8d9`

## Marketplace and plugin versions

| Plugin | Claude marketplace source | Codex marketplace source | Claude manifest | Generated Codex manifest |
| --- | --- | --- | --- | --- |
| persona-manager | `./plugins/persona-manager` | `./plugins/persona-manager/.generated/persona-manager` | `2.0.2` | `2.0.2` |
| persona-dashboard | `./plugins/persona-dashboard` | `./plugins/persona-dashboard/.generated/persona-dashboard` | `2.0.1` | `2.0.1` |
| personas-mesh | `./plugins/personas-mesh` | `./plugins/personas-mesh/.generated/personas-mesh` | `1.0.1` | `1.0.1` |

## Current callers

- `.claude-plugin/marketplace.json` is the Claude marketplace caller and resolves the three authored `plugins/*` roots above.
- `.agents/plugins/marketplace.json` is the Codex marketplace caller and resolves their tracked `.generated/*` adapters.
- `tests/personas-test.sh` checks each authored plugin manifest and the Claude marketplace; `tests/framework-contract-test.py` imports all three plugin roots for contract checks.
- `.github/workflows/ci.yml` runs `tests/run-tests.sh`, validates every `plugin.json`, the two Persona Manager persona-dev assets, and both canonical marketplace files.

## Personas Mesh tracked source inventory (SHA-256)

```text
e12c68c6d1be4211534332d81c7c630289400c6c3d4f01fef9100baf24b5decb  plugins/personas-mesh/.claude-plugin/plugin.json
c80fd54f8ac58b9dcf07cb9c83433093e5bd4267e9df7a76d6e4a92e14f6dacb  plugins/personas-mesh/.generated/personas-mesh/.codex-plugin/plugin.json
75ec4eb8ab4d467d768a472e6ab22e78aa599fe884030737b2dab37af30d4a75  plugins/personas-mesh/.generated/personas-mesh/bin/install-launchers
750ec06ad79eb98bc74bee65e3818400cd0402e97818fc197408dbc05bfb6c1b  plugins/personas-mesh/.generated/personas-mesh/bin/mirror-all
7bba6b983d4da74eb55716ced3899cbee104ea2cf224dfeb80c5138087b4aa3c  plugins/personas-mesh/.generated/personas-mesh/bin/render-config
8d0c5346c93e0c5fea33938d8eb596956b5135bb682c23bef7a4269dd6258d16  plugins/personas-mesh/.generated/personas-mesh/bin/sync-all
cdeea2d60a5a901e54f6e33e3057180879d6eb0a874ebd7d194036a8924677ff  plugins/personas-mesh/.generated/personas-mesh/bin/sync-persona
7da4b4f22c312efa8f2f9b1811977b6d23e9db4c338914db827130b7caaf3b98  plugins/personas-mesh/.generated/personas-mesh/bin/sync-user-all
c3e97b75d44c6c1dbdbc89e698eb48a58948f077a4c6cc88c34b8e62bb8c5e0f  plugins/personas-mesh/.generated/personas-mesh/bin/sync-user-persona
2d5103134b4161e70172518f892d35fe01af8050805bb238bf925f862ec60761  plugins/personas-mesh/.generated/personas-mesh/capabilities.json
6b144feafeb5434d91ade8b894583bc32a5459595846669e6228f137c43a61ff  plugins/personas-mesh/.generated/personas-mesh/skills/mesh-doctor/SKILL.md
93534dbb5488aa80ce682f74f302b6788864c68616845e623c51cafce686e9c3  plugins/personas-mesh/.generated/personas-mesh/skills/setup/SKILL.md
cce0296672691f64228cdb4d9fe3e5e0a0c9e9b7965606b228790f26ae223840  plugins/personas-mesh/.generated/personas-mesh/skills/status/SKILL.md
7143d652ffafaee4e8441e37015109fbbedc3d79dc2c71b5d952b3548f5426b2  plugins/personas-mesh/.generated/personas-mesh/systemd/personas-mesh-mirror.service
3da24a0dd9d22a6aeb7f454dced595de9eb173ba309aa3d91ed95c126992171a  plugins/personas-mesh/.generated/personas-mesh/systemd/personas-mesh-mirror.timer
73d5993009e226bb39535bfdbdac3cb77ac6121f5def9a4d5de1f34bf7021f42  plugins/personas-mesh/.generated/personas-mesh/systemd/personas-mesh-sync.service
0bb3dc4d32c9b6cc66a21b4439c251ad952d4da5fb68a758dfc2d725b92919bd  plugins/personas-mesh/.generated/personas-mesh/systemd/personas-mesh-sync.timer
154bee17ebd29b9324e9bc75012a110c076da80228b16c6e76d2506109c4e50f  plugins/personas-mesh/.generated/personas-mesh/systemd/personas-mesh-user-sync.service
1f3463df05a8c3928a0a01ebee000c034c8b72008754f76f9f9d40cd77380304  plugins/personas-mesh/.generated/personas-mesh/systemd/personas-mesh-user-sync.timer
24bacaaa7a65eb93ae33e84f0245195b81ea9c7e0b90a3766878704a71b4409c  plugins/personas-mesh/.generated/personas-mesh/templates/.gitattributes
078ef10a06eb60fad0aefaf1e5048ab8d9b760f261897c8bc9bf6b3e721843d0  plugins/personas-mesh/.generated/personas-mesh/templates/.gitignore.additions
d8e397af03b5b032f21d0aa967086f0c78b33c87b76f2e9898ae0a144df7de02  plugins/personas-mesh/.generated/personas-mesh/templates/.mcp.json.template
9b0d0a701aef1738e0a8ab1f94a166d6c8987770173b92c3c809a79dffb8121b  plugins/personas-mesh/.generated/personas-mesh/templates/profile-env.example
ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356  plugins/personas-mesh/.generated/personas-mesh/templates/settings.local.json.template
8360e742c286c37c7f5a15b5786ce711ee9a286435a8b4cda2520b715cb302ef  plugins/personas-mesh/CLAUDE.md
19ee5b8b234ec1f471db55ea32e00d1d414fbdd26d682c61844d8a695d893fbc  plugins/personas-mesh/README.md
75ec4eb8ab4d467d768a472e6ab22e78aa599fe884030737b2dab37af30d4a75  plugins/personas-mesh/bin/install-launchers
750ec06ad79eb98bc74bee65e3818400cd0402e97818fc197408dbc05bfb6c1b  plugins/personas-mesh/bin/mirror-all
7bba6b983d4da74eb55716ced3899cbee104ea2cf224dfeb80c5138087b4aa3c  plugins/personas-mesh/bin/render-config
8d0c5346c93e0c5fea33938d8eb596956b5135bb682c23bef7a4269dd6258d16  plugins/personas-mesh/bin/sync-all
cdeea2d60a5a901e54f6e33e3057180879d6eb0a874ebd7d194036a8924677ff  plugins/personas-mesh/bin/sync-persona
7da4b4f22c312efa8f2f9b1811977b6d23e9db4c338914db827130b7caaf3b98  plugins/personas-mesh/bin/sync-user-all
c3e97b75d44c6c1dbdbc89e698eb48a58948f077a4c6cc88c34b8e62bb8c5e0f  plugins/personas-mesh/bin/sync-user-persona
d4011e1d4242f0e2175b038b9c99e331c6d63e308479f24321992efddbfab601  plugins/personas-mesh/hooks/session-start.sh
b4b11c11f1ec7eea01e00c9110576bf6e109763ed62cb93caf0c6c1cc7ec0c2c  plugins/personas-mesh/hooks/stop.sh
2d5103134b4161e70172518f892d35fe01af8050805bb238bf925f862ec60761  plugins/personas-mesh/interop/capabilities.json
a0ba4a93b814383f4e06eb5f73cfa907b36e90dc372f09624203f79d047b41c2  plugins/personas-mesh/skill-rules.json
6b144feafeb5434d91ade8b894583bc32a5459595846669e6228f137c43a61ff  plugins/personas-mesh/skills/mesh-doctor/SKILL.md
15836a1f365c8bcf9718d92d24f3ef697bd9115f6237fbc757e379c7c0c30b63  plugins/personas-mesh/skills/setup/SKILL.md
cce0296672691f64228cdb4d9fe3e5e0a0c9e9b7965606b228790f26ae223840  plugins/personas-mesh/skills/status/SKILL.md
7143d652ffafaee4e8441e37015109fbbedc3d79dc2c71b5d952b3548f5426b2  plugins/personas-mesh/systemd/personas-mesh-mirror.service
3da24a0dd9d22a6aeb7f454dced595de9eb173ba309aa3d91ed95c126992171a  plugins/personas-mesh/systemd/personas-mesh-mirror.timer
73d5993009e226bb39535bfdbdac3cb77ac6121f5def9a4d5de1f34bf7021f42  plugins/personas-mesh/systemd/personas-mesh-sync.service
0bb3dc4d32c9b6cc66a21b4439c251ad952d4da5fb68a758dfc2d725b92919bd  plugins/personas-mesh/systemd/personas-mesh-sync.timer
154bee17ebd29b9324e9bc75012a110c076da80228b16c6e76d2506109c4e50f  plugins/personas-mesh/systemd/personas-mesh-user-sync.service
1f3463df05a8c3928a0a01ebee000c034c8b72008754f76f9f9d40cd77380304  plugins/personas-mesh/systemd/personas-mesh-user-sync.timer
24bacaaa7a65eb93ae33e84f0245195b81ea9c7e0b90a3766878704a71b4409c  plugins/personas-mesh/templates/.gitattributes
078ef10a06eb60fad0aefaf1e5048ab8d9b760f261897c8bc9bf6b3e721843d0  plugins/personas-mesh/templates/.gitignore.additions
d8e397af03b5b032f21d0aa967086f0c78b33c87b76f2e9898ae0a144df7de02  plugins/personas-mesh/templates/.mcp.json.template
9b0d0a701aef1738e0a8ab1f94a166d6c8987770173b92c3c809a79dffb8121b  plugins/personas-mesh/templates/profile-env.example
ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356  plugins/personas-mesh/templates/settings.local.json.template
```

This inventory is calculated from the Task-0 baseline worktree and identifies both authored and tracked generated Mesh files. Reproduce it with: `git ls-files -z plugins/personas-mesh | sort -z | xargs -0 sha256sum`.

## Baseline gate

- `HOME=$(mktemp -d) bash tests/run-tests.sh`: passed — 22 shell checks and 11 Python contract tests; temporary home was deleted afterward.
- CI correction: `.github/workflows/ci.yml` validates the existing `assets/hooks-template.json` and `assets/settings-template.json` paths, plus both canonical marketplace files. The gate itself creates and uses a temporary `HOME`; it does not read a live `~/.personas`.
