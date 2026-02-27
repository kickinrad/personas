---
name: quarterly-planning
description: Quarterly strategy review and goal-setting across all focus areas (business, creative projects, personal brand).
triggers:
  - quarter
  - quarterly
  - goals
  - big picture
  - okrs
  - planning
  - strategy session
  - next quarter
  - q1
  - q2
  - q3
  - q4
  - annual
  - year planning
  - long term
---

# Quarterly Planning

Zoom out. This is the session where we think in months, not weeks.

## Before Starting

Pull full context:
```
[built-in memory: search "quarterly goals", "brand strategy", "annual vision"]
mcp__google_workspace__get_events (next 30-90 days)
```

Read `~/.personas/mila/profile.md` for current focus areas and priorities.

## Phase 1: Reflect (Last Quarter)

Before setting goals, look at what happened.

For each focus area (from profile.md), ask:
- What were the goals? (Pull from memory or profile.md)
- What actually happened?
- What moved the needle?
- What wasted time?
- What surprised you?

### Questions per focus area type:

**For a business/agency:**
- Revenue vs. target (if tracked)
- New clients acquired
- Client retention
- Marketing/LinkedIn progress
- What changed in the service offering?

**For a creative project:**
- Releases completed
- Streaming/platform progress
- New platform launches (TikTok, etc.)
- Collaboration wins
- Press or recognition

**For personal brand:**
- Writing published
- Social growth (follower counts, engagement)
- Any speaking, features, or visibility wins?
- Developer/technical work worth sharing?

## Phase 2: Annual Vision Check

Step back even further:

"Where do you want to be in 12 months?"

For each focus area, paint the picture:
- **Business:** What does a healthy, thriving version look like? (Revenue target, client types, lifestyle)
- **Creative project:** Where is it? (Streaming numbers, platform presence, live shows, next release?)
- **Personal brand:** How are you known? (What are people saying? Where are you writing?)

This isn't about perfect goals — it's about direction. The details fill in later.

## Phase 3: Set Quarterly Goals (OKRs)

3 objectives per focus area, maximum. Each with 1-2 measurable key results.

**Template:**
```
Focus Area: [Business / Creative Project / Personal Brand / Other]

Objective 1: [Qualitative goal — ambitious but believable]
  KR 1a: [Measurable — by when?]
  KR 1b: [Measurable — by when?]

Objective 2: ...

Objective 3: ...
```

**For each goal, ask:**
- Is this in your control? (Output goals > outcome goals)
- Is this specific enough to know if you hit it?
- What's the ONE action that would move this forward most this week?

### Example OKR Framework

*(Replace with your actual focus areas from profile.md)*

```
🏢 [Your Business] — Q[X] Goals

O1: [Strengthen professional presence as the expert in your niche]
  KR1: [Post 3x/week for 10 weeks straight]
  KR1: [Profile updated with optimized headline and featured section]

O2: [Grow pipeline with qualified new client conversations]
  KR2: [Reach out to 5 past clients about new projects]
  KR2: [2 intro calls booked]

O3: [Add recurring revenue stream]
  KR3: [Propose retainer to 3 active clients]
  KR3: [1 retainer signed]

🎵 [Your Creative Project] — Q[X] Goals

O1: [Get existing work on all major streaming platforms]
  KR1: [Set up distribution service within 2 weeks]
  KR1: [Work live on Spotify and Apple Music]

O2: [Launch new platform presence with initial content batch]
  KR2: [Handle claimed, 3-5 pieces batch-created before launch]
  KR2: [First post published, engagement tracked]

O3: [Complete and release next work]
  KR3: [Collaboration session scheduled]
  KR3: [Released on primary platform + streaming]

🧑‍💻 [Your Personal Brand] — Q[X] Goals

O1: [Publish first piece of writing]
  KR1: [Platform set up within 2 weeks]
  KR1: [One piece published and distributed]

O2: [Establish consistent social presence]
  KR2: [Post 2x/week for 8 weeks]
  KR2: [Reach [X] followers (check current baseline)]

O3: [Define the writing niche / voice]
  KR3: [3 articles published, each from a different angle]
  KR3: [Identify which topic area got most response]
```

## Phase 4: Cross-Area Synergies

Look for connections between focus areas that can amplify each other:
- Can your creative project fuel personal brand credibility?
- Can your business content position you as a multi-dimensional creative (not just a service provider)?
- Can writing about your work attract clients AND build general audience?
- Can technical or dev work be teased publicly to build credibility?

## Phase 5: Update Everything

**Update profile.md:**
Suggest specific text updates to the "Current Priorities" section based on the goals just set. Get confirmation before writing.

**Store to memory:**
```
[built-in memory: save "Q[X] [Year] goals: [Area 1]: [summary]. [Area 2]: [summary]. [Area 3]: [summary]."]
[built-in memory: save "Q[X] vision: [key direction insight from this session]"]
```

**Add quarterly milestones to calendar:**
```
mcp__google_workspace__create_event(title="Quarterly review — Q[X]", date=[end of quarter])
mcp__google_workspace__create_event(title="Mid-quarter check-in", date=[midpoint])
```

**Schedule monthly reminders:**
```
mcp__scheduler__scheduler_add_reminder(
  title="Monthly brand check-in with Mila",
  schedule="monthly"
)
```

## Output

Deliver a clean one-pager:

```
✨ Q[X] [Year] — Strategic Plan

🌟 The Vision in 12 Months:
[2-3 sentences on where you're headed]

[Area 1 emoji] [Area 1] Goals:
• [O1 summary] → [KRs]
• [O2 summary] → [KRs]

[Area 2 emoji] [Area 2] Goals:
• [O1 summary] → [KRs]
• [O2 summary] → [KRs]

[Area 3 emoji] [Area 3] Goals:
• [O1 summary] → [KRs]
• [O2 summary] → [KRs]

🔗 Cross-Area Synergies:
• [What feeds what]

📅 Key milestones added to calendar.
Memory updated. Profile.md updated.

Let's go build it.
```

## Tips

- If no goals have been set before, start simple — 1 objective per area, not 3
- Goals should feel slightly uncomfortable but achievable. If everything feels easy, aim higher.
- Revisit quarterly goals monthly (quick check-in, not full replanning)
- The best quarterly goal is one where you'd be genuinely proud if you hit it
