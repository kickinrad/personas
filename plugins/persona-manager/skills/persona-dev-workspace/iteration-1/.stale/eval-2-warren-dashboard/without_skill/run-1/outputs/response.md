# Warren Dashboard - Design & Implementation Guide

## The Problem

Warren produces a spending breakdown during weekly review sessions, but the data lives only in chat history. Finding it means scrolling back through conversation logs. Four sessions in, this is friction that compounds: you either skip the review because it's annoying to reference, or you waste time hunting for numbers you already asked for.

The fix is a persistent dashboard file that Warren writes to automatically as part of every weekly review.

---

## What to Build

A **Markdown dashboard file** at a fixed path that Warren updates on every weekly review. No web server, no database, no separate app. Just a structured `.md` file that:

- Renders beautifully in VS Code (or any Markdown viewer)
- Is human-readable as plain text
- Can be version-controlled so you have historical snapshots
- Warren writes to it directly using file tools — no extra infrastructure

The dashboard lives at:
```
~/projects/personal/finances/warren-dashboard.md
```

(Or wherever makes sense in your project structure. The path should be hardcoded in Warren's persona config so he always knows where to find it.)

---

## Dashboard Structure

The file has two sections: a **Current Snapshot** that Warren overwrites on every review, and a **History Log** that Warren appends to, building a running record.

```markdown
# Warren Dashboard
> Last updated: 2026-03-03 | Week of Feb 24 – Mar 2

---

## This Week at a Glance

| Category        | Spent   | Budget  | Status  |
|-----------------|---------|---------|---------|
| Groceries       | $312.40 | $350    | OK      |
| Dining Out      | $187.20 | $150    | OVER    |
| Transport       | $94.60  | $120    | OK      |
| Entertainment   | $45.00  | $100    | OK      |
| Subscriptions   | $67.83  | $70     | OK      |
| **TOTAL**       | **$707.03** | **$790** | **OK** |

## Highlights

- Dining out over budget by $37.20 (3rd week in a row)
- Groceries trending down — $40 under budget
- No irregular / surprise expenses this week

## Net Position

- Income this week: $2,400.00
- Total spend: $707.03
- Net: +$1,692.97

---

## History

| Week              | Total Spend | vs Budget | Net      |
|-------------------|-------------|-----------|----------|
| Feb 24 – Mar 2    | $707.03     | -$82.97   | +$1,692.97 |
| Feb 17 – Feb 23   | $891.42     | +$101.42  | +$1,508.58 |
| Feb 10 – Feb 16   | $743.18     | -$46.82   | +$1,656.82 |
| Feb 3 – Feb 9     | $812.55     | +$22.55   | +$1,587.45 |
```

---

## Commands to Add to Warren

Add these slash commands (or natural-language triggers) to Warren's persona definition:

### `/review` — Weekly Review (modified)

The existing weekly review flow should be updated to **always end with a dashboard write**. After Warren generates the breakdown in chat, he should:

1. Parse/calculate the final numbers
2. Overwrite the "This Week at a Glance" and "Highlights" sections
3. Append a new row to the History table
4. Report confirmation: "Dashboard updated at `~/projects/personal/finances/warren-dashboard.md`"

### `/dashboard` — Quick View

Warren reads and displays the current dashboard inline in chat. Useful when you want a refresher mid-week without triggering a full review.

```
"Hey Warren, show me the dashboard"
→ Warren reads warren-dashboard.md and displays it
```

### `/dashboard-history` — Trend View

Warren reads the history table and adds commentary: which categories are trending, whether you're improving over time, any patterns worth noting.

### `/dashboard-reset` — Archive + Reset

When you want to start a new period (new month, new quarter), Warren:
1. Copies the current dashboard to `warren-dashboard-archive-YYYY-MM.md`
2. Clears the History table (keeping headers)
3. Resets the snapshot section

---

## Data Flow: How Warren Populates the Dashboard

### During a Weekly Review Session

The flow should be:

```
1. You trigger review (e.g. "Warren, let's do the weekly review")
2. Warren gathers data (asks questions, reads transaction exports, etc.)
3. Warren produces breakdown IN CHAT (same as today)
4. Warren calls Write tool → updates warren-dashboard.md
5. Warren confirms: "Dashboard updated. [path]"
```

The key change is step 4 — Warren uses the `Write` (or `Edit`) file tool to persist the numbers. This requires Warren's persona to have file write permissions in its MCP/tool config.

### Dashboard Write Logic

Warren should:

- **Overwrite** the top "Current Snapshot" block (between two `---` markers)
- **Append** one row to the History table at the bottom
- **Never** rewrite the History section from scratch (preserve the record)

A simple approach: Warren uses two sentinel comments in the file to know where to write:

```markdown
<!-- SNAPSHOT_START -->
(Warren overwrites everything here)
<!-- SNAPSHOT_END -->

## History
(Warren appends rows here)
```

### If Warren Can't Write (Tool Unavailable)

Warren should degrade gracefully: produce the formatted dashboard block in chat with a message like "I couldn't update the file automatically — here's the block to paste in manually." This avoids silent failures.

---

## Warren Persona Config Changes

In Warren's persona definition file, add or update:

### System Prompt Addition

```
After every weekly review, you MUST update the financial dashboard at:
~/projects/personal/finances/warren-dashboard.md

Use the Write/Edit tool to:
1. Replace the content between <!-- SNAPSHOT_START --> and <!-- SNAPSHOT_END --> with this week's summary table and highlights
2. Append a new row to the History table at the bottom of the file

Format numbers as USD with 2 decimal places. Always include the week date range.
After writing, confirm with the exact file path so the user can open it.

If the dashboard file does not exist, create it using the template structure.
```

### Tool Permissions

Ensure Warren's persona config grants access to:
- `Read` (to check existing dashboard before writing)
- `Write` or `Edit` (to update the dashboard)

In Claude Code persona configs this is typically set in the `tools` or `permissions` section of the persona YAML/JSON. Exact key depends on your persona-manager schema — check how other personas with file access are configured.

---

## Directory Setup

Create the finances directory and seed the dashboard file:

```bash
mkdir -p ~/projects/personal/finances

# Create the initial dashboard template
cat > ~/projects/personal/finances/warren-dashboard.md << 'EOF'
# Warren Dashboard
> Last updated: (not yet run)

---

<!-- SNAPSHOT_START -->
## This Week at a Glance

*No review run yet. Start with: "Warren, let's do the weekly review"*
<!-- SNAPSHOT_END -->

---

## History

| Week | Total Spend | vs Budget | Net |
|------|-------------|-----------|-----|
EOF

echo "Dashboard template created."
```

---

## Viewing the Dashboard

Since this is a Markdown file, you have several zero-config options:

**In VS Code:** Open `warren-dashboard.md` → `Ctrl+Shift+V` for the rendered preview. Keep this in a split pane.

**In terminal:**
```bash
# If you have glow installed (recommended):
glow ~/projects/personal/finances/warren-dashboard.md

# Or bat for syntax highlighting:
bat ~/projects/personal/finances/warren-dashboard.md
```

**Add a shell alias** to `~/.config/zsh/.zshrc`:
```bash
alias warren-dash='bat ~/projects/personal/finances/warren-dashboard.md'
alias wd='warren-dash'  # short version
```

---

## Why Not a Web App or Database?

You could build a React dashboard, a SQLite database, a Notion integration. Don't. The Markdown file approach wins here because:

- **Zero infrastructure** — nothing to break, nothing to host
- **Warren can write it natively** — file tools are first-class in Claude Code
- **It's already in your workflow** — you're already in the terminal / VS Code
- **Version control is free** — `git add warren-dashboard.md` and you have a full history
- **Portable** — if you switch from Warren to a different system, the data is still there

The complexity ceiling for this use case is a well-structured Markdown file. Stay below it.

---

## Implementation Order

1. Create the directory and seed the template file (5 minutes)
2. Add the system prompt addition to Warren's persona config (10 minutes)
3. Verify tool permissions in Warren's config (5 minutes)
4. Run one test review session — confirm Warren writes to the file
5. Add the `warren-dash` alias to `.zshrc`
6. Optionally add a VS Code workspace that opens the dashboard in a split

That's it. Next weekly review, Warren writes the numbers, and you never scroll through chat history again.
