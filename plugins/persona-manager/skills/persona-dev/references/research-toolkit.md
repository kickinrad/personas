# Research toolkit — discovery categories + where each capability lives

Canonical reference shared by `persona-dev` Phase 2 (Research) and `self-improve` Level 4 (Tool & Integration Discovery). Both point here — don't restate the list in either skill.

Before building anything custom, investigate what already exists. Think broadly — personas have a rich toolkit beyond MCP servers:

1. **MCP servers** — search for community or official MCP servers relevant to the domain (recipe APIs, financial data, calendar, etc.). Existing servers beat custom solutions
2. **CLI tools** — identify useful CLI tools already installed or easily available (`gh`, `jq`, domain-specific CLIs). Many problems have mature solutions
3. **APIs** — identify REST/GraphQL APIs the persona could call directly via `curl` or scripts in `tools/`. Not everything needs an MCP server — sometimes a simple API call in a bash script is the right tool
4. **Skills** — plan domain skills that wrap CLI tools, API workflows, or multi-step processes into reusable SKILL.md files. Skills are the persona's playbooks — they turn "I know how to use this tool" into "here's the complete workflow"
5. **Agents** — consider whether the persona needs specialized subagents (in `.claude/agents/`) for complex autonomous tasks like research, analysis, or multi-step operations
6. **Hooks** — beyond the standard SessionStart/Stop/PreCompact, consider domain-specific hooks (e.g., a PreToolUse hook that validates data before writes, a Stop hook that generates a summary)
7. **Scripts** — bash or python scripts in `tools/` for data pipelines, API wrappers, formatters, or anything the persona does repeatedly
8. **Reference material** — domain-specific best practices, checklists, templates, or frameworks that should live in `docs/`
9. **Scheduled tasks** — identify workflows that benefit from timed reminders or delayed checks. Any persona can schedule tasks using natural language ("remind me at 3pm to...", "in 45 minutes, check whether..."). These are session-scoped — they vanish on exit; suggest Desktop scheduled tasks or GitHub Actions for durable scheduling
10. **Expansion packs** — check if a personas-framework expansion pack covers it:
    - `persona-dashboard:install` — visual dashboard with task tracking (good for personas with ongoing work, reviews, or regular check-ins)

## Where each capability lives

| Discovery | Where it lives | When to choose it |
|-----------|---------------|-------------------|
| MCP server (existing) | `.mcp.json` + sandbox allowlist | Persistent connection to an external service |
| MCP server (custom) | Propose — user configures | Only if nothing exists |
| CLI tool | Document in CLAUDE.md or wrap in a skill | Mature tool already exists for the job |
| API (direct) | `tools/` script or skill instructions | Simple HTTP calls, no persistent connection needed |
| Skill | `.claude/skills/{domain}/{name}/SKILL.md` | Multi-step workflow the persona will repeat |
| Agent | `.claude/agents/{name}.md` | Autonomous subtask needing its own context |
| Hook | `hooks.json` | Behavioral automation tied to session events |
| Script | `tools/{name}` | Data processing, automation, one-off utilities |
| Scheduled task | Scheduling patterns in CLAUDE.md | Timed reminders, delayed checks |
| Reference doc | `docs/` | Domain knowledge the persona should internalize |
| Expansion pack | Invoke the pack's install skill (e.g., `persona-dashboard:install`) | Dashboard, future packs |
