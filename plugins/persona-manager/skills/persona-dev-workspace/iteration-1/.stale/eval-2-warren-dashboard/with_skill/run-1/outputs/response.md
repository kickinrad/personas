# Warren Spending Dashboard — Build Guidance

## What You're Solving

After every weekly review, Warren generates a structured spending breakdown inline in the chat. You have to scroll back through conversation history to find it. You've done this 4 sessions in a row. The fix is to have the weekly-review skill write a structured `WEEKLY_REVIEW.md` data file after every run, and add a "Weekly Review" tab to Warren's existing dashboard that renders it visually.

This is a **two-part change**: update the skill, update the dashboard. No new tooling required — Warren already has a running HTTP server via `open.sh`.

---

## What to Build

### 1. New data file: `WEEKLY_REVIEW.md`

Warren's weekly-review skill should write this file after every session. The dashboard fetches and renders it. The file lives at:

```
~/projects/personal/personas/plugins/warren/WEEKLY_REVIEW.md
```

Warren writes this directly using file tools — same as MEMORY.md. Structure:

```markdown
# Weekly Review — [Week of Mon DD YYYY]

_Generated: [ISO timestamp]_

## Cash Flow

| | Amount |
|---|---|
| Income | $X,XXX |
| Expenses | $X,XXX |
| **Net** | **$X,XXX** |

_vs prior week: ▲/▼ $XXX_

## Budget Health

| Category | Spent | Budget | Status |
|---|---|---|---|
| Dining | $XXX | $XXX | ⚠️ Over |
| Groceries | $XXX | $XXX | ✓ OK |
| Transport | $XXX | $XXX | 🔶 Close |
| ... | | | |

Monthly burn rate: $XXX/day — [on track / running hot]

## Account Balances

| Account | Balance |
|---|---|
| [Account name] | $X,XXX |
| [Account name] | $X,XXX |

Total liquid: $X,XXX

## Notable Transactions

- [Description — $XXX — [merchant/category]]
- ...

## Action Items

1. [Specific action with dollar amount]
2. [Specific action]
3. [Specific action]

## Verdict

[One sentence. Honest.]
```

The structure mirrors exactly what the weekly-review skill already produces in chat — just written to a file instead of (only) to the terminal.

---

### 2. Update the weekly-review skill

File: `/home/wilst/projects/personal/personas/plugins/warren/skills/finance/weekly-review/SKILL.md`

Add a **Step 5** after the existing Step 4 ("Store snapshot"):

```markdown
**5. Write to dashboard**
After storing to memory, write the full briefing to `WEEKLY_REVIEW.md` in this directory
using the structured format defined in the Dashboard section of CLAUDE.md.
Use `Write` (overwrite) — this file always holds the most recent review only.
The dashboard reads this file; it does not need history (MEMORY.md has that).
```

The full updated SKILL.md procedure section becomes:

```markdown
## Procedure

**1. Refresh data**
Call `refresh_accounts` to ensure current balances.

**2. Pull the numbers**
- `get_cashflow` — current week (Mon–Sun, or last 7 days)
- `get_budgets` — current month status
- `get_accounts` — current balances

**3. Build the briefing (always in this order)**

[existing format block — unchanged]

**4. Store snapshot**
Store to built-in memory — include: date, net cashflow, total liquid balance, budget flags, any notable patterns.

**5. Write to dashboard**
Write the full briefing to `WEEKLY_REVIEW.md` in this directory using the structured
markdown table format. Overwrite the file — it holds the most recent review only.
Prior reviews are preserved in MEMORY.md.
```

---

### 3. Add "Weekly Review" tab to `dashboard.html`

File: `/home/wilst/projects/personal/personas/plugins/warren/dashboard.html`

#### 3a. Add the tab button

In the `<nav class="tabs">` section, add after the existing Priorities tab button:

```html
<button class="tab" onclick="switchTab('weekly',this)"><span class="prefix">&gt;_</span> Weekly Review</button>
```

#### 3b. Add the tab panel

After the closing `</div>` of `<!-- PRIORITIES TAB -->`, add:

```html
<!-- WEEKLY REVIEW TAB -->
<div id="tab-weekly" class="tab-panel">
  <div id="weekly-review-content"></div>
</div>
```

#### 3c. Add rendering logic to `loadContent()`

The existing `loadContent()` function does a `Promise.all` fetching `profile.md`, `MEMORY.md`, and `CLAUDE.md`. Extend it to also fetch `WEEKLY_REVIEW.md`:

```javascript
const [profileMd, memoryMd, claudeMd, weeklyMd] = await Promise.all([
  fetch('profile.md'         + bust).then(r => { if (!r.ok) throw new Error('profile.md → HTTP ' + r.status); return r.text(); }),
  fetch('MEMORY.md'          + bust).then(r => { if (!r.ok) throw new Error('MEMORY.md → HTTP '  + r.status); return r.text(); }),
  fetch('CLAUDE.md'          + bust).then(r => { if (!r.ok) throw new Error('CLAUDE.md → HTTP '  + r.status); return r.text(); }),
  fetch('WEEKLY_REVIEW.md'   + bust).then(r => r.ok ? r.text() : null),
]);
```

Note that `WEEKLY_REVIEW.md` uses a soft fetch — it returns `null` if missing (first run before any review has happened) rather than throwing. Then after the existing `renderMd` calls:

```javascript
const weeklyEl = document.getElementById('weekly-review-content');
if (weeklyMd) {
  renderWeeklyReview(weeklyEl, weeklyMd);
} else {
  showError(weeklyEl, 'No weekly review on file yet — run "weekly review" with Warren to generate one.');
}
```

#### 3d. Add `renderWeeklyReview()` function

Add this function to the `<script>` block, before `loadContent()`:

```javascript
// ── WEEKLY REVIEW RENDERER ────────────────────────
// Renders WEEKLY_REVIEW.md with budget rows color-coded by status emoji.
function renderWeeklyReview(container, md) {
  container.replaceChildren();

  // Status badge mapping
  const statusMap = {
    '⚠️': { cls: 'red',   label: 'OVER'  },
    '🔶': { cls: 'amber', label: 'CLOSE' },
    '✓':  { cls: 'green', label: 'OK'    },
  };

  // Parse budget table rows and inject color classes, then render as markdown
  // We do this by post-processing the rendered HTML, not the markdown source.
  const wrapper = document.createElement('div');
  wrapper.className = 'md-content weekly-review-content';
  renderMd(wrapper, md);

  // Color-code budget table rows based on status cell content
  wrapper.querySelectorAll('table').forEach(table => {
    const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim().toLowerCase());
    const statusIdx = headers.indexOf('status');
    if (statusIdx === -1) return;

    table.querySelectorAll('tbody tr').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (!cells[statusIdx]) return;
      const statusText = cells[statusIdx].textContent.trim();
      for (const [emoji, cfg] of Object.entries(statusMap)) {
        if (statusText.includes(emoji)) {
          row.style.borderLeft = `3px solid var(--${cfg.cls === 'red' ? 'red' : cfg.cls === 'amber' ? 'amber' : 'green'})`;
          cells[statusIdx].style.color = `var(--${cfg.cls === 'red' ? 'red' : cfg.cls === 'amber' ? 'amber' : 'green'})`;
          cells[statusIdx].style.fontFamily = "'JetBrains Mono', monospace";
          cells[statusIdx].style.fontSize = '11px';
          break;
        }
      }
    });
  });

  // Highlight verdict line
  wrapper.querySelectorAll('h2').forEach(h2 => {
    if (h2.textContent.trim() === 'Verdict') {
      const next = h2.nextElementSibling;
      if (next && next.tagName === 'P') {
        next.style.fontFamily = "'Cormorant Garamond', serif";
        next.style.fontSize = '20px';
        next.style.fontStyle = 'italic';
        next.style.color = 'var(--text-bright)';
        next.style.borderLeft = '4px solid var(--blue)';
        next.style.paddingLeft = '16px';
        next.style.marginTop = '8px';
      }
    }
  });

  container.appendChild(wrapper);
}
```

#### 3e. Add loading state initialization

In `loadContent()`, after the existing `showLoading` calls, add:

```javascript
const weeklyEl = document.getElementById('weekly-review-content');
showLoading(weeklyEl, 'Loading weekly review...');
```

---

### 4. What TASKS.md should look like

Warren already has a dashboard and priorities tab. The `TASKS.md` format (per the persona-dev skill spec) is the right place for action items surfaced during the weekly review. After a weekly review, Warren should also write the 3 action items into `TASKS.md` under `## Active`. This means the Priorities tab (which already parses `MEMORY.md`'s checklist) should optionally also pull from `TASKS.md`, or Warren should copy action items there explicitly.

Recommended `TASKS.md` at `/home/wilst/projects/personal/personas/plugins/warren/TASKS.md`:

```markdown
# Tasks

## Active
- [ ] **[Action from weekly review]** — [context], due [date if applicable]

## Waiting On

## Someday

## Done
- [x] ~~Example completed action~~ (2026-03-01)
```

The weekly-review skill's Step 5 should be extended: after writing `WEEKLY_REVIEW.md`, also append the 3 action items from the review into `TASKS.md` under `## Active`. Warren uses `Read` then `Edit` to insert them just below the `## Active` heading, preserving existing items.

---

## Summary of Changes

| File | Change | How |
|------|--------|-----|
| `skills/finance/weekly-review/SKILL.md` | Add Step 5: write `WEEKLY_REVIEW.md` after every review | Edit the file |
| `skills/finance/weekly-review/SKILL.md` | Add Step 6: append action items to `TASKS.md` | Edit the file |
| `dashboard.html` | Add "Weekly Review" tab + panel | Edit the file |
| `dashboard.html` | Add `renderWeeklyReview()` JS function | Edit the file |
| `dashboard.html` | Extend `loadContent()` to fetch `WEEKLY_REVIEW.md` | Edit the file |
| `WEEKLY_REVIEW.md` | New file, written by Warren after each session | Warren creates on first review |
| `TASKS.md` | New file, action items written here | Warren creates on first review |

No changes to `CLAUDE.md`, `open.sh`, or `profile.md` are needed. Version bump: this is a **minor** change (new skill capability + dashboard tab), so bump `0.x.0` → `0.(x+1).0` in both `plugin.json` and `marketplace.json`.

---

## How It Flows After This

1. You run `warren "weekly review"` as usual
2. Warren pulls data, builds the briefing in chat (unchanged)
3. Warren writes `WEEKLY_REVIEW.md` (overwriting previous)
4. Warren appends the 3 action items to `TASKS.md`
5. Warren stores snapshot to memory (unchanged)
6. You open the dashboard: `bash /home/wilst/projects/personal/personas/plugins/warren/open.sh`
7. Click the "Weekly Review" tab — full breakdown, color-coded budget rows, verdict highlighted
8. Priorities tab already shows the new action items from `TASKS.md`

No more scrolling through chat. The numbers live in the dashboard permanently until the next review overwrites them.
