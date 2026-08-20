# Personas folder parity evidence

## Current v5 canary — 2026-08-17

The synthetic, non-secret Atlas fixture at `/tmp/personas-v5-canary` exercised
the v5 contract: portable `AGENTS.md`, optional profile and memory routing,
and role-skill discovery. No live persona, credential, or external system was
mutated.

### Codex

```text
cd /tmp/personas-v5-canary && codex exec --skip-git-repo-check --ephemeral --ignore-user-config --sandbox read-only --json
```

Final result exactly:

```text
Atlas | weather ahead | do not publish or mutate external systems without approval | CERULEAN-COMPASS | HARBOR-SEVEN | NORTHSTAR-READY
```

This proves `AGENTS.md` loading plus profile, memory, and skill routing.

### Claude Code

```text
cd /tmp/personas-v5-canary && claude --setting-sources project,local --model claude-opus-4-6[1m] --plugin-dir ~/projects/markets/personas-framework -p --output-format json
```

Final result exactly:

```text
Atlas|weather ahead|Ask before publication|CERULEAN-COMPASS|HARBOR-SEVEN|NORTHSTAR-READY
```

The JSON `modelUsage` reports `claude-opus-4-6[1m]` with context window
`1000000`; there were no permission denials. This proves the Claude import
path and the tracked model setting under the same synthetic fixture.

### Current verdict

Codex and Claude Code passed the v5 behavior canary. This evidence covers
explicit folder context, not synchronization of runtime-native memory stores.

## Historical v3 canary — 2026-07-31

_Recorded 2026-07-31 against the sanitized Atlas folder in a temporary Git
repository. No live persona home was read or changed._

## Probe

Both runtimes were asked to load their native project instructions, read every
required persona source and `atlas-review` skill, and return six fields:
identity, voice, boundary, skill, profile, and memory.

The temporary ignored local context contained:

- preferred name: `River`;
- explicit memory phrase: `cobalt compass`.

## Codex

- Client: `codex-cli 0.146.0`
- Model reported by client: `gpt-5.6-sol`
- Mode: ephemeral, read-only sandbox
- Native discovery: `AGENTS.md`
- Result:

```json
{"identity":"Atlas","voice":"Direct, calm, concise, and plainspoken about technical risk.","boundary":"Never claim a test ran without its output.","skill":"atlas-review","profile":"River","memory":"cobalt compass"}
```

## Claude Code

- Client: Claude Code `2.1.220`
- Model reported by client: `claude-sonnet-5`
- Mode: print, no session persistence, read-only tools
- Native discovery: `CLAUDE.md`
- Result:

```json
{"identity":"Atlas","voice":"Direct, calm, and concise, explaining technical risk in plain language","boundary":"Never claim a test ran without its output.","skill":"atlas-review","profile":"River","memory":"cobalt compass"}
```

## Verdict

Both runtimes passed the same six behavioral probes for the historical 3.0.0
folder contract.

This evidence proves explicit folder-memory reading. It does not claim that
Claude and Codex native auto-memory stores synchronize.
