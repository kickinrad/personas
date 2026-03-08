# Warren Tax Context — Persona Dev Response

Hey Wils! Good call — if Warren keeps asking the same question every session, that's a clear signal the answer belongs in `profile.md`, not in your head.

Per the persona-dev skill's canonical definitions:

> **profile.md** — WHO you are, WHAT you have, HOW you like to work. Stable facts that don't change session to session.

Your filing status, W-2 vs. freelance split, and joint filing status are stable facts. They belong in `profile.md`.

---

## What to Update

**File:** `~/.personas/warren/profile.md`

Your profile already has a solid `## 2025 Tax Summary` section, but it's focused on dollar amounts from a specific year. What's missing is a **Tax Context** section that captures the structural facts Warren needs before running any review — the things that frame how he should interpret your numbers regardless of which tax year it is.

---

## Proposed Addition

Add this section immediately after the `## Income Sources` section (before `## 2025 Tax Summary`), around line 109:

```markdown
---

## Tax Filing Context

| Key | Detail |
|-----|--------|
| **Filing status** | Married filing jointly (MFJ) — Wils + Sako |
| **Wils income type** | Mixed: self-employed (b.f.f. Schedule C) + investment distributions (1099-R, inherited IRA) |
| **Sako income type** | W-2 (Upspring) |
| **Quarterly estimated taxes** | Required for Wils — self-employment income is not withheld |
| **SE tax** | Applies to b.f.f. net profit (Schedule C) |
| **Key deductions** | SEP-IRA contributions, home office (simplified method), ACA premiums |
| **Inherited IRA RMDs** | Required annually through 2035 — plan distributions to minimize tax impact |
| **Relevant forms** | Schedule C (b.f.f.), 1099-R (inherited IRA), Form 8962 (ACA reconciliation) |

**Standing rule for Warren:** Do NOT ask about filing status or income type at the start of a weekly review. This context is permanent unless `profile.md` is updated.
```

---

## Why profile.md and Not CLAUDE.md

The persona-dev skill is clear on the distinction:

| Layer | What goes here |
|-------|---------------|
| `profile.md` | WHO you are, WHAT you have — stable facts |
| `CLAUDE.md` rules | HOW the persona behaves — permanent behavioral rules |

The tax situation is a *fact about you*, not a *rule about Warren's behavior*. It belongs in `profile.md`. If Warren's tendency to ask about it is a behavioral pattern worth stamping out, you could add a note to `CLAUDE.md` under **Important Rules** — but the right fix is making the data available so the question never needs to be asked in the first place.

---

## Optional: CLAUDE.md Rule Addition

If you want to make it explicit that Warren should never ask about tax context, you can append this to Warren's **Important Rules** section in `CLAUDE.md`:

```markdown
8. **Tax context is in profile.md** — never ask about filing status, income type, or W-2/freelance split at session start; read it from profile.md
```

---

## Summary

| Change | File | Type |
|--------|------|------|
| Add `## Tax Filing Context` section | `~/.personas/warren/profile.md` | User approves + writes |
| (Optional) Add rule #8 | `~/projects/personal/personas/plugins/warren/CLAUDE.md` | Claude proposes, user approves |

The `profile.md` change is the core fix. Warren reads it every session before doing anything — once that section exists, he has everything he needs without asking.

Want me to write these changes directly to the files?
