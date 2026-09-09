# Using Personas

Open a persona folder in Claude Code or Codex. Codex reads `AGENTS.md`;
Claude Code imports the same definition through `CLAUDE.md`. Role workflows
live under `skills/`. New folders inherit the runtime's model choice.

## Maintain a persona

Ask `personas:persona-dev` to create, evolve, reconcile, or activate a persona.
It reviews the folder and proposes changes before writing. Existing identity,
settings, integrations, and private context remain persona-owned.

Ask `personas:self-improve` to review repeated feedback and propose a focused
change to identity, procedure, or memory.

## Private context and memory

Optional `user/profile.md` and `user/memory/MEMORY.md` are ignored local
Markdown. Either runtime can read them when present. Native runtime memory is
separate and does not synchronize through Personas.

Keep `user/`, local settings, `.mcp.json`, and credentials out of Git. For
personalized Claude Code Cloud use, choose a private repository and commit
only content intended to travel. A fresh checkout normally has no `user/`
directory; supply additional context in the session when needed.

## Native agents and Codex profiles

The bundled helper can expose a persona as a native Claude or Codex agent,
or generate an independent Codex MCP profile. From the plugin source root,
preview the selected adapters:

```bash
python3 skills/persona-dev/scripts/persona-native-sync.py --persona /path/to/atlas --runtime all
```

Add `--apply` after reviewing the output. Each generated artifact belongs to
its source persona. The helper refuses foreign or unmarked destinations;
[troubleshooting](troubleshooting.md) covers legacy ownership conflicts.

| Option | Output |
|---|---|
| `--runtime claude` | Claude native agent |
| `--runtime codex --codex-artifact agent` | Codex native agent |
| `--runtime codex --codex-artifact profile` | Codex MCP profile |
| `--runtime all` | Both native agents and the Codex profile |

Codex artifacts default to `all`. A profile is written to
`$CODEX_HOME/persona-<slug>.config.toml`; load it with
`codex --profile persona-<slug>` from the persona folder. Native agents read
the live absolute `AGENTS.md`, so their runtime must have access to that path.

MCP configuration comes from ignored `.mcp.json`. Opt in to each Codex binding
with `--codex-mcp NAME` or the file's `codexMcpServers` list. Supported bindings
use stdio or HTTP; unsupported fields, transports, and credential literals
produce an error. Unselected bindings remain private to their existing runtime.

## Runtime support

Claude Code and Codex use native entry files and shared persona skills. Claude
Code Cloud uses the publishable Claude folder with environment-local context.
Gemini CLI and Kimi Code have no authored adapter. See the dated
[runtime evidence](runtime-evidence.md) for what has been exercised.
