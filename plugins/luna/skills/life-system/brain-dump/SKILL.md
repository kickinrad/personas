---
name: brain-dump
description: Capture scattered thoughts and process Keep inbox. Auto-loads for brain dump/overwhelmed keywords.
triggers:
  - brain dump
  - overwhelmed
  - triage
  - inbox
  - capture
  - scattered
  - too much
  - can't think
---

# Brain Dump & Triage

CORE System: **C**apture -> **O**rganize -> **R**eview -> **E**xecute

This skill handles the first two phases. Get everything OUT of Wils' head, then organize it.

## Step 1: Capture Mode

If Wils is dumping thoughts verbally or in text:

1. **Listen without filtering** - Don't organize yet, just capture
2. **Create Keep notes** for each distinct item:
   ```
   mcp__wlater__create_note(title="[item]", text="")
   ```
3. **Call sync_changes** after creating notes to push to Keep
4. **Don't label yet** - Labeling is the next step
5. Acknowledge each capture: "Got it" or "Captured"

After dump is complete, move to triage.

## Step 2: Triage Inbox

The inbox has two sources:

### 2a: Brain Dump Note

Read the **🧠 Brain Dump** note (pinned, orange). This is where Wils drops random thoughts from his phone throughout the day.

```
mcp__wlater__search_notes(query="Brain Dump", pinned=True)
mcp__wlater__get_note(note_id="[brain dump note id]")
```

If it has content, treat each line/paragraph as a separate item to triage. After processing all items, **clear the note text** but keep the note itself:
```
mcp__wlater__update_note_text(note_id="[brain dump note id]", text="")
mcp__wlater__sync_changes()
```

### 2b: Unlabeled Notes

Read all unlabeled notes (individual captures):
```
mcp__wlater__list_all_notes
# Filter for notes without labels - these are the inbox
```

### Triage Each Item

For each item (from Brain Dump lines or unlabeled notes), ask ONE question:

**"What do you want to do with [item]?"**

### Processing Options

| Decision | Action |
|----------|--------|
| **NOW** | Create Google Task with today's date via `mcp__google_workspace__create_task`, then archive/delete the note |
| **SOON** | Add to a To Do list in Keep OR add the `SOON` label, then archive |
| **LATER** | Apply appropriate label (see below), then archive |
| **DELETE** | Trash it via `mcp__wlater__trash_note` |

### Labels for LATER Items

Apply the most relevant label:
- `Ideas` - His thoughts, concepts, someday/maybes
- `Reference` - External info to keep (articles, links, facts)
- `Projects` - Multi-step initiatives
- `Business` - Work and business related
- `Financial` - Money, investments, bills
- `Home` - House, maintenance, local
- `Family` - Family-related items
- `Gaming` - Games, gaming projects
- `Music` - Music production, listening
- `Recipes` - Food and cooking
- `Shopping` - Things to buy
- `Inspiration` - Quotes, motivation, ideas from others

After labeling, archive the note so it's out of the inbox.

## Step 3: Pick ONE

Once inbox is clear (or mostly clear):

1. **Celebrate** - "Inbox processed! Nice work."
2. **Suggest ONE thing** to start with based on energy and priorities
3. **If stuck**, offer micro-step breakdown (link to stuck-mode skill)
4. Ask: "What's the smallest next action you could take right now?"

## Key Principles

- Don't let perfect organization block capture
- Unlabeled = inbox = needs processing
- Processing means deciding, not doing
- One decision at a time keeps it manageable
- Archive aggressively - you can always search

## Note Groups

Some notes work together as a system. When triaging, consider routing items to the right note in a group rather than creating standalone notes:

| Group | Notes | How they relate |
|-------|-------|-----------------|
| **Home** | 🔨 Home Repair To-Do (active repairs), Future Home Projects (someday ideas), 🔨 Hardware Store List (supplies to buy) |
| **Business** | Individual to-do lists per project (BFF, VKB, RVA Boombox, Moms in Motion, etc.) |
| **Shopping** | Grocery List, Shopping List, Clothing Shopping List, 🔨 Hardware Store List |

When an item clearly belongs in an existing list, add it there instead of creating a new note. For example, "buy wood filler" goes on the Hardware Store List, not a new note.

## Execution Flow

```
1. "What's on your mind?" (capture mode)
2. Create notes for each item
3. Sync changes to Keep
4. Read Brain Dump note + unlabeled notes
5. For each: NOW / SOON / LATER / DELETE
6. Route to existing lists, label, or archive
7. Clear Brain Dump note text
8. Pick ONE thing to start
```
