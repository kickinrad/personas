# Troubleshooting

Common issues and fixes when working with personas.

## Persona Won't Start

**"command not found" when typing a persona name**
- Shell aliases not loaded. Run: `source ~/.personas/.aliases.sh`
- Check that `~/.personas/{name}/CLAUDE.md` exists (the alias script requires it)
- Restart your shell after creating a new persona

**Persona activates but ignores its CLAUDE.md**
- Personas only activate when CWD is the persona's directory. The alias handles this, but if you run `claude` manually, `cd` into the persona dir first
- Check that `.claude-flags` includes `--setting-sources project,local` (isolates the persona's config)

## Memory Not Persisting

**"My persona doesn't remember anything between sessions"**
- Verify `autoMemoryDirectory` is set in `.claude/settings.local.json` (NOT `settings.json` — Claude ignores it there as a security measure)
- The path must be **absolute** (e.g., `/home/user/.personas/warren/user/memory`). Relative paths break on WSL
- Check that `user/memory/` directory exists: `ls ~/.personas/{name}/user/memory/`
- Verify the Stop hook is present in `hooks.json` — it reminds the persona to persist learnings

**Memory files exist but persona doesn't read them**
- Check that `user/memory/MEMORY.md` exists and has entries pointing to topic files
- Only the first 200 lines of MEMORY.md are loaded — keep the index concise

## Profile Interview Not Triggering

**Persona skips the first-session interview**
- Verify `hooks.json` has the SessionStart hook that reads `user/profile.md`
- Check that `user/profile.md` exists and contains unfilled template placeholders
- If the profile was already partially filled, the persona may skip the interview — check for incomplete sections

## Sandbox Issues

**Permission denied errors on Linux/WSL2**
- Bubblewrap must be installed: `which bwrap || sudo apt-get install bubblewrap socat`
- If bubblewrap is missing, the sandbox can't enforce restrictions and you'll get prompts instead of autonomous mode

**Persona can't access an MCP server**
- Check that the server's domain is in `.claude/settings.json` → `network.allowedDomains`
- Default is only `api.anthropic.com` — you must add domains for each MCP server

**"ls ../" works when it shouldn't (sandbox not blocking)**
- Verify `.claude/settings.json` has `"sandbox": { "enabled": true }` and `"denyRead": ["../"]`
- On Windows native, sandbox is not available — this is expected behavior

## MCP Server Issues

**MCP server not connecting**
- Validate `.mcp.json` syntax: `jq . ~/.personas/{name}/.mcp.json`
- Check that the server's domain is in `allowedDomains` in `.claude/settings.json`
- If using Desktop Chat or Cowork, MCP servers must also be in `claude_desktop_config.json` (global), not just `.mcp.json`

**MCP works in CLI but not Desktop**
- CLI and Desktop Code tab read `.mcp.json` (per-persona)
- Desktop Chat and Cowork read `claude_desktop_config.json` (global). Servers need to be in both files for full coverage
- Desktop config locations:
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Restart Claude Desktop after modifying the config

## Cross-Platform Issues

**WSL2: Persona works in CLI but not Desktop**
- Desktop runs on Windows, not WSL. Personas must be accessible from the Windows side
- Create personas on the Windows side: `/mnt/c/Users/{WINUSER}/.personas/`
- Symlink from WSL: `ln -s /mnt/c/Users/{WINUSER}/.personas ~/.personas`
- The symlink must be created from WSL terminal, not from Cowork or Desktop

**WSL2: Slow I/O when persona is on Windows side**
- Files on `/mnt/c/` have worse I/O than native WSL paths
- If using CLI only, keep personas in WSL's `~/.personas/` for better performance
- Cross-filesystem penalty is a WSL limitation, not a personas issue

**Windows native: Getting permission prompts for everything**
- Windows has no OS-level sandbox. Permission prompts are expected and are your safety net
- Never add `--dangerously-skip-permissions` to `.claude-flags` on Windows — there's no sandbox to protect you

## Public Repo Issues

**Accidentally pushed personal data to a public repo**
1. Don't panic — act quickly
2. Uncomment `user/` in `.gitignore`
3. Remove from tracking: `git rm -r --cached user/`
4. Commit the fix: `git commit -m "fix: gitignore user/ for public repo"`
5. **Create a fresh remote** instead of force-pushing — old commits in the history still contain the data
6. If secrets were exposed, rotate all affected API keys immediately (see credential rotation in your persona's CLAUDE.md)

**Public repo guard keeps blocking my commits**
- The guard blocks when `user/` isn't gitignored, personal files are staged, `.mcp.json` is tracked, or secret-pattern files are staged
- Follow the fix instructions in the guard's error message
- If the repo should be private: `gh repo edit --visibility private`

## Persona Update Issues

**"persona-update broke my hooks"**
- If you customized `hooks.json` beyond the framework template, persona-update may conflict
- Check git diff to see what changed: `git diff hooks.json`
- Restore your version if needed: `git checkout HEAD -- hooks.json`
- Then manually merge any new framework hooks

**Framework version mismatch warning on every session**
- Run persona-update to sync: say "update persona" in a session
- Or manually update `.framework-version` to match the current plugin version

## Getting Help

- Framework issues: [github.com/kickinrad/personas/issues](https://github.com/kickinrad/personas/issues)
- Claude Code issues: [github.com/anthropics/claude-code/issues](https://github.com/anthropics/claude-code/issues)
