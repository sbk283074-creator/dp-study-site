#!/usr/bin/env python3
"""Chapter 53 demo, part 1 -- escaping measured at the DOM, not at the string.

An escaping function is judged by whether the payload ends up as text. The
cheapest way to ask that question is to parse the result and look at what
elements and attributes came out, because that is what the browser will do.

Four HTML contexts, six payloads, twenty-four renders. Each render is done twice
-- once raw, once with html.escape -- and parsed. A render is broken if it
produced an element or an attribute the clean render did not have.
"""
from html import escape
from html.parser import HTMLParser


class Inventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = set()
        self.attrs = set()

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        for name, _value in attrs:
            self.attrs.add((tag, name))

    handle_startendtag = handle_starttag


CONTEXTS = [
    ("element body", "<p>{v}</p>"),
    ("attr, double", '<a href="{v}">x</a>'),
    ("attr, single", "<a href='{v}'>x</a>"),
    ("attr, unquoted", "<a href={v}>x</a>"),
]

PAYLOADS = [
    '"><b>bold</b>',
    "'><b>bold</b>",
    "</a><img src=x onerror=y>",
    "javascript:alert(1)",
    "a onmouseover=alert(1) b",
    "<b>plain</b>",
]

SAFE = "SAFE"


def inventory(fragment):
    parser = Inventory()
    parser.feed(fragment)
    parser.close()
    return parser.tags, parser.attrs


def extra(context, value, base_tags, base_attrs):
    tags, attrs = inventory(context.format(v=value))
    return sorted(tags - base_tags), sorted(attrs - base_attrs)


def main():
    print(f"  contexts                           {len(CONTEXTS):>3}")
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print(f"  renders                            "
          f"{len(CONTEXTS) * len(PAYLOADS):>3} x 2")
    print()
    print(f"    {'context':<18}{'raw':>8}{'escaped':>10}")

    raw_total = 0
    esc_total = 0
    still_broken = []
    for name, template in CONTEXTS:
        base_tags, base_attrs = inventory(template.format(v=SAFE))
        raw_here = 0
        esc_here = 0
        for payload in PAYLOADS:
            if any(extra(template, payload, base_tags, base_attrs)):
                raw_here += 1
            if any(extra(template, escape(payload, quote=True),
                         base_tags, base_attrs)):
                esc_here += 1
                still_broken.append((name, payload))
        raw_total += raw_here
        esc_total += esc_here
        print(f"    {name:<18}{raw_here:>6} of {len(PAYLOADS):<3}"
              f"{esc_here:>9} of {len(PAYLOADS):<3}")

    print()
    print(f"  renders broken raw                 {raw_total:>3} of "
          f"{len(CONTEXTS) * len(PAYLOADS)}")
    print(f"  renders broken after html.escape    {esc_total:>3} of "
          f"{len(CONTEXTS) * len(PAYLOADS)}")

    print()
    print("  still broken after escaping, with what appeared")
    for name, payload in still_broken:
        print(f"    {name:<18}{payload!r}")

    print()
    print("  html.escape turns the four characters that end a string into")
    print("  entities, and that is the right thing in a quoted attribute and")
    print("  in an element body. it does not add the quotes.")
    print()
    print("  in an unquoted attribute there is nothing to end, so the")
    print("  payload does not need a quote -- it needs a space, and a space")
    print("  is not one of the four characters an HTML escaper escapes. the")
    print("  fix for that context is not an encoder at all. it is a pair of")
    print("  quotes, and the encoder on top of them.")


if __name__ == "__main__":
    main()
