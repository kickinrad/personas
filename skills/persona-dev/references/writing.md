# Writing a persona

How to write a persona's `AGENTS.md` and skills so the agent behaves the same
way every run. Adapted from Matt Pocock's
[`writing-for-agents`](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents)
(MIT) and Anthropic's
[prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).

## What loads, and when

- `AGENTS.md` loads at every session start and stays loaded. It is the
  identity kernel: role, craft, voice, and role-specific boundaries, in the
  template's order. At most 400 words.
- `PERSONAS.md` holds the shared rules, imported by `AGENTS.md`. Never restate
  a shared rule in `AGENTS.md`; add only where this persona differs.
- `skills/` hold procedures, loaded when their description fires. A workflow
  the persona repeats goes in a skill, never in `AGENTS.md`.
- `user/` holds private profile and memory, read only when relevant.

Every line of `AGENTS.md` costs attention on every turn, so a line earns its
place only when it changes behaviour in most sessions.

## Rules

- **Earn each line.** Write from an observed failure or a real interview
  answer, never from what a persona "should" say. Delete any sentence the
  model already does by default.
- **Say what to do.** State the target behaviour; a prohibition makes the
  banned behaviour more available. Keep a ban only for a hard boundary, and
  pair it with what to do instead. Give the reason in a clause; skip capitals
  and "NEVER" shouting.
- **Leading words.** One well-known word anchors a behaviour in a token
  (*triage*, *mise en place*, *tape-reading*). Prefer the craft's own terms of
  art over coined ones.
- **One home per meaning.** A rule lives in `AGENTS.md`, `PERSONAS.md`, a
  skill, or the vault, never in two. Elsewhere, link to it.
- **Pointers name their trigger.** A line that sends the agent elsewhere says
  when to go: "for meal plans, use the `julia-meal-plan` skill".
- **Skill descriptions are triggers.** Verb first, then "Use when" with one
  phrase per distinct situation, then "Not for" naming the nearest sibling.
  Put the trigger words in the first 160 characters.
- **Finish lines are checkable.** Each skill ends on a condition the agent can
  test, such as "every item has a price and a store".

## Check it

Cold-read the folder as a stranger would. The persona's role, craft and voice
should be clear from `AGENTS.md` alone, with no shared rule repeated. Then run
one starter eval graded by the Craft's Proof.
