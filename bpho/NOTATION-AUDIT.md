# Notation audit — every symbol in the drill bank, with the root symbol in particular

The brief was to sweep the notation across all sections and look for errors, with the
radical named specifically. This is the record of that sweep: what was measured, what was
wrong, what was fixed, and what now stops each fault from returning.

**Scope.** 7 sections, 175 questions, 86 hand-authored figures, 333 radical occurrences in
the section source.

**Result.** Four defects, all fixed. Three of them were invisible to every check that
existed at the time — which is the part worth reading, because in each case the check that
would have caught it had to be written against a *different text* than the one already in
use.

---

## 1. The instrument

Four sweeps, each answering a question the others cannot:

| Sweep | Reads | Answers |
|---|---|---|
| `tools/bank/radical_audit.py` | rendered text | is any radical's **scope** ambiguous? |
| `tools/bank/notation_audit.py` | rendered + raw | what are all 333 radicals, how are they spelled, and is any entity malformed? |
| `tools/bank/check_render.js` | **the DOM** | does any entity survive to the page the student reads? |
| `gates.py all` | every text | does any section now fail a gate? |

`check_render.js` is the one that is not a model. The other three reason about what a
renderer *will* do; that one asks Chromium. It walks all 375 questions the page exposes
through their real route and greps `innerText` for anything shaped like an entity.

---

## 2. The finding that mattered: a radical with no overbar

A radical written as a character carries no overbar, so **its scope is carried entirely by
parentheses**. Three shapes:

```
√(hc/G)        explicit — the radicand is delimited
√2  √r  √200   conventional — the radicand is a single token, so there is nowhere else to stop
√3W/2          AMBIGUOUS — (√3)·W/2 or √(3W)/2, and nothing on the page says which
```

`S07-09` option C was the third shape. It is a statics question — a cylinder in a V-groove
with faces at 60° and 30° — whose entire discriminator is *which of the two normal forces*
is being asked for. `W/2` is the force on the left face and `W√3/2` is the force on the
right, so the ambiguous reading sat directly on the distinction the question tests. It now
reads `W√3/2`.

The sweep of all 333 radicals found **no other instance**, and that negative result is half
the finding: the check is narrow because the corpus is, and keeping it narrow is what stops
it firing on correct content.

### The check had to be written twice

The first version ran on `visible()` — the tag-stripper every other lint in `gates.py`
uses. It reported nothing on the very option it was written for:

```
raw      : '&#8730;3<code>W</code>/2'
visible  : '√3 W /2'      -> no match
```

`visible()` replaces **every** tag with a space. So the `<code>` boundary became a space
after the `3`, and the lint measured a radical whose radicand had clearly ended. The blind
spot was in the *measurement*, not the regex — the regex was correct and had been
unit-tested against the exact string.

`rendered()` now models the page instead: an **inline** tag vanishes, a **block** tag
leaves a gap. The check judges both readings, and the mutant suite carries a case for each
direction (`notation.ambiguous_radical_scope` must fire; `notation.single_token_radical_is_fine`
must stay silent on `√2 × √(h/g)`).

---

## 3. Seven figures were valid HTML and invalid XML

`fig/*.svg` is an XML document that the page inlines into HTML. That asymmetry hides a real
fault: `&theta;`, `&Omega;` and `&mu;` are **HTML** named entities, and XML defines exactly
five — `amp`, `lt`, `gt`, `quot`, `apos`. A figure using `&theta;` therefore renders
perfectly on the site and is **not a well-formed SVG document**, failing the moment it is
opened on its own.

Seven figures had shipped that way:

| Figure | Entity | Used for |
|---|---|---|
| `s02-05`, `s03-16`, `s03-18` | `&theta;` | a pendulum angle |
| `s02-12`, `s03-04`, `s03-10` | `&Omega;` | a resistance |
| `s03-21` | `&mu;` | a capacitance in µF |

Every text-level check read the entity as text and saw a theta, which is why it survived.
Only a parse sees it. Three things now prevent it:

- `svgkit.svg()` — the single choke point every figure passes through — **raises** on a
  named entity, so it cannot be emitted in the first place;
- `figure_errors()` runs `ET.fromstring` on every figure, so the gate fails if one appears
  anyway;
- a mutant (`figure.named_entity_breaks_xml`) builds a scratch copy of `fig/` with
  `&theta;` injected and asserts the gate fires. It copies rather than corrupting the real
  directory, because an interrupted mutant must not be able to leave a broken figure
  behind.

All 86 figures now parse. Verified across the whole space, not just the bank: the only
other file matching a named entity was `tools/paper2025/fig/r0-02.svg`, which uses `&lt;` —
one of the five XML *does* define.

---

## 4. Eleven error messages that named no gate

The mutation harness asserts `err.startswith(gate)`. `figure_errors()` appended **untagged**
strings — eleven of them — so the moment a mutant was written for the new XML check, the
suite reported:

```
figure.named_entity_breaks_xml   G8   *** MISSED ***
```

on a defect the gate had caught correctly. The honest-looking conclusion was "the gate is
broken"; the true one was "the gate is fine and cannot be seen". The strings are now tagged
`G8`, and the class is closed rather than the incident:

`check_messages_are_tagged()` runs as a **pre-flight** in `mutants.py`, walks `gates.py`
with `ast`, and refuses to start if any message that reaches the error list fails to name
its gate. It also accepts a helper that stamps its whole list at the return — which is what
`figure_errors()` now does, and the better shape, since the prefix is applied once instead
of eleven times.

An error nobody can attribute is an error nobody owns.

---

## 5. One symbol, three spellings

The root symbol was stored three ways: `&radic;` in 15 questions, `&#8730;` in 25, and the
bare `√` character in 2. All three render identically, so this was never visible on the
page — but the two non-numeric forms each carry a failure mode:

- **`&radic;` is HTML-only.** It is the same hazard as the seven figures above, sitting in
  the content instead of in a file. The data is only ever rendered as HTML today, so it is
  not a live bug — but it is the same class of risk, and the corpus is one mechanism away
  from being parsed as XML.
- **The bare character** survives every tool run until one of them writes the file without
  an explicit encoding.

`&#8730;` has neither problem, so **119 occurrences across sections 1, 2, 3, 5 and 7 were
normalised to it** — the form the newer sections already used. A G3 lint now enforces it,
and it reads the **raw** source, because `_html.unescape()` maps `&radic;` and `&#8730;` to
the same character and by the time `visible()` has run the two are indistinguishable.

### The normalisation introduced a bug, and G12 caught it within a minute

`S07-12`'s first `rel` label held a literal `√`. Rewriting it to `&#8730;` was right for
every HTML field and wrong for that one: a `rel` label is passed through `esc()` — because
`priority.js` reuses it as a topic *name* — so the candidate would have read
`&#8730;(γP/ρ)` verbatim.

```
G12 S07-12: the rel[0] contains '&', but this field is rendered as PLAIN TEXT,
            so the candidate would see 'The speed of sound in a gas is &#8730;(γP/ρ)…'
```

The fix was to put the character back, and to write the reason next to the line. The
corpus has **two** notation policies and they follow the two renderers:

| Field | Renderer | Spelling |
|---|---|---|
| `stem`, `opts`, `sol`, `trap` | injected as **HTML** | numeric reference — `&#8730;`, `&#952;` |
| `topic`, every `rel` label | passed through **`esc()`** | the character itself — `√`, `θ` |

They are not an inconsistency; they are the two renderers. The lesson is that the sweep
which caused the bug was *mechanical* — a find-and-replace that does not know which field
it is in will always be wrong in one of them.

---

## 6. What was checked and found clean

Negative results, stated so they are not re-litigated:

- **No second ambiguous radical.** All 333 swept; `S07-09` was the only one.
- **Every radicand is hand-computable**, which matters on a non-calculator paper. The
  awkward-looking ones are all legitimate: `√0.20 ≈ 0.45`, `√0.81 = 0.9`, `√625 = 25`,
  `√300 = 17`, `√1.25 ≈ 1.1`, `√0.21 ≈ 0.458`. Each is either exact or sits behind an `≈`.
- **No unknown, control, or malformed entities.** 80 distinct entities in use, none of them
  undefined, none missing a semicolon.
- **Nothing reaches the page unrendered.** All 375 questions the site exposes, walked
  through their real route: **0** unrendered entities, 0 console errors, and **132** radical
  glyphs rendered as U+221A alongside 21 other symbol types.
- **Every figure source reproduces its artefact byte for byte.** Regenerating sections 1–7
  and diffing against the committed `fig/*.svg` produces no change, so the gate is reading
  the same figure the author wrote.
- **Every radical-bearing answer was re-derived.** `S07-09` was checked by hand as well as
  by machine: resolving horizontally gives `N_right = √3·N_left`, vertically gives
  `2·N_left = W`, so `N_left = W/2` — option B, which is the stored key and which agrees
  with the question's own `check` expression.

---

## 7. Enforcement

Each finding, and the thing that now prevents it:

| Finding | Prevented by | Mutant |
|---|---|---|
| an ambiguous radical scope | G3 radical-scope lint, judged on both readings | `notation.ambiguous_radical_scope` / `notation.single_token_radical_is_fine` |
| a named entity in a figure | `svgkit.svg()` raises; G8 parses the file | `figure.named_entity_breaks_xml` |
| an error message naming no gate | pre-flight `check_messages_are_tagged()` | — (structural, checked directly) |
| a second spelling of the root | G3 root-form lint on the raw source | `notation.named_root_entity` / `notation.numeric_root_is_fine` |
| an entity in an escaped field | G12 | `render.markup_in_a_rel_label` / `render.plain_unicode_is_fine` |
| an entity reaching the page | `check_render.js` | — (checks the DOM, not the source) |

The suite is now **51 mutants**, all behaving, and the pre-flight refuses to start if any
message in `gates.py` cannot be attributed.

---

## 8. Reproducing this audit

From `bpho/tools/bank/`:

```sh
python radical_audit.py        # every radical's scope, ambiguous ones only
python notation_audit.py       # all 333, their spellings, entity hygiene
python gates.py all            # the twelve gates over all seven sections
python mutants.py              # 51 mutants + the pre-flight tag audit
```

From `bpho/`, with the local server up (`127.0.0.1:8901`, rooted at the repo root):

```sh
NODE_PATH=<playwright-core> node tools/bank/check_render.js
```

`check_render.js` discovers its questions from `window.BPHO_QUESTIONS`, so sections 8–40
are covered by it with no edit.

---

## 9. What this audit did not check

Stated plainly, because the pattern in this project is that each audit finds the faults its
instrument can see and no others:

- **The notation's typography is not checked** — whether a symbol sits on the baseline, or
  whether a subscript is legible at the printed size, needs a person looking at a page.
  The four figures and questions captured during this audit were read by eye; the other 171
  were not.
- **`tools/paper2025/` and `tools/r0sample/` were swept for the XML fault but not for
  radical scope.** They reproduce official BPhO material through a separate pipeline and
  were deliberately left unmodified. They are clean on the XML check.
- **The bare `√` character remains legitimate in `rel` labels**, so the root symbol is
  still spelled two ways in the corpus as a whole. That is by design, and the G3 form lint
  is scoped to the HTML fields precisely so it does not fight G12.
