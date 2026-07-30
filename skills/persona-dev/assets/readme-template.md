# Persona README template

Every persona repo gets a short README. Keep it minimal — this isn't a library, it's a personal assistant.

```markdown
# {PersonaName} {emoji}

> {One-line role description}

A self-evolving AI persona built on [Claude Code](https://claude.com/claude-code) using the [personas](https://github.com/kickinrad/personas-framework) framework.

## Privacy boundary

Publishable files define the role and procedure: `CLAUDE.md`, `AGENTS.md`, the
output style, role-local skills, tools, and this README. Local-only files are
`user/profile.md`, `user/memory/`, `.claude/settings.local.json`, and `.mcp.json`;
the generated `.gitignore` excludes them. Credentials, tokens, signing keys, and
passwords stay in the approved credential manager and never enter Git, including
private repositories.

Persona creation is offline: it reads bundled templates and writes only the chosen
persona directory. It opens no listener and sends no telemetry. Runtime providers
may make their own requests when you start a session; review their settings before
use.

### Claude Cloud (private repository only)

Only after separately authorizing GitHub access, create or select a repository
and prove its authenticated GitHub visibility is exactly `PRIVATE`. Persona
Manager performs that proof before creation, and generated CI enforces it on
every push. Complete that boundary before writing or committing any personalized context.
Cloud startup needs no GitHub token; its offline check is:

```bash
.claude/hooks/public-repo-guard.sh --check-cloud-binding
```

A mismatched repository marker and origin stop the Cloud session. Public,
internal, unauthenticated, unreachable, or unknown visibility stop creation or
local verification. Private visibility does not permit credentials in Git.

## Usage

```bash
{name}              # interactive session
{name} "do weekly"  # one-shot prompt
```

## Setup

See the [personas framework](https://github.com/kickinrad/personas-framework) for installation and setup.
```

For **public repos**, consider adding a brief "What it does" section describing the persona's domain and skills.
