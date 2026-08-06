# Personas folder parity evidence

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

Both runtimes passed the same six behavioral probes. Codex support is therefore
promoted from experimental to supported for the 3.0.0 folder contract.

This evidence proves explicit folder-memory reading. It does not claim that
Claude and Codex native auto-memory stores synchronize.
