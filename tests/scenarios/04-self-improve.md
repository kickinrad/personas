# Scenario 04: Self-Improve Skill Audit

Verify that the self-improve skill activates and performs a meaningful audit.

## Grader Type

LLM-judge

## Setup

- Test persona exists with filled-in profile and some memory entries
- `skills/self-improve/SKILL.md` exists
- At least one domain skill exists

## Prompt

```
Run a self-improvement audit. Check my memory, skills, and workspace for anything that could be improved.
```

## Assertions

### LLM-judge
- [ ] The persona activated the self-improve skill (evidence of reading SKILL.md or following its workflow)
- [ ] The persona reviewed `user/memory/MEMORY.md` and memory files
- [ ] The persona checked existing skills for completeness or improvement opportunities
- [ ] The persona inspected the workspace for hygiene issues (stale files, missing dirs, etc.)
- [ ] The persona proposed at least one concrete improvement (rule promotion, new skill, cleanup, etc.)
- [ ] The persona followed the propose/approve pattern — did NOT make changes without asking first
- [ ] The proposed improvements are relevant and actionable (not generic filler)
