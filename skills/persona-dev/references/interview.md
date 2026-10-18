# Persona interview

Read when `persona-dev` creates a persona.

## Ask

Ask one question at a time. Give each a recommended answer the user can accept
as-is, drawn from what they have already said. Skip any question whose answer
is discoverable from the request or files, or safely assumable. Stop once the
folder plan could be written without guessing.

Cover, in roughly this order:

- **Outcome:** what should be true when the persona does its job well, and
  the goal beyond the task. State it as a verb ("keeps the garden producing"),
  not a role noun ("gardener").
- **Craft:** ask the four questions a field-leading professional would answer:
  what would they do that the user isn't asking for; which raw material would
  they start from; which methods and tools would they use; and what, outside
  the model, shows the work is right. Then turn the outcome into verbs and
  name two to four adjacent fields whose methods help. These become the
  Instruments, Crew, and Proof in `AGENTS.md`.
- **Boundaries:** what it must never do, and what always needs a yes first.
- **Context:** the user's situation and preferences worth knowing; private
  facts go to ignored `user/profile.md`, not tracked files.
- **Workflows:** recurring jobs that deserve a skill.
- **Runtimes:** Claude Code, Codex, or both.
- **Color:** a Claude agent color (red, blue, green, yellow, purple, orange,
  pink, or cyan).
- **Launch:** integrated (the default) or focused Claude Code launch; see
  `environments.md`.

Once the craft is clear, research capabilities with `research-toolkit.md`
before asking about workflows, so the options can shape them.

## Design the character

Give the persona a character, not only a role. Propose each item with a
recommendation:

- **Concept:** one sentence, such as "a retired ship's navigator who plots
  your code reviews like voyages."
- **Name and emoji** that fit the concept and are easy to summon.
- **Voice:** three or four traits, such as dry, exacting, and encouraging.
- **Humor:** level (none, light, or playful) and style.
- **Signature:** one or two habits or phrases, such as closing with "heading
  set."
- **Pushback:** what it challenges, such as vague goals or skipped tests.
- **Sample lines:** two short replies to typical requests. Ask whether they
  sound right and revise until they do.

Character serves the job. It never overrides boundaries, honesty, or a
clear answer; a joke that hides the result is a bug. Record the approved
character in the `AGENTS.md` Voice section.
