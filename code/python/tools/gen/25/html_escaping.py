"""Chapter 25 -- a value interpolated into HTML stops being text.

Seven strings a user can type, placed into a paragraph and into an attribute,
each time with and without html.escape. The count is of values that add markup
to the page.
"""

import html
from html.parser import HTMLParser

TEXT_TEMPLATE = "<p>Hello, {value}!</p>"
ATTR_TEMPLATE = '<input value="{value}">'

VALUES = [
    ("ada", "an ordinary name"),
    ("a & b", "an ampersand"),
    ("<b>bold</b>", "a tag"),
    ('"quoted"', "quote characters"),
    ("<script>alert(1)</script>", "a script element"),
    ("5 > 3", "a comparison"),
    ('" onfocus="alert(1)', "an attribute, closed and reopened"),
]


class Counter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = 0
        self.attributes = 0

    def handle_starttag(self, tag, attrs):
        self.tags += 1
        self.attributes += len(attrs)

    def handle_endtag(self, tag):
        self.tags += 1


def measure(document):
    counter = Counter()
    counter.feed(document)
    return counter.tags, counter.attributes


def render(template, value, escape):
    if escape:
        value = html.escape(value, quote=True)
    return template.replace("{value}", value)


base_tags, _ = measure(render(TEXT_TEMPLATE, "", False))
_, base_attributes = measure(render(ATTR_TEMPLATE, "", False))

rows = []
for value, _ in VALUES:
    raw_tags, _ = measure(render(TEXT_TEMPLATE, value, False))
    safe_tags, _ = measure(render(TEXT_TEMPLATE, value, True))
    _, raw_attributes = measure(render(ATTR_TEMPLATE, value, False))
    _, safe_attributes = measure(render(ATTR_TEMPLATE, value, True))
    rows.append((value,
                 raw_tags - base_tags, safe_tags - base_tags,
                 raw_attributes - base_attributes,
                 safe_attributes - base_attributes))


def extra(column):
    return sum(1 for row in rows if row[column] > 0)


print(f"{len(rows)} values, put into text and into an attribute")
print()
print(f"{'value':<34}{'text raw':>10}{'text safe':>11}{'attr raw':>10}"
      f"{'attr safe':>11}")
print("-" * 76)
for value, *counts in rows:
    print(f"{value:<34}{counts[0]:>10}{counts[1]:>11}{counts[2]:>10}"
          f"{counts[3]:>11}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'values tried':<46}{len(rows):>8}")
print(f"{'values that add an element, unescaped':<46}{extra(1):>8}")
print(f"{'values that add an attribute, unescaped':<46}{extra(3):>8}")
print(f"{'values that add markup anywhere, unescaped':<46}"
      f"{sum(1 for row in rows if row[1] > 0 or row[3] > 0):>8}")
print(f"{'values that add markup anywhere, escaped':<46}"
      f"{sum(1 for row in rows if row[2] > 0 or row[4] > 0):>8}")

print()
print("The two columns on the right are the ones that matter, and they are the")
print("ones people forget. Escaping for a text position is the habit everybody")
print("has; escaping for an attribute is the same function with `quote=True`,")
print("and it is the difference between a value inside the quotes and a value")
print("that closes the quotes and opens an attribute of its own.")
print()
print("The counts are small and the consequence is not. Two values here add an")
print("element, which is how a page gets rewritten; two add an attribute,")
print("which is how a script gets attached to an element that was not going to")
print("have one. Both are the same mistake -- text was put somewhere that")
print("parses -- and both are removed by the same function.")
print()
print("So the rule is about the position, not the value. There is no such")
print("thing as a safe string to interpolate: a string is safe for one context")
print("and dangerous in the next, and the same name is safe in a paragraph and")
print("not in an attribute. Escape at the point of use, with the function that")
print("knows the context, and never assemble HTML by concatenation when a")
print("templating engine will do the escaping for you.")
