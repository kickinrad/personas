---
name: content-planning
description: Build content calendar across Instagram, TikTok, LinkedIn, and writing. Platform-specific strategy per track.
triggers:
  - content
  - what should i post
  - content calendar
  - schedule posts
  - post ideas
  - posting schedule
  - content ideas
  - content plan
  - what to post
---

# Content Planning

Build a content calendar that's realistic to execute and actually aligned with Wils' goals — not generic, not busywork.

## Before Starting

Pull context from memory and profile:
```
mcp__openmemory__openmemory_query("content strategy")
mcp__openmemory__openmemory_query("platform performance")
mcp__google_workspace__get_events (next 2-4 weeks)
```

Check: Are there upcoming releases, milestones, or deadlines that anchor the calendar?

## Clarify Scope

Ask: "Are we planning for this week, this month, or building a repeatable framework?"

- **Week:** Quick batch — 5-7 posts across platforms
- **Month:** Full calendar with themes and campaigns
- **Framework:** Repeatable posting cadence they can run on autopilot

## Platform-Specific Strategy

### 📸 Instagram

**@wilsxt / @wavytone (Music track)**
- Wavytone content: clips, studio moments, process videos, collab content with Chet
- Format mix: Reels > Carousels > Static (algorithm reality in 2025)
- Cadence: 3-4x/week (Reels perform on Tues/Wed/Fri historically)
- Research current audio trends: `WebSearch("instagram reels trending sounds [month year]")`

**@bff.llc (Agency track)**
- Before/afters, client wins (with permission), process glimpses, local Richmond angle
- Format: Carousels for portfolio, Reels for personality/behind-scenes
- Cadence: 2-3x/week

**Unified @wilsxt personal content:**
- The "person behind the brands" — bridges music + work identity
- Avoid splitting personality artificially; Wils is one person

### 🎵 TikTok (Wavytone)
- Not started yet — early mover advantage in jazz/hip-hop fusion niche
- Launch strategy: 3-5 videos before "going live" (content buffer)
- Format: 15-30 sec clips win discovery; full tracks as stitchable hooks
- Research: `WebSearch("jazz hip hop fusion TikTok creators 2025")`
- Handle to claim: check @wavytoneorchestra or @wavytone

### 💼 LinkedIn (Agency + Personal brand)
- b.f.f. thought leadership: WordPress tips, client process insights, RVA business scene
- Personal: developer/creative perspective on tools, AI, creative process
- Format: Text-heavy posts perform (no images needed); occasional carousels
- Cadence: 2-3x/week, consistent more important than volume
- DO NOT: pure promotional posts ("hire me") — educate and add value instead
- Research: `WebSearch("LinkedIn content strategy B2B agency 2025")`

### ✍️ Writing (Blog/Substack/Medium)
- Long-form: 1 piece per month minimum to start (sustainable)
- Topics: developer + creative perspective, tools, building in public, Richmond creative scene
- Cross-post strategy: Write once → Substack (owned list) + Medium (discovery) + LinkedIn excerpt
- Research worth doing: `WebSearch("Substack vs Medium 2025 writer strategy")`

## Building the Calendar

### Weekly Content Framework (sustainable cadence)

| Day | Platform | Track | Format |
|-----|----------|-------|--------|
| Mon | LinkedIn | Agency/Personal | Text post |
| Tue | Instagram @wavytone | Music | Reel |
| Wed | LinkedIn | Agency/Personal | Text post |
| Thu | Instagram @bff.llc | Agency | Carousel or Reel |
| Fri | Instagram @wavytone | Music | Reel |
| Sat | TikTok | Music | Short clip |
| (Monthly) | Substack/Medium | Personal | Long-form |

Adjust based on Wils' actual capacity. A sustainable 3x/week beats an unsustainable 7x/week.

## Content Ideation

For each upcoming piece, define:
1. **Platform + Handle**
2. **Track** (Agency / Music / Personal)
3. **Topic/Hook**
4. **Format** (Reel, carousel, text, etc.)
5. **Call to action** (if any)
6. **Publish date**

### Content Idea Generation

For Wavytone content:
- Behind the scenes: recording "skepta bounce" — what was the process?
- Genre education: "what is jazz hip-hop fusion?" (searchable, educational)
- Chet Frierson collab content (cross-posting potential)
- Richmond music scene angle ("sounds from Richmond")
- Covers/interpolations of known tracks in the Wavytone style

For b.f.f. content:
- Client transformation (before/after — get permission)
- "How we build WordPress sites that clients can actually edit"
- Richmond small business spotlight
- Tips: "3 things your website needs before running ads"

For personal brand content:
- "What it's like to run an agency AND produce music"
- Tools I'm building (tease ez-claude without revealing everything)
- Creative process posts

## Store + Schedule

Store insights to memory:
```
mcp__openmemory__openmemory_store("Content calendar [date]: [summary of plan]")
mcp__openmemory__openmemory_store("[Any platform insight discovered during planning]")
```

Add content drops to calendar:
```
mcp__google_workspace__create_event(title="Post: [topic]", date=[date])
```

## Output

Deliver a clean calendar in this format:

```
📅 Content Calendar — Week of [date]

Mon: [Platform] | [Topic] | [Format]
Tue: [Platform] | [Topic] | [Format]
...

📝 Notes:
- [Any strategy insight]
- [Platform-specific tip]

🎯 Goal for this week: [One measurable outcome]
```

## Tips

- Start with what Wils has (Wavytone content from recording) before creating new assets
- If he has zero content ready, the first step is a content batch session, not a calendar
- Remind him: content creation ≠ strategy. Showing up consistently matters more than perfection
- Research trending sounds/formats before finalizing Reel/TikTok ideas
