<p align="center">
  <img src="assets/banner.svg" alt="Personas" width="650">
</p>

# Personas

Re-explaining your preferences, working style, and boundaries to every new AI
session is exhausting. Personas helps you create one durable collaborator whose
role and procedure travel with its repository while personal context stays
local.

Persona Manager supports **Claude Code local**, **Claude Code Cloud** (only in a
private personalized repository), and **Codex**. Start by installing the
Persona Manager plugin:

```text
/plugin marketplace add kickinrad/personas-framework
/plugin install persona-manager@personas
```

## Before you start

- Claude Code local or Codex, plus permission to install a plugin.
- A local directory you may use for the persona home. The guided path uses
  `~/.personas/atlas`; choose another empty path if that name is already taken.
- Five to ten minutes for a useful sanitized first home, then a role review.
  `bin/personas create` makes the initial files deterministically; the skill
  adds role-specific procedure after you review its plan.
- For Claude Cloud, separately authorized GitHub access to an existing or new
  **private** persona repository. The framework repository may be public; each
  personalized Cloud persona repository is private.

No example below asks for a real profile, credential, or integration. See the
[sanitized Atlas example](examples/atlas-sanitized/README.md) before adapting
the flow to your own work.

## Quickstart: Claude Code local

1. Install Persona Manager with the commands above.
2. Create the sanitized initial home from a source checkout:

   ```bash
   bin/personas create atlas --destination ~/.personas --profile claude-local --json
   ```

   Expected JSON has `"status": "PASS"` and `"path": "…/atlas"`. The
   command makes a sibling staging directory and atomically renames it only on
   success; it opens no listener, sends no telemetry, or contacts a network.
3. In Claude Code, ask `persona-manager:persona-dev` to add Atlas’s role
   procedure for reviewing small software projects. It shows a plan and waits
   for approval before changing the sanitized home.
4. Expect `CLAUDE.md`, a thin `AGENTS.md`, role-local `skills/`, `.claude/`
   settings and hooks, plus local `user/` state.
5. Verify:

   ```bash
   bin/personas verify ~/.personas/atlas --profile claude-local
   ```

   Expected output begins `PASS: atlas` and ends with a count of checks. In an
   installed plugin context, use
   `${CLAUDE_PLUGIN_ROOT}/bin/personas verify … --profile claude-local`.

## Quickstart: Codex

1. Add the marketplace and install the same root plugin:

   ```bash
   codex plugin marketplace add kickinrad/personas-framework
   codex plugin add persona-manager --marketplace personas
   ```

2. Create the same sanitized home without Claude-only requirements:

   ```bash
   bin/personas create atlas --destination ~/.personas --profile codex --json
   ```

3. Ask Codex to refine the role after reviewing a plan. The plugin’s shared
   skills provide the procedure; the short `AGENTS.md` loads shared `CLAUDE.md`
   doctrine instead of duplicating it. Then verify without applying
   Claude-only requirements:

   ```bash
   bin/personas verify ~/.personas/atlas --profile codex
   ```

   A `PASS` means the shared and Codex checks passed. A Claude setting is not
   required by this profile.

## Quickstart: Claude Code Cloud

Cloud is for a persona repository you have deliberately made private. Before
creation, verification, CI, and every Cloud `SessionStart`, authenticated GitHub
evidence must report visibility exactly `PRIVATE`. Public, internal, unknown,
unavailable, or ambiguous evidence fails closed.

1. With separate approval, create or select the private persona repository.
   Repository creation is deliberately not performed by Persona Manager.
2. Prepare authenticated visibility inspection in both environments:

   - Locally, authenticate the GitHub CLI (`gh`).
   - `gh` is not pre-installed in Anthropic's Cloud VM. In the Claude Code
     Cloud environment, install it with the environment setup script and set a
     least-privilege `GH_TOKEN` environment variable that can read repository
     metadata for this private repository. The token belongs only in the Cloud
     environment—not in Git, project settings, prompts, or logs. Anyone allowed
     to edit that Cloud environment can see its variables, so keep access
     narrow.

   Persona Manager also accepts an explicitly configured
   `PERSONA_GITHUB_CLI` adapter for SessionStart and
   `PERSONAS_GITHUB_VISIBILITY_ADAPTER` for create/verify in controlled
   environments. Every adapter must fail closed unless authenticated evidence
   is exactly `PRIVATE`.
3. Create only after local `gh` can prove
   the named repository is `PRIVATE`:

   ```bash
   bin/personas create atlas --destination /workspace/personas --profile claude-cloud --repository OWNER/REPO --json
   ```

   The command uses `gh repo view OWNER/REPO --json visibility --jq .visibility`
   unless an explicit `PERSONAS_GITHUB_VISIBILITY_ADAPTER` is supplied for a
   controlled environment. A public, internal, unknown, unavailable, or
   ambiguous result writes neither final nor staging persona files. A `PASS`
   home includes a private-repository CI workflow, Cloud SessionStart preflight,
   and a committed `.persona-cloud-repository` marker binding the home to that
   exact GitHub repository. This path initializes a new empty local Git
   repository with that origin only; it does not create, clone, or push a
   remote. Adopting an existing nonempty repository requires separately approved
   migration work.
4. Commit only publishable doctrine and procedure: `CLAUDE.md`, `AGENTS.md`,
   role-local skills, public settings, hooks, README, and the generated CI
   workflow.
5. Keep `user/profile.md`, `user/memory/`, `.claude/settings.local.json`,
   `.mcp.json`, and every credential out of Git. Private visibility does not
   protect committed credentials; they are always forbidden.
6. The native project hook in `.claude/settings.json` verifies both the origin and its
   `.persona-cloud-repository` binding before it claims personalized context
   is safe to load. Verify with the Cloud profile:

   ```bash
   bin/personas verify /path/to/persona --profile claude-cloud --json
   ```

   `PASS` requires the binding to match `origin` and authenticated evidence
   of exactly `PRIVATE`; an unavailable `gh` or adapter is a failure, not an
   assumption of safety.

Persona Manager does not create GitHub repositories. Keep that separately
authorized operator action; the command receives a repository identity and
proves it private before it writes any Cloud persona file.

## What gets stored where

Publishable persona definition: role procedure, `CLAUDE.md`, thin `AGENTS.md`,
role-local skills, public settings, hooks, and README. Local-only state:
profile, memory, local settings, connection configuration, and credentials.
The generated `.gitignore` keeps local-only state out of Git by default.

Cloud auto-memory is environment-local. It is not presented as a portable
cross-session transport. Move any durable shared knowledge through its owning
system deliberately; do not copy it into a repository just to make it travel.

## Verify and recover

`bin/personas verify` is read-only. It returns `PASS`, `WARN`, or `FAIL` and
does not repair a home. Use `--profile shared`, `claude-local`, `codex`, or
`claude-cloud` to evaluate the relevant contract.

```bash
bin/personas verify /path/to/persona --profile shared --json
```

Use `WARN` for inspection, such as framework drift or a legacy local
`self-improve` copy. Resolve `FAIL` using the exact path in the report, then
run the same command again. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for
cancellation, recovery, and Cloud failure handling.

## Support matrix

| Surface | Status | What is supported |
|---|---|---|
| Claude Code local | Native | Shared skills, Claude settings, hooks, and verification |
| Claude Code Cloud | Preview, private only | Private-visibility preflight, bound repository, public doctrine, explicit local-state boundary |
| Codex | Native | Shared plugin skills, thin `AGENTS.md`, trusted plugin hook, Codex verification |
| Gemini CLI / Kimi Code | Unsupported | No adapter is authored |

For framework development, run `bash tests/run-tests.sh`. It uses temporary
homes and does not touch `~/.personas`.
