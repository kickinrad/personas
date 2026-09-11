# Using Personas

Start Claude Code or Codex from your persona's folder. Ask for help with the
job you made it for; you don't need to repeat its whole role in every prompt.

Codex reads `AGENTS.md`. Claude Code reads the same definition through the
`@AGENTS.md` line in `CLAUDE.md`. The persona reads the matching workflow under
`skills/` when a task needs it. [Julia](../examples/julia/README.md) shows how
these few files fit together.

## Integrated and focused use

By default, a persona works alongside your normal Claude Code or Codex setup.
That keeps the tools and conveniences you already use while adding the
persona's project instructions, skills, and settings.

During creation, you can instead choose Claude Code's focused use for fewer
user-level customizations:

```bash
claude --setting-sources project,local
```

Codex has no supported equivalent, so it stays integrated with your normal
configuration. Focused Claude use does not replace managed organization policy,
authentication, or command-line options. A persona folder organizes
configuration—it is not a separate account or security container.

## Maintain a persona

Ask `personas:persona-dev` to create a persona, improve an existing one, or
check that its files still work together. It reviews what you have and proposes
changes before writing. Your existing personality, settings, connections, and
private context are yours to keep.

If you keep giving the same correction, ask `personas:self-improve` to help
make it stick. For example: “You keep suggesting meals with too much cleanup.
Review that feedback and propose a small change.” It can suggest an update to
the role, a workflow, or memory; you review the change.

## Settings and tools

Each persona can have its own Claude settings in `.claude/settings.json` and
Codex settings in `.codex/config.toml`. New personas use your runtime's model
choice unless you set one explicitly. Existing model choices are preserved.

Keep role-specific instructions and skills in the persona folder rather than
adding them to your global setup. Optional MCP connections let an agent work
with outside tools, such as a recipe library. Configure those privately and
grant only the access the role needs. Julia works without any connections.

Opening a folder does **not** automatically turn off global instructions,
settings, or tools. Runtime permissions and organization policies still apply.
For example, a Codex profile layers on top of its base user configuration;
it is not an isolated account. If you need a restricted toolset, configure it
in the runtime and check the active tools before using sensitive data.

## Private context and memory

Use optional `user/profile.md` for things the persona should know about you,
and `user/memory/MEMORY.md` for lessons worth keeping. For a chef, that might
mean your usual cooking time or a preference for one-pan dinners. Both are
ordinary local Markdown files, ignored by Git and readable by either runtime.

This is file-based context, not automatic access to past conversations.
Claude Code and Codex also have their own memory features; Personas does not
synchronize those.

Keep `user/`, local settings, `.mcp.json`, and credentials out of Git. Ignored
files won't come along when someone clones your persona or opens it in Cloud.
Provide any missing context in the session. If you deliberately share personal
context through a private repository, review exactly what you commit; never
commit credentials.

## Native agents and Codex profiles

Opening the folder is enough to get started. If you also want to call the
persona as a native Claude or Codex agent, the bundled helper creates the
runtime files that point to it. It can also create a separate Codex MCP profile.

From a checkout of this repository, preview what it would create:

```bash
python3 skills/persona-dev/scripts/persona-native-sync.py --persona /path/to/julia --runtime all
```

Replace `/path/to/julia` with your persona's location. Review the output, then
add `--apply` to write the files. The helper checks which persona owns an
existing file and refuses to overwrite someone else's or a hand-written one.
See [troubleshooting](troubleshooting.md) if an older file has no ownership record.

| Option | Output |
|---|---|
| `--runtime claude` | Claude native agent |
| `--runtime codex --codex-artifact agent` | Codex native agent |
| `--runtime codex --codex-artifact profile` | Codex MCP profile |
| `--runtime all` | Both native agents and the Codex profile |

Codex outputs default to `all`. A profile is written to
`$CODEX_HOME/persona-<slug>.config.toml`; load it with
`codex --profile persona-<slug>` from the persona folder. Native agents read
the live absolute `AGENTS.md`, so their runtime must have access to that path.

The helper reads MCP connections from ignored `.mcp.json`. Choose each
connection you want to make available to Codex with `--codex-mcp NAME` or the
file's `codexMcpServers` list. It supports stdio and HTTP connections and stops
on unsupported fields, connection types, or embedded credentials. Connections
you haven't selected aren't copied to Codex.

## Runtime support

Claude Code and Codex share the role and skills through their own entry files.
Claude Code Cloud uses the committed Claude folder; your ignored local files
stay on your machine. There are no bundled adapters for Gemini CLI or Kimi
Code. The dated [runtime evidence](runtime-evidence.md) records what we've
tested, including the limits of the Cloud checks.
