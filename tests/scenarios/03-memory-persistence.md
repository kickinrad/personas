# Scenario 03: Memory Persistence

Verify that the persona writes meaningful learnings to memory during and at the end of a session.

## Grader Type

Code-based

## Setup

- Test persona exists with filled-in `user/profile.md`
- `user/memory/MEMORY.md` exists but is empty or minimal (fresh state)
- No existing memory files beyond MEMORY.md

## Prompt

```
I want you to remember these preferences for future sessions. Save them to memory files now:
1. I always prefer TypeScript over JavaScript for new projects
2. My team uses pnpm, not npm or yarn
3. We follow trunk-based development with short-lived feature branches

Write the memory files to user/memory/ with proper frontmatter (name, description, type fields) and update user/memory/MEMORY.md with links to the new files. Do this now, don't just acknowledge — actually create the files.
```

## Assertions

### Code-based
- [ ] At least one new `.md` file exists in `user/memory/` (besides MEMORY.md)
- [ ] `user/memory/MEMORY.md` has been updated with at least one entry
- [ ] A memory file mentions "TypeScript" or "pnpm" or "trunk-based"
- [ ] Memory files have frontmatter with `name`, `description`, and `type` fields
- [ ] `user/memory/MEMORY.md` contains a link (relative path) to the new memory file(s)

### Negative checks
- [ ] No memory file contains sensitive data patterns (API keys, tokens, passwords)
- [ ] Memory files are concise (each under 50 lines)
