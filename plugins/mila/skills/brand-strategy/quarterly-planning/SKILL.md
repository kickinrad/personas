---
name: quarterly-planning
description: Quarterly strategy review and goal-setting across all three tracks (agency, music, personal brand).
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
mcp__openmemory__openmemory_query("quarterly goals")
mcp__openmemory__openmemory_query("brand strategy")
mcp__openmemory__openmemory_query("annual vision")
mcp__google_workspace__get_events (next 30-90 days)
```

## Phase 1: Reflect (Last Quarter)

Before setting goals, look at what happened.

For each track, ask:
- What were the goals? (Pull from OpenMemory or profile.md)
- What actually happened?
- What moved the needle?
- What wasted time?
- What surprised you?

### 🏢 b.f.f. Agency
- Revenue vs. target (if tracked)
- New clients acquired
- Client retention
- LinkedIn/marketing progress
- What changed in the service offering?

### 🎵 Wavytone Orchestra
- Releases completed
- Streaming/platform progress
- TikTok status
- Collaboration wins
- Press or recognition

### 🧑‍💻 Personal Brand
- Writing published
- Social growth (follower counts, engagement)
- Twitter/Bluesky progress
- Any speaking, features, or visibility wins?

## Phase 2: Annual Vision Check

Step back even further:

"Where do you want to be in 12 months?"

For each track, paint the picture:
- **b.f.f.:** What does a healthy, thriving agency look like? (Revenue target, client types, team size, lifestyle)
- **Wavytone:** Where is the music project? (Streaming numbers, TikTok presence, live shows, EP released?)
- **Personal brand:** How are you known? (What are people saying? Where are you writing? What's your LinkedIn like?)

This isn't about perfect goals — it's about direction. The details fill in later.

## Phase 3: Set Quarterly Goals (OKRs)

3 objectives per track, maximum. Each with 1-2 measurable key results.

**Template:**
```
Track: [Agency / Music / Personal Brand]

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

### Example Framework (fill in with Wils' actual goals)

```
🏢 b.f.f. Agency — Q[X] Goals

O1: Strengthen LinkedIn presence as the boutique WordPress expert for nonprofits
  KR1: Post 3x/week for 10 weeks straight
  KR1: Profile updated with optimized headline and featured section

O2: Grow pipeline with 2 qualified new client conversations
  KR2: Reach out to 5 past clients about new projects
  KR2: 2 intro calls booked

O3: Add recurring revenue through maintenance retainers
  KR3: Propose retainer to 3 active clients
  KR3: 1 retainer signed

🎵 Wavytone — Q[X] Goals

O1: Get "skepta bounce" on all major streaming platforms
  KR1: Set up DistroKid (or chosen distributor) within 2 weeks
  KR1: Track live on Spotify and Apple Music

O2: Launch TikTok presence with 5 videos published
  KR2: Handle claimed, 3-5 videos batch-created before launch
  KR2: First video published, 100+ views

O3: Complete and release next Wavytone track
  KR3: Recording session with Chet scheduled
  KR3: Track released on Bandcamp + streaming

🧑‍💻 Personal Brand — Q[X] Goals

O1: Publish first piece of writing
  KR1: Substack set up within 2 weeks
  KR1: One piece published and distributed

O2: Establish consistent LinkedIn presence
  KR2: Post 2x/week for 8 weeks
  KR2: Reach [X] followers (check current baseline)

O3: Define the writing niche / voice
  KR3: 3 articles published, each from a different angle
  KR3: Identify which topic area got most response
```

## Phase 4: Cross-Track Synergies

Look for connections between tracks that can amplify each other:
- Can Wavytone content fuel personal brand credibility?
- Can b.f.f. LinkedIn content position Wils as a creative professional (music + dev) rather than just a service provider?
- Can writing about the agency attract agency clients AND build general audience?
- Can the ez-claude/developer work be teased publicly to build developer cred?

## Phase 5: Update Everything

**Update profile.md:**
Suggest specific text updates to the "Current Priorities" section based on the goals just set. Wils approves.

**Store to OpenMemory:**
```
mcp__openmemory__openmemory_store("Q[X] [Year] goals: Agency: [summary]. Music: [summary]. Brand: [summary].")
mcp__openmemory__openmemory_store("Q[X] vision: [key direction insight from this session]")
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
[2-3 sentences on where Wils is headed]

🏢 Agency Goals:
• [O1 summary] → [KRs]
• [O2 summary] → [KRs]

🎵 Music Goals:
• [O1 summary] → [KRs]
• [O2 summary] → [KRs]

🧑‍💻 Personal Brand Goals:
• [O1 summary] → [KRs]
• [O2 summary] → [KRs]

🔗 Cross-Track Synergies:
• [What feeds what]

📅 Key milestones added to calendar.
Memory updated. Profile.md updated.

Let's go build it.
```

## Tips

- If Wils hasn't set goals before, start simple — 1 objective per track, not 3
- Goals should feel slightly uncomfortable but achievable. If everything feels easy, aim higher.
- Revisit quarterly goals monthly (quick check-in, not full replanning)
- The best quarterly goal is one where you'd be genuinely proud if you hit it
