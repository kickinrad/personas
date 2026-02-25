---
name: writing-practice
description: Writing career workflow - topic ideation, outlining, publishing, and distributing across blog/Substack/Medium.
triggers:
  - write
  - writing
  - blog
  - substack
  - article
  - thoughts
  - newsletter
  - medium
  - publish
  - writing practice
  - thought leadership
  - post ideas
  - draft
---

# Writing Practice

Building Wils as a writer and thought leader — developer, creative, and maker perspective.

## Before Starting

```
mcp__openmemory__openmemory_query("writing topics")
mcp__openmemory__openmemory_query("personal brand writing")
mcp__openmemory__openmemory_query("published articles")
```

## Current Writing State

Wils has writing ambitions but hasn't launched yet. Platforms to set up: blog (personal site?), Substack, Medium. Distribution via Twitter/Bluesky + LinkedIn after publish.

## Agenda — Pick the Focus

Ask Wils which mode:

1. **Topic ideation** — finding something worth writing about
2. **Outline a piece** — take a topic from idea to structure
3. **Platform strategy** — where to publish and why
4. **Distribution plan** — how to spread a piece after publishing
5. **Writing habit** — building the consistency

---

## 1. Topic Ideation

Wils' perspective is legitimately unique — developer + creative + agency owner + musician. That combination creates takes nobody else has.

**Content pillars to explore:**

### Developer/Tools Lens
- "How I use AI agents to run my creative life" (ez-claude — without revealing everything)
- "Building tools for yourself vs. building products"
- "The Claude Code ecosystem is underrated — here's what I've built"
- "Why I made a personal chef AI" (Julia — interesting human story)

### Agency/Business Lens
- "Running a boutique agency in a world of templates"
- "What nonprofits actually need from a web designer"
- "How I think about pricing custom work"
- "Lessons from building WordPress sites that clients can actually edit"

### Music/Creative Lens
- "Making music in the margins of a full-time creative career"
- "What jazz and software development have in common"
- "Building Wavytone Orchestra — an experimental project from Richmond"
- "The Richmond creative scene: underrated and growing"

### Intersection (most interesting to readers)
- "Running an agency, making music, and building AI tools — here's how I manage it"
- "The creative professional's stack in 2025"
- "Why I stopped separating my identities and let them collide"

**Ideation process:**
Ask: "What's something you've learned recently that you wish someone had told you earlier?"
Ask: "What do people ask you about that you always have a good answer to?"
Ask: "What's an opinion you have that most people in your field would disagree with?"

Research trending topics: `WebSearch("developer personal brand topics 2025")`
Research: `WebSearch("Substack topics growing 2025")`

---

## 2. Outlining a Piece

Once a topic is chosen, build a tight outline:

**Template:**
```
Title: [Working title — make it specific and searchable]
Audience: [Who is this for?]
Hook: [First sentence — why should they care?]
Thesis: [One sentence — what's the main point?]

Structure:
1. [Section — ~200 words]
2. [Section — ~200 words]
3. [Section — ~200 words]
4. [Section — ~200 words]

Closing: [Call to action or reflection — what should they do/think?]

Target length: [800-1200 words for Substack/blog; 400-600 for LinkedIn]
```

Good writing advice to pass on:
- One idea per piece — ruthlessly cut anything that doesn't serve the thesis
- Specifics > generalities (Richmond, Wavytone, bff.llc > "I run a business")
- First draft is always garbage — the goal is to get it done, not get it right

---

## 3. Platform Strategy

Research current recommendations: `WebSearch("Substack vs Medium vs personal blog 2025")`

**Working framework (to validate with research):**

| Platform | Role | Why |
|----------|------|-----|
| **Substack** | Primary — owned audience | Email list = owned channel, discovery through Substack Notes |
| **Medium** | Secondary — discoverability | SEO power, built-in audience for developer/creative topics |
| **wilstierney.com** | Portfolio anchor | Links to Substack, showcases best work |
| **LinkedIn** | Distribution | Excerpt + link drives professional traffic |
| **Twitter/Bluesky** | Distribution | Thread or link post |

**Write once, distribute everywhere** — Substack is the source of truth, syndicate elsewhere.

Setup checklist (if not done):
- [ ] Substack: Create account, choose name (wilstierney? wavytone? bff?)
- [ ] Medium: Claim profile, link to main site
- [ ] wilstierney.com: Add writing/blog section or link to Substack

---

## 4. Distribution Plan

After publishing:

**Day 0 (Publish day):**
- Send to Substack subscribers
- Post on LinkedIn: compelling excerpt + "full piece linked"
- Post on Twitter/Bluesky: thread version or quote + link

**Day 2-3:**
- Post on Medium (with canonical URL pointing back to Substack to avoid SEO split)
- Engage with any comments/responses

**Day 7+:**
- Re-share on LinkedIn if it performed well
- Repurpose: Instagram carousel summarizing key points
- Add to wilstierney.com featured writing section

**Calendar it:**
```
mcp__google_workspace__create_event(title="Publish: [title]", date)
mcp__google_workspace__create_event(title="Distribute: [title] - LinkedIn/Twitter", date+1)
```

---

## 5. Writing Habit

Building consistency:

**Minimum viable writing habit:**
- One piece per month to start — achievable without burning out
- Dedicated writing block: when does Wils have time and mental energy?
- Draft in Notion/Obsidian → Edit → Publish (don't draft in Substack)

**Schedule a monthly writing block:**
```
mcp__scheduler__scheduler_add_reminder(
  title="Writing day — [topic from list]",
  schedule="monthly"
)
```

---

## Store Insights

```
mcp__openmemory__openmemory_store("Writing topics list: [topics from this session]")
mcp__openmemory__openmemory_store("Writing platforms decision: [whatever is decided]")
mcp__openmemory__openmemory_store("Published: [title] on [date] — [performance notes]")
```

## Tips

- The developer + musician + agency owner combination is genuinely rare — lean into the intersection
- Don't wait until the writing is "good enough" to publish — ship it, improve next time
- Substack's discovery (Notes, recommendations) is actively growing — early mover advantage
- One published piece is worth 10 drafted ones
