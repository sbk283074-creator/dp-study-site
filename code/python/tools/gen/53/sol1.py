"""Chapter 53 -- practice 1.

Three rendering contexts, four escapers, and the two questions that are
not the same question: did the value break out of its context, and did
the consumer read back what was written. An escaper can fail either one
on its own.
"""

import html
import json

PAYLOADS = [
    "</script><img src=x onerror=alert(1)>",
    '"+(alert(1))+"',
    "\\",
    "line1\nline2",
    "&lt;b&gt;",
    "O'Brien",
]

CONTEXTS = ["title text", "href, double-quoted", "js string"]


def esc_none(v):
    return v


def esc_html(v):
    return html.escape(v)


def esc_json(v):
    return json.dumps(v)[1:-1]


def esc_json_html(v):
    out = json.dumps(v)[1:-1]
    return (out.replace("<", "\\u003c").replace(">", "\\u003e")
               .replace("&", "\\u0026"))


ESCAPERS = [
    ("none", esc_none),
    ("html", esc_html),
    ("json", esc_json),
    ("json+<", esc_json_html),
]


def as_js_string(inserted):
    """The JS parser does not decode entities, so this is the only way to
    ask what the string literal evaluates to."""
    try:
        return json.loads('"' + inserted + '"')
    except ValueError:
        return None


def breaks(context, inserted):
    if context == "title text":
        return "<" in inserted
    if context == "href, double-quoted":
        return '"' in inserted
    return "</script" in inserted.lower() or as_js_string(inserted) is None


def survives(context, inserted, payload):
    if context == "js string":
        return as_js_string(inserted) == payload
    return html.unescape(inserted) == payload


def main():
    print(f"  contexts                            {len(CONTEXTS)}")
    print(f"  payloads                            {len(PAYLOADS)}")
    print(f"  escapers                            {len(ESCAPERS)}")
    print(f"  renders                             "
          f"{len(CONTEXTS) * len(ESCAPERS) * len(PAYLOADS)}")
    print()

    total = len(PAYLOADS)
    for heading, test in (("broke out of its context", breaks),
                          ("came back unchanged", survives)):
        print("    " + heading)
        print("    {:<22}".format("") +
              "".join("{:>9}".format(name) for name, _ in ESCAPERS))
        for context in CONTEXTS:
            row = "    {:<22}".format(context)
            for name, esc in ESCAPERS:
                n = 0
                for payload in PAYLOADS:
                    inserted = esc(payload)
                    if test is survives:
                        n += 1 if survives(context, inserted, payload) else 0
                    else:
                        n += 1 if breaks(context, inserted) else 0
                row += "{:>9}".format("%d of %d" % (n, total))
            print(row)
        print()

    print("    held and preserved the value")
    print("    {:<22}".format("") +
          "".join("{:>9}".format(name) for name, _ in ESCAPERS))
    covered = {}
    for context in CONTEXTS:
        row = "    {:<22}".format(context)
        for name, esc in ESCAPERS:
            ok = 0
            for payload in PAYLOADS:
                inserted = esc(payload)
                if not breaks(context, inserted) and survives(
                        context, inserted, payload):
                    ok += 1
            row += "{:>9}".format("%d of %d" % (ok, total))
            if ok == total:
                covered.setdefault(name, []).append(context)
        print(row)
    print()
    for name, _ in ESCAPERS:
        print("    {:<9} covers {} of {}".format(
            name, len(covered.get(name, [])), len(CONTEXTS)))
    print()

    named = [(n, covered[n]) for n, _ in ESCAPERS if n in covered]
    print("  the last table is the only one that is a verdict. a value has")
    print("  to do both things, and no escaper manages it everywhere:")
    for name, contexts in named:
        print("    {:<8} {}".format(name, ", ".join(contexts)))
    print()
    print("  `html` is the right answer for the two html contexts and the")
    print("  wrong one for the script, where it does not break out and does")
    print("  not survive either -- the browser never decodes the entities,")
    print("  so the value arrives as `&quot;`.")
    print()
    print("  `json` is the mirror image. it survives in the script, where")
    print("  the parser does understand a backslash, and it breaks out of")
    print("  the other two, which are read by an html parser that does not.")
    print("  adding the three character escapes makes it safe in the script")
    print("  -- and it is still not safe in a quoted attribute, for exactly")
    print("  the reason it was not before.")
    print()
    print("  the rule is not which escaper is strongest. it is that the")
    print("  escaper is chosen by the parser that will read the value, and")
    print("  a page that renders one value into three contexts needs three")
    print("  of them, chosen per context rather than once at the top.")


main()
