"""Chapter 28 -- a template is a contract about missing values.

One page with five placeholders and three values supplied, rendered three ways.
The count is of placeholders left in the output, and of renderers that refuse to
produce a page at all.
"""

from string import Template

PAGE = "<h1>$title</h1><p>by $author</p><p>$body</p><p>$date</p><p>$tags</p>"
DATA = {"title": "A short note", "author": "ada", "body": "It works."}
PLACEHOLDERS = ["title", "author", "body", "date", "tags"]


def by_replace(text, data):
    for key, value in data.items():
        text = text.replace("$" + key, value)
    return text


def by_template(text, data):
    return Template(text).substitute(data)


def by_safe_template(text, data):
    return Template(text).safe_substitute(data)


def attempt(function):
    try:
        return function(PAGE, DATA), False
    except KeyError:
        return "", True


def remaining(text):
    return sum(1 for name in PLACEHOLDERS if "$" + name in text)


RENDERERS = [
    ("str.replace", by_replace),
    ("Template.substitute", by_template),
    ("Template.safe_substitute", by_safe_template),
]

rows = []
for label, function in RENDERERS:
    output, raised = attempt(function)
    rows.append((label, len(DATA), len(DATA) - remaining(output),
                 remaining(output), raised))

print(f"one page, {len(PLACEHOLDERS)} placeholders, {len(DATA)} values supplied")
print()
print(f"{'renderer':<26}{'placeholders':>13}{'replaced':>10}{'left':>6}"
      f"{'raised':>8}")
print("-" * 63)
for label, total, replaced, left, raised in rows:
    print(f"{label:<26}{len(PLACEHOLDERS):>13}{replaced:>10}{left:>6}"
          f"{('yes' if raised else 'no'):>8}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'placeholders in the template':<46}{len(PLACEHOLDERS):>8}")
print(f"{'values supplied':<46}{len(DATA):>8}")
print(f"{'renderers tried':<46}{len(rows):>8}")
print(f"{'renderers that produced a page':<46}"
      f"{sum(1 for r in rows if not r[4]):>8}")
print(f"{'renderers that raised on the first missing key':<46}"
      f"{sum(1 for r in rows if r[4]):>8}")
print(f"{'renderers that left a placeholder in the page':<46}"
      f"{sum(1 for r in rows if r[3]):>8}")

print()
print("Two of the three renderers finish, and both of them hand the reader a")
print("page with `$date` and `$tags` still in it. Nothing is logged, nothing")
print("raises, and the page is served. That is the failure mode a template")
print("system is supposed to prevent, and the reason to prefer the one that")
print("refuses: `substitute` stops at the first name it cannot find, which is")
print("noisy in development and correct in production.")
print()
print("The third renderer, `safe_substitute`, is not the safe default -- it is")
print("the deliberate choice for a value that is genuinely optional. Used as")
print("the default it is the same silent failure as `replace`, with better")
print("syntax.")
print()
print("And none of the three escapes anything. A value containing `<` is")
print("placed in the page as `<`, which is the previous chapter's problem")
print("arriving through a new door. The reason to use a real template engine")
print("is not the substitution syntax -- that is the easy part -- it is the")
print("autoescaping, which is on by default and is the only reason the")
print("templates in this chapter can be trusted with user input.")
