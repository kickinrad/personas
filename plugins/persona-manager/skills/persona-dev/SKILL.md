---
name: persona-dev
description: This skill should be used when the user asks to "create a new persona", "build me a persona", "add a skill to an existing persona", "wire a plugin into a persona", "enable a plugin for a persona", "update a persona's CLAUDE.md or profile", "set up hooks or self-improvement", or "document a new MCP tool in a persona". Also triggers when the user says "create a persona for".
---

# Persona Development

Personas live in `~/.personas/{name}/`, each as its own git-tracked directory with sandbox isolation.

> **Running from outside a persona home.** `persona-manager` is enabled only inside each persona's own `.claude/settings.json`, so from the main `/home/wilst` workspace — where persona-creation handoffs naturally land — `Skill('persona-manager:persona-dev')` won't resolve. Since this skill's job is scaffolding NEW persona homes, it must be reachable from outside them: read the cached copy at `~/.claude/plugins/cache/personas/persona-manager/<version>/skills/persona-dev/SKILL.md` and execute the procedure manually.

## Persona Structure

Each persona contains:

```
~/.personas/{name}/
├── .claude/
│   ├── settings.json              # Sandbox config (committed)
│   ├── settings.local.json        # autoMemoryDirectory (gitignored, created during setup)
│   ├── output-styles/             # Personality, tone, style (committed)
│   ├── hooks/
│   │   └── public-repo-guard.sh   # Blocks personal data in public repos (committed)
│   └── skills/
│       └── {domain}/{skill}/SKILL.md  # Domain skills (self-improve ships via the persona-manager plugin, not locally)
├── .gitignore                     # Secrets exclusion
├── hooks.json                     # SessionStart + Stop + StopFailure + PreCompact + PostCompact + PreToolUse hooks
├── .framework-version             # Framework version stamp (committed)
├── CLAUDE.md                      # Personality + rules
├── .mcp.json                      # MCP server config (gitignored)
├── tools/                         # Utilities, scripts, pipelines (committed)
├── docs/                          # Reference materials, plans (committed)
└── user/                          # Personal data silo (gitignored for public sharing)
    ├── profile.md                 # User context (filled from interview)
    └── memory/                    # Native auto-memory
        ├── MEMORY.md              # Index (first 200 lines loaded)
        └── *.md                   # Topic files (read on demand)
```

**Workspace organization:**
- `docs/` — domain knowledge, reference materials, plans. Use subdirs for categories (`docs/reference/`)
- `tools/` — executable tools, utilities, data pipelines. Each tool gets its own subdir if non-trivial
- `.claude/skills/` — reusable multi-step workflows (SKILL.md files)
- `user/` — personal data silo, ensure ALL personal data lands here: profile.md and auto-memory. Gitignored for public sharing
- Root — only framework files. Don't dump loose files here

---

## Creating a New Persona

### Phase 1: Discovery

Before building anything, understand what this persona needs to be. **Use `AskUserQuestion` for ALL discovery questions** — not conversational prompting. This gives the user structured input fields instead of a wall of text. Ask one topic at a time, with follow-ups as needed.

**Step 1: Domain & Name** — `AskUserQuestion`
- What domain or role? (finance advisor, personal chef, brand strategist, etc.)
- Suggest 4-5 fun, memorable first names that fit the role
- Let the user pick or propose their own
- Use `multiSelect: false` with name options + a "Something else" option

**Step 2: Personality & Voice** — `AskUserQuestion`
- Present 3-4 personality archetypes that fit the domain (e.g., "Enthusiastic mentor", "Dry-witted expert", "Patient teacher", "Opinionated veteran")
- Include a brief preview of each (1-2 sentences showing how it would sound)
- Ask for preferences: casual vs formal, opinionated vs neutral, proactive vs reactive

**Step 3: Workflows & Capabilities** — `AskUserQuestion`
- What key workflows will it handle? (weekly reviews, meal planning, code review, etc.)
- Are there recurring multi-step tasks? (→ skill planning)
- What kind of data does it work with? (→ tool/script needs)
- What should the persona push back on? (→ anti-patterns in CLAUDE.md)

**Step 4: User Context** — `AskUserQuestion`
- What does the user need the persona to know about them? (info, accounts, preferences, constraints)
- This shapes `user/profile.md` — ask what sections matter for this domain

**Step 5: Environment** — `AskUserQuestion`
- What environment? (CLI only, Desktop only, or both)
- Autodetect OS when possible (`uname`, check for WSL, check for Windows paths)
- Present detected config and confirm
- This determines Phase 9 setup (aliases, Desktop config, or both)

**Step 6: External Services** — `AskUserQuestion`
- What external services or APIs does the persona need?
- Present common integrations for the domain as options
- This feeds directly into Phase 2 research

**Step 7: Inheritance Posture** — `AskUserQuestion`

Personas inherit some things from the user's `~/.claude/` directory by default. Ask which posture the user wants for this persona — high-level first, then drill down if they want granular control.

**Initial question** (single-select):
- **Strict isolation** — block global CLAUDE.md, no extra plugins. The persona only sees its own scaffold + the framework defaults (persona-manager, personas-mesh)
- **Selective inheritance (Recommended)** — block global CLAUDE.md, but choose plugins explicitly from `~/.claude/plugins/marketplaces/`. Default for most personas
- **Open inheritance** — inherit Wils's global CLAUDE.md too (for personas that want the user's voice/style/red-lines applied). Rare; only choose if the persona is meant to *be* an extension of the user

**If "Selective inheritance":** drill down with up to two follow-up `AskUserQuestion` calls:

1. *Block global CLAUDE.md?* — yes (default) writes `claudeMdExcludes: ["**/.claude/CLAUDE.md"]` to the persona's `.claude/settings.json`. No keeps the leak
2. *Which plugins to enable?* — multi-select from the available plugins. Discover them via:
   ```bash
   for mp in ~/.claude/plugins/marketplaces/*/plugins/*/.claude-plugin/plugin.json; do
     jq -r '.name' "$mp"
   done
   ```
   Default-checked: `persona-manager@personas`, `personas-mesh@personas`, `vault@core`, `obsidian@obsidian-skills` (every persona needs the framework pair plus vault + obsidian for the shared-brain integration baked into CLAUDE.md). User adds domain-relevant plugins beyond those

**If "Strict isolation":** apply the same as Selective with claudeMdExcludes ON and only the two framework plugins enabled. No drill-down.

**If "Open inheritance":** skip `claudeMdExcludes`. Still ask which plugins to enable (the global plugin set doesn't auto-merge — the persona's settings.json explicitly lists them).

Store the chosen posture (and chosen plugin list) so Phase 5h can apply them.

Don't rush this. A well-understood persona is easier to build and evolves better. Ask follow-up questions — domain expertise matters.

### Phase 2: Research

Before writing a single file, research what tools and integrations could enhance this persona. Work through the discovery categories and the where-it-lives table in [references/research-toolkit.md](./references/research-toolkit.md) — MCP servers, CLI tools, APIs, skills, agents, hooks, scripts, reference material, scheduled tasks, and expansion packs (e.g., `persona-dashboard:install`).

Present findings to the user: "Here's what I found that could enhance this persona: [list]. Which of these should we include?"

### Phase 3: Plan Review

Before touching the filesystem, present the complete persona plan to the user for approval using `AskUserQuestion`. This is the gate — nothing gets built until the user says go.

**Include in the plan summary:**
1. **Identity** — name, role, personality archetype chosen in Phase 1
2. **Integrations** — every MCP server, CLI tool, API, and script from Phase 2 research, with status (found / needs setup / custom build)
3. **Skills** — planned domain skills with trigger phrases and brief descriptions
4. **Hooks** — standard 6 + any domain-specific hooks identified
5. **Sandbox** — network domains to allowlist for MCP servers and APIs
6. **File inventory** — complete list of files and directories that will be created
7. **Environment** — CLI/Desktop/both, OS detected, proposed launch flags

Present this as a single `AskUserQuestion` with options:
- "Looks good — build it" → proceed to Phase 4
- "I want to change something" → discuss and loop back
- "Start over" → return to Phase 1

**Do NOT proceed to scaffolding until the user approves the plan.** This prevents the assistant from barreling through file creation without alignment on what's being built.

### Phase 4: Scaffold

**First, validate the persona name:**
- Must match `^[a-z][a-z0-9-]*$` — lowercase letters, numbers, and hyphens only
- Must start with a letter (not a number or hyphen)
- No dots, slashes, spaces, or special characters — these break shell aliases and directory paths
- Maximum 30 characters — keeps paths manageable
- Reject immediately if the name contains `.`, `..`, `/`, `\`, spaces, or shell metacharacters (`$`, `` ` ``, `!`, `;`, `&`, `|`, etc.) — these could cause path traversal or command injection
- If invalid, explain why and suggest a corrected version (e.g., "My Finance Bot" → "finance-bot")

**Then check if the persona already exists:**
- If `~/.personas/{name}/CLAUDE.md` exists, stop and ask: "A persona named `{name}` already exists. Update it, or pick a different name?"
- Don't proceed with scaffolding if it would overwrite an existing persona

**Determine the personas root directory:** environment-dependent — see [references/environments.md](./references/environments.md) for the per-environment matrix (macOS / Linux / WSL2 / Windows native / Cowork), Cowork detection, and the WSL2 + Desktop symlink procedure.

**Check sandbox prerequisites before scaffolding:**
- On Linux/WSL2: verify `bwrap` (bubblewrap) is installed: `command -v bwrap`
- If missing, warn the user and offer the install command before proceeding:
  - Ubuntu/Debian: `sudo apt-get install bubblewrap socat`
  - Fedora: `sudo dnf install bubblewrap socat`
- Don't block scaffolding — the persona will work without sandbox (with permission prompts instead). But warn clearly: "Without bubblewrap, the sandbox won't work and `--dangerously-skip-permissions` won't be safe to use. You'll get permission prompts for every action."
- On macOS: Seatbelt is built-in, no check needed
- On Windows native: no sandbox available, this is expected — flag it and move on

Create the directory structure:

```bash
mkdir -p ~/.personas/{name}/{.claude/output-styles,.claude/hooks,.claude/skills,tools,docs,user/memory}
```

### Phase 5: Build core files

> **🛑 Sacred rule for `user/` — never overwrite existing files.**
>
> Anything under `~/.personas/{name}/user/` is the user's personal data: profile, memory pages, MEMORY index. These accrue value over time and CANNOT be regenerated from a template. Before writing any file under `user/`, check whether it already exists. If it does, **skip the write and report what was preserved** ("preserved existing user/profile.md"). Only write if the file is missing — i.e., this is a true first scaffold.
>
> This rule applies whether persona-dev is being run on a fresh persona or invoked again on an existing one to apply framework scaffold updates. The framework's templates are bootstrap material, not source-of-truth. If you find yourself about to clobber a populated `user/profile.md` or `user/memory/MEMORY.md`, **stop and ask the user** — never assume regeneration is safe.

**5a. Write CLAUDE.md**

Use the template from `references/claude-md-template.md`. Key decisions:

- **Role summary**: One paragraph of spec-sheet expertise and operational focus. Personality and voice go in the output-style (`.claude/output-styles/`), NOT here. Boundary test: "Would this change how the persona SOUNDS, or what it DOES?" If SOUNDS → output-style. If DOES → CLAUDE.md
- **Workspace Hygiene section**: Include it — every persona must maintain its own workspace
- **Self-Improvement**: Point to the plugin-shipped self-improve skill — `Skill('persona-manager:self-improve')` — one line, not inline

**5b. Create user/profile.md** *(only if it does not already exist — see sacred rule above)*

**Guard first:** if `~/.personas/{name}/user/profile.md` already exists, skip this entire step and report "preserved existing user/profile.md". Do not read the template, do not customize, do not write. The existing profile is the user's personal data and is not yours to regenerate.

If the file is missing, use `references/profile-template.md` as a starting point and customize it for this persona's domain:
- Rename/add/remove sections to fit the domain (e.g., a finance persona needs "Accounts & Assets", a chef persona needs "Dietary Restrictions")
- Update placeholders to be domain-specific
- Update the interview instructions comment with persona-specific guidance on what to ask and how to probe deeper

Write directly to `user/profile.md`. On first session, the SessionStart hook reads this, sees the unfilled placeholders, and interviews the user to populate each section in place. No separate template file needed — the profile IS the template until it's filled out.

**Important: Use AskUserQuestion for the profile interview.** The persona should use the `AskUserQuestion` tool (not just conversation) when interviewing the user to fill out their profile. This provides a structured input experience — the user sees a clear question with context, rather than a wall of conversational text. Add this to the interview instructions in the template:
```
Use AskUserQuestion to ask each section's questions — one section at a time.
Present what you're asking about and why, then let the user respond.
```

**5c. Create output-style**

Create `.claude/output-styles/{name}.md` using `references/output-style-template.md`. This file defines WHO the persona IS:

- **Who I Am** — personality, narrative expertise, voice, opinions
- **How I'll Be** — behavioral traits (how the persona operates, not what it knows)
- **What I Won't Do** — character-driven refusals and anti-patterns (NOT operational rules — those go in CLAUDE.md)

The boundary rule: voice and personality go here; operational procedures, skills, tools, and security go in CLAUDE.md. Narrative expertise ("After 20 years in finance, I've seen every fad crash and burn...") goes here. Spec-sheet expertise ("Domains: budgeting, investing, tax planning") goes in CLAUDE.md's Role section.

The same split governs rule changes after scaffolding: when a shared rule propagates across personas, its invariant core lands in each persona independently while the warmth — the voice and framing in files like this one — stays untouched. See "Propagating a Shared Rule Across Personas" in the sibling `persona-update` skill.

Use the strong/weak examples from the template as guidance. The persona should have opinions and a point of view — bland personas get ignored.

**5d. Create first domain skill(s)**

Write at least one skill under `.claude/skills/{domain}/{skill-name}/SKILL.md` with:
- YAML frontmatter (name, description, triggers)
- Step-by-step workflow
- Expected output format

**5e. Self-improve skill — ships via the plugin, nothing to copy**

The `self-improve` skill (rule promotion, skill creation, tool discovery, periodic audits) is served by the persona-manager plugin itself, which every persona enables through `enabledPlugins` in Phase 5h. Do NOT scaffold a local copy at `.claude/skills/self-improve/` — a local copy duplicates the plugin skill and drifts. (Memory is handled by Claude Code's native auto-memory system, not by the self-improve skill.)

**5f. Set up hooks**

Copy `references/hooks-template.json` to `hooks.json` in the persona root. Copy `references/public-repo-guard.sh` to `.claude/hooks/public-repo-guard.sh` and make it executable (`chmod +x`). These hooks:
- **PreToolUse** (command, matcher: Bash): Runs `public-repo-guard.sh` before git commit/push — checks if the repo is public and blocks if personal data (`user/`, `.mcp.json`, secrets) would be exposed. Every persona gets this by default
- **SessionStart** (command): Injects instruction to read `user/profile.md` and interview the user if unfilled. No dependencies — just echoes a JSON instruction for Claude to act on. Must be `type: "command"` (SessionStart only supports command hooks)
- **Stop** (prompt): Prompts the persona to reflect on session insights — native auto-memory captures them automatically. Does NOT instruct manual file writes
- **StopFailure** (command): Writes a crash marker to `user/memory/.last-crash` when a session dies from an API error. PostCompact and the next SessionStart can detect this and offer to recover lost context
- **PreCompact** (prompt): Prompts reflection before compaction — auto-memory handles persistence. Does NOT instruct manual file writes
- **PostCompact** (command): After compaction, checks for the crash marker and reminds the persona to review what may have been lost

**5g. Create .gitignore**

Copy `references/gitignore-template` to `.gitignore`.

**5h. Configure sandbox + inheritance**

Copy `references/settings-template.json` to `.claude/settings.json`, then apply the inheritance posture chosen in Phase 1 Step 7:

- If posture is Strict or Selective with "block global CLAUDE.md = yes" → keep the `claudeMdExcludes: ["**/.claude/CLAUDE.md"]` from the template
- If posture is Open or Selective with "block global CLAUDE.md = no" → remove the `claudeMdExcludes` key
- Set `enabledPlugins` to the user's chosen plugin list (always include `persona-manager@personas` and `personas-mesh@personas` as the framework minimum)

Add any persona-specific network domains for MCP servers to `allowedDomains`. The template includes `extraKnownMarketplaces` and `enabledPlugins` to auto-install persona-manager — this gives every persona access to persona-dev for self-evolution without manual plugin installation.

Also create `.claude/settings.local.json` with the memory directory and output-style setting. **Use the absolute path** to the persona's memory directory — relative paths break on WSL where the project root is on `/mnt/c/` but Claude resolves relative paths from the Linux side:
```json
{
  "autoMemoryDirectory": "/absolute/path/to/.personas/{name}/user/memory",
  "outputStyle": "{PersonaName}"
}
```
For example, if the persona lives at `~/.personas/warren/`, the value would be `/home/username/.personas/warren/user/memory` (Linux/WSL) or `/Users/username/.personas/warren/user/memory` (macOS). Use the actual resolved path, not `~`.

**`outputStyle` must match the `name:` field in `.claude/output-styles/{name}.md` exactly** (case-sensitive). The convention is Capitalized — `Warren`, `Piper`, `Mila`. Without this, the persona boots in default Claude voice and the user has to run `/output-style {PersonaName}` manually each session.

**Important:** `autoMemoryDirectory` and `outputStyle` must be in `settings.local.json`, not `settings.json`. Claude Code ignores `autoMemoryDirectory` in project settings (`.claude/settings.json`) as a security measure — it only works from local or user settings. The `settings.local.json` file is gitignored, so persona-dev must create it during setup on each machine.

**Setting-source precedence — why the persona's output-style wins.** The persona alias launches with `--setting-sources project,local` (Phase 8), which loads only the `project` source (`.claude/settings.json`) and `local` source (`.claude/settings.local.json`) — the `user` source (`~/.claude/settings.json`) is excluded entirely. Output-style resolves by source precedence `local > project > user`, so the `outputStyle` in `settings.local.json` wins and there is **no fallback to any global output-style** — a persona that omits the key boots in default Claude voice, never the user's global style. To verify which style a persona actually uses: confirm `outputStyle` in `.claude/settings.local.json` names a file that exists in `.claude/output-styles/`, check that `.claude/settings.json` doesn't set a conflicting `outputStyle`, and run `/output-style` in a live persona session to see the resolved active style.

**5i. Create README.md**

Every persona repo gets a short README — copy the skeleton from [references/readme-template.md](./references/readme-template.md) and fill in the placeholders. Keep it minimal; this isn't a library, it's a personal assistant.

**5j. Scaffold the vault home**

The persona's vault home is where its durable knowledge accrues (decisions, playbooks, captures). Bootstrap it now so the persona has a MOC to land work in from session one.

1. Dispatch the `vault:curator` agent — the single vault front door — to pick the persona's natural domain home per the routing paragraph in `references/claude-md-template.md` (venture work under `Areas/Ventures/<Name>/`, agency work under `Areas/BFF/`, personal-admin domains under `Areas/Personal Admin/…`, and so on).
2. Have curator create the MOC folder note at that home — curator owns the write; don't write vault files directly.
3. The MOC stub should have proper frontmatter (`author: {name}`, `type: moc`, `tags: [personas]`, `created: <date>`), an "Open work" section, and a "Recent captures" section.
4. Skip Phase 5j with a clear warning if `~/.vault/` is unreachable (machine without WSL mount).

**5k. Validate scaffold**

Before proceeding, verify all required files exist:
- [ ] `README.md`
- [ ] `CLAUDE.md`
- [ ] `.claude/output-styles/{name}.md` (voice and personality)
- [ ] `user/profile.md` (template with placeholders, ready for first-session interview)
- [ ] `hooks.json`
- [ ] `.claude/hooks/public-repo-guard.sh` (executable)
- [ ] `.gitignore`
- [ ] `.claude/settings.json`
- [ ] `.claude/settings.local.json` (autoMemoryDirectory configured)
- [ ] `enabledPlugins` in `.claude/settings.json` includes `persona-manager@personas` (ships the self-improve skill)
- [ ] At least one domain skill in `.claude/skills/`
- [ ] `.framework-version` (stamped with current plugin version)
- [ ] Vault-home MOC exists at the persona's natural domain home (skipped if Phase 5j unavailable)

If anything is missing, fix it now — don't proceed with gaps.

**5L. Stamp framework version**

Write the current plugin version to `.framework-version` in the persona root. Read the version from this plugin's `.claude-plugin/plugin.json`. This single-line file tracks which framework version the persona was built with — persona-update uses it to detect drift.

### Phase 6: Configure integrations

If Phase 2 identified useful tools and integrations:

1. Document everything in CLAUDE.md under "Tools & Integrations" — organized by type (MCP servers, CLI tools, APIs, scripts)
2. For MCP servers: add domains to `.claude/settings.json` → `network.allowedDomains`, tell the user how to configure `.mcp.json` (gitignored — secrets go here)
3. For CLI tools: add usage instructions to relevant skills or CLAUDE.md
4. For APIs: create wrapper scripts in `tools/` or document usage patterns in skills
5. For skills: write the SKILL.md files that wrap tool usage into complete workflows
6. For agents: create agent definitions in `.claude/agents/` with appropriate system prompts and tool access
7. For hooks: add entries to `hooks.json` for domain-specific behavioral automation
8. For scripts: write to `tools/`, make executable, add brief comment header
9. For expansion packs: ask the user if they want to install them now

### Phase 7: Initialize git + GitHub sync

```bash
cd ~/.personas/{name}
git init
git add -A
git commit -m "feat({name}): initial scaffold"
```

**Always ask about GitHub sync** — don't skip this step:
- "Want to set up a GitHub repo so this persona syncs across machines?"
- If yes: `gh repo create {github-username}/{name} --private --source=. --push`
- If no: Skip — can always add a remote later
- Explain the benefit: backup, version history, sharing between CLI/Desktop/machines

**After creating the repo, set description and topics:**
```bash
gh repo edit --description "{PersonaName} — {one-line role description}. A self-evolving AI persona on Claude Code."
gh repo edit --add-topic claude-code --add-topic persona
```
Add 1-2 domain-specific topics too (e.g., `finance`, `cooking`, `fitness`).

**Public vs private — the persona handles this, not the user:**
- **Private repo (default):** Safe to commit everything including `user/` (profile, memories). Good for personal backup and cross-machine sync
- **Public repo:** If the user chooses public (or says "make it public"), the persona MUST immediately:
  1. Uncomment `user/` in `.gitignore`
  2. Remove `user/` from git tracking: `git rm -r --cached user/`
  3. Commit the change: `git commit -m "fix({name}): gitignore user/ for public repo"`
  4. Create a fresh remote (don't push existing history that may contain personal data)
- **Going public later:** If the self-improve skill or the user detects the repo has gone public, the persona handles the same steps automatically — don't ask the user to do it manually, they'll forget. The `public-repo-guard.sh` hook is the safety net, but the persona should proactively fix the gitignore rather than waiting for the hook to block

**Never commit these to any repo (public or private):**
- `.mcp.json` — contains API keys and secrets (always gitignored)
- Files matching `*.env`, `*.secret`, `*.key`, `*.pem` — credential files

### Phase 7b: Join the meshes

Wire the new persona into the two mesh layers. Keep this step thin — `personas-mesh:setup` owns the per-persona wiring detail; don't restate its procedure here.

**(a) Git mesh (state sync).** Create the hub bare repo and swap the persona's origin:

```bash
ssh wils@cloud git init --bare /srv/personas/{name}.git
cd ~/.personas/{name}
git remote rename origin github 2>/dev/null || true   # keep GitHub as mirror if it exists
git remote add origin ssh://wils@cloud/srv/personas/{name}.git
git push -u origin main
```

Then run `Skill('personas-mesh:setup')` for the rest of the per-persona wiring (sync hooks, `.gitattributes`, rendered configs, timers).

**(b) Bridgey spoke (agent mesh).** Give the persona an A2A endpoint:

1. Pick the next free port in the 8092+ range — check the hub's `~/.bridgey/bridgey.config.json` for ports already taken
2. Create `~/.bridgey/personas/{name}.config.json` (copy a sibling persona's config; swap name, port, token)
3. Add the persona's entry to the hub config's agents array
4. Install + enable a `bridgey-persona@{name}.service` unit
5. Restart the hub so it picks up the new spoke

### Phase 8: Configure launch flags

Autodetect the environment, present the recommended flag set, walk the user through customization via `AskUserQuestion`, then write the chosen flags to `~/.personas/{name}/.claude-flags` (a single line, sourced by the alias). The full procedure — detection script, per-flag walkthrough table, defaults by environment — lives in [references/launch-flags.md](./references/launch-flags.md).

**Windows guardrail:** never write `--dangerously-skip-permissions` to `.claude-flags` on Windows native — no OS-level sandbox exists there; refuse even if the user insists (canonical warning in [references/launch-flags.md](./references/launch-flags.md)).

### Phase 9: Configure access + verify

Set up access per the environment detected in Phase 1 — shell aliases (macOS/Linux/WSL2), a PowerShell function (Windows native), or Claude Desktop project-folder + MCP config merge. The full procedure, including environment limitations, is the "Configure Access" section of [references/lifecycle-meta.md](./references/lifecycle-meta.md).

Then verify the persona works — run through the "Testing a Persona" checklist in the same file.

---

## Wiring a Plugin into an Existing Persona

To give an existing persona a capability that ships as a Claude Code plugin, wire it in this order — each step gates the next:

1. **Register the marketplace** — if the plugin's marketplace isn't in the persona's `.claude/settings.json` → `extraKnownMarketplaces`, add it:
   ```json
   "extraKnownMarketplaces": {
     "{marketplace}": { "source": { "source": "github", "repo": "{owner}/{repo}" } }
   }
   ```
2. **Enable the plugin** — add `"{plugin}@{marketplace}": true` to `enabledPlugins` in the same file. The plugin auto-installs on next launch — no manual `/plugin install`.
3. **Scope sandbox + permissions** — add any domains the plugin's tools call to `network.allowedDomains`. If the plugin needs writes outside the persona's directory (e.g., a token-refresh file), extend `filesystem.allowWrite` to exactly those paths — no broader.
4. **Document in CLAUDE.md** — add the plugin's skills to the persona's Skills table (trigger phrase, skill name, what happens), plus a usage-posture line under Tools & Integrations stating how this persona uses the capability (e.g., read-only queries for coaching context, never writes). An enabled plugin the CLAUDE.md never mentions won't be reached for — and a posture narrower than what the plugin allows must be stated explicitly.
5. **Verify** — restart the persona session, confirm the plugin's skills are listed, and run one trigger phrase end-to-end.

---

## Lifecycle meta — three-layer model, aliases, expansion, testing, troubleshooting

For the meta-context around the 9-phase scaffold above (three-layer model, profile vs memory boundary, CLI alias setup script, first-session flow, MCP availability check, expansion packs, testing checklist, troubleshooting, guiding persona growth), see [references/lifecycle-meta.md](./references/lifecycle-meta.md).

---

## References

Templates and helper files used by the scaffolding phases above. All live in `references/` alongside this SKILL.md.

- [claude-md-template](./references/claude-md-template.md) — CLAUDE.md skeleton written in Phase 5a
- [output-style-template](./references/output-style-template.md) — `.claude/output-styles/{name}.md` skeleton written in Phase 5c
- [profile-template](./references/profile-template.md) — `user/profile.md` skeleton written in Phase 5b
- [readme-template](./references/readme-template.md) — `README.md` skeleton written in Phase 5i
- [research-toolkit](./references/research-toolkit.md) — Phase 2 discovery categories + where-it-lives table (shared with self-improve Level 4)
- [environments](./references/environments.md) — Phase 4 personas-root matrix, Cowork detection, WSL2 symlink
- [launch-flags](./references/launch-flags.md) — Phase 8 flag reference; canonical Windows `--dangerously-skip-permissions` prohibition
- [lifecycle-meta](./references/lifecycle-meta.md) — three-layer model, CLI aliases, Phase 9 access setup, testing, troubleshooting
