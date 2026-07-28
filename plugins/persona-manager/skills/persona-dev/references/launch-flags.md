# Claude launch flags

Read this reference only when configuring the Claude launcher for a persona.
Codex loads the persona through its workspace and `AGENTS.md`; it does not use
`.claude-flags`.

## Contract

Discover supported flags from the installed Claude CLI before proposing them.
Store the approved single-line set in `.claude-flags`; the launcher reads it as
configuration, not shell code.

`--setting-sources project,local` isolates the persona's project and local
settings from unrelated global Claude settings. Add other flags only for a
proven role requirement and after explaining the authority they grant.

Permission bypass is not a persona default. Use the runtime's sandbox and
approval policy. A persona configuration may not weaken the global safety
contract or turn missing sandbox evidence into assumed protection.

Verify the launcher tokenizes the stored flags correctly, starts in the persona
root, loads `CLAUDE.md`, and leaves the equivalent Codex entrypoint untouched.
