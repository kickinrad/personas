# Julia example

Julia is a fictional personal chef who helps you get dinner on the table.
Tell her what's in the kitchen, how much time you have, and what sounds good.
She'll help you choose a meal and figure out how to make it.

This folder defines a self-contained AI collaborator: her role, voice,
boundaries, and meal-planning skill stay together. She needs no recipe service
or grocery integration, just your usual Claude Code or Codex access. Your
runtime may still load global rules and tools; the folder isn't a sandbox.

## Try her out

Clone the repository and open the example:

```bash
git clone https://github.com/kickinrad/personas.git
cd personas/examples/julia
claude
```

Use `codex` instead of `claude` if that's your runtime. You don't need to
install the Personas plugin to try this existing folder. Then ask:

```text
Julia, I have eggs, spinach, a can of beans, and tortillas. What should I make
in 25 minutes? I would like one vegetarian dinner and a short shopping list.
```

```text
Plan three easy dinners for two people this week. We like bright, spicy food,
have one busy night, and want leftovers once. Show the plan before changing
any lists or calendars.
```

```text
I want to cook for friends on Saturday, but I have never made risotto. Give me
a low-stress menu, a prep timeline, and substitutions for a dairy-free guest.
```

## Make her yours

Change Julia's voice in `AGENTS.md`, adjust how she plans meals in the skill,
or ask her to help you edit either. Here's where everything lives:

- `AGENTS.md` says who Julia is, how she talks, and when she needs your approval.
- `CLAUDE.md` points Claude Code to that same definition.
- `.claude/settings.json` and `.codex/config.toml` hold each runtime's settings.
- `skills/julia-meal-plan/SKILL.md` explains how she plans meals.

For preferences you'd like her to remember, add ignored `user/profile.md` or
`user/memory/MEMORY.md` locally. Neither is included or required here. Julia
can suggest a grocery list, but needs your approval and a separately configured
connection to change a shared list or place an order.

To create a separate persona, [install Personas](../../README.md#install)
and ask:

```text
Use personas:persona-dev to create a personal-chef persona named Julia. Show
me the complete folder plan before writing anything.
```
