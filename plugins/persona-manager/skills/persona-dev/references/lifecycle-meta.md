# Persona lifecycle meta — three-layer model, aliases, expansion, testing

Reference for the meta-context around the 9-phase scaffold in `SKILL.md`. Loaded on demand when answering questions about how personas work, not when scaffolding.

---

## Three-Layer Model

Every persona uses three layers — never mix them:

| Layer | File | Who Writes | Content |
|-------|------|-----------|---------|
| **Personality** | `CLAUDE.md` | Human (Claude proposes) | Role, rules, skills, communication style |
| **Context** | `user/profile.md` | Claude (from user interview, via AskUserQuestion) | Personal data, accounts, preferences |
| **Memory** | `user/memory/` | Native auto-memory (automatic via autoMemoryDirectory in settings.local.json). Stop/PreCompact hooks trigger reflection only — never manual file writes | Session outcomes, learnings, patterns |

---

## Profile.md vs Memory — Canonical Definitions

| Question | Answer | File |
|----------|--------|------|
| Will this be true next month without action? | Yes | `user/profile.md` |
| Did Claude discover or decide this? | Yes | `user/memory/MEMORY.md` |
| Should this always happen, every session? | Yes | `CLAUDE.md` rule |

**user/profile.md** = WHO you are, WHAT you have, HOW you like to work. Stable facts.
**user/memory/MEMORY.md** = WHAT HAPPENED, WHAT WAS DECIDED, WHAT WORKED. Dynamic learnings.
**CLAUDE.md rules** = HOW THE PERSONA BEHAVES. Permanent, promoted from patterns.

---

## CLI Aliases

Personas are invoked by name from any directory via shell functions that auto-discover `~/.personas/*/`.

### Setup

Create `~/.personas/.aliases.sh`:

```bash
#!/usr/bin/env bash
# Auto-discover personas and create shell functions
# Source this from your .bashrc, .zshrc, or equivalent

for _persona_dir in "$HOME/.personas"/*/; do
  [ -d "$_persona_dir" ] || continue
  _persona_name=$(basename "$_persona_dir")
  [ -f "${_persona_dir}CLAUDE.md" ] || continue

  # Read per-persona flags, or fall back to safe defaults
  if [ -f "${_persona_dir}.claude-flags" ]; then
    _flags=$(cat "${_persona_dir}.claude-flags")
  else
    _flags="--setting-sources project,local --remote-control"
  fi

  # Flags expand at eval-time into literal tokens in the function body.
  # Do NOT store in a local variable — zsh won't word-split it.
  eval "${_persona_name}() {
    if [ \$# -gt 0 ]; then
      (cd \"${_persona_dir}\" && claude ${_flags} -p \"\$*\")
    else
      (cd \"${_persona_dir}\" && claude ${_flags})
    fi
  }"
done
unset _persona_dir _persona_name _flags
```

**Source from your shell config** (add to `~/.zshrc` or `~/.bashrc`):

```bash
[ -f "$HOME/.personas/.aliases.sh" ] && source "$HOME/.personas/.aliases.sh"
```

After creating or updating a persona: `source ~/.personas/.aliases.sh` or restart your shell.

**Usage:**
- `{name}` — interactive session
- `{name} "do weekly review"` — one-shot prompt

**Per-persona flags:** Each persona stores its flags in `.claude-flags` (a single line). This is configured during Phase 8 (flag setup). If the file is missing, the alias falls back to safe defaults (no `--dangerously-skip-permissions`).

**What the flags do:**
- `--name {name}` — labels the session in the terminal title and prompt bar so you know which persona is running
- `--setting-sources project,local` — loads only the persona's `settings.json` and `settings.local.json` (ignores `~/.claude/settings.json`). Note: does NOT affect `CLAUDE.md` loading — that's blocked separately via `claudeMdExcludes` in the persona's `.claude/settings.json`
- `--dangerously-skip-permissions` — skips permission prompts. **Only safe when sandbox is enabled** (macOS/Linux/WSL2). Never use on Windows native
- `--remote-control` — enables browser extension and external tool integration (Claude in Chrome, etc.)

---

## First Session Flow

On first session, `user/profile.md` contains an unfilled template with placeholders and interview instructions. The SessionStart hook reads it, sees the placeholders, and uses `AskUserQuestion` to interview the user section by section. The persona follows the interview instructions embedded in the file to ask the right questions and fill out the profile in place.

On subsequent sessions, the SessionStart hook reads `user/profile.md` automatically. If any sections are still incomplete, the persona prompts the user to fill in the gaps before proceeding.

---

## MCP Availability Check

Always embed this pattern in every persona's Session Start (already in the CLAUDE.md template):

```
After reading user/profile.md: Check which MCP tools are available.
For any disconnected server, tell the user what's unavailable
and ask: skip for now, or help set it up?
Offer text-only mode if all MCPs are unavailable.
```

When adding MCP servers:
1. Document tools in CLAUDE.md under "MCP Tools Available"
2. Add domains to `.claude/settings.json` → `network.allowedDomains`
3. Configure the server in `.mcp.json` (gitignored)

---

## Expansion Packs

Optional capabilities that can be installed into personas after creation:

| Pack | Skill | What it adds | Good for |
|------|-------|-------------|----------|
| Dashboard | `persona-manager:persona-dashboard` | Visual dashboard (HTML), task tracking, open.sh | Personas with ongoing work, reviews, regular check-ins |

These are separate skills in persona-manager — invoke them when the user asks for the capability, or suggest them during Phase 2 (Research) when creating a persona.

During self-audits, personas can also discover expansion packs that would help with recurring needs.

---

## Testing a Persona

After creation, verify:

- [ ] Run `{name}` — does the SessionStart hook read `user/profile.md` (or trigger the interview if unfilled)?
- [ ] Try each skill trigger — does the right skill activate?
- [ ] Ask something outside its domain — does it redirect gracefully?
- [ ] End a session — does native auto-memory capture session learnings (check `user/memory/MEMORY.md` for new entries)?
- [ ] Check sandbox — `ls ../` from within the persona should fail

Test with adversarial prompts too — ask the persona to do something it shouldn't. A good persona redirects gracefully rather than blindly complying.

---

## Troubleshooting

**"command not found" when typing a persona name:**
- Shell aliases not loaded — run `source ~/.personas/.aliases.sh`
- Check that `~/.personas/{name}/CLAUDE.md` exists (the alias script requires it)

**Persona doesn't pick up profile:**
- Verify the file exists: `ls ~/.personas/{name}/user/profile.md`
- Check that hooks.json includes the SessionStart hook (reads user/profile.md automatically)

**MCP server not connecting:**
- Check `.mcp.json` syntax: `jq . ~/.personas/{name}/.mcp.json`
- Check the persona's `.claude/settings.json` for `allowedDomains` — MCP servers need network access

**Sandbox errors (Linux):**
- Bubblewrap must be installed: `which bwrap || sudo apt install bubblewrap`

---

## Guiding Persona Growth

Tips for users to get the most out of persona evolution:

**Do:**
- Correct the persona explicitly — "no, always do X instead" creates clear auto-memory entries that can be promoted to rules
- Review memory periodically — read `user/memory/MEMORY.md`, clean up entries that are wrong or stale
- Approve good promotions — when the persona proposes a rule or skill that fits, approve it
- Use trigger phrases consistently — this trains both you and the persona

**Avoid:**
- Vague feedback — "be better at this" gives the persona nothing actionable
- Editing persona files directly — tell the persona to make changes so it creates proper memory/commits
- Skipping the approval step — the propose/approve pattern exists to prevent drift
