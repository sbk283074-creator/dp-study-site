#!/usr/bin/env python3
"""Chapter 50 demo, part 1 -- the asset inventory nobody wrote down.

An asset is anything whose loss costs somebody something. A design document
names a handful. The code has more, because every table, every config file,
every log and every cache is an asset whether or not anyone wrote it down.
The gap between the two lists is the point: an asset that appears in no
document has no owner, and an asset with no owner is not being protected by
anybody in particular.

The second half is about the asset people forget hardest -- the log. A log
line is written by the code, stored on disk, shipped to a third party and
read by whoever is on call. It is the one asset nobody classifies, because
"it is only debug output".

Everything below is counted. Nothing is timed and nothing depends on the
machine.
"""

# name, where it lives, documented?, has an owner?, encrypted at rest?, in retention policy?
ASSETS = [
    ("users",           "table",  True,  True,  False, True),
    ("decks",           "table",  True,  True,  False, True),
    ("cards",           "table",  True,  True,  False, True),
    ("sessions",        "table",  False, False, False, False),
    ("password_hashes", "table",  True,  True,  True,  True),
    ("settings.env",    "config", False, False, True,  False),
    ("app.log",         "log",    False, True,  False, False),
    ("access.log",      "log",    False, True,  False, False),
    ("redis cache",     "cache",  False, False, False, False),
    ("uploads/",        "object", True,  True,  False, True),
    ("backups/",        "backup", False, True,  True,  False),
]

# column index, how the table heads it, how a failure reads
CONTROLS = [
    (2, "documented",       "not documented"),
    (3, "owned",            "not owned"),
    (4, "encrypted at rest", "not encrypted at rest"),
    (5, "retained",         "not in the retention policy"),
]

# One entry per request shape the app handles. The third field is exactly what
# the logger writes after the path -- in this app, whatever the handler got.
SHAPES = [
    ("GET",  "/health",       ""),
    ("GET",  "/decks",        "limit=20&offset=0"),
    ("GET",  "/decks/8842",   "deck_id=8842"),
    ("POST", "/login",        "email=ada@example.com&password=hunter2"),
    ("POST", "/login",        "email=grace@example.com&password=hunter2"),
    ("POST", "/register",     "email=new@example.com&password=letmein"),
    ("POST", "/decks",        "Authorization=Bearer eyJhbGciOiJIUzI1NiJ9"),
    ("GET",  "/me",           "Authorization=Bearer eyJhbGciOiJIUzI1NiJ9"),
    ("POST", "/cards",        "front=hola&back=hello"),
    ("PUT",  "/cards/12",     "card_id=12&front=hola"),
    ("GET",  "/search",       "q=spanish+verbs"),
    ("POST", "/upload",       "file=notes.pdf"),
    ("GET",  "/export",       "deck_id=8842&token=eyJhbGciOiJIUzI1NiJ9"),
    ("POST", "/reset",        "email=ada@example.com"),
    ("GET",  "/admin/users",  "email=ada@example.com"),
]

SECRET_MARKERS = ("password", "token", "authorization", "api_key", "secret")
PII_MARKERS = ("@",)
TRACE_LENGTH = 500          # one day of requests


def mark(value, markers):
    low = value.lower()
    return any(m in low for m in markers)


def line_for(shape):
    method, path, params = shape
    return f"{method} {path} {params}".rstrip()


def main():
    width = max(len(a[0]) for a in ASSETS)

    print("The assets the code has, and the four controls over each")
    print()
    print(f"  {'asset':<{width}}  {'kind':<7}  "
          + "  ".join(f"{lbl:<19}" for _, lbl, _ in CONTROLS))
    for row in ASSETS:
        name, kind = row[0], row[1]
        cells = "  ".join(f"{('yes' if row[i] else 'NO'):<19}" for i, _, _ in CONTROLS)
        print(f"  {name:<{width}}  {kind:<7}  {cells}")

    print()
    documented = [a for a in ASSETS if a[2]]
    print(f"  assets in the code                 {len(ASSETS):>3}")
    print(f"  assets in the design document      {len(documented):>3}")
    print(f"  assets nobody wrote down           {len(ASSETS) - len(documented):>3}")

    for idx, _, neg in CONTROLS:
        missing = [a[0] for a in ASSETS if not a[idx]]
        print(f"  {neg:<30} {len(missing):>3}   {', '.join(missing)}")

    # An asset is only protected if all four controls hold. Count the ones that
    # fail, and how many failures each one has -- the distribution is the story,
    # not the total.
    failures = {}
    for row in ASSETS:
        bad = sum(1 for i, _, _ in CONTROLS if not row[i])
        failures.setdefault(bad, []).append(row[0])
    print()
    print("  controls failing, per asset")
    for bad in sorted(failures):
        names = ", ".join(failures[bad])
        print(f"    {bad} of 4 failing: {len(failures[bad]):>2}  {names}")

    # ---------------------------------------------------------------- the log
    trace = [SHAPES[i % len(SHAPES)] for i in range(TRACE_LENGTH)]
    lines = [line_for(s) for s in trace]

    secret_lines = [ln for ln in lines if mark(ln, SECRET_MARKERS)]
    pii_lines = [ln for ln in lines if mark(ln, PII_MARKERS)]
    both = [ln for ln in lines if mark(ln, SECRET_MARKERS) and mark(ln, PII_MARKERS)]

    secret_shapes = [s for s in SHAPES if mark(line_for(s), SECRET_MARKERS)]
    pii_shapes = [s for s in SHAPES if mark(line_for(s), PII_MARKERS)]

    print()
    print(f"The log, over {TRACE_LENGTH} requests ({len(SHAPES)} distinct shapes, cycled)")
    print()
    print(f"  lines written                      {len(lines):>4}")
    print(f"  lines carrying a credential        {len(secret_lines):>4}"
          f"   ({len(secret_lines) / len(lines):.1%})")
    print(f"  lines carrying an email address    {len(pii_lines):>4}"
          f"   ({len(pii_lines) / len(lines):.1%})")
    print(f"  lines carrying both                {len(both):>4}")
    print()
    print(f"  distinct request shapes            {len(SHAPES):>4}")
    print(f"  shapes that leak a credential      {len(secret_shapes):>4}"
          f"   ({len(secret_shapes) / len(SHAPES):.1%} of shapes)")
    print(f"  shapes that leak an email          {len(pii_shapes):>4}")

    print()
    print("  the shapes responsible, and the lines each contributes per day")
    per_day = {}
    for i, s in enumerate(trace):
        if mark(lines[i], SECRET_MARKERS):
            key = line_for(s)
            per_day[key] = per_day.get(key, 0) + 1
    for key in sorted(per_day, key=lambda k: (-per_day[k], k)):
        print(f"    {per_day[key]:>3}/day  {key}")

    # A year of this, because the log has no retention policy and nothing rotates it.
    bytes_per_day = sum(len(ln) + 1 for ln in lines)
    cred_per_year = len(secret_lines) * 365
    bytes_per_year = bytes_per_day * 365
    print()
    print(f"  a year of this, at {TRACE_LENGTH} requests a day")
    print(f"    log written                      {bytes_per_day:>10,} B/day"
          f"   {bytes_per_year:>12,} B/year")
    print(f"    credential-bearing lines         {len(secret_lines):>10,}/day"
          f"   {cred_per_year:>12,}/year")
    print(f"    {'retention policy':<33}{'none':>10}")
    print(f"    {'encrypted at rest':<33}{'no':>10}")
    print(f"    {'owner':<33}{'nobody':>10}")


if __name__ == "__main__":
    main()
