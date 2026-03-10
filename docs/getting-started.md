# Getting Started

This guide walks you through setting up the personas framework and running your first session.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- Git
- zsh or bash
- Linux (bubblewrap) or macOS (Seatbelt) for native sandboxing

## 1. Clone the Framework

The framework repo contains persona-manager (the meta-tool for scaffolding and evolving personas). Individual personas live separately in `~/.personas/`.

```bash
git clone https://github.com/kickinrad/personas.git ~/personas
cd ~/personas
```

## 2. Set Up Shell Aliases

Personas are invoked by name from any directory. Add the following to your shell config (e.g., `~/.zshrc`, `~/.bashrc`, or a sourced file like `~/.config/zsh/.personas.zsh`):

```bash
_PERSONAS_ROOT="$HOME/.personas"

for _p_dir in "$_PERSONAS_ROOT"/*/; do
  [[ -d "$_p_dir" ]] || continue
  _p_name=$(basename "$_p_dir")
  [[ -f "${_p_dir}CLAUDE.md" ]] || continue

  if [[ ! -f "${_p_dir}.mcp.json" ]]; then
    printf '{\n  "mcpServers": {}\n}\n' > "${_p_dir}.mcp.json"
  fi

  eval "${_p_name}() {
    if [[ \$# -gt 0 ]]; then
      (cd \"${_p_dir}\" && claude \
        --mcp-config \"${_p_dir}.mcp.json\" \
        --strict-mcp-config \
        -p \"\$*\")
    else
      (cd \"${_p_dir}\" && claude \
        --mcp-config \"${_p_dir}.mcp.json\" \
        --strict-mcp-config)
    fi
  }"
done
unset _PERSONAS_ROOT _p_dir _p_name
```

Then reload your shell:

```bash
source ~/.zshrc  # or whatever file you added it to
```

**What this does:**
- Scans `~/.personas/` for directories with a `CLAUDE.md`
- Creates a shell function for each persona (e.g., `warren`, `julia`)
- Each function `cd`s into the persona directory and runs Claude Code with the persona's MCP config
- `--strict-mcp-config` prevents global MCP servers from leaking into persona sessions

> **Tip:** Update `_PERSONAS_ROOT` if you store personas somewhere other than `~/.personas/`.

## 3. Create or Install a Persona

Create a persona using persona-manager, or manually scaffold one into `~/.personas/`:

```bash
# Using persona-manager
persona-manager "create a personal chef persona"

# Or list existing personas
ls ~/.personas/
# julia/  warren/  mila/
```

## 4. Configure Your Profile

Each persona ships a `profile.md.example` with the fields it needs. Copy it and fill in your details:

```bash
cp ~/.personas/julia/profile.md.example ~/.personas/julia/profile.md
```

Open `~/.personas/julia/profile.md` in your editor and fill in the blanks. This file is gitignored — your personal data stays local.

**What goes in profile.md:**
- Your name and household details
- Preferences relevant to that persona's domain
- Infrastructure details (API endpoints, service URLs)
- Anything the persona should know about you

## 5. Configure MCP Servers (Optional)

Some personas integrate with external services via MCP servers. Each persona's `CLAUDE.md` lists which MCP servers it can use.

Create or edit `.mcp.json` in the persona directory:

```json
{
  "mcpServers": {
    "mealie": {
      "command": "npx",
      "args": ["-y", "@mealie/mcp-server"],
      "env": {
        "MEALIE_URL": "https://mealie.example.com",
        "MEALIE_API_KEY": "your-api-key"
      }
    }
  }
}
```

This file is gitignored. Never commit API keys.

> **Tip:** If you use a password manager like `pass`, you can reference secrets inline: `"MEALIE_API_KEY": "$(pass show mealie/api-key)"`.

## 6. Run Your First Session

```bash
# Interactive session
julia

# One-shot prompt
julia "plan meals for the week"
```

On first launch, the persona will:
1. Read your `profile.md` for context
2. Check which MCP servers are connected
3. Tell you if anything is unavailable and offer to help set it up

## 7. First Session Walkthrough

Here is what to expect in your first interactive session:

1. **Profile check** — The persona reads your `profile.md`. If something is missing or unclear, it will ask.
2. **MCP availability** — It reports which integrations are connected and which are not.
3. **Try a skill** — Each persona has trigger phrases. For Julia, try "what's for dinner" or "plan meals for the week." For Warren, try "weekly review" or "budget health."
4. **Memory** — After the session, the persona writes learnings to `.claude/memory/MEMORY.md`. These persist across sessions.

## Troubleshooting

### "command not found" when typing a persona name

Your shell aliases are not loaded. Make sure you:
- Added the alias snippet to your shell config
- Ran `source ~/.zshrc` (or equivalent)
- Set `_PERSONAS_ROOT` to the correct path

### Persona does not pick up profile.md

- Verify the file exists: `ls ~/.personas/{name}/profile.md`
- Make sure you copied from `profile.md.example`, not renamed it
- Check that you are running the persona from the aliases, not from a random directory

### MCP server not connecting

- Check `.mcp.json` syntax: `jq . ~/.personas/{name}/.mcp.json`
- Verify the MCP server package is installed: `npx -y @package/name --version`
- Check API keys are valid
- Some MCP servers require network access — check the persona's `.claude/settings.json` for `allowedDomains`

### Sandbox errors (Linux)

- Bubblewrap (`bwrap`) must be installed: `which bwrap || sudo apt install bubblewrap`
- If you see permission errors, check `.claude/settings.json` — the `filesystem.allowWrite` and `filesystem.denyRead` arrays control access

### Sandbox errors (macOS)

- Seatbelt is built into macOS — no extra installation needed
- If a persona cannot access a file it should, check `.claude/settings.json` paths

## Next Steps

- [Creating Personas](creating-personas.md) — Build your own custom persona
- [Self-Improvement](self-improvement.md) — Understand how personas evolve
