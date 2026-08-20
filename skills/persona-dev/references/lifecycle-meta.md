# Persona folder ownership

| Concern | Owning surface |
|---|---|
| Identity, voice, role, boundaries | `AGENTS.md` |
| Claude Code loading and mechanics | `CLAUDE.md`, `.claude/` |
| Codex loading and mechanics | `AGENTS.md`, `.codex/` |
| Reusable role procedure | `skills/<workflow>/SKILL.md` |
| Local profile and explicit memory | ignored `user/` |
| Durable external knowledge | its canonical external system |

Adapters load the portable source; they do not restate it. Native auto-memory
is runtime-owned and is not a replacement for explicit portable persona memory.

Before finishing a persona change, inspect the tree and diff, confirm private
state remains ignored, and verify that both runtime entry files point at the
same portable authority.
