#!/usr/bin/env python3
"""Chapter 51 demo, part 7 -- escaping is per-sink, so "sanitise" is not a function.

Every sink parses its input with different rules, which means the encoding
that neutralises a value in one sink is wrong in another. The word for a
function that makes a value safe for *all* of them does not exist, and this
script counts why: it builds the matrix.

Six payloads, eight sinks, seven encoders, and for each pair a test of whether
the encoded value is still dangerous in that sink. Every test is a small
structural check, so the counts are exact and nothing depends on the machine.

The last table is the interesting one. Exactly one encoder makes all eight
sinks safe, and it does it by destroying the value.
"""

PAYLOADS = [
    "<script>alert(1)</script>",
    "' OR 1=1 --",
    "$(id)",
    "../etc/passwd",
    "a\nINJECTED",
    '{"json": "value"}',
]

# ---------------------------------------------------------------- the sinks
# Each returns True when the value is still dangerous in that sink.


def html_body(v):
    return "<script" in v or "<img" in v


def html_attribute(v):
    return '"' in v


def js_string(v):
    return "'" in v or "\\" in v or "<" in v


def url_query(v):
    return "&" in v or "=" in v or "#" in v


def sql_literal(v):
    return v.count("'") % 2 == 1


def log_line(v):
    return "\n" in v or "\r" in v


def http_header(v):
    return "\n" in v or "\r" in v


def json_string(v):
    return '"' in v or "\\" in v


SINKS = [
    ("HTML body", html_body),
    ("HTML attribute", html_attribute),
    ("JavaScript string", js_string),
    ("URL query", url_query),
    ("SQL literal", sql_literal),
    ("log line", log_line),
    ("HTTP header", http_header),
    ("JSON string", json_string),
]

SHORT = {
    "HTML body": "HTMLbody",
    "HTML attribute": "HTMLattr",
    "JavaScript string": "JSstr",
    "URL query": "URLquery",
    "SQL literal": "SQLlit",
    "log line": "logline",
    "HTTP header": "HTTPhdr",
    "JSON string": "JSONstr",
}

# -------------------------------------------------------------- the encoders


def enc_none(v):
    return v


def enc_html(v):
    return (v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def enc_js(v):
    return (v.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
             .replace("<", "\\x3c"))


def enc_url(v):
    out = []
    for ch in v:
        if ch.isalnum() or ch in "-._~":
            out.append(ch)
        else:
            out.append(f"%{ord(ch):02X}")
    return "".join(out)


def enc_sql(v):
    return v.replace("'", "''")


def enc_json(v):
    return (v.replace("\\", "\\\\").replace('"', '\\"')
             .replace("\n", "\\n").replace("\r", "\\r"))


def enc_strip_newlines(v):
    return v.replace("\n", "").replace("\r", "")


ENCODERS = [
    ("none", enc_none),
    ("html_escape", enc_html),
    ("js_escape", enc_js),
    ("url_quote", enc_url),
    ("sql_double", enc_sql),
    ("json_escape", enc_json),
    ("strip_newlines", enc_strip_newlines),
]


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print(f"  sinks                              {len(SINKS):>3}")
    print(f"  encoders                           {len(ENCODERS):>3}")

    # pairs[encoder][sink] = how many payloads stay safe
    fixes = {}
    for ename, fn in ENCODERS:
        row = {}
        for sname, check in SINKS:
            safe = sum(1 for p in PAYLOADS if not check(fn(p)))
            row[sname] = safe
        fixes[ename] = row

    print()
    print(f"    {'encoder':<18}" + "".join(f"{SHORT[s]:>10}" for s, _ in SINKS))
    for ename, _ in ENCODERS:
        cells = "".join(f"{fixes[ename][s]:>10}" for s, _ in SINKS)
        print(f"    {ename:<18}{cells}")
    print(f"    {'':<18}" + "".join(f"{SHORT[s]:>10}" for s, _ in SINKS))
    print(f"    (cells are payloads out of {len(PAYLOADS)} that stay safe)")

    print()
    print("  sinks each encoder makes safe, out of " + str(len(SINKS)))
    totals = {}
    for ename, _ in ENCODERS:
        n = sum(1 for s, _ in SINKS if fixes[ename][s] == len(PAYLOADS))
        totals[ename] = n
        print(f"    {ename:<18}{n:>3}")

    universal = [e for e in totals if totals[e] == len(SINKS)]
    print()
    print(f"  encoders that make every sink safe   {len(universal)}"
          f"   {', '.join(universal) if universal else '--'}")

    # An encoder can also make a sink *less* safe than leaving the value alone.
    baseline = fixes["none"]
    print()
    print("  sinks each encoder makes worse than doing nothing")
    worse_total = 0
    for ename, _ in ENCODERS:
        if ename == "none":
            continue
        bad = [s for s, _ in SINKS if fixes[ename][s] < baseline[s]]
        if bad:
            worse_total += 1
            print(f"    {ename:<18}{len(bad)}   {', '.join(bad)}")
    print(f"    encoders that make at least one sink worse   {worse_total}")

    # Does the universal one preserve the value?
    print()
    unchanged = {ename: sum(1 for p in PAYLOADS if fn(p) == p)
                 for ename, fn in ENCODERS}

    print("  and whether each encoder returns the value unchanged")
    print(f"    {'encoder':<18}{'payloads unchanged':>19}")
    for ename, _ in ENCODERS:
        print(f"    {ename:<18}{unchanged[ename]:>19}")

    rest = {e: n for e, n in totals.items()
            if e != "none" and e not in universal}
    best = max(rest, key=lambda e: (rest[e], -unchanged[e], e))
    print()
    print(f"  the best encoder short of {universal[0]} fixes {totals[best]} of "
          f"{len(SINKS)} sinks ({best}),")
    print(f"  and rewrites {len(PAYLOADS) - unchanged[best]} of the "
          f"{len(PAYLOADS)} payloads to do it.")
    print(f"  the one that fixes all {len(SINKS)} ({universal[0]}) rewrites "
          f"every value it is given.")
    print()
    print(f"  and {worse_total} of the {len(ENCODERS) - 1} encoders that change "
          f"anything make")
    print("  at least one sink less safe than leaving the value alone, which is")
    print("  the failure mode nobody writes a test for.")


if __name__ == "__main__":
    main()
