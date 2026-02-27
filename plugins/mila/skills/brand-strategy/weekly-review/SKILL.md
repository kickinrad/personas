---
name: weekly-review
description: Monday check-in across all focus areas. Review wins, momentum, set Top 3 priorities per area for the week.
triggers:
  - weekly review
  - this week
  - week ahead
  - week review
  - priorities
  - what should i focus on
  - monday
  - start the week
  - week planning
---

# Weekly Review

A Monday ritual that sets the tone for the whole week. Look back to look forward.

## Before Starting

Read `~/.personas/mila/profile.md` for focus areas and current priorities.

Query memory for last week's intentions:
```
[built-in memory: search "weekly priorities [current week]", "brand strategy decisions"]
```

## Phase 1: Look Back (Last Week)

Ask: "How did last week go? Walk me through each focus area — what moved, what stalled, what surprised you?"

Listen, ask follow-up questions, then synthesize. Use profile.md to know the focus areas — structure the review around them.

### For a business/agency:
- Any new leads or client conversations?
- Deliverables completed or delayed?
- Marketing activity — anything posted?
- Revenue or pipeline movement?

### For a creative project:
- Any production sessions?
- Platform activity (streams, engagement)?
- New platform progress (TikTok, etc.)?
- Collaboration conversations?

### For personal brand:
- Any writing done (even drafts)?
- Social posts or engagement?
- Technical or developer work worth sharing someday?

## Phase 2: Momentum Check

Look at what's actually working across all focus areas:
- What had energy last week?
- What felt like pushing a boulder uphill?
- Is there anything to stop doing?

## Phase 3: Set Top 3 Per Focus Area

Facilitate setting exactly THREE priorities per focus area for the coming week. Not five. Not ten. Three.

Use profile.md to fill in the actual focus area names:

```
[🏢 Business/Agency] — Top 3:
1.
2.
3.

[🎵 Creative Project] — Top 3:
1.
2.
3.

[🧑‍💻 Personal Brand] — Top 3:
1.
2.
3.
```

Push back if something is vague ("post more" → "post 2 [platform] [format] with specific content angle").

## Phase 4: Check Calendar

```
mcp__google_workspace__get_events (this week)
```

Are there any deadlines, meetings, or milestones this week that affect the priorities? Adjust if needed.

## Phase 5: Update + Store

1. **Suggest profile.md update** — if Current Priorities are stale, propose new text to confirm
2. **Store to memory:**
```
[built-in memory: save "Week of [date] priorities: [Area 1]: [1,2,3]. [Area 2]: [1,2,3]. [Area 3]: [1,2,3]."]
[built-in memory: save "[Any notable insight or decision from this review]"]
```
3. **Add to Google Tasks** — any action items with due dates:
```
mcp__google_workspace__create_task(title, due_date)
```

## Output Format

End the session with:

```
✨ Week of [date] — Top 3 Per Focus Area

[Area 1 emoji + name]
1. [Priority]
2. [Priority]
3. [Priority]

[Area 2 emoji + name]
1. [Priority]
2. [Priority]
3. [Priority]

[Area 3 emoji + name]
1. [Priority]
2. [Priority]
3. [Priority]

📅 Key dates this week: [from calendar]

Let's make it happen.
```

## Tips

- If not much happened on a focus area, that's useful data — is it intentional deprioritization or drift?
- If all focus areas feel chaotic, help identify the ONE thing that would create the most relief
- Monday energy is often low — be warm, not intense
