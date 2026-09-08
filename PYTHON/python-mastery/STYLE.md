# Author style guide — READ BEFORE WRITING ANY CHAPTER

You are writing chapters of **Python Mastery**, a self-contained teaching book that takes a
complete beginner to building (a) a full-stack web application and (b) a complete Pygame game.

Voice: a sharp, patient senior engineer sitting next to the learner. Direct. No filler, no
"Great question!", no emoji, no marketing language. Explain *why*, then show *how*.

## File format

Each chapter is one Markdown file in `chapters/`, named `NN-slug.md`.

Front matter (required, exact keys):

```
---
chapter: 4
part: 1
title: Control Flow
summary: One or two sentences saying what the reader will be able to DO after this chapter.
minutes: 35
tags: [if/else, loops, boolean logic]
---
```

Part numbers:
1 = Foundations · 2 = Leveling Up · 3 = Real-World Python · 4 = Track A (Full-Stack Web)
5 = Track B (Game Development) · 6 = Appendices

## Required chapter skeleton

1. Opening paragraph — no heading. 3–5 sentences: what problem this chapter solves and why it
   matters in real code.
2. `##` sections teaching the material (use `###` for sub-topics). Order: concept → smallest
   working example → what changed → when you'd use it.
3. At least one `:::scenario` callout with a `:::solution` — a realistic workplace situation and
   how a Python developer actually handles it.
4. `## Key takeaways` — 4–8 bullets, each a complete, checkable statement.
5. `## Practice` — 4–6 exercises as checkbox list items: `- [ ] Build a ...`
   Order them easiest → hardest. Exercises must be *doable with only what's been taught so far
   plus earlier chapters*.
6. `## Solutions` — a `:::solution Exercise 1` block per exercise, with working code and 1–3
   sentences explaining the reasoning.

## Markdown conventions the build script understands

- Headings: `##`, `###`, `####` only. Never `#` (the chapter title comes from front matter).
- Code fences: always give a language — `python`, `bash`, `text`, `sql`, `html`, `js`, `json`.
  Use `text` (or no output language) for program output.
- Callouts — put the title after the kind:

  `:::note This is the heading`
  body text, may contain code fences, lists, paragraphs
  `:::`

  Kinds available: `note`, `tip`, `warning`, `danger`, `pitfall`, `scenario`, `solution`, `try`.
  Use `scenario` (purple) for real-world situations, `solution` (green) for the fix,
  `pitfall` for mistakes learners actually make.

- Inline code with single backticks; bold with `**`; links as `[text](https://...)`.
- Tables with standard pipe syntax.
- Lists: `-` for bullets, `1.` for ordered. Indent 2 spaces for nesting.
- Do **not** use raw HTML, `<details>`, footnotes, or emoji.

## Content rules

- Every runnable snippet must be complete and copy-pasteable, and must actually work on
  Python 3.12+. Prefer `pathlib` over `os.path`, f-strings over `.format()`/`%`, type hints in
  later chapters only (Part 2 chapter 16 onward).
- Show the output when it isn't obvious. Use a separate `text` fence.
- When you introduce a concept, name the problem *before* the feature. Bad: "Here is a dict."
  Good: "You need to look up a value by name, not by position — that's what a dict is for."
- Call out at least one real pitfall per chapter (mutable default args, `is` vs `==`,
  `list.sort()` returning `None`, off-by-one, etc.) using `:::pitfall`.
- Cross-reference other chapters naturally in prose ("we'll use this in Chapter 27 when we
  build the API"). Do not link with URLs — just name them.
- Length: 900–1600 words of prose plus code. Dense is fine; waffle is not.
- Never say "in this chapter we will learn". Just teach it.
