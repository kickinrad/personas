# Capability research

Read once the interview has made the role clear, or when an existing persona
needs a new tool, integration, skill, hook, or reusable worker.

## Search

Look for what would help this role, in this order:

1. Installed runtime capabilities: the session's skills, plugins, and MCP
   servers.
2. The official Claude Code and Codex plugin marketplaces.
3. The official MCP Registry (`registry.modelcontextprotocol.io`) and MCP
   servers published by the service's own vendor.
4. Apps and services with an API or CLI, where an installed CLI or an
   `op run`-style launcher that injects credentials at runtime fits.
5. Community skills, always labeled unofficial.

## Present

For each option, state:

- what it enables for this role;
- official or community;
- maintenance signals, such as recent releases, publisher, and adoption;
- auth and cost;
- privacy and data exposure: what leaves the machine, and to whom;
- runtime support: Claude Code, Codex, or both.

Recommend a small starting set, name what to skip and why, and let the user
choose. Build locally only when the role has a distinct trigger or procedure
nothing existing covers:

| Need | Preferred shape |
|---|---|
| Existing external service connection | runtime plugin, app, or MCP binding |
| Mature deterministic operation | installed CLI |
| Repeated multi-step role procedure | persona-local skill |
| Isolated one-run investigation or review | fresh runtime worker |
| Independently reusable delegated pipeline | persona-local agent |
| Lifecycle enforcement | one narrow hook |
| Deterministic transformation | `tools/` script |
| Role-local explanatory depth | `docs/` reference |
| Durable knowledge or current state | its canonical owner |

## Adopt

Installing, connecting, or creating an account requires the user's explicit
approval, asked separately. Approved choices feed the folder plan: MCP servers
in the ignored `.mcp.json`, with the ones subagents need listed in
`agentMcpServers`, and Claude plugins under `enabledPlugins` in
`.claude/settings.json`. Keep credentials and local configuration outside
tracked files. Record an executable dependency in the owning component; a
knowledge citation is never an installation edge.

## Verify

For each approved capability, confirm: the plugin is installed; settings and
MCP configuration agree; private bindings resolve outside Git; the credential
resolver succeeds; a fresh session in the persona discovers and uses it; and
one isolation control shows it does not fire outside its declared trigger.
