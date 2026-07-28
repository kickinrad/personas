<p align="center">
  <img src="assets/banner.svg" alt="personas" width="650">
</p>

# Personas

Personas is a framework for isolated, git-tracked AI assistant identities.
Framework mechanics live here; each persona's identity, voice, role procedure,
configuration, and local cache live in its own home.

## Release units

| Plugin | Purpose |
|---|---|
| `persona-manager` | Create, extend, update, and deterministically validate persona homes |
| `persona-dashboard` | Install an optional read-only browser view of persona-local context |
| `personas-mesh` | Synchronize persona repositories and render profile-local configuration |

The dashboard is not an action system. Google Tasks remains authoritative for
actions, Google Calendar for time, and Obsidian for projects and durable
knowledge.

## Claude Code

Install the marketplace and manager:

```text
/plugin marketplace add kickinrad/personas
/plugin install persona-manager@personas
```

Then ask Claude to create a persona. `persona-dev` discovers the role and
environment, presents a complete plan, and waits for approval before writing.
Every generated persona enables the plugin-shipped
`persona-manager:self-improve`; no persona-local copy is created.

## Persona home

```text
~/.personas/<name>/
├── CLAUDE.md
├── README.md
├── .claude/
│   ├── settings.json
│   ├── settings.local.json
│   ├── hooks/
│   ├── output-styles/
│   └── skills/
├── hooks.json
├── docs/
├── tools/
└── user/
    ├── profile.md
    └── memory/
```

`user/memory/` is native auto-memory. Persona-local skills contain role
procedure. Durable user and system knowledge belongs in its canonical knowledge
system rather than copied framework instructions.

## Runtime support

Claude Code is the canonical native runtime. Each plugin declares the proven
state of Claude, Codex, Gemini CLI, and Kimi Code support in
`interop/capabilities.json`. Portable scripts may serve as a replacement while
an ungenerated skill or plugin adapter remains unsupported.

## Validation

```bash
bash tests/run-tests.sh
plugins/persona-manager/bin/validate-persona ~/.personas/<name>
```

Repository tests use temporary fixture homes and never mutate live personas.
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for source, validation, dashboard,
and mesh recovery.
