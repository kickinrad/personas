# Persona Dashboard

Optional read-only HTML viewer for a persona's profile, memory index, and
operating instructions.

The install skill copies one HTML asset and creates a local browser launcher.
The page reads:

- `user/profile.md`
- `user/memory/MEMORY.md`
- `CLAUDE.md`

It creates no action, calendar, project, or knowledge record. Google Tasks owns
actions, Google Calendar owns time, and Obsidian owns projects and durable
knowledge.

From a persona session:

```text
install a persona dashboard
```

Runtime support and gaps are declared in `interop/capabilities.json`.
