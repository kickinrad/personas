# Launch flags — detection, walkthrough, Windows safety boundary

Canonical reference for Phase 8 (Configure launch flags) of `persona-dev`. This file owns the flag explanations and the Windows `--dangerously-skip-permissions` prohibition — other surfaces (SKILL.md spine, lifecycle-meta, persona-update, persona-validator) point here rather than restating.

## Step 1: Autodetect environment

```bash
# Detect OS and sandbox support
if [[ "$(uname -s)" == "Darwin" ]]; then
  OS="macOS"         # Seatbelt built-in, sandbox always available
  SANDBOX_OK=true
elif grep -qi microsoft /proc/version 2>/dev/null; then
  OS="WSL2"          # bubblewrap needed
  SANDBOX_OK=$(command -v bwrap &>/dev/null && echo true || echo false)
elif [[ "$(uname -s)" == "Linux" ]]; then
  OS="Linux"         # bubblewrap needed
  SANDBOX_OK=$(command -v bwrap &>/dev/null && echo true || echo false)
elif [[ "$OS" == "Windows_NT" ]] || command -v cmd.exe &>/dev/null; then
  OS="Windows"       # No sandbox support
  SANDBOX_OK=false
fi
```

If sandbox prerequisites are missing on Linux/WSL2, tell the user:
```bash
sudo apt-get install bubblewrap socat  # Ubuntu/Debian
sudo dnf install bubblewrap socat      # Fedora
```

## Step 2: Present default flags and walk through customization

Present the detected config and walk the user through each flag using `AskUserQuestion`. Explain what each one does, why it matters, and the tradeoff. **All flags are optional** — the user decides:

| Flag | What it does | Ask the user |
|------|-------------|--------------|
| `--setting-sources project,local` | Loads only this persona's `settings.json` and `settings.local.json`, ignoring `~/.claude/settings.json`. Keeps permissions, sandbox, and MCP config isolated. **Note:** does NOT affect `CLAUDE.md` loading — for that, the persona's `.claude/settings.json` uses `claudeMdExcludes` to block `~/.claude/CLAUDE.md` from auto-discovery | "This keeps your persona's settings isolated from your global Claude config. Recommended ON unless you want global settings to merge in. Enable?" |
| `--dangerously-skip-permissions` | Skips permission prompts for every tool use. **Only safe when OS-level sandbox is active** (macOS/Linux/WSL2) — the sandbox restricts filesystem + network even without prompts. **NEVER on Windows** | "This lets the persona work without asking permission for every action. It's safe because the sandbox restricts what it can access. Want autonomous mode, or prefer to approve actions manually?" |
| `--remote-control` | Enables browser extension integration and external tool connections | "This allows tools like the Chrome extension to connect to your persona. Enable?" |
| `--chrome` | Enables Claude in Chrome browser automation. Gives the persona access to your Chrome browser for web interaction, form filling, screenshots, and debugging | "This lets the persona interact with your Chrome browser (requires the Claude in Chrome extension). Does this persona need browser access?" |

**Resulting flag sets by environment (defaults, all customizable):**

| Environment | Sandbox? | Default flags |
|-------------|----------|---------------|
| macOS | Yes (Seatbelt) | `--setting-sources project,local --dangerously-skip-permissions --remote-control` |
| Linux | Yes (bubblewrap) | `--setting-sources project,local --dangerously-skip-permissions --remote-control` |
| WSL2 | Yes (bubblewrap) | `--setting-sources project,local --dangerously-skip-permissions --remote-control` |
| Windows native | **No** | `--setting-sources project,local --remote-control` |

`--chrome` is not in the defaults but is always offered as an optional addition during the walkthrough.

---

**⚠ WINDOWS NATIVE — CRITICAL SAFETY WARNING ⚠**

**NEVER use `--dangerously-skip-permissions` on Windows native.** Windows does not have OS-level sandboxing (no Seatbelt, no bubblewrap). This flag would give the persona **completely unrestricted access** to the entire filesystem and network — it could read any file, delete anything, and make arbitrary network requests with zero guardrails.

On macOS/Linux/WSL2, `--dangerously-skip-permissions` is safe because the sandbox blocks dangerous operations at the OS level even when permissions are skipped. On Windows, there is no such safety net.

**If the user asks to enable it on Windows, refuse and explain why.** Even if they insist. This is not a preference — it's a safety boundary. The persona-dev skill must enforce this by never writing `--dangerously-skip-permissions` to `.claude-flags` on Windows native, regardless of user request.

---

**Presentation flow:**

1. Show the recommended flag set for the detected OS environment (from the table above)
2. Briefly explain what each flag does in plain language
3. Ask: "These are the recommended defaults for your {OS} setup. Look good, or want to customize?"
4. If the user wants to customize, walk through each flag individually using `AskUserQuestion` — use the "Ask the user" column from the table above
5. `--chrome` is always presented as an optional addition: "Want to add Chrome browser automation? This lets the persona interact with web pages in your Chrome browser (requires the Claude in Chrome extension)."
6. On Windows, explain why `--dangerously-skip-permissions` is not available before moving on
7. Summarize the final chosen flags before writing to `.claude-flags`

## Step 3: Store the flags

Write the chosen flags into `~/.personas/{name}/.claude-flags` (a single line, sourced by the alias):

```bash
echo '--setting-sources project,local --dangerously-skip-permissions --remote-control' > ~/.personas/{name}/.claude-flags
```

This file is read by `.aliases.sh` so each persona can have its own flag configuration.
