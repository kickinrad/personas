# Changelog

## 0.11.0 — 2026-10-18

- **Craft:** every persona states its outcome as a verb and gains a Craft
  section naming its instruments and raw inputs, the adjacent fields it
  borrows methods from, and the outside proof that its work is right. The
  interview asks the four questions a field-leading professional would answer,
  after Felix Rieseberg's
  [How to be more ambitious](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/).
- **Shared rules:** rules every persona shares live once in the plugin's
  `assets/PERSONAS.md`. The sync helper writes an identical `PERSONAS.md`
  into each persona, which its `AGENTS.md` imports, and reports drift.
- **Breaking:** personas no longer use `CLAUDE.md`. Claude Code 2.1.281 or
  later reads `AGENTS.md` directly; delete each persona's `CLAUDE.md` and add
  the `@PERSONAS.md` line. The fleet verifier flags any that remain.
- **Evals:** `persona-native-sync.py --eval-plugin DIR` wraps a persona for
  `claude plugin eval`, compared against plain Claude. `self-improve` turns a
  promoted correction into a private replay case in `user/evals/`.
- Remove the pre-0.9 `.mcp.json` migration, the unread capability
  declaration, and tests that asserted documentation wording. The fleet
  verifier moves to `skills/persona-dev/scripts/`.

## 0.10.0 — 2026-10-05

- Use the root plugin directory for both Claude Code and Codex, with
  `.claude-plugin/plugin.json` as the release manifest.
- Keep Codex runtime support declared in the capability contract without a
  second plugin manifest. Persona native subagent sync remains available.

## 0.9.1 — 2026-10-05

- Clarify when persona development and persona-local self-improvement apply.
- Keep repository contributor guidance in `AGENTS.md`; remove the root
  `CLAUDE.md` import that Claude's strict plugin validator rejects.

## 0.9.0 — 2026-10-03

- **Layout change:** the subagent MCP allowlist moves from `.mcp.json`
  `agentMcpServers` to a tracked `.agent-mcp.json` list of server names, so
  `claude mcp add` no longer erases it. `persona-native-sync.py --apply`
  migrates an existing list, and the fleet verifier flags one left behind.
- The fleet verifier now reports a persona folder that lost its `AGENTS.md`
  instead of silently skipping it.
- Drop the unread Gemini CLI, Kimi Code, folder-memory, and Cloud entries
  from the capability declaration. Behaviour is unchanged.

## 0.8.0 — 2026-09-25

- Create personas through an interview: one question at a time, each with a
  recommended answer, covering the job, boundaries, context, workflows,
  runtimes, color, and launch.
- Research capabilities during the interview, from installed ones through
  official marketplaces, the MCP Registry, vendor servers, CLIs, and labeled
  community skills, and recommend a small starting set with auth, cost,
  privacy, and runtime support for each.
- Design each persona's character: concept, name, emoji, voice traits, humor,
  signature, pushback, and sample lines. The `AGENTS.md` template's Voice
  section now holds these placeholders.
- Say "always-loaded" instead of "resident" for content in every session's
  context, including the fleet verifier's heading error.

## 0.7.2 — 2026-09-24

- Declare global residency for Claude Code and Codex, matching how the
  plugin is installed and enabled.

## 0.7.1 — 2026-09-24

- Project remote MCP servers that use SSE or Claude Code's `oauth` setting
  (`clientId` and `callbackPort` only) into Claude subagents. Codex agents
  skip them, and the sync helper reports each skip instead of failing.
- Reject any other OAuth field, such as `clientSecret`, as a credential.
- Allow environment references and boolean flags under credential-named keys
  while still rejecting literal values.

## 0.7.0 — 2026-09-23

- Summon any persona as a native subagent from Claude Code or Codex. The sync
  helper writes one agent per runtime that reads the live `AGENTS.md` and
  resolves the persona's `skills/` and `user/` paths from its folder.
- Choose a Claude agent color with `--color`; later runs keep it.
- Give subagents the persona's tools: servers named in `.mcp.json`
  `agentMcpServers` are projected into both the Claude and Codex agents.
- **Breaking:** rename `codexMcpServers` to `agentMcpServers`; the
  `mcp_servers` alias is no longer read.
- **Breaking:** remove the generated Codex profile and the `--codex-artifact`
  and `--codex-mcp` options. Move older generated profiles and agents aside,
  then regenerate.
- Flag tracked private context (`user/`, local settings, `.mcp.json`, `.env`)
  in the fleet verifier, and drop checks for pre-0.6 folder layouts.
- Consolidate documentation into usage and troubleshooting guides.

## 0.6.0 — 2026-09-11

- Reset the public version from 6.2.2 as a one-time early-development
  correction; history and existing tags are unchanged.
- Keep focused launch as a Claude Code option. Codex remains integrated until
  it offers a supported user-configuration exclusion control.
- Reject HTTP MCP URLs with embedded credentials before projecting them to a
  Codex profile.

Earlier releases are recorded in Git history.
