# Scenario 02: SessionStart Hook + Profile Interview

Verify that the SessionStart hook fires, reads the profile template, and initiates a structured interview.

## Grader Type

LLM-judge + Code-based

## Setup

- Test persona exists at `~/.personas/test-eval-persona/` with full scaffold
- `user/profile.md` contains unfilled template with placeholders (as left by persona-dev)
- No prior sessions (fresh persona)

## Prompt

```
Hello, this is my first session.
```

## Simulated User Responses

When `AskUserQuestion` is invoked, respond with:
- Name: "Test User"
- Role: "QA Engineer"
- For any other questions: provide reasonable default answers
- After 3 questions answered, say: "That's enough for now, let's move on"

## Assertions

### Code-based
- [ ] `user/profile.md` has been modified (differs from original template)
- [ ] `user/profile.md` contains "Test User" somewhere in its content
- [ ] `user/profile.md` contains at least one filled-in section (no longer all placeholders)

### LLM-judge
- [ ] The persona read `user/profile.md` early in the session (evidence in transcript)
- [ ] The persona used `AskUserQuestion` (not just conversation) to interview the user
- [ ] The persona asked questions section-by-section, not all at once
- [ ] The persona populated `user/profile.md` with the user's answers in place
- [ ] The persona checked MCP tool availability at some point during session start
