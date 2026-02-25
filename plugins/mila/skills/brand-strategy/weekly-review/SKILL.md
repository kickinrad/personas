---
name: weekly-review
description: Monday check-in across all three tracks. Review wins, momentum, set Top 3 priorities per track for the week.
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

Query OpenMemory for last week's intentions:
```
mcp__openmemory__openmemory_query("weekly priorities [current week]")
mcp__openmemory__openmemory_query("brand strategy decisions")
```

## Phase 1: Look Back (Last Week)

Ask Wils: "How did last week go? Walk me through each track — what moved, what stalled, what surprised you?"

Listen, ask follow-up questions, then synthesize:

### 🏢 Agency (b.f.f.)
- Any new leads or client conversations?
- Deliverables completed or delayed?
- LinkedIn activity — anything posted?
- Revenue or pipeline movement?

### 🎵 Music (Wavytone)
- Any production sessions?
- Platform activity (Bandcamp streams, IG engagement)?
- TikTok progress (if applicable)?
- Collaboration conversations?

### 🧑‍💻 Personal Brand
- Any writing done (even drafts)?
- Social posts or engagement?
- Developer work worth sharing someday?

## Phase 2: Momentum Check

Look at what's actually working across all tracks:
- What had energy last week?
- What felt like pushing a boulder uphill?
- Is there anything to stop doing?

## Phase 3: Set Top 3 Per Track

Facilitate setting exactly THREE priorities per track for the coming week. Not five. Not ten. Three.

```
🏢 b.f.f. Agency — Top 3:
1.
2.
3.

🎵 Wavytone Orchestra — Top 3:
1.
2.
3.

🧑‍💻 Personal Brand — Top 3:
1.
2.
3.
```

Push back if something is vague ("post more" → "post 2 Wavytone Reels with specific content angle").

## Phase 4: Check Calendar

```
mcp__google_workspace__get_events (this week)
```

Are there any deadlines, meetings, or milestones this week that affect the priorities? Adjust if needed.

## Phase 5: Update + Store

1. **Suggest profile.md update** — if Current Priorities are stale, propose new text for Wils to confirm
2. **Store to OpenMemory:**
```
mcp__openmemory__openmemory_store("Week of [date] priorities: Agency: [1,2,3]. Music: [1,2,3]. Brand: [1,2,3].")
mcp__openmemory__openmemory_store("[Any notable insight or decision from this review]")
```
3. **Add to Google Tasks** — any action items with due dates:
```
mcp__google_workspace__create_task(title, due_date)
```

## Output Format

End the session with:

```
✨ Week of [date] — Top 3 Per Track

🏢 b.f.f. Agency
1. [Priority]
2. [Priority]
3. [Priority]

🎵 Wavytone Orchestra
1. [Priority]
2. [Priority]
3. [Priority]

🧑‍💻 Personal Brand
1. [Priority]
2. [Priority]
3. [Priority]

📅 Key dates this week: [from calendar]

Let's make it happen.
```

## Tips

- If Wils hasn't done much on a track, that's useful data — is it intentional deprioritization or drift?
- If all three tracks feel chaotic, help identify the ONE thing that would create the most relief
- Monday energy is often low — be warm, not intense
