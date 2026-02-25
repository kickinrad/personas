---
name: morning-briefing
description: Daily briefing with weather, markets, calendar, tasks. Auto-loads for morning/briefing keywords.
triggers:
  - morning
  - briefing
  - good morning
  - what's today
  - start the day
---

# Morning Briefing

Present the day so Wils wakes up ready to execute, not make decisions. Be friendly, upbeat, and use emojis for this skill.

## Data to Gather

### 1. Weather (WebSearch: "Richmond VA weather today")
- Current conditions, high/low temps
- What to wear recommendation based on conditions

### 2. Markets (WebSearch: "stock market futures S&P Nasdaq premarket movers")
- S&P 500, Nasdaq, Dow futures direction
- Top premarket movers (gainers/losers)
- Major economic events or earnings today
- 2-3 specific plays to watch

### 3. Calendar (mcp__google_workspace__get_events for today + tomorrow)
- Today's events with any prep notes needed
- Tomorrow's key commitments to be aware of
- This week's upcoming deadlines

### 4. Tasks (mcp__google_workspace__list_tasks)
- Tasks due today - highlight the Big 3 if set
- Flag any overdue items that need attention

### 5. Keep Inbox (mcp__wlater__list_all_notes, filter unlabeled)
- Check for any urgent unlabeled notes needing immediate attention
- Note inbox count for awareness

## Output Format

Present as a sectioned briefing with these headers:

```
☀️ Weather & What to Wear
[Current conditions, high/low, clothing recommendation]

📈 Market Snapshot
[Futures, movers, plays to watch]

📅 Today's Schedule
[Events with times and prep notes]

✅ Tasks & Big 3
[Due today, Big 3 highlighted, overdue flagged]

👀 Heads Up
[Tomorrow's commitments, this week's deadlines]

💬 Daily Spark
[Inspiring quote or tip for the day]
```

## Execution Steps

1. Run WebSearch for Richmond VA weather
2. Run WebSearch for market futures and premarket movers
3. Call mcp__google_workspace__get_events for today and tomorrow
4. Call mcp__google_workspace__list_tasks for current tasks
5. Call mcp__wlater__list_all_notes and filter for unlabeled (inbox)
6. Compile into the output format above
7. End with an encouraging send-off for the day

## Tips

- Keep market info actionable, not overwhelming
- For weather, be specific about layers/jacket/umbrella
- If calendar is empty, celebrate the open space
- If inbox is zero, celebrate inbox zero
- Match energy to time of day - upbeat for morning
