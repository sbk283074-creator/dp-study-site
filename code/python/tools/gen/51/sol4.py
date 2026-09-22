#!/usr/bin/env python3
"""Exercise 4 -- the log file that reports requests nobody made.

Every field in a log line is separated by a character the writer chose and the
attacker can supply. This script writes forty requests to a log two ways and
counts the lines that come out, the lines that no request produced, and the
addresses those lines are attributed to.
"""
REQUESTS = 40

# path, user agent
SHAPES = [
    ("/", "Mozilla/5.0"),
    ("/notes", "Mozilla/5.0"),
    ("/notes/12", "curl/8.0"),
    ("/search?q=hola", "Mozilla/5.0"),
    ("/me", "curl/8.0"),
    ("/static/app.css", "Mozilla/5.0"),
    ("/notes", "curl/8.0\n10.0.0.9 - root - GET /admin 200"),
    ("/notes/12",
     "curl/8.0\n10.0.0.9 - root - GET /admin 200\n"
     "10.0.0.9 - root - POST /users 201"),
]

REAL_IPS = ["203.0.113.7", "203.0.113.8", "198.51.100.4"]
FORGED_IP = "10.0.0.9"


def requests():
    out = []
    for i in range(REQUESTS):
        path, ua = SHAPES[i % len(SHAPES)]
        out.append((REAL_IPS[i % len(REAL_IPS)], path, ua))
    return out


def write_naive(reqs):
    return [f"{ip} - GET {path} {ua}" for ip, path, ua in reqs]


def write_escaped(reqs):
    def clean(s):
        return s.replace("\r", "\\r").replace("\n", "\\n")

    return [f"{ip} - GET {clean(path)} {clean(ua)}" for ip, path, ua in reqs]


def lines_of(records):
    out = []
    for rec in records:
        out.extend(rec.split("\n"))
    return out


def report(label, records):
    lines = lines_of(records)
    forged = [l for l in lines if l.startswith(FORGED_IP)]
    mentions = sum(l.count(FORGED_IP) for l in lines)
    print(f"  {label}")
    print(f"    requests                            {len(records):>3}")
    print(f"    lines in the file                   {len(lines):>3}")
    print(f"    lines that begin like a request     {len(forged):>3}")
    print(f"    mentions of the payload address     {mentions:>3}")
    return len(lines), len(forged)


def main():
    reqs = requests()
    hostile = [r for r in reqs if "\n" in r[2]]
    extra = sum(r[2].count("\n") for r in reqs)

    print(f"  requests                            {len(reqs):>3}")
    print(f"  requests with a newline in a field  {len(hostile):>3}")
    print(f"  newlines those requests supply      {extra:>3}")
    print()
    report("written as it arrives", write_naive(reqs))
    print()
    report("written with the separators escaped", write_escaped(reqs))

    print()
    print("  escaping the newline does not remove the payload. the text is")
    print("  still in the line and still readable. what it removes is the")
    print("  payload's ability to be a line, which is the only thing it")
    print("  needed in order to look like a request.")
    print()
    print(f"  a reader that trusts the file now sees {extra} requests from")
    print(f"  {FORGED_IP} that never happened, and none of them are unusual")
    print("  enough to notice next to the ones that did.")


if __name__ == "__main__":
    main()
