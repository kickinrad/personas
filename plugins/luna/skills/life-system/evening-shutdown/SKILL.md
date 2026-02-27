---
name: evening-shutdown
description: Guided evening shutdown - wins, inbox, Big 3, disconnect. Auto-loads for shutdown/evening keywords.
triggers:
  - shutdown
  - evening
  - wrap up
  - end of day
  - big 3
  - close out
  - done for today
  - signing off
---

# Evening Shutdown

Guide the user through shutting down so they can truly disconnect. Be warm and supportive. The goal is mental closure - everything captured, tomorrow planned, mind at rest.

## Phase 1: Review Today

**Ask:** "What got done today? Any wins to celebrate?"

- **Celebrate accomplishments** genuinely - even small ones count
- **For unfinished items:** "What got in the way?" (no judgment, just understanding)
- **Extract lessons:** Note any insights for `.claude/journal.md` if significant

Don't rush this - acknowledging wins matters.

## Phase 2: Process Inbox

Use the brain-dump triage workflow. The inbox has two sources:

1. **🧠 Brain Dump note** (pinned, orange) - parse each line as a separate item
2. **Unlabeled Keep notes** - individual captures via `mcp__wlater__list_all_notes`

For each item, ask: "NOW / SOON / LATER / DELETE?"

3. Process decisions:
   - **NOW** -> Create Google Task for tomorrow
   - **SOON** -> Add to a To Do list or SOON label
   - **LATER** -> Apply label and archive (or route to an existing list - see Note Groups in brain-dump skill)
   - **DELETE** -> Trash it
4. Clear the Brain Dump note text after processing
5. Sync changes when done

If both sources are empty: "Inbox zero! Nice work today."

## Phase 3: Plan Tomorrow

### Check To Do Lists

Review To Do lists in Keep for items worth tackling tomorrow:
```
mcp__wlater__list_all_notes
# Look for list-type notes with checkboxes
```

### Set the Big 3

**Ask:** "What are your Big 3 for tomorrow?"

These are the 3 things that will make tomorrow feel successful. Not 5. Not 10. Three.

For each Big 3 item:
1. Create as Google Task with tomorrow's date
2. Add a specific time if it needs time-blocking:
   ```
   mcp__google_workspace__create_task(
     title="[task]",
     due_date="[tomorrow]",
     due_time="[specific time if needed]"
   )
   ```

### Review Tomorrow's Calendar

Check what's already scheduled:
```
mcp__google_workspace__get_events(date=[tomorrow])
```

- Note any prep needed for meetings
- Identify best time blocks for Big 3
- Flag conflicts or tight schedules

## Phase 4: Open Loops

**Ask:** "Anything still bouncing around in your head?"

This is the final brain dump - capture EVERYTHING lingering:

- Ideas that popped up today
- Things you're worried about
- Decisions that can wait but you're thinking about
- Random thoughts

Create Keep notes for each. Don't process them now - just capture so the mind can let go.

## Phase 5: Shutdown Confirmation

Wrap up with:

1. **Confirm first task:** "Your first task tomorrow is [X]. Ready to go?"
2. **Remind to close:** "Time to close work apps and tabs"
3. **Warm send-off:**

> "You've done good work today. Your Big 3 for tomorrow are set. Enjoy your evening guilt-free. See you tomorrow!"

## Execution Checklist

```
[ ] Celebrated today's wins
[ ] Processed inbox (unlabeled notes)
[ ] Set Big 3 for tomorrow as Tasks
[ ] Reviewed tomorrow's calendar
[ ] Captured open loops
[ ] Confirmed first task is clear
[ ] Permission to disconnect granted
```

## Tips

- If the user seems tired, keep it brief
- If inbox is huge, process top 5 and defer rest
- Big 3 should be achievable, not aspirational
- End on a positive note always
