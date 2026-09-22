#!/usr/bin/env python3
"""Chapter 51 demo, part 6 -- the log is a sink like any other.

A log file is read by a person and by a parser, and both of them decide where
one record ends by looking for a newline. So a value that contains a newline
does not extend a record; it *starts a new one*, and the new record is written
in the logger's voice rather than the attacker's.

The payloads here are harmless strings. What they forge is a log line, which
is the point: the damage is to the evidence, not to the system. Sixty
requests, twelve of which carry a query that is not a query.
"""
NORMAL_QUERIES = ["q=holiday", "q=verbs", "limit=20", "sort=name", "q=hola"]

CLAIM = "2026-01-01 00:00:00 INFO auth login success user="
FORGED = "x\n" + CLAIM + "admin\n" + CLAIM + "root"

REQUESTS = 60


def build():
    out = []
    for i in range(REQUESTS):
        q = FORGED if i % 5 == 0 else NORMAL_QUERIES[i % len(NORMAL_QUERIES)]
        out.append(("GET", "/search", q))
    return out


def log_naive(text, method, path, q):
    text.append(f"{method} {path} q={q}")


def log_escaped(text, method, path, q):
    safe = q.replace("\r", "\\r").replace("\n", "\\n")
    text.append(f"{method} {path} q={safe}")


def to_file(text):
    """What lands in the file: the logger writes a string, the file has lines."""
    lines = []
    for chunk in text:
        lines.extend(chunk.split("\n"))
    return lines


def main():
    trace = build()
    hostile = [r for r in trace if "\n" in r[2]]

    naive_written = []
    for method, path, q in trace:
        log_naive(naive_written, method, path, q)

    escaped_written = []
    for method, path, q in trace:
        log_escaped(escaped_written, method, path, q)

    naive = to_file(naive_written)
    escaped = to_file(escaped_written)

    forged = [ln for ln in naive if not ln.startswith("GET ")]
    claims = [ln for ln in forged if "login success" in ln]
    forged_escaped = [ln for ln in escaped if not ln.startswith("GET ")]

    print(f"  requests made                      {REQUESTS:>3}")
    print(f"  requests carrying a newline        {len(hostile):>3}")
    print(f"  strings handed to the log          {len(naive_written):>3}")
    print(f"  the payload, as a value            {FORGED!r}")
    print()
    print(f"    {'':<24}{'lines written':>14}{'not a request':>15}"
          f"{'claiming success':>18}")
    print(f"    {'newlines written as-is':<24}{len(naive):>14}{len(forged):>15}"
          f"{len(claims):>18}")
    print(f"    {'newlines escaped':<24}{len(escaped):>14}{len(forged_escaped):>15}"
          f"{0:>18}")

    print()
    print(f"  a parser splitting on newlines sees {len(naive)} events from "
          f"{REQUESTS} requests.")
    print(f"  {len(claims)} of them record a successful login as a privileged user.")
    print()
    print("  every forged line is attributable to nobody, and the request")
    print("  that produced it is the one line in the group that looks normal.")
    print()
    print(f"  escaping the value takes the count from {len(naive)} lines to "
          f"{len(escaped)} -- one per request.")


if __name__ == "__main__":
    main()
