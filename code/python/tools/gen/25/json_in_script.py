"""Chapter 25 -- JSON is not JavaScript, and a script element ends at </script.

Five payloads embedded into a script element two ways: raw, and with the three
characters that can end the element replaced. The count is of payloads that
survive the trip through the parser, and of the characters json.dumps leaves
alone.
"""

import json
from html.parser import HTMLParser

PAYLOADS = [
    ("ordinary", '{"name": "ada"}'),
    ("apostrophe", '{"name": "O\'Brien"}'),
    ("closing tag", '{"name": "</script>"}'),
    ("closing tag, upper case", '{"name": "</SCRIPT>"}'),
    ("closing tag, with a space", '{"name": "</script >"}'),
]

DANGEROUS = "<>&"


class ScriptReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.script = []
        self.outside = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.inside = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside = False

    def handle_data(self, data):
        (self.script if self.inside else self.outside).append(data)


def escape(payload):
    return (payload.replace("<", "\\u003c")
                   .replace(">", "\\u003e")
                   .replace("&", "\\u0026"))


def document(payload, safe):
    """The page, and the exact body that was embedded in it."""
    body = escape(payload) if safe else payload
    return f"<script>const data = {body};</script>", body


def parse(document_text):
    reader = ScriptReader()
    reader.feed(document_text)
    return "".join(reader.script), "".join(reader.outside)


rows = []
for label, payload in PAYLOADS:
    raw_document, raw_body = document(payload, False)
    safe_document, safe_body = document(payload, True)
    raw_script, raw_outside = parse(raw_document)
    safe_script, safe_outside = parse(safe_document)
    rows.append((label,
                 raw_body in raw_script, raw_outside != "",
                 safe_body in safe_script, safe_outside != ""))

leaves_alone = [character for character in DANGEROUS
                if character in json.dumps({"name": character})]


def count(column):
    return sum(1 for row in rows if row[column])


print(f"{len(rows)} JSON payloads embedded into a script element")
print()
print(f"{'payload':<28}{'raw keeps':>11}{'raw leaks':>11}{'safe keeps':>12}"
      f"{'safe leaks':>12}")
print("-" * 74)
for label, kept, leaked, safe_kept, safe_leaked in rows:
    print(f"{label:<28}{('yes' if kept else 'no'):>11}"
          f"{('yes' if leaked else 'no'):>11}"
          f"{('yes' if safe_kept else 'no'):>12}"
          f"{('yes' if safe_leaked else 'no'):>12}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'payloads tried':<46}{len(rows):>8}")
print(f"{'payloads intact after parsing, raw':<46}{count(1):>8}")
print(f"{'payloads intact after parsing, escaped':<46}{count(3):>8}")
print(f"{'payloads that leaked text out of the element, raw':<46}{count(2):>8}")
print(f"{'payloads that leaked text out of the element, escaped':<46}"
      f"{count(4):>8}")
print(f"{'characters json.dumps leaves alone':<46}{len(leaves_alone):>8}")
print(f"{'characters the escape replaces':<46}{len(DANGEROUS):>8}")

print()
print(f"The leak row is the trap: {count(2)} of the {len(rows)} payloads end the script element early")
print("when they are embedded exactly as json.dumps produces them, and the")
print("count does not change for the capitalised form or the one with a space.")
print("All three are accepted, because an HTML tag name is case-insensitive")
print("and the close of an element may be followed by whitespace -- so a check")
print("that looks for the one exact spelling of the tag finds none of them.")
print()
print("That is not a bug in json.dumps. JSON is a data format and `<` is an")
print(f"ordinary character in it, so all {len(leaves_alone)} of the characters that matter to HTML come")
print("through untouched -- which is correct for a file and wrong for a page.")
print("The two formats agree on almost everything and disagree on exactly the")
print("characters that decide how the page is parsed.")
print()
print("So JSON that is going into HTML is a different encoding problem from")
print("JSON that is going into a file. Escape `<`, `>` and `&` after")
print("serialising -- the `\\u003c` form, so the result is still valid JSON --")
print("and the payload is data again. Better still, do not put data in a script")
print("element at all: send it as a separate request, or read it from a data")
print("attribute that the HTML escaper already handled.")
