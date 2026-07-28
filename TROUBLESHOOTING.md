# Troubleshooting

## A skill cannot find its templates

Run from an installed or source plugin context that provides
`${CLAUDE_PLUGIN_ROOT}`. Framework skills resolve sibling references from that
root; they do not search an assumed marketplace or cache directory.

## Persona validation fails

```bash
plugins/persona-manager/bin/validate-persona /path/to/persona --json
```

The validator is read-only. Fix reported structure, JSON, sandbox, memory-path,
gitignore, or hook errors before stamping `.framework-version`.

If it reports `.claude/skills/self-improve/`, the persona has a legacy local
duplicate. The canonical skill ships with `persona-manager`; inspect and retire
the local copy only with explicit approval.

## Framework update notices do not appear

Confirm `persona-manager@personas` is enabled and the plugin's
`hooks/framework-version.sh` is executable. The hook resolves its own plugin
root and compares it with the persona's `.framework-version`.

## Dashboard cannot load a tab

Launch it through the generated `open-dashboard.sh` so the browser can fetch
`user/profile.md`, `user/memory/MEMORY.md`, and `CLAUDE.md`. The dashboard is
read-only and intentionally has no task or calendar store.

## Mesh scripts are newer than installed launchers

Source edits do not update active launchers. During an approved activation, run:

```bash
plugins/personas-mesh/bin/install-launchers
```

Each stable launcher records its source version, SHA-256, and immutable
installed artifact. Reinstall unit templates and run `systemctl --user
daemon-reload` only as part of the same approved activation.

## Mesh configuration rendering fails

Verify `op` is available and either `OP_SERVICE_ACCOUNT_TOKEN` or
`OP_SERVICE_ACCOUNT_TOKEN_FILE` is configured. Probe with an exit code while
discarding output:

```bash
op read "op://<vault>/<item>/<field>" >/dev/null
```

`render-config` fails before replacing its target if a secret or placeholder is
missing. When both files are JSON, rendered keys win and unrelated existing keys
remain.

## Mesh sync is unhealthy

Run `personas-mesh:status`, then `personas-mesh:mesh-doctor`. Profile roots, hub
transport, and deployment topology come from external profile configuration and
canonical operational knowledge, not plugin source.
