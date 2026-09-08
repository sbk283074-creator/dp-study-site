---
chapter: 25
part: 4
title: HTML, CSS & JS for Python Developers
summary: Learn just enough HTML, CSS, and JavaScript to build a real front end — the parts you will actually use, explained by analogy to Python.
minutes: 45
tags: [html, css, javascript, dom, fetch, forms, xss, flexbox]
---

You are about to write web applications, and web applications have a second language in the
browser whether you like it or not. The good news: you do not need to become a frontend developer.
You need to read HTML without flinching, write CSS that produces a layout you intended rather than
one you discovered, and write roughly fifty lines of JavaScript that fetch data and update the
page. That is the gap between "my API returns JSON" and "I have a product". This chapter closes it,
using Python as the reference point the whole way.

## HTML: structure, not appearance

HTML is a tree of **elements**. Each element is a tag, optional attributes, and content:

```html
<p class="note" id="intro">Hello, world.</p>
```

`<p>` opens, `</p>` closes, `class` and `id` are attributes, and the text between is the content.
Elements nest, and they must nest correctly — the browser will silently "fix" badly nested markup
in ways you did not intend, so close tags in the reverse order you opened them.

A handful of elements have no content and no closing tag (**void elements**): `<img>`, `<br>`,
`<input>`, `<meta>`, `<link>`.

```html
<img src="/static/logo.png" alt="TaskForge" width="120">
```

`alt` is not optional decoration — it is what screen readers announce and what shows when the image
fails to load.

### The skeleton every page has

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TaskForge</title>
    <link rel="stylesheet" href="/static/style.css">
  </head>
  <body>
    <h1>Tasks</h1>
    <script src="/static/app.js" defer></script>
  </body>
</html>
```

`<head>` is metadata (not displayed); `<body>` is what you see. The viewport meta tag is what makes
a page respect a phone's width instead of pretending to be a 980px desktop and zooming out. `defer`
on the script means "run this after the HTML is parsed", which is almost always what you want —
without it, `document.querySelector` in your script can run before the elements exist.

### Semantic tags

You could build every page out of `<div>` and `<span>`. Do not. Semantic elements tell browsers,
screen readers, search engines, and future-you what a region *is*:

| Tag | Meaning |
| --- | --- |
| `<header>` | Introductory content for a page or section |
| `<nav>` | Navigation links |
| `<main>` | The primary content, once per page |
| `<section>` | A thematic grouping, usually with a heading |
| `<article>` | Self-contained content (a post, a card, a comment) |
| `<aside>` | Tangential content (sidebar, related links) |
| `<footer>` | Closing content for a page or section |

`<div>` is a generic block container and `<span>` is a generic inline one. Use them for layout
only, when nothing semantic fits.

### Forms: `name` is what the server sees

This is the part Python developers get wrong most often. A form sends data to the server, and the
only thing that identifies each field is its `name` attribute — not its `id`, not its placeholder,
not its label.

```html
<form action="/tasks" method="post">
  <label for="title">Task</label>
  <input id="title" name="title" type="text" required maxlength="200">

  <label for="priority">Priority</label>
  <select id="priority" name="priority">
    <option value="low">Low</option>
    <option value="medium" selected>Medium</option>
    <option value="high">High</option>
  </select>

  <label>
    <input type="checkbox" name="done" value="1"> Done
  </label>

  <button type="submit">Add task</button>
</form>
```

Submitted as `application/x-www-form-urlencoded`, the body is literally:

```text
title=Write+the+report&priority=high&done=1
```

FastAPI then binds it:

```python
from fastapi import Form


@app.post("/tasks")
def create_task(title: str = Form(...), priority: str = Form("medium"), done: bool = Form(False)):
    ...
```

Notice how `id` and `name` diverge in purpose: `id` is unique in the document and used by `<label
for=...>` and `document.querySelector("#title")`; `name` is the wire format. A field with an `id`
and no `name` sends nothing at all. Also note `value` versus content: for `<input>`, the submitted
value comes from `value` (or what the user typed); for `<select>` it comes from the chosen
`<option value=...>`; for a checkbox, an unchecked box submits **nothing** — that is why
`done: bool = Form(False)` needs a default.

### Escaping

HTML gives five characters special meaning, and if user content contains them you have two
problems: broken markup and a security hole.

| Character | Write as | Why |
| --- | --- | --- |
| `<` | `&lt;` | starts a tag |
| `>` | `&gt;` | ends a tag |
| `&` | `&amp;` | starts an entity |
| `"` | `&quot;` | delimits an attribute |
| `'` | `&#39;` | delimits an attribute |

Everything else — including all non-ASCII text — is fine as-is provided the document declares
`<meta charset="utf-8">`.

## CSS: appearance and layout

CSS is a list of rules. Each rule selects elements and sets properties on them:

```css
/* selector            { property: value; } */
article.task           { margin-bottom: 0.75rem; }
```

### Selectors

| Selector | Matches |
| --- | --- |
| `p` | every `<p>` |
| `.note` | every element with `class="note"` |
| `#intro` | the element with `id="intro"` |
| `article.task` | `<article class="task">` |
| `article > h2` | an `<h2>` that is a direct child of `<article>` |
| `article h2` | any `<h2>` inside `<article>`, at any depth |
| `button:hover` | a button while hovered |
| `input:focus` | an input while focused |
| `[data-done="1"]` | elements with that attribute value |

Specificity decides conflicts: `id` beats `class` beats element, and later rules beat earlier ones
of equal specificity. When in doubt, open DevTools, click the element, and read which rule won.

### The box model

Every element is a box: **content** → `padding` → `border` → `margin`. Margins collapse between
siblings (the larger wins, they do not add), which surprises everyone once.

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}
```

That single rule makes `width: 300px` mean 300px *total* instead of 300px plus padding plus border.
Put it at the top of every stylesheet.

### Flexbox: the five properties you need

Flexbox lays out items in one dimension — a row or a column.

```css
.toolbar {
  display: flex;
  justify-content: space-between; /* main axis: start | center | end | space-between */
  align-items: center;            /* cross axis: stretch | start | center | end */
  gap: 0.75rem;                   /* space between items, no margin hacks */
  flex-wrap: wrap;                /* allow a second line instead of squashing */
}
```

```html
<div class="toolbar">
  <h2>Tasks</h2>
  <button>New task</button>
</div>
```

That is the whole toolkit for nav bars, card rows, and button groups. `flex: 1` on a child means
"take the remaining space", which solves the classic "sidebar plus content" split.

### Grid: two dimensions

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  gap: 1rem;
}
```

Read that as: as many columns as fit, each at least 16rem wide, sharing leftover space equally. It
is a responsive card grid with no media query at all.

### Custom properties and a dark-mode palette

```css
:root {
  --bg: #f7f7f8;
  --surface: #ffffff;
  --text: #1c1c1f;
  --muted: #6b7280;
  --accent: #2563eb;
  --border: #e5e7eb;
  --radius: 8px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #101114;
    --surface: #181a1f;
    --text: #e8e8ea;
    --muted: #9ca3af;
    --accent: #60a5fa;
    --border: #2a2d34;
  }
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, sans-serif;
  line-height: 1.5;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
}
```

`--name` defines a custom property, `var(--name)` uses it. Defining the palette once on `:root`
and flipping it inside one media query gets you dark mode for free, because every rule that uses
`var()` updates automatically.

One explicit media query for small screens:

```css
@media (max-width: 40rem) {
  .toolbar { flex-direction: column; align-items: stretch; }
}
```

## JavaScript: behaviour

JavaScript is not Python with semicolons, but the first eighty percent maps cleanly.

### Variables, functions, strings

```js
let count = 0;            // reassignable
const api = "/api/tasks"; // const binding; the object it points to can still mutate
count += 1;

const greet = (name) => `Hello, ${name}!`;   // arrow function + template literal
const add = (a, b) => a + b;                 // implicit return
const shout = (s) => s.toUpperCase();

console.log(greet("Ada"), add(2, 3), shout("hi"));
```

Template literals use backticks and `${}` — they are f-strings. Arrow functions are lambdas:
`(x) => x * 2` is `lambda x: x * 2`. Three gotchas that will bite you:

- `==` coerces types (`1 == "1"` is `true`). Always use `===`.
- `null` and `undefined` are both "nothing" but different nothings. Use `??` for defaults:
  `const page = data.page ?? 1`.
- Semicolons are optional; the rules for when they are inserted are not. Use them.

### Arrays and objects

```js
const tasks = [
  { id: 1, title: "Write the report", done: false, tags: ["work", "q3"] },
  { id: 2, title: "Buy paint", done: true, tags: ["home"] },
];

tasks.filter((t) => !t.done)
     .map((t) => t.title.toUpperCase())
     .forEach((t) => console.log(t));

const byId = Object.fromEntries(tasks.map((t) => [t.id, t]));
const names = tasks.map((t) => t.title);
const first = tasks.find((t) => t.done);
```

| Python | JavaScript |
| --- | --- |
| `list` | `Array` |
| `dict` | `Object` (or `Map`) |
| `len(xs)` | `xs.length` |
| `xs.append(x)` | `xs.push(x)` |
| `[f(x) for x in xs]` | `xs.map((x) => f(x))` |
| `[x for x in xs if p(x)]` | `xs.filter((x) => p(x))` |
| `sum`, `min`, `max` | `xs.reduce(...)`, `Math.min(...xs)` |
| `d["k"]` | `d.k` or `d["k"]` |
| `"k" in d` | `"k" in d` or `d.k !== undefined` |
| `d.get("k", default)` | `d.k ?? default` |
| `f"{a}-{b}"` | `` `${a}-${b}` `` |
| `lambda x: x + 1` | `(x) => x + 1` |
| `try/except` | `try/catch` |
| `None` | `null` / `undefined` |
| `async def` / `await` | `async function` / `await` |
| `asyncio.gather` | `Promise.all` |
| `json.dumps` / `loads` | `JSON.stringify` / `JSON.parse` |
| `dict` comprehension over zip | `Object.fromEntries(...)` |
| `raise ValueError("x")` | `throw new Error("x")` |

The biggest difference is style: JS leans on method chaining with callbacks where Python leans on
comprehensions. Same operations, different idiom.

### Finding and changing elements

```js
const list = document.querySelector("#task-list");       // first match
const buttons = document.querySelectorAll(".task button"); // all matches
const form = document.querySelector("form");

const item = document.createElement("li");
item.className = "task";
item.dataset.id = "12";           // becomes data-id="12" in the HTML
item.textContent = "Buy paint";   // safe: sets text, never markup
list.append(item);

item.classList.add("done");
item.classList.toggle("done");
item.remove();
```

`document` is the page. `querySelector` takes the same selectors CSS does. Build elements with
`createElement` and set `textContent`, and you never have to think about escaping.

### Events

```js
form.addEventListener("submit", async (event) => {
  event.preventDefault();                       // stop the browser's full-page reload
  const title = form.querySelector("#title").value;
  await createTask(title);
  form.reset();
});

list.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-id]");
  if (!button) return;                          // clicked something else
  completeTask(button.dataset.id);
});
```

Two patterns worth memorising. `event.preventDefault()` is how you stop a form from doing its
default full-page submit. **Event delegation** — one listener on the parent, `event.target.closest()`
to find what was actually clicked — is how you handle elements that do not exist yet, without
attaching a listener to each one as you create it.

### fetch, async/await, and updating the page

```js
async function loadTasks() {
  const response = await fetch("/api/tasks");
  if (!response.ok) {
    throw new Error(`server said ${response.status}`);
  }
  const tasks = await response.json();      // parse JSON body
  render(tasks);
}

async function createTask(title) {
  const response = await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, priority: "medium" }),
  });
  if (!response.ok) throw new Error(`create failed: ${response.status}`);
  return response.json();
}

function render(tasks) {
  list.replaceChildren(
    ...tasks.map((task) => {
      const li = document.createElement("li");
      li.className = task.done ? "task done" : "task";
      li.textContent = task.title;          // textContent, never innerHTML
      return li;
    })
  );
}

loadTasks().catch((err) => console.error("load failed:", err));
```

Every piece of that has a Python equivalent you already know: `await` works exactly as it does in
`asyncio` (Chapter 21), `fetch` is `requests`, and `await response.json()` is
`response.json()`. Two traps: `fetch` does **not** reject on 404 or 500 — you must check
`response.ok` yourself — and you must `await` the `.json()` call because the body arrives
separately from the headers.

`console.log`, `console.warn`, and `console.error` print to the DevTools **Console** tab. It is
your `print()` debugger: log the object, inspect it interactively, set a breakpoint by clicking a
line number in **Sources**.

## How the Python backend and the JS frontend fit together

The division is simple and worth stating explicitly:

| Layer | Runs | Owns |
| --- | --- | --- |
| Python (FastAPI) | server | validation, business rules, database, auth, rendering templates |
| HTML | browser | structure |
| CSS | browser | appearance |
| JS | browser | interaction: fetch data and update the DOM |

The contract between them is HTTP plus JSON. Your Python exposes:

```python
@app.get("/api/tasks")
def list_tasks() -> list[dict]:
    return [{"id": t.id, "title": t.title, "done": t.done} for t in repo.list_tasks()]
```

and your JS consumes exactly that shape. When the two disagree, the bug is at the boundary, so
check the Network tab first: did the request go out, what did the server return, and what did your
code do with it.

:::note Chapter 28 offers the other path
Everything in this chapter is needed to read, review, and debug a frontend. It is not needed to
*build* most of one. Chapter 28 introduces HTMX, which lets the server return small fragments of
HTML that the browser swaps into the page, so the loop stays in Python: no JSON serialisation
layer, no client-side rendering, no duplicated validation. If JavaScript is not where you want to
spend your time, read this chapter for comprehension and build with HTMX.
:::

:::scenario "The search box types one character per second"
You added a search field that filters tasks as the user types. On your machine it is fine. The
team in the other office reports that typing "report" takes eight seconds and shows results in a
random order — "repor" appearing after "report".
:::

:::solution Debounce the input, and cancel the previous request
Two bugs, both invisible with a local server.

**Bug 1: one request per keystroke.** Every `input` event fires `fetch`. Seven characters means
seven round trips, and the browser caps concurrent connections, so they queue. Debounce: wait
until the user stops typing.

**Bug 2: responses arrive out of order.** Even debounced, a slow earlier request can land after a
faster later one, overwriting good results with stale ones. Track the request and ignore anything
that is not the newest.

```js
let requestId = 0;

function debounce(fn, delay = 250) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

async function search(query) {
  const id = ++requestId;
  const response = await fetch(`/api/tasks?q=${encodeURIComponent(query)}`);
  const tasks = await response.json();
  if (id !== requestId) return;   // a newer search already started; discard
  render(tasks);
}

searchInput.addEventListener("input", debounce((e) => search(e.target.value), 250));
```

Three details that matter:

- `encodeURIComponent` — never build a query string by concatenation. A `&` or `#` in the user's
  text breaks the URL, and worse, injects parameters.
- The stale-response guard is a general pattern, not a search-specific hack. Any time two requests
  can be in flight, decide which one wins.
- Rebuilding the whole list on every keystroke also loses focus and scroll position. For a bigger
  list, diff by id and update only the rows that changed — or let the server do the filtering and
  return HTML, which is what Chapter 28 does.

Also filter server-side with a `LIMIT`. "Debounced" is not the same as "cheap": a query that scans
50,000 rows per keystroke is still a query that scans 50,000 rows.
:::

:::pitfall Forgetting to escape user content (XSS)
This is the single most dangerous bug in web development, and it is one line long.

```js
// WRONG: task.title is user input
li.innerHTML = `<strong>${task.title}</strong>`;
```

If someone creates a task titled `<img src=x onerror="fetch('/api/tasks', {method:'DELETE'})">`,
that string becomes *markup*, the browser executes it, and it runs with the user's cookies. That
is **cross-site scripting**: your site delivered the attacker's code to your user's browser. It
reads their session, submits forms as them, and deletes their data. `innerHTML` with interpolated
user data is the bug; so is a Python f-string that drops user input straight into HTML.

Three rules, in order of preference:

1. **Use `textContent`, not `innerHTML`.** Text is text; the browser will not parse it.
   ```js
   const strong = document.createElement("strong");
   strong.textContent = task.title;
   li.append(strong);
   ```
2. **If you truly need markup, escape it.** Never write your own escaper.
   ```js
   const escapeHtml = (s) =>
     s.replace(/[&<>"']/g, (c) =>
       ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
     );
   ```
3. **Prefer letting the server render.** Jinja2, which Chapter 28 uses, **autoescapes** by
   default: `{{ task.title }}` in a template produces `&lt;img src=x ...&gt;` and the browser
   displays it as text. This is the strongest argument for server-rendered templates — escaping is
   the default, and you have to opt out with `| safe` rather than remember to opt in.

The same principle applies to every sink, not just HTML: use parameterised queries for SQL
(Chapter 19), never build shell strings from user input, and never put user data in a `href` or
`src` without checking the scheme (`javascript:` URLs are still executable).

Related performance version of the same mistake: rebuilding the entire DOM on every keystroke.
Beyond the XSS risk of `innerHTML`, replacing 500 rows on each input event destroys focus, scroll
position, and text selection. See the scenario above.
:::

## Key takeaways

- HTML describes structure with nested elements; semantic tags (`main`, `article`, `nav`) say what
  a region *is*, and `<div>` is for layout only.
- In a form, `name` is the wire format — it is the only attribute the server sees. `id` is for
  labels and `querySelector`.
- Unchecked checkboxes submit nothing, so give those fields a server-side default.
- CSS: set `box-sizing: border-box` globally, use flexbox for one-dimensional layout
  (`display:flex`, `justify-content`, `align-items`, `gap`, `flex-wrap`) and grid for
  two-dimensional, and put your palette in `:root` custom properties so dark mode is one media
  query.
- JS arrays and objects are Python lists and dicts; `map`/`filter`/`reduce` replace
  comprehensions, and template literals are f-strings.
- Use `===` not `==`, `??` for defaults, and remember `fetch` only rejects on network failure —
  check `response.ok` for 4xx and 5xx.
- Update the page with `createElement` + `textContent`, and handle dynamic elements with event
  delegation on a parent.
- `innerHTML` with user data is a cross-site scripting hole. Use `textContent`, or let Jinja2
  autoescape it for you.
- The Python backend owns rules and data; the JS frontend owns interaction; HTTP and JSON are the
  contract between them, and the DevTools Network tab is where you debug it.

## Practice

- [ ] Write `profile.html`: semantic markup for a personal profile page — `header`, `main` with
      two `section`s, `aside`, `footer`, one image with `alt`, and a link.
- [ ] Style it: `box-sizing: border-box`, a `:root` palette with a dark-mode media query, a
      flexbox `nav`, and a two-column `main`/`aside` layout that stacks below `40rem`.
- [ ] Write JS that toggles a `dark` class on `<body>` when a button is clicked, and reports the
      current state with `console.log`.
- [ ] Given `GET /api/tasks` returning a JSON array of `{id, title, done}` objects, write
      `loadTasks()` and `render()` that put them into `<ul id="task-list">` using
      `textContent`. Include error handling for a non-OK response.
- [ ] Add a form that POSTs JSON to `/api/tasks` with `event.preventDefault()`, then refreshes the
      list without reloading the page.
- [ ] Add a debounced search box (250 ms) with a stale-response guard, and verify in the Network
      tab that typing seven characters produces one request, not seven.

## Solutions

:::solution Exercise 1
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ada Lovelace</title>
    <link rel="stylesheet" href="/static/style.css">
  </head>
  <body>
    <header>
      <h1>Ada Lovelace</h1>
      <nav>
        <a href="/">Home</a>
        <a href="/notes">Notes</a>
      </nav>
    </header>

    <main>
      <section>
        <h2>About</h2>
        <p>Mathematician, and the author of the first published algorithm.</p>
      </section>
      <section>
        <h2>Selected work</h2>
        <ul>
          <li>Notes on the Analytical Engine</li>
        </ul>
      </section>
    </main>

    <aside>
      <h3>Elsewhere</h3>
      <p><a href="https://example.com">Personal site</a></p>
    </aside>

    <footer><p>&copy; 2026</p></footer>
  </body>
</html>
```
`&copy;` is an HTML entity — the escape mechanism from the table above. Semantics matter beyond
tidiness: a screen reader can jump straight to `<main>`, and search engines use the headings to
build an outline.
:::

:::solution Exercise 2
```css
*,
*::before,
*::after { box-sizing: border-box; }

:root {
  --bg: #f7f7f8;
  --surface: #ffffff;
  --text: #1c1c1f;
  --border: #e5e7eb;
  --accent: #2563eb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #101114;
    --surface: #181a1f;
    --text: #e8e8ea;
    --border: #2a2d34;
    --accent: #60a5fa;
  }
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, sans-serif;
}

header nav {
  display: flex;
  gap: 1rem;
}

.columns {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.columns main { flex: 1; }
.columns aside { width: 16rem; }

@media (max-width: 40rem) {
  .columns { flex-direction: column; }
  .columns aside { width: 100%; }
}
```
`flex: 1` on `<main>` means "take whatever `<aside>` did not", which is why the sidebar keeps its
fixed `16rem`. One media query flips the axis — no separate mobile stylesheet, no duplicated
markup.
:::

:::solution Exercise 3
```js
const button = document.querySelector("#theme-toggle");

button.addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  console.log("dark mode is now", dark);   // toggle() returns the resulting state
  button.textContent = dark ? "Light mode" : "Dark mode";
});
```
`classList.toggle` returns `true` if the class ended up present, so you can set the button label
from it. `console.log` output appears in the DevTools Console tab; pass several values
(`console.log("state", dark)`) and you can expand objects interactively.
:::

:::solution Exercise 4
```js
const list = document.querySelector("#task-list");

async function loadTasks() {
  const response = await fetch("/api/tasks");
  if (!response.ok) {
    throw new Error(`GET /api/tasks failed: ${response.status}`);
  }
  return response.json();
}

function render(tasks) {
  list.replaceChildren(
    ...tasks.map((task) => {
      const li = document.createElement("li");
      li.className = task.done ? "task done" : "task";
      li.dataset.id = String(task.id);
      li.textContent = task.title;   // textContent, so no escaping needed
      return li;
    })
  );
}

loadTasks().then(render).catch((err) => console.error(err));
```
Two things that trip people up: `fetch` resolves for `404` and `500`, so the `response.ok` check is
mandatory; and `.json()` returns a promise, so it needs its own `await`. `replaceChildren(...items)`
replaces all children in one call — the spread turns the array into arguments.
:::

:::solution Exercise 5
```js
const form = document.querySelector("#new-task");

form.addEventListener("submit", async (event) => {
  event.preventDefault();                 // no full-page reload
  const input = form.querySelector("input[name='title']");
  const title = input.value.trim();
  if (!title) return;

  const response = await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, priority: "medium" }),
  });

  if (!response.ok) {
    console.error("create failed:", response.status);
    return;
  }

  form.reset();
  render(await loadTasks());              // re-fetch and redraw
});
```
`event.preventDefault()` is the line that turns a normal form POST into an in-page update.
`Content-Type: application/json` is required or FastAPI will not parse the body. Re-fetching after
the write keeps the client and server from drifting apart — the alternative, optimistically
inserting the row, breaks the moment the server rejects it or assigns a different id.
:::

:::solution Exercise 6
```js
let requestId = 0;

function debounce(fn, delay = 250) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

async function search(query) {
  const id = ++requestId;
  const response = await fetch(`/api/tasks?q=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error(`search failed: ${response.status}`);
  const tasks = await response.json();
  if (id !== requestId) return;    // stale: a newer search is in flight
  render(tasks);
}

document
  .querySelector("#search")
  .addEventListener("input", debounce((e) => search(e.target.value), 250));
```
`clearTimeout` before `setTimeout` is the whole mechanism: each keystroke cancels the pending call,
so only the last one fires. The `requestId` guard handles the ordering problem that debouncing
does not — a slow request can still overtake a fast one. Confirm in the Network tab that you see
one request for a seven-character word, and that rapid edits leave only the newest result on
screen.
:::
