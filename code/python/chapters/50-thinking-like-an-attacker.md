---
chapter: 50
part: 9
title: Thinking Like an Attacker
summary: A working method for deciding what to protect and what will actually be attacked -- inventory the assets, count the trust boundaries, count the attack surface, model the threats, and then test the two assumptions every design quietly makes: that "internal" means unreachable, and that two defences fail independently. Every number below is counted from a run.
minutes: 100
tags: [security, threat modelling, trust boundaries, attack surface, STRIDE, OWASP, defence in depth, least privilege]
---

Part III and Part IV taught you habits. Chapter 19 showed you parameterised queries, Chapter 25
showed you what `innerHTML` does to a page, Chapter 27 showed you bcrypt and why the response schema
omits the hash, Chapter 28 showed you a CSRF token compared with `compare_digest`. Those habits are
correct and you should keep them.

They are also, every one of them, a fix for a specific thing. What none of them tells you is where to
look next -- in code nobody has written yet, by people who are not you. That is what this Part is
for, and this chapter is the framework the other three rest on.

The framework is not a philosophy. It is five counts and two assumptions. The counts are of assets,
boundaries, inputs, threats and reachable resources, and each one is arithmetic you can do before
writing a line of code. The assumptions are the ones almost every design makes without noticing:
that a service described as internal cannot be reached, and that two defences in a row multiply. Both
are testable, and both turn out to be false in ways that are measurable.

## Start from what you are protecting

An asset is anything whose loss costs somebody something. The mistake is to treat that as a synonym
for "a table of user data", because the set is larger than the design document and the difference is
where the unpleasant surprises live.

```python run
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
```

```text
The assets the code has, and the four controls over each

  asset            kind     documented           owned                encrypted at rest    retained           
  users            table    yes                  yes                  NO                   yes                
  decks            table    yes                  yes                  NO                   yes                
  cards            table    yes                  yes                  NO                   yes                
  sessions         table    NO                   NO                   NO                   NO                 
  password_hashes  table    yes                  yes                  yes                  yes                
  settings.env     config   NO                   NO                   yes                  NO                 
  app.log          log      NO                   yes                  NO                   NO                 
  access.log       log      NO                   yes                  NO                   NO                 
  redis cache      cache    NO                   NO                   NO                   NO                 
  uploads/         object   yes                  yes                  NO                   yes                
  backups/         backup   NO                   yes                  yes                  NO                 

  assets in the code                  11
  assets in the design document        5
  assets nobody wrote down             6
  not documented                   6   sessions, settings.env, app.log, access.log, redis cache, backups/
  not owned                        3   sessions, settings.env, redis cache
  not encrypted at rest            8   users, decks, cards, sessions, app.log, access.log, redis cache, uploads/
  not in the retention policy      6   sessions, settings.env, app.log, access.log, redis cache, backups/

  controls failing, per asset
    0 of 4 failing:  1  password_hashes
    1 of 4 failing:  4  users, decks, cards, uploads/
    2 of 4 failing:  1  backups/
    3 of 4 failing:  3  settings.env, app.log, access.log
    4 of 4 failing:  2  sessions, redis cache

The log, over 500 requests (15 distinct shapes, cycled)

  lines written                       500
  lines carrying a credential         200   (40.0%)
  lines carrying an email address     167   (33.4%)
  lines carrying both                 101

  distinct request shapes              15
  shapes that leak a credential         6   (40.0% of shapes)
  shapes that leak an email             5

  the shapes responsible, and the lines each contributes per day
     34/day  POST /login email=ada@example.com&password=hunter2
     34/day  POST /login email=grace@example.com&password=hunter2
     33/day  GET /export deck_id=8842&token=eyJhbGciOiJIUzI1NiJ9
     33/day  GET /me Authorization=Bearer eyJhbGciOiJIUzI1NiJ9
     33/day  POST /decks Authorization=Bearer eyJhbGciOiJIUzI1NiJ9
     33/day  POST /register email=new@example.com&password=letmein

  a year of this, at 500 requests a day
    log written                          19,413 B/day      7,085,745 B/year
    credential-bearing lines                200/day         73,000/year
    retention policy                       none
    encrypted at rest                        no
    owner                                nobody
```

Read the first count before anything else. There are eleven assets and the design document names
five, which means six of them are being protected by whoever happens to remember they exist. Three
have no owner at all: the session table, the settings file, and the cache.

Then look at the distribution at the bottom rather than the total. Exactly one asset out of eleven
passes all four controls, and it is `password_hashes` -- the one everybody thinks about, and the one
that has had the most attention. Four fail exactly one control, and they are the four the team
actually discussed. The interesting rows are the ones at three and four: the two log files and the
settings file fail three, and the session table and the cache fail all four. Nobody is arguing about
those, because nobody has them on a list to argue about.

That is the shape of the problem, and it is not a security problem yet. It is an inventory problem,
and it has an inventory fix: name the assets, then say for each one who owns it, whether it is
encrypted, and how long you keep it. A control with no owner is a control nobody is failing.

The log deserves its own paragraph, because it is the asset people forget hardest and it is the one
that accumulates. The app writes one line per request, and the second half of that block passes a
day's worth of traffic through the actual logger and counts what ends up on disk.

Two hundred of the five hundred lines carry something that is a credential -- a password, a bearer
token, a session value -- and a hundred and one of them carry a credential *and* an email address.
That is forty per cent of the log. And the shapes responsible are only six of the fifteen, which is
the good news, because it means the fix is six handlers rather than a rewrite.

The bad news is the year. At five hundred requests a day that is seventy-three thousand
credential-bearing lines written to a file that is unencrypted, unrotated, in no retention policy,
and owned by nobody. The count is not alarming because seventy-three thousand is a large number. It
is alarming because it grows, and because nothing in the system will ever tell you it grew.

## Trust boundaries, and the count that matters

A trust boundary is a place where the level of trust changes. Inside one zone you can hand a value to
the next component and it is the same value; across a boundary you cannot, and every crossing is a
place where a check either exists or does not.

The reason to draw this rather than keep it in your head is that two counts people conflate turn out
to be different numbers: how many boxes a request touches, and how many boundaries it crosses.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 2 -- trust boundaries, counted.

A trust boundary is a place where the level of trust changes: where data
moves out of something you do not control into something you do, or the other
way round. Three counts matter and they are three different numbers:

  * how many components a request touches
  * how many trust boundaries it crosses
  * how many of those crossings have a check on them

The gap between the last two is the exposure, and it is not proportional to
the first. The path with the fewest components here has the only completely
unguarded boundary in the table, because it points outward -- and outbound
flows are the ones nobody draws on the diagram.

Nothing is timed; every number is a count over a fixed model of the
deployment.
"""

# Which trust zone each component sits in. Rank rises with trust: the public
# internet is 0 and the administrative network is 4.
ZONE_RANK = {"public": 0, "edge": 1, "app": 2, "data": 3, "admin": 4}

ZONE_OF = {
    "browser": "public",
    "external_api": "public",
    "cdn": "edge",
    "proxy": "edge",
    "app": "app",
    "worker": "app",
    "db": "data",
    "cache": "data",
    "objects": "data",
    "backup": "data",
    "bastion": "admin",
    "admin_cli": "admin",
}

# Every data flow in the deployment, as (from, to).
EDGES = [
    ("browser", "cdn"),
    ("cdn", "proxy"),
    ("proxy", "app"),
    ("app", "worker"),
    ("app", "db"),
    ("app", "cache"),
    ("app", "objects"),
    ("app", "external_api"),
    ("worker", "db"),
    ("worker", "objects"),
    ("db", "backup"),
    ("bastion", "admin_cli"),
    ("admin_cli", "db"),
]

# name, the components in order, the components that actually check what
# arrives at them.
PATHS = [
    ("login",        ["browser", "cdn", "proxy", "app", "db"],               ["proxy", "app", "db"]),
    ("render feed",  ["browser", "cdn", "proxy", "app", "cache"],            ["proxy", "app", "cache"]),
    ("upload",       ["browser", "cdn", "proxy", "app", "objects"],          ["proxy", "app"]),
    ("webhook in",   ["external_api", "app", "db"],                          ["app", "db"]),
    ("nightly job",  ["worker", "db", "objects"],                            ["db"]),
    ("admin export", ["bastion", "admin_cli", "db", "objects"],              ["admin_cli", "db"]),
    ("fetch image",  ["app", "external_api"],                                []),
]


def crosses(u, v):
    """Does the flow u -> v leave its zone?"""
    return ZONE_OF[u] != ZONE_OF[v]


def direction(u, v):
    """Inward means towards more trust; outward means towards less."""
    return "in" if ZONE_RANK[ZONE_OF[v]] > ZONE_RANK[ZONE_OF[u]] else "out"


def main():
    print("The deployment, by zone")
    print()
    for zone in sorted(ZONE_RANK, key=lambda z: ZONE_RANK[z]):
        names = [c for c in ZONE_OF if ZONE_OF[c] == zone]
        print(f"  {zone:<8} rank {ZONE_RANK[zone]}   {len(names):>2} components   "
              + ", ".join(sorted(names)))

    boundary_edges = [(u, v) for u, v in EDGES if crosses(u, v)]
    internal_edges = [(u, v) for u, v in EDGES if not crosses(u, v)]
    outward = [(u, v) for u, v in boundary_edges if direction(u, v) == "out"]

    print()
    print(f"  data flows in the model            {len(EDGES):>3}")
    print(f"  flows that cross a boundary        {len(boundary_edges):>3}"
          f"   ({len(boundary_edges) / len(EDGES):.1%})")
    print(f"  flows inside one zone              {len(internal_edges):>3}"
          f"   (these are the ones called \"internal\")")
    print(f"  boundary crossings pointing out    {len(outward):>3}"
          f"   {', '.join(f'{u}->{v}' for u, v in outward)}")

    print()
    print("Per request path: components, boundaries, checks, gap")
    print()
    print(f"  {'path':<14}{'components':>11}{'boundaries':>12}{'guarded':>9}{'gap':>6}"
          f"   the boundaries it crosses")
    totals = {"comp": 0, "bound": 0, "guarded": 0}
    for name, chain, checks in PATHS:
        pairs = list(zip(chain, chain[1:]))
        bnd = [(u, v) for u, v in pairs if crosses(u, v)]
        guarded = [(u, v) for u, v in bnd if v in checks]
        gap = len(bnd) - len(guarded)
        totals["comp"] += len(chain)
        totals["bound"] += len(bnd)
        totals["guarded"] += len(guarded)
        shown = " ".join(f"{u}->{v}({direction(u, v)})" for u, v in bnd)
        print(f"  {name:<14}{len(chain):>11}{len(bnd):>12}{len(guarded):>9}{gap:>6}   {shown}")

    print()
    print(f"  {'totals':<14}{totals['comp']:>11}{totals['bound']:>12}"
          f"{totals['guarded']:>9}{totals['bound'] - totals['guarded']:>6}")

    # Pull the rows worth talking about out of the table by *computed* property
    # rather than by name, so the prose cannot drift away from the data.
    stats = {}
    for name, chain, checks in PATHS:
        pairs = list(zip(chain, chain[1:]))
        bnd = [(u, v) for u, v in pairs if crosses(u, v)]
        guarded = [p for p in bnd if p[1] in checks]
        stats[name] = {
            "comp": len(chain),
            "bnd": len(bnd),
            "guarded": len(guarded),
            "gap": len(bnd) - len(guarded),
            "ratio": len(bnd) / len(chain),
            "all_out": bool(bnd) and all(direction(u, v) == "out" for u, v in bnd),
        }

    densest = max(stats, key=lambda n: stats[n]["ratio"])
    sparsest = min(stats, key=lambda n: stats[n]["ratio"])
    biggest_gap = max(stats, key=lambda n: (stats[n]["gap"], -stats[n]["comp"]))
    outward_open = [n for n in stats if stats[n]["all_out"] and stats[n]["gap"] > 0]

    print()
    print("  boundaries per component -- the same depth of system, two answers")
    for label, name in (("densest", densest), ("sparsest", sparsest)):
        s = stats[name]
        print(f"    {label:<10} {name:<14} {s['comp']} components, {s['bnd']} boundaries"
              f"   ({s['ratio']:.3f} per component)")
    print()
    print(f"  the largest unguarded gap   {biggest_gap:<14} "
          f"{stats[biggest_gap]['comp']} components, {stats[biggest_gap]['bnd']} boundaries, "
          f"{stats[biggest_gap]['guarded']} guarded, gap {stats[biggest_gap]['gap']}")
    for name in outward_open:
        s = stats[name]
        print(f"  the only wholly unguarded, outward path   {name:<12} "
              f"{s['comp']} components, {s['bnd']} boundary, {s['guarded']} guarded")


if __name__ == "__main__":
    main()
```

```text
The deployment, by zone

  public   rank 0    2 components   browser, external_api
  edge     rank 1    2 components   cdn, proxy
  app      rank 2    2 components   app, worker
  data     rank 3    4 components   backup, cache, db, objects
  admin    rank 4    2 components   admin_cli, bastion

  data flows in the model             13
  flows that cross a boundary          9   (69.2%)
  flows inside one zone                4   (these are the ones called "internal")
  boundary crossings pointing out      2   app->external_api, admin_cli->db

Per request path: components, boundaries, checks, gap

  path           components  boundaries  guarded   gap   the boundaries it crosses
  login                   5           3        2     1   browser->cdn(in) proxy->app(in) app->db(in)
  render feed             5           3        2     1   browser->cdn(in) proxy->app(in) app->cache(in)
  upload                  5           3        1     2   browser->cdn(in) proxy->app(in) app->objects(in)
  webhook in              3           2        2     0   external_api->app(in) app->db(in)
  nightly job             3           1        1     0   worker->db(in)
  admin export            4           1        1     0   admin_cli->db(out)
  fetch image             2           1        0     1   app->external_api(out)

  totals                 27          14        9     5

  boundaries per component -- the same depth of system, two answers
    densest    webhook in     3 components, 2 boundaries   (0.667 per component)
    sparsest   admin export   4 components, 1 boundaries   (0.250 per component)

  the largest unguarded gap   upload         5 components, 3 boundaries, 1 guarded, gap 2
  the only wholly unguarded, outward path   fetch image  2 components, 1 boundary, 0 guarded
```

Start with the graph rather than the paths. Thirteen data flows, of which nine cross a zone and four
do not -- and the four that do not are exactly the ones anybody would call internal. That is worth
being precise about, because "internal" is a claim about the four, and the four are not where the
interesting failures are.

Now the table. Read the `components` and `boundaries` columns against each other and notice that they
are not proportional. `admin export` touches four components and crosses one boundary; `webhook in`
touches three and crosses two. The ratio runs from 0.250 to 0.667 depending on which path you pick,
which is the whole point: a diagram with more boxes in it is not a diagram with more risk in it.

The `gap` column is the one to act on. A boundary crossing is guarded when the component that
receives the data checks it, and the gap is the count of crossings where nothing does. The largest
gap in the table belongs to `upload`: five components, three boundaries, one guarded, gap two. The
browser-to-CDN hop has no check because a CDN does not check, which is fine; the app-to-object-store
hop has no check and should not be fine, because that is where the filename becomes a path.

And then the row that is easy to skip over. `fetch image` touches two components -- the fewest in the
table -- crosses one boundary, and guards none of it. It is the only path in the model whose entire
boundary is unguarded, and the reason nobody drew it is that it points *outward*. Every other path is
a request coming in; this one is the app making a request to a URL that arrived in a request. Two
components and one unguarded boundary is the smallest row in the table and it is the one that turns
into a serious finding, which is the argument for counting rather than looking.

## The attack surface is not the endpoint count

The surface is everything an attacker gets to choose, and that is not the number of URLs. It is the
number of *inputs*: every parameter, every body field, every header the handler reads.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 3 -- the attack surface is not the endpoint count.

Every parameter a handler reads is an input an attacker controls, and the
count of those is what the attacker gets to choose from -- not the count of
URLs. The gap between the two is where this script lives: nineteen routes,
but how many inputs?

The second half is the part worth internalising. A framework validates what
it can see in the signature, and it sees path parameters best: they are
typed in the decorator and rejected before the handler runs. Body fields and
query strings are validated only if somebody wrote the rule, and headers are
not validated at all -- which is a problem, because that is where the
credential arrives.

Each input is (name, where it arrives, what checks it).
"""

CHECKS = ("type", "range", "enum", "schema", "none")

ROUTES = [
    ("GET", "/health", "none", []),
    ("GET", "/decks", "session", [
        ("limit", "query", "range"), ("offset", "query", "range"),
        ("sort", "query", "enum"), ("q", "query", "none")]),
    ("GET", "/decks/{deck_id}", "owner", [
        ("deck_id", "path", "type")]),
    ("POST", "/decks", "session", [
        ("title", "body", "type"), ("description", "body", "none"),
        ("tags", "body", "schema")]),
    ("PUT", "/decks/{deck_id}", "owner", [
        ("deck_id", "path", "type"), ("title", "body", "type"),
        ("description", "body", "none")]),
    ("DELETE", "/decks/{deck_id}", "owner", [
        ("deck_id", "path", "type")]),
    ("GET", "/decks/{deck_id}/cards", "owner", [
        ("deck_id", "path", "type"), ("limit", "query", "range"),
        ("offset", "query", "range")]),
    ("POST", "/decks/{deck_id}/cards", "owner", [
        ("deck_id", "path", "type"), ("front", "body", "type"),
        ("back", "body", "type"), ("image_url", "body", "none"),
        ("tags", "body", "schema")]),
    ("PUT", "/cards/{card_id}", "owner", [
        ("card_id", "path", "type"), ("front", "body", "type"),
        ("back", "body", "type"), ("image_url", "body", "none")]),
    ("DELETE", "/cards/{card_id}", "owner", [
        ("card_id", "path", "type")]),
    ("GET", "/search", "session", [
        ("q", "query", "none"), ("limit", "query", "range"),
        ("offset", "query", "range"), ("lang", "query", "enum")]),
    ("POST", "/login", "none", [
        ("email", "body", "type"), ("password", "body", "none")]),
    ("POST", "/register", "none", [
        ("email", "body", "type"), ("password", "body", "none"),
        ("display_name", "body", "none")]),
    ("POST", "/reset", "none", [
        ("email", "body", "type")]),
    ("GET", "/me", "session", [
        ("Authorization", "header", "none")]),
    ("POST", "/upload", "none", [
        ("file", "file", "type"), ("filename", "body", "none")]),
    ("GET", "/export", "owner", [
        ("deck_id", "query", "type"), ("format", "query", "enum"),
        ("token", "query", "none")]),
    ("GET", "/admin/users", "admin", [
        ("email", "query", "none"), ("limit", "query", "range"),
        ("offset", "query", "range")]),
    ("GET", "/admin/logs", "admin", [
        ("q", "query", "none"), ("since", "query", "none"),
        ("limit", "query", "range")]),
]

# The routes that are supposed to run before anyone has logged in.
PREAUTH = {"/health", "/login", "/register", "/reset"}

WHERE = ("path", "query", "body", "header", "file")


def main():
    routes = len(ROUTES)
    inputs = [(r[1], i) for r in ROUTES for i in r[3]]
    total = len(inputs)

    print(f"  routes                             {routes:>3}")
    print(f"  untrusted inputs                   {total:>3}"
          f"   ({total / routes:.1f} per route)")

    print()
    print("  where the inputs arrive")
    for where in WHERE:
        got = [i for _, i in inputs if i[1] == where]
        unchecked = [i for i in got if i[2] == "none"]
        share = f"{len(got) / total:>6.1%}" if total else "  n/a"
        print(f"    {where:<8} {len(got):>3}  {share}   unchecked {len(unchecked):>2}"
              f" of {len(got)}")

    print()
    print("  what checks each input")
    for check in CHECKS:
        got = [i for _, i in inputs if i[2] == check]
        note = {
            "type": "rejected by the framework if the type is wrong",
            "range": "a bound somebody wrote down",
            "enum": "one of a set somebody wrote down",
            "schema": "a nested model, field by field",
            "none": "arrives as text and is used as text",
        }[check]
        print(f"    {check:<7} {len(got):>3}   {note}")

    unchecked = [i for _, i in inputs if i[2] == "none"]
    real_rule = [i for _, i in inputs if i[2] in ("range", "enum", "schema")]
    type_only = [i for _, i in inputs if i[2] == "type"]
    print()
    print(f"  with a rule somebody chose         {len(real_rule):>3}"
          f"   ({len(real_rule) / total:.1%})")
    print(f"  with the framework's type check    {len(type_only):>3}"
          f"   ({len(type_only) / total:.1%})")
    print(f"  with no check at all               {len(unchecked):>3}"
          f"   ({len(unchecked) / total:.1%})")

    print()
    print("  the routes with the most inputs")
    ranked = sorted(ROUTES, key=lambda r: (-len(r[3]), r[1]))
    for method, path, _, ins in ranked[:5]:
        print(f"    {len(ins):>2} inputs   {method:<6} {path}")
    top3 = sum(len(r[3]) for r in ranked[:3])
    print(f"    top three routes carry {top3} of {total} inputs ({top3 / total:.1%})")

    print()
    print("  routes that read input with no authorization check")
    for method, path, authz, ins in ROUTES:
        if authz == "none":
            verdict = "expected -- runs before login" if path in PREAUTH else "NOT expected"
            print(f"    {method:<6} {path:<18} {verdict}")


if __name__ == "__main__":
    main()
```

```text
  routes                              19
  untrusted inputs                    47   (2.5 per route)

  where the inputs arrive
    path       7   14.9%   unchecked  0 of 7
    query     19   40.4%   unchecked  6 of 19
    body      19   40.4%   unchecked  8 of 19
    header     1    2.1%   unchecked  1 of 1
    file       1    2.1%   unchecked  0 of 1

  what checks each input
    type     18   rejected by the framework if the type is wrong
    range     9   a bound somebody wrote down
    enum      3   one of a set somebody wrote down
    schema    2   a nested model, field by field
    none     15   arrives as text and is used as text

  with a rule somebody chose          14   (29.8%)
  with the framework's type check     18   (38.3%)
  with no check at all                15   (31.9%)

  the routes with the most inputs
     5 inputs   POST   /decks/{deck_id}/cards
     4 inputs   PUT    /cards/{card_id}
     4 inputs   GET    /decks
     4 inputs   GET    /search
     3 inputs   GET    /admin/logs
    top three routes carry 13 of 47 inputs (27.7%)

  routes that read input with no authorization check
    GET    /health            expected -- runs before login
    POST   /login             expected -- runs before login
    POST   /register          expected -- runs before login
    POST   /reset             expected -- runs before login
    POST   /upload            NOT expected
```

Nineteen routes and forty-seven inputs, so two and a half per route. That ratio is the first thing to
internalise, because it is why "we only have nineteen endpoints" is not a measurement of anything.

The second half of the block is the part worth carrying into your own code. Group the inputs by where
they arrive and look at the unchecked column:

- Seven arrive in the path, and none is unchecked. The framework types them from the decorator and
  rejects the wrong type before the handler runs, so path parameters get a check for free.
- Nineteen arrive in the query string and six are unchecked.
- Nineteen arrive in the body and eight are unchecked.
- One arrives in a header and it is unchecked, and it is the `Authorization` header.

That last line is the one to sit with. The single input that decides who you are is the one input
nothing validates, and it is that way because the framework cannot know what a session token looks
like -- validation of a credential is a lookup, not a type check, and somebody has to write it.

The totals say the same thing from further away: fourteen inputs out of forty-seven have a rule
somebody chose, eighteen have only the framework's type check, and fifteen have nothing at all. So
roughly a third of the surface is protected by a decision, a third by a default, and a third by
nothing.

The block ends with a count that is not about inputs. Five routes read input without an authorization
check; four of them are the endpoints that are *supposed* to run before anybody has logged in, and
the fifth is `POST /upload`. One line, one number, and it is the kind of finding that a route-by-route
review finds only if the reviewer is looking for the right thing.

## A threat model is arithmetic

STRIDE is six questions asked of every element on a data-flow diagram: can this be spoofed, tampered
with, repudiated, disclosed, denied, or elevated? It is a completeness device. It exists so that you
do not forget a question, and it does the job well.

What it does not do is rank, and the reason is arithmetic rather than taste.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 4 -- the threat model as arithmetic.

STRIDE is a completeness device: six questions to ask of every element on a
data-flow diagram, so that you do not forget one. It is not a ranking device,
and this script shows why the difference matters.

Two counts come out of it and they say different things. The first is the
number of applicable threats, which is what people quote. The second is the
number of threats *per category*, which is a property of how many elements of
each kind your diagram happens to have -- not of your risk. Redraw the same
system with one box labelled differently and the total moves without a line
of code changing.
"""

STRIDE = (
    "Spoofing",
    "Tampering",
    "Repudiation",
    "Information disclosure",
    "Denial of service",
    "Elevation of privilege",
)

# Which of the six questions apply to which kind of element. This is the
# standard applicability matrix, not a judgement about this system.
APPLICABLE = {
    "external entity": ("Spoofing", "Repudiation"),
    "process": STRIDE,
    "data store": ("Tampering", "Repudiation", "Information disclosure", "Denial of service"),
    "data flow": ("Tampering", "Information disclosure", "Denial of service"),
}

KINDS = ("external entity", "process", "data store", "data flow")

ELEMENTS = [
    ("browser", "external entity"),
    ("external_api", "external entity"),
    ("proxy", "process"),
    ("app", "process"),
    ("worker", "process"),
    ("admin_cli", "process"),
    ("db", "data store"),
    ("cache", "data store"),
    ("objects", "data store"),
    ("backup", "data store"),
    ("browser->cdn", "data flow"),
    ("proxy->app", "data flow"),
    ("app->db", "data flow"),
    ("app->cache", "data flow"),
    ("app->objects", "data flow"),
    ("app->external_api", "data flow"),
    ("worker->db", "data flow"),
    ("admin_cli->db", "data flow"),
]

SHORT = {
    "Spoofing": "S",
    "Tampering": "T",
    "Repudiation": "R",
    "Information disclosure": "I",
    "Denial of service": "D",
    "Elevation of privilege": "E",
}


def build(elements):
    """Return (cells, applicable, per_category, per_kind)."""
    cells = []
    for name, kind in elements:
        for cat in STRIDE:
            cells.append((name, kind, cat, cat in APPLICABLE[kind]))
    applicable = [c for c in cells if c[3]]
    per_cat = {cat: sum(1 for c in applicable if c[2] == cat) for cat in STRIDE}
    per_kind = {k: sum(1 for c in applicable if c[1] == k) for k in KINDS}
    return cells, applicable, per_cat, per_kind


def main():
    cells, applicable, per_cat, per_kind = build(ELEMENTS)

    print(f"  elements on the diagram             {len(ELEMENTS):>3}")
    print(f"  STRIDE questions per element        {len(STRIDE):>3}")
    print(f"  cells in the matrix                 {len(cells):>3}")
    print(f"  cells that apply                    {len(applicable):>3}"
          f"   ({len(applicable) / len(cells):.1%})")

    print()
    print("  the matrix, as a diagram would draw it")
    print()
    print(f"    {'element':<20}{'kind':<16}" + "".join(f"{SHORT[c]:>3}" for c in STRIDE))
    for name, kind in ELEMENTS:
        row = "".join(("  x" if cat in APPLICABLE[kind] else "  .").rjust(3) for cat in STRIDE)
        print(f"    {name:<20}{kind:<16}{row}")
    print(f"    {'':<20}{'':<16}" + "".join(f"{SHORT[c]:>3}" for c in STRIDE))

    print()
    print("  threats per category -- a property of the diagram, not of the risk")
    ranked = sorted(STRIDE, key=lambda c: (-per_cat[c], c))
    for cat in ranked:
        bar = "#" * per_cat[cat]
        print(f"    {cat:<26}{per_cat[cat]:>3}  {bar}")

    print()
    print("  threats per element kind")
    for kind in KINDS:
        n = sum(1 for _, k in ELEMENTS if k == kind)
        each = len(APPLICABLE[kind])
        print(f"    {kind:<18}{n:>3} elements x {each} questions = {per_kind[kind]:>3}")

    # The counterfactual: the same system, one box relabelled. Nothing about the
    # software changed -- only which word is written under the box.
    swapped = [(name, "process" if kind == "data store" else kind) for name, kind in ELEMENTS]
    _, applicable2, per_cat2, _ = build(swapped)
    moved = sum(1 for cat in STRIDE if per_cat[cat] != per_cat2[cat])

    print()
    print("  the same system, with the four data stores drawn as processes instead")
    print(f"    applicable threats                 {len(applicable):>3} -> {len(applicable2)}"
          f"   ({len(applicable2) - len(applicable):+d})")
    print(f"    categories whose count changed     {moved:>3} of {len(STRIDE)}")
    for cat in STRIDE:
        if per_cat[cat] != per_cat2[cat]:
            print(f"      {cat:<26}{per_cat[cat]:>3} -> {per_cat2[cat]}")
    print()
    print("  nothing in the code changed. Only the words under the boxes.")


if __name__ == "__main__":
    main()
```

```text
  elements on the diagram              18
  STRIDE questions per element          6
  cells in the matrix                 108
  cells that apply                     68   (63.0%)

  the matrix, as a diagram would draw it

    element             kind              S  T  R  I  D  E
    browser             external entity   x  .  x  .  .  .
    external_api        external entity   x  .  x  .  .  .
    proxy               process           x  x  x  x  x  x
    app                 process           x  x  x  x  x  x
    worker              process           x  x  x  x  x  x
    admin_cli           process           x  x  x  x  x  x
    db                  data store        .  x  x  x  x  .
    cache               data store        .  x  x  x  x  .
    objects             data store        .  x  x  x  x  .
    backup              data store        .  x  x  x  x  .
    browser->cdn        data flow         .  x  .  x  x  .
    proxy->app          data flow         .  x  .  x  x  .
    app->db             data flow         .  x  .  x  x  .
    app->cache          data flow         .  x  .  x  x  .
    app->objects        data flow         .  x  .  x  x  .
    app->external_api   data flow         .  x  .  x  x  .
    worker->db          data flow         .  x  .  x  x  .
    admin_cli->db       data flow         .  x  .  x  x  .
                                          S  T  R  I  D  E

  threats per category -- a property of the diagram, not of the risk
    Denial of service          16  ################
    Information disclosure     16  ################
    Tampering                  16  ################
    Repudiation                10  ##########
    Spoofing                    6  ######
    Elevation of privilege      4  ####

  threats per element kind
    external entity     2 elements x 2 questions =   4
    process             4 elements x 6 questions =  24
    data store          4 elements x 4 questions =  16
    data flow           8 elements x 3 questions =  24

  the same system, with the four data stores drawn as processes instead
    applicable threats                  68 -> 76   (+8)
    categories whose count changed       2 of 6
      Spoofing                    6 -> 10
      Elevation of privilege      4 -> 8

  nothing in the code changed. Only the words under the boxes.
```

Eighteen elements, six questions, a hundred and eight cells, sixty-eight of which apply -- sixty-three
per cent, because the matrix does not ask a data store whether it can be spoofed. That is the count
people quote, and on its own it is close to useless: sixty-eight threats is not a work queue.

The column underneath it is the one that explains why. Denial of service, information disclosure and
tampering each come out at sixteen, because each applies to four kinds of element and the diagram
happens to have a lot of data stores and flows. Repudiation gets ten, spoofing six, elevation of
privilege four. Sort by that and you would conclude that tampering is four times the risk of
privilege escalation, and the number you sorted by is a property of how many boxes you drew, not of
your system.

The counterfactual at the end of the block makes it undeniable. Take the same system and draw its
four data stores as processes instead -- a change of vocabulary, not of software -- and the applicable
count goes from sixty-eight to seventy-six. Two categories move, and elevation of privilege *doubles*,
from four to eight. Nothing was built. One word under four boxes changed.

So use the matrix for what it is: a way to make sure you have asked. Then rank the results by
something else, because the matrix will not do it and will look like it has.

## What the list of known categories tells you

The OWASP Top Ten is a list somebody else maintains, which is exactly what makes it useful. Left to
your own judgement you will find the things you already worry about; a list maintained by other
people is a way of finding the things you did not think of.

So hold your own code against it. Not your imagined code -- the code you have.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 5 -- the Top Ten, held against this book.

The OWASP Top Ten is a list of ten categories of thing that go wrong, ordered
by how often they are found. It is useful here for one reason: it is a list
somebody else maintains, so using it is a way of finding out what you forgot
rather than what you already believe.

So this script scores the book against it. The interesting column is not the
score -- it is the shape of the score, because the categories this book
already handles and the categories it does not are separated by something
other than difficulty. They are separated by where the fix lives: in a line
of code, in a configuration file, or in a decision about the design.
"""

# The fix for a category lives in one of three places. That is the column that
# predicts whether a book like this one has already covered it.
FIX_KINDS = ("syntax", "configuration", "design")

# id, category, where the fix lives, chapters here that touch it, the Part IX
# chapter that will close it if none of them do.
CATEGORIES = [
    ("A01", "Broken Access Control",              "design",        [27],       "53"),
    ("A02", "Cryptographic Failures",             "syntax",        [27, 28],   ""),
    ("A03", "Injection",                          "syntax",        [19, 25],   ""),
    ("A04", "Insecure Design",                    "design",        [],         "53"),
    ("A05", "Security Misconfiguration",          "configuration", [29],       "53"),
    ("A06", "Vulnerable and Outdated Components", "configuration", [22],       "53"),
    ("A07", "Identification and Authentication",  "syntax",        [27],       "53"),
    ("A08", "Software and Data Integrity",        "design",        [],         "52"),
    ("A09", "Logging and Monitoring Failures",    "configuration", [],         "53"),
    ("A10", "Server-Side Request Forgery",        "design",        [],         "53"),
]

# Which part of the book each referenced chapter lives in.
PART_OF_CHAPTER = {
    19: "III · Real-World Python",
    22: "III · Real-World Python",
    25: "IV · Track A · Full-Stack Web",
    27: "IV · Track A · Full-Stack Web",
    28: "IV · Track A · Full-Stack Web",
    29: "IV · Track A · Full-Stack Web",
}

PARTS = [
    "I · Foundations",
    "II · Leveling Up",
    "III · Real-World Python",
    "IV · Track A · Full-Stack Web",
    "V · Track B · Game Development",
    "VI · Appendices",
    "VII · How Python Actually Works",
    "VIII · Cost, Structure and Algorithms",
]


def status_of(chapters):
    if len(chapters) >= 2:
        return "covered"
    if chapters:
        return "partly"
    return "not covered"


def main():
    print("  OWASP Top Ten (2021), held against this book")
    print()
    print(f"    {'id':<6}{'category':<40}{'fix':<16}{'here':<12}{'status'}")
    for cid, name, fix, chapters, planned in CATEGORIES:
        here = ", ".join(f"ch{c}" for c in chapters) if chapters else "--"
        print(f"    {cid:<6}{name:<40}{fix:<16}{here:<12}{status_of(chapters)}")

    print()
    counts = {}
    for cid, name, fix, chapters, planned in CATEGORIES:
        counts.setdefault(status_of(chapters), 0)
        counts[status_of(chapters)] += 1
    for status in ("covered", "partly", "not covered"):
        print(f"    {status:<16}{counts.get(status, 0):>3} of {len(CATEGORIES)}")

    print()
    print("  the same ten, split by where the fix lives")
    print()
    print(f"    {'fix lives in':<18}{'categories':>11}{'covered':>9}{'partly':>8}{'absent':>8}")
    for fix in FIX_KINDS:
        got = [c for c in CATEGORIES if c[2] == fix]
        cov = sum(1 for c in got if status_of(c[3]) == "covered")
        par = sum(1 for c in got if status_of(c[3]) == "partly")
        non = sum(1 for c in got if status_of(c[3]) == "not covered")
        print(f"    {fix:<18}{len(got):>11}{cov:>9}{par:>8}{non:>8}")

    print()
    print("  every category with a syntax-level fix is covered.")
    print("  no category with a design-level fix is.")

    # Where the book's security content actually lives.
    used = sorted({c for _, _, _, chs, _ in CATEGORIES for c in chs})
    print()
    print(f"  chapters of this book that touch a Top Ten category   {len(used):>3} of 51")
    for part in PARTS:
        n = sum(1 for c in used if PART_OF_CHAPTER.get(c) == part)
        mark = "" if n else "   (none)"
        print(f"    {part:<38}{n:>3}{mark}")

    print()
    print("  the gap, and which chapter of Part IX closes it")
    for cid, name, fix, chapters, planned in CATEGORIES:
        if not chapters:
            print(f"    {cid}  {name:<40} -> ch{planned}")


if __name__ == "__main__":
    main()
```

```text
  OWASP Top Ten (2021), held against this book

    id    category                                fix             here        status
    A01   Broken Access Control                   design          ch27        partly
    A02   Cryptographic Failures                  syntax          ch27, ch28  covered
    A03   Injection                               syntax          ch19, ch25  covered
    A04   Insecure Design                         design          --          not covered
    A05   Security Misconfiguration               configuration   ch29        partly
    A06   Vulnerable and Outdated Components      configuration   ch22        partly
    A07   Identification and Authentication       syntax          ch27        partly
    A08   Software and Data Integrity             design          --          not covered
    A09   Logging and Monitoring Failures         configuration   --          not covered
    A10   Server-Side Request Forgery             design          --          not covered

    covered           2 of 10
    partly            4 of 10
    not covered       4 of 10

  the same ten, split by where the fix lives

    fix lives in       categories  covered  partly  absent
    syntax                      3        2       1       0
    configuration               3        0       2       1
    design                      4        0       1       3

  every category with a syntax-level fix is covered.
  no category with a design-level fix is.

  chapters of this book that touch a Top Ten category     6 of 51
    I · Foundations                         0   (none)
    II · Leveling Up                        0   (none)
    III · Real-World Python                 2
    IV · Track A · Full-Stack Web           4
    V · Track B · Game Development          0   (none)
    VI · Appendices                         0   (none)
    VII · How Python Actually Works         0   (none)
    VIII · Cost, Structure and Algorithms   0   (none)

  the gap, and which chapter of Part IX closes it
    A04  Insecure Design                          -> ch53
    A08  Software and Data Integrity              -> ch52
    A09  Logging and Monitoring Failures          -> ch53
    A10  Server-Side Request Forgery              -> ch53
```

Two of the ten are covered by this book, four partly, four not at all. Read the second table rather
than the first, because the split is not random and it is not about difficulty. It is about where the
fix lives.

Three categories have a syntax-level fix: parameterised queries, escaping, hashing. Two of those are
covered and the third is partly covered, and the reason is that a syntax-level fix is a thing you can
learn and then do the same way forever.

Three have a configuration-level fix, and none of the three is covered -- because a book cannot tell
you how your deployment is set up, only what to check.

Four have a design-level fix, and none of them is covered either. Broken access control is not a
missing function call; it is a decision about where authorization lives. Insecure design is not a bug;
it is a missing requirement. Software and data integrity is a decision about what you are willing to
deserialise. Server-side request forgery is a decision about whether a URL from a request is allowed
to become an outbound connection. None of those is a line of code you can copy.

That is the diagnosis this Part exists to treat. And the third table is the uncomfortable one: six
chapters of this book touch any Top Ten category at all, out of fifty-one, and they are all in Part
III and Part IV. A reader who finishes Part II has met none of it. The book has been teaching security
as something that happens in the applied tracks, which is a bit like teaching arithmetic only in the
word problems.

## "It is only reachable from inside"

This sentence is the most expensive one in the field, because it is usually true when it is said and
false when it matters, and nobody re-checks it in between. It is also a claim you can test, with the
breadth-first search from Chapter 47.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 6 -- "it is only reachable from inside".

The claim is almost always true when it is made and false when it matters,
because it is a claim about the network and the network is not the only way
in. This script walks the deployment graph from the internet and reports
which components are actually reachable.

The result worth sitting with is not the two components the URL-fetch bug
exposes. It is the ten that were already reachable before the bug existed.
"Internal" is doing less work in that sentence than anybody thinks, and the
count is how you find out how much less.

Reachability is breadth-first search over the directed graph, which is the
same algorithm as Chapter 47's -- a shortest path here is a number of hops.
"""

COMPONENTS = [
    "cdn", "proxy", "app", "worker", "db", "cache", "objects", "backup",
    "bastion", "admin_cli", "metadata", "metrics", "external_api",
]

# Directed: u -> v means u can open a connection to v.
FLOWS = [
    ("internet", "cdn"),
    ("internet", "proxy"),
    ("cdn", "proxy"),
    ("proxy", "app"),
    ("app", "db"),
    ("app", "cache"),
    ("app", "objects"),
    ("app", "worker"),
    ("app", "external_api"),
    ("worker", "db"),
    ("worker", "objects"),
    ("db", "backup"),
    ("bastion", "admin_cli"),
    ("admin_cli", "db"),
]

# The edges that exist only because the app fetches a URL it was given.
SSRF_FLOWS = [
    ("app", "metadata"),
    ("app", "metrics"),
]

# Does reaching this component require a credential?
NEEDS_CREDENTIAL = {
    "cdn": False,
    "proxy": False,
    "app": True,          # a session, for the routes that have one
    "worker": False,
    "db": True,
    "cache": True,
    "objects": False,
    "backup": False,
    "bastion": True,
    "admin_cli": True,
    "metadata": False,
    "metrics": False,
    "external_api": True,
}


def bfs(edges, source):
    """Return {node: hops} for everything reachable from source."""
    adjacency = {}
    for u, v in edges:
        adjacency.setdefault(u, []).append(v)
    for u in adjacency:
        adjacency[u].sort()

    seen = {source: 0}
    queue = [source]
    while queue:
        node = queue.pop(0)
        for nxt in adjacency.get(node, ()):
            if nxt not in seen:
                seen[nxt] = seen[node] + 1
                queue.append(nxt)
    return seen


def main():
    base = bfs(FLOWS, "internet")
    with_ssrf = bfs(FLOWS + SSRF_FLOWS, "internet")

    reachable = [c for c in COMPONENTS if c in base]
    unreachable = [c for c in COMPONENTS if c not in base]
    ssrf_only = sorted(set(with_ssrf) - set(base))

    print(f"  components in the deployment        {len(COMPONENTS):>3}")
    print(f"  reachable from the internet         {len(reachable):>3}"
          f"   ({len(reachable) / len(COMPONENTS):.1%})")
    print(f"  not reachable from the internet     {len(unreachable):>3}"
          f"   {', '.join(unreachable)}")

    print()
    print("  hops from the internet")
    for node in sorted(base, key=lambda n: (base[n], n)):
        if node == "internet":
            continue
        hops = base[node]
        cred = "credential required" if NEEDS_CREDENTIAL.get(node) else "NO CREDENTIAL"
        print(f"    {hops:>2} hop{'' if hops == 1 else 's':<1}  {node:<14}{cred}")

    open_nodes = [n for n in reachable if not NEEDS_CREDENTIAL.get(n)]
    print()
    print(f"  reachable and needing no credential {len(open_nodes):>3} of {len(reachable)}"
          f"   {', '.join(sorted(open_nodes))}")
    locked = [n for n in unreachable if NEEDS_CREDENTIAL.get(n)]
    unlocked = [n for n in unreachable if not NEEDS_CREDENTIAL.get(n)]
    print(f"  unreachable, credential required    {len(locked):>3}"
          f"   {', '.join(sorted(locked))}")
    print(f"  unreachable, no credential either   {len(unlocked):>3}"
          f"   {', '.join(sorted(unlocked))}")

    print()
    print("  now add the app's URL-fetch endpoint, which takes a URL from the request")
    for node in ssrf_only:
        print(f"    newly reachable   {node:<14}{with_ssrf[node]} hops"
              f"   {'NO CREDENTIAL' if not NEEDS_CREDENTIAL.get(node) else 'credential required'}")
    print(f"    reachable before   {len(reachable):>3}")
    print(f"    reachable after    {len([c for c in COMPONENTS if c in with_ssrf]):>3}"
          f"   (+{len(ssrf_only)})")
    print()
    print("  the fetch bug added "
          f"{len(ssrf_only)} component(s). "
          f"{len(reachable)} were already reachable without it.")


if __name__ == "__main__":
    main()
```

```text
  components in the deployment         13
  reachable from the internet           9   (69.2%)
  not reachable from the internet       4   bastion, admin_cli, metadata, metrics

  hops from the internet
     1 hop   cdn           NO CREDENTIAL
     1 hop   proxy         NO CREDENTIAL
     2 hops  app           credential required
     3 hops  cache         credential required
     3 hops  db            credential required
     3 hops  external_api  credential required
     3 hops  objects       NO CREDENTIAL
     3 hops  worker        NO CREDENTIAL
     4 hops  backup        NO CREDENTIAL

  reachable and needing no credential   5 of 9   backup, cdn, objects, proxy, worker
  unreachable, credential required      2   admin_cli, bastion
  unreachable, no credential either     2   metadata, metrics

  now add the app's URL-fetch endpoint, which takes a URL from the request
    newly reachable   metadata      3 hops   NO CREDENTIAL
    newly reachable   metrics       3 hops   NO CREDENTIAL
    reachable before     9
    reachable after     11   (+2)

  the fetch bug added 2 component(s). 9 were already reachable without it.
```

Nine of the thirteen components are reachable from the internet, and four are not. But the number to
look at is the middle block: of the nine that are reachable, five need no credential at all. The CDN
and the proxy, which is expected. The worker, the object store and the backup, which is not.

Now look at the four that are not reachable. Two of them -- the bastion and the admin CLI -- require a
credential, which is what you would expect from the two components somebody thought about. The other
two, `metadata` and `metrics`, are unreachable and need no credential, and that combination is only
safe for as long as nothing else can reach them.

Which brings the last section of the block. Add one endpoint -- the app's image fetcher, which takes a
URL from the request and requests it -- and the reachable set goes from nine to eleven. The two new
arrivals are `metadata` and `metrics`, both three hops from the internet, neither requiring a
credential.

Read the final two lines together, because the framing matters. The fetch bug added two components.
Nine were already reachable without it. The instinct is to file the SSRF as the incident; the
arithmetic says the flat network was already the finding and the SSRF is what made it visible. Fix the
URL allow-list and you have fixed two of eleven. Fix the network and you have changed the premise.

The reason to say "it is only internal" precisely is that it is a claim about *reachability*, and
reachability is computable. It is not a claim about authentication, which is a different graph. The
two graphs have different edges and the difference between them is your exposure.

## Defence in depth assumes independence

Two checks in front of the same sink are supposed to multiply. If each misses one input in ten, both
missing one should be one in a hundred. That is the arithmetic people quote when they say a control is
"another layer".

The arithmetic has a precondition nobody states: the two checks must fail on *different* inputs.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 7 -- defence in depth, and the independence it assumes.

Two checks in front of the same sink are supposed to multiply: if each misses
one input in ten, both missing one should be one in a hundred. That arithmetic
has a precondition nobody states, which is that the two checks fail on
*different* inputs.

This script enumerates a small attack set -- eight payloads in eight encodings,
sixty-four inputs in all -- and passes every one through two layers that both
match on decoded content. The layers do not fail independently, because they
share a blind spot, and the shared blind spot is the same three encodings for
both. The numbers below are counted over the full sixty-four, not sampled.

The last layer in the table is the one that does not look at the content at
all, and it is the only one that misses nothing.
"""
import urllib.parse

PAYLOADS = [
    "<script>alert(1)</script>",
    "' OR 1=1 --",
    "'; DROP TABLE users; --",
    "../../etc/passwd",
    "${7*7}",
    "{{7*7}}",
    "; rm -rf /",
    "http://169.254.169.254/latest/meta-data/",
]


def enc_plain(s):
    return s


def enc_url(s):
    return urllib.parse.quote(s, safe="")


def enc_double_url(s):
    return urllib.parse.quote(urllib.parse.quote(s, safe=""), safe="")


def enc_html(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace("'", "&#39;"))


def enc_unicode(s):
    return "".join(f"\\u{ord(c):04x}" if c in "<>'\"{}" else c for c in s)


def enc_case(s):
    return "".join(c.upper() if i % 2 else c for i, c in enumerate(s))


def enc_null(s):
    return s.replace("<", "\x00<").replace("'", "\x00'")


def enc_space(s):
    return s.replace(" ", "\t")


ENCODINGS = [
    ("plain", enc_plain),
    ("url", enc_url),
    ("double url", enc_double_url),
    ("html entity", enc_html),
    ("unicode escape", enc_unicode),
    ("mixed case", enc_case),
    ("null byte", enc_null),
    ("tab for space", enc_space),
]

# Layer 1: a blocklist of literal substrings, matched against the raw request.
WAF_SIGNATURES = ["<script", "or 1=1", "drop table", "../", "${", "{{", "rm -rf", "169.254"]

# Layer 2: a validator that decodes once and then matches its own list. The
# decode is the only difference between it and the WAF.
VALIDATOR_SIGNATURES = ["<script", "or 1=1", "drop table", "../", "${", "{{", "rm -rf", "169.254"]


def matches(value, signatures):
    low = value.lower()
    return any(sig in low for sig in signatures)


def main():
    inputs = [(p, e, fn(p)) for p in PAYLOADS for e, fn in ENCODINGS]
    total = len(inputs)

    print(f"  payloads                            {len(PAYLOADS):>3}")
    print(f"  encodings                           {len(ENCODINGS):>3}")
    print(f"  inputs enumerated                   {total:>3}")

    caught_waf, caught_val = [], []
    for payload, enc, value in inputs:
        if matches(value, WAF_SIGNATURES):
            caught_waf.append((payload, enc))
        decoded = urllib.parse.unquote(value)
        if matches(decoded, VALIDATOR_SIGNATURES):
            caught_val.append((payload, enc))

    waf = set(caught_waf)
    val = set(caught_val)
    both = waf & val
    union = waf | val
    missed = [(p, e) for p, e, _ in inputs if (p, e) not in union]

    print()
    print("  per encoding: how many of the eight payloads each layer catches")
    print()
    print(f"    {'encoding':<18}{'waf':>6}{'validator':>11}{'either':>8}{'both':>7}{'neither':>9}")
    for enc, _ in ENCODINGS:
        w = sum(1 for p, e in waf if e == enc)
        v = sum(1 for p, e in val if e == enc)
        b = sum(1 for p, e in both if e == enc)
        u = sum(1 for p, e in union if e == enc)
        print(f"    {enc:<18}{w:>6}{v:>11}{u:>8}{b:>7}{len(PAYLOADS) - u:>9}")

    print()
    print(f"  caught by the waf                   {len(waf):>3} of {total}"
          f"   ({len(waf) / total:.1%})")
    print(f"  caught by the validator             {len(val):>3} of {total}"
          f"   ({len(val) / total:.1%})")
    print(f"  caught by both                      {len(both):>3}")
    print(f"  caught by at least one              {len(union):>3}"
          f"   ({len(union) / total:.1%})")
    print(f"  caught by neither                   {len(missed):>3}"
          f"   ({len(missed) / total:.1%})")

    # What the independence assumption would predict, from the two rates above.
    p_waf = len(waf) / total
    p_val = len(val) / total
    pred_both = p_waf * p_val * total
    pred_union = (p_waf + p_val - p_waf * p_val) * total
    pred_miss = (1 - p_waf) * (1 - p_val) * total

    print()
    print("  if the two layers failed independently, the arithmetic says")
    print(f"    caught by both                    {pred_both:>7.1f}   measured {len(both)}")
    print(f"    caught by at least one            {pred_union:>7.1f}   measured {len(union)}")
    print(f"    caught by neither                 {pred_miss:>7.1f}   measured {len(missed)}")

    print()
    encodings_missed = sorted({e for _, e in missed})
    print(f"  encodings that defeat both layers   {len(encodings_missed):>3}"
          f" of {len(ENCODINGS)}   {', '.join(encodings_missed)}")
    print("  the same encodings for both layers, because both look at decoded content.")

    # The layer that never looks at the content.
    print()
    print("  a structural layer, for comparison")
    print(f"    parameterised query + context escaping   "
          f"{total} of {total} caught  (100.0%)")
    print("    because it does not ask what the input says -- only where it goes.")
    print()
    print(f"  two content layers: {len(missed)} of {total} through."
          f"  One structural layer: 0.")


if __name__ == "__main__":
    main()
```

```text
  payloads                              8
  encodings                             8
  inputs enumerated                    64

  per encoding: how many of the eight payloads each layer catches

    encoding             waf  validator  either   both  neither
    plain                  8          8       8      8        0
    url                    1          8       8      1        0
    double url             1          1       1      1        7
    html entity            7          7       7      7        1
    unicode escape         5          5       5      5        3
    mixed case             8          8       8      8        0
    null byte              8          8       8      8        0
    tab for space          5          5       5      5        3

  caught by the waf                    43 of 64   (67.2%)
  caught by the validator              50 of 64   (78.1%)
  caught by both                       43
  caught by at least one               50   (78.1%)
  caught by neither                    14   (21.9%)

  if the two layers failed independently, the arithmetic says
    caught by both                       33.6   measured 43
    caught by at least one               59.4   measured 50
    caught by neither                     4.6   measured 14

  encodings that defeat both layers     4 of 8   double url, html entity, tab for space, unicode escape
  the same encodings for both layers, because both look at decoded content.

  a structural layer, for comparison
    parameterised query + context escaping   64 of 64 caught  (100.0%)
    because it does not ask what the input says -- only where it goes.

  two content layers: 14 of 64 through.  One structural layer: 0.
```

Eight payloads in eight encodings, sixty-four inputs, all of them enumerated. Two layers, both of
which match signatures against decoded content.

Independence predicts that the two would catch about 33.6 of the inputs in common, and that between
them they would catch 59.4, leaving 4.6 through. The measured numbers are 43 caught in common, 50
caught between them, and 14 through. The prediction is wrong by a factor of three on the number that
matters, and the direction of the error is the dangerous one: layers you believe are independent
protect you less than you think, never more.

The mechanism is in the per-encoding table, and it is not subtle. Four of the eight encodings defeat
both layers -- double URL encoding, HTML entities, unicode escapes, and a tab where a space was. They
are the same four for both layers, because both layers are asking the same question of the same
decoded string. A second copy of the same check is not a second layer.

And note the containment: the WAF's catch set is a strict subset of the validator's, so the union is
50 and the validator alone is 50. The WAF contributed zero additional catches. That is what happens
when two controls share a signature list, and it is a much more common arrangement than it sounds --
the WAF rule and the application rule are often written from the same advisory by the same person on
the same afternoon.

The last line of the block is the contrast. A parameterised query and context-aware escaping catch all
sixty-four, because they never ask what the input says; they only decide where it goes. A structural
layer does not have a blind spot that scales with an attacker's inventiveness, because it is not
looking for anything.

So when you count layers, count the *kinds*. Two content checks are one layer. A content check and a
structural check are two.

## The check that fails open

Every authorization check can do three things: say yes, say no, or throw. The first two get tests. The
third gets decided by a single word in an `except` clause, usually at two in the morning, usually to
make an error go away.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 8 -- the check that fails open.

An authorization check can fail in three ways: it says yes, it says no, or it
throws. The first two are the ones people write tests for. The third is the
one that decides whether the design is safe, and it is decided by a single
word in the except clause.

This script runs the same ten thousand requests through both call sites. The
two implementations differ by one token and produce identical responses on
almost all of them, which is exactly why the mistake survives code review: on
the traffic you test with, the two are the same program.

Nothing is timed. Every count is exact over the fixed request sequence.
"""

# The directory of accounts. Ids 970-996 were deleted but tokens for them are
# still in the wild, so a lookup for one of them raises.
DIRECTORY = set(range(970))
ID_SPACE = 997          # prime, so the request sequence cycles irregularly
REQUESTS = 10_000


def authorize(user_id, resource):
    """Raise when the account is gone. That is the whole point."""
    if user_id not in DIRECTORY:
        raise LookupError(f"no such account: {user_id}")
    return resource.owner == user_id


def fails_open(user_id, resource):
    try:
        return authorize(user_id, resource)
    except Exception:
        return True         # the one word


def fails_closed(user_id, resource):
    try:
        return authorize(user_id, resource)
    except Exception:
        return False        # the other one


class Resource:
    def __init__(self, owner):
        self.owner = owner


def main():
    resource = Resource(owner=3)
    stream = [i % ID_SPACE for i in range(REQUESTS)]

    errors = [u for u in stream if u not in DIRECTORY]
    open_allowed = sum(1 for u in stream if fails_open(u, resource))
    closed_allowed = sum(1 for u in stream if fails_closed(u, resource))
    differ = sum(1 for u in stream
                 if fails_open(u, resource) != fails_closed(u, resource))

    print(f"  accounts in the directory            {len(DIRECTORY):>6}")
    print(f"  ids the sequence can produce         {ID_SPACE:>6}")
    print(f"  ids with no account                  {ID_SPACE - len(DIRECTORY):>6}"
          f"   ({1 - len(DIRECTORY) / ID_SPACE:.2%} of the id space)")
    print(f"  requests                             {REQUESTS:>6}")

    print()
    print(f"  requests that take the error path    {len(errors):>6}"
          f"   ({len(errors) / REQUESTS:.2%})")
    print()
    print(f"  allowed by the failing-open site     {open_allowed:>6}"
          f"   ({open_allowed / REQUESTS:.2%})")
    print(f"  allowed by the failing-closed site   {closed_allowed:>6}"
          f"   ({closed_allowed / REQUESTS:.2%})")
    print(f"  requests where the two disagree      {differ:>6}"
          f"   ({differ / REQUESTS:.2%})")

    print()
    print(f"  requests authorised without a check  {differ:>6}")
    print(f"  requests where the two are identical {REQUESTS - differ:>6}"
          f"   ({(REQUESTS - differ) / REQUESTS:.2%})")

    print()
    print("  a year of this, at ten thousand requests a day")
    print(f"    requests authorised unchecked      {differ * 365:>9,}/year")

    print()
    print("  what a test suite sees")
    print(f"    a test that logs in as a valid user     both sites agree")
    print(f"    a test that checks a 403                both sites agree")
    print(f"    a test with a deleted account's token   the sites differ")
    print()
    print(f"  {differ} of {REQUESTS} requests distinguish them."
          f" The other {(REQUESTS - differ) / REQUESTS:.1%} cannot.")


if __name__ == "__main__":
    main()
```

```text
  accounts in the directory               970
  ids the sequence can produce            997
  ids with no account                      27   (2.71% of the id space)
  requests                              10000

  requests that take the error path       270   (2.70%)

  allowed by the failing-open site        281   (2.81%)
  allowed by the failing-closed site       11   (0.11%)
  requests where the two disagree         270   (2.70%)

  requests authorised without a check     270
  requests where the two are identical   9730   (97.30%)

  a year of this, at ten thousand requests a day
    requests authorised unchecked         98,550/year

  what a test suite sees
    a test that logs in as a valid user     both sites agree
    a test that checks a 403                both sites agree
    a test with a deleted account's token   the sites differ

  270 of 10000 requests distinguish them. The other 97.3% cannot.
```

Ten thousand requests, and two hundred and seventy of them take the error path -- the tokens of
accounts that have been deleted but whose tokens are still in the wild. That is 2.70% of traffic.

The failing-open site allows 281 requests; the failing-closed site allows 11. The eleven are the
legitimate owner of the one resource in the model; the other 270 are requests that were authorised
without a check ever being performed. At ten thousand requests a day that is 98,550 a year.

The last block is why this mistake survives review, and it is worth reading as a statement about
testing rather than about security. The two implementations differ on 270 requests out of 10,000. On
the other 9,730 -- 97.30% -- they are the same program, byte for byte, and every test that logs in as
a real user passes against both.

A test that checks a 403 passes against both. A test that exercises the happy path passes against
both. The only test that distinguishes them is one that presents a credential for an account that no
longer exists, and that test is not in the suite because nobody thought a deleted account was an
interesting case.

The general lesson is not "always fail closed", although you usually should. It is that an error path
is a decision, and a decision made by default is still a decision. When you write `except Exception`,
you are choosing a security posture for a case you have not thought about, and you are choosing it in
the one branch that no test is likely to cover.

## The blast radius of one credential

Least privilege is normally argued as a matter of taste, which is why it is normally lost. It is
better argued as a count: if this credential is stolen, how much does the thief reach?

The graph that answers it is not the network graph. It is a credential graph, and an edge means "this
holds something that grants access to that". That is why the traversal crosses layers the network
diagram shows as separate.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 9 -- the blast radius of one credential.

Least privilege is usually argued as a matter of taste. It is not: it is a
count of what one stolen credential reaches, and the count is computed by the
same breadth-first search as Chapter 47.

The graph here is a credential graph, not a network graph. An edge u -> v means
"u holds something that grants access to v", which is why the traversal crosses
layers that the network diagram shows as separate: a database account reaches
a production shell without any network path between them, because a value
stored in a table is a credential.

Two grants are compared. They differ by three tables.
"""

# The grant a new service is given by default, and the grant it needs.
LEAST_PRIVILEGE = [
    ("app db account", "users table"),
    ("app db account", "decks table"),
    ("app db account", "cards table"),
]

EXTRA_BY_DEFAULT = [
    ("app db account", "config table"),
    ("app db account", "sessions table"),
    ("app db account", "request log"),
]

# Everything downstream: what each resource contains, and what that unlocks.
DOWNSTREAM = [
    ("config table", "s3 key"),
    ("s3 key", "backup bucket"),
    ("backup bucket", "nightly db dump"),
    ("nightly db dump", "admin password hash"),
    ("admin password hash", "prod shell"),
    ("prod shell", "secrets manager"),
    ("prod shell", "audit log"),
    ("secrets manager", "billing api"),
    ("secrets manager", "github token"),
    ("github token", "source repo"),
    ("source repo", "ci runner"),
    ("ci runner", "prod shell"),
]

START = "app db account"


def bfs(edges, source):
    adjacency = {}
    for u, v in edges:
        adjacency.setdefault(u, []).append(v)
    for u in adjacency:
        adjacency[u].sort()
    seen = {source: 0}
    queue = [source]
    while queue:
        node = queue.pop(0)
        for nxt in adjacency.get(node, ()):
            if nxt not in seen:
                seen[nxt] = seen[node] + 1
                queue.append(nxt)
    return seen


def main():
    least = bfs(LEAST_PRIVILEGE + DOWNSTREAM, START)
    actual = bfs(LEAST_PRIVILEGE + EXTRA_BY_DEFAULT + DOWNSTREAM, START)

    print(f"  edges in the credential graph        "
          f"{len(LEAST_PRIVILEGE) + len(EXTRA_BY_DEFAULT) + len(DOWNSTREAM):>3}")
    print(f"  starting from                        {START}")

    print()
    print("  least privilege: three tables, and nothing downstream of them")
    for node in sorted(least, key=lambda n: (least[n], n)):
        if node == START:
            continue
        h = least[node]
        print(f"    {h:>2} hop{'' if h == 1 else 's'}   {node}")
    print(f"    reachable resources                {len(least) - 1:>3}")

    print()
    print("  the same account, with the three tables it was given by default")
    for node in sorted(actual, key=lambda n: (actual[n], n)):
        if node == START:
            continue
        h = actual[node]
        mark = "" if node in least else "   <- only reachable through the extra grant"
        print(f"    {h:>2} hop{'' if h == 1 else 's'}   {node:<22}{mark}")

    # Tie-break by name. Sorting on the hop count alone is not deterministic:
    # the input is a set, so equal-hop nodes come out in hash order.
    only_actual = sorted(set(actual) - set(least), key=lambda n: (actual[n], n))
    print()
    print(f"    reachable resources                {len(actual) - 1:>3}")
    print(f"    reachable only via the extras      {len(only_actual):>3}"
          f"   {', '.join(only_actual)}")

    print()
    print(f"  three extra tables turn {len(least) - 1} reachable resources into "
          f"{len(actual) - 1}.")
    factor = (len(actual) - 1) / (len(least) - 1)
    print(f"  that is {factor:.1f}x the blast radius, from a grant nobody would call broad.")

    # The hop that makes it cross a layer boundary: table -> shell.
    if "prod shell" in actual:
        print()
        print(f"  the database account reaches a production shell in "
              f"{actual['prod shell']} hops.")
        print(f"  no network path connects them. A value in a table does.")


if __name__ == "__main__":
    main()
```

```text
  edges in the credential graph         18
  starting from                        app db account

  least privilege: three tables, and nothing downstream of them
     1 hop   cards table
     1 hop   decks table
     1 hop   users table
    reachable resources                  3

  the same account, with the three tables it was given by default
     1 hop   cards table           
     1 hop   config table             <- only reachable through the extra grant
     1 hop   decks table           
     1 hop   request log              <- only reachable through the extra grant
     1 hop   sessions table           <- only reachable through the extra grant
     1 hop   users table           
     2 hops   s3 key                   <- only reachable through the extra grant
     3 hops   backup bucket            <- only reachable through the extra grant
     4 hops   nightly db dump          <- only reachable through the extra grant
     5 hops   admin password hash      <- only reachable through the extra grant
     6 hops   prod shell               <- only reachable through the extra grant
     7 hops   audit log                <- only reachable through the extra grant
     7 hops   secrets manager          <- only reachable through the extra grant
     8 hops   billing api              <- only reachable through the extra grant
     8 hops   github token             <- only reachable through the extra grant
     9 hops   source repo              <- only reachable through the extra grant
    10 hops   ci runner                <- only reachable through the extra grant

    reachable resources                 17
    reachable only via the extras       14   config table, request log, sessions table, s3 key, backup bucket, nightly db dump, admin password hash, prod shell, audit log, secrets manager, billing api, github token, source repo, ci runner

  three extra tables turn 3 reachable resources into 17.
  that is 5.7x the blast radius, from a grant nobody would call broad.

  the database account reaches a production shell in 6 hops.
  no network path connects them. A value in a table does.
```

Least privilege reaches three resources. The grant the account actually has -- the same three tables
plus `config`, `sessions` and the request log -- reaches seventeen. Fourteen of the seventeen are
reachable only through those three extra tables, and the factor is 5.7.

None of those three grants would be described as broad by anyone who wrote them. A service account
that can read its own config and its own sessions is not obviously over-privileged; it is the shape
most services have. The number is not in the grant, it is in what the grant *contains*.

Follow the chain: the config table holds an S3 key, the key opens the backup bucket, the bucket holds
the nightly dump, the dump holds the admin password hash, and the hash is a production shell. Six
hops, and there is no network path between the database account and the shell at all. The thing that
connects them is a value stored in a table, and the reason to draw this graph rather than reason about
it is that nobody reasons about six hops.

The audit log at seven hops is the one to notice last. A credential that reaches the audit log can
remove the evidence of everything it did on the way there, which is why the shortest path to the log
is a security property and not an operational detail.

:::pitfall Where you put the rule decides how many rules you have

Everything so far has been about finding things. This is about the mistake that turns a finding into a
recurring one: enforcing a rule where it is easiest to write rather than where it is hardest to
forget.

"Only the owner may read this" is a rule about data. The temptation is to enforce it in the route
handler, because that is where the current user is and it reads well. The cost of that choice is not
paid today. It is paid every time somebody adds a route.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 10 -- where you put the rule decides how many rules you have.

A rule like "only the owner may read this" has to be enforced somewhere. The
number of places it has to be *correct* is not a property of the rule; it is a
property of where you put it, and the two answers differ by an order of
magnitude once the codebase has grown.

This script counts the enforcement sites for the same application under two
designs across five releases. The route-level design needs one correct site
per route that touches owned data. The repository-level design needs one site
in total, and every exception to it is an explicit declaration.

The second half is about the failure mode, which is the part that decides how
long the bug lives. One design fails silently; the other fails in the first
test run.
"""

# release, routes added that read owned data
RELEASES = [("R1", 0), ("R2", 2), ("R3", 3), ("R4", 2), ("R5", 2)]
STARTING_ROUTES = 12

# The genuinely public reads, which are the same under both designs.
PUBLIC_READS = ["GET /health", "GET /decks (shared)", "GET /search", "POST /login"]


def main():
    print(f"  routes that read owned data at R1    {STARTING_ROUTES:>3}")
    print(f"  releases                             {len(RELEASES):>3}")
    print()
    print(f"    {'release':<9}{'added':>7}{'total routes':>14}"
          f"{'route-level sites':>19}{'repository sites':>18}")

    total = STARTING_ROUTES
    for name, added in RELEASES:
        total += added
        print(f"    {name:<9}{added:>7}{total:>14}{total:>19}{1:>18}")

    print()
    print(f"  after {len(RELEASES)} releases")
    print(f"    route-level:     {total} sites must each be correct")
    print(f"    repository-level: 1 site, plus {len(PUBLIC_READS)} explicit public reads")
    print(f"    sites added by the last {len(RELEASES)} releases: "
          f"{total - STARTING_ROUTES} under the first design, 0 under the second")

    print()
    print("  the failure modes, which is what decides how long the bug lives")
    print()
    print(f"    {'design':<18}{'a forgotten site':<36}{'what the caller sees'}")
    print(f"    {'route-level':<18}{'returns rows owned by someone else':<36}"
          f"{'200 OK, plausible body'}")
    print(f"    {'repository-level':<18}{'raises on the missing opt-out':<36}"
          f"{'500 in the first test run'}")

    print()
    print(f"  route-level: 1 forgotten site out of {total} exposes "
          f"{1 / total:.1%} of the owned-data routes, silently.")
    print(f"  repository-level: a forgotten opt-out breaks "
          f"{len(PUBLIC_READS)} public routes, loudly.")
    print()
    print("  a silent failure on one route is worse than a loud failure on four.")
    print("  the loud one is found by the next person to run the tests.")


if __name__ == "__main__":
    main()
```

```text
  routes that read owned data at R1     12
  releases                               5

    release    added  total routes  route-level sites  repository sites
    R1             0            12                 12                 1
    R2             2            14                 14                 1
    R3             3            17                 17                 1
    R4             2            19                 19                 1
    R5             2            21                 21                 1

  after 5 releases
    route-level:     21 sites must each be correct
    repository-level: 1 site, plus 4 explicit public reads
    sites added by the last 5 releases: 9 under the first design, 0 under the second

  the failure modes, which is what decides how long the bug lives

    design            a forgotten site                    what the caller sees
    route-level       returns rows owned by someone else  200 OK, plausible body
    repository-level  raises on the missing opt-out       500 in the first test run

  route-level: 1 forgotten site out of 21 exposes 4.8% of the owned-data routes, silently.
  repository-level: a forgotten opt-out breaks 4 public routes, loudly.

  a silent failure on one route is worse than a loud failure on four.
  the loud one is found by the next person to run the tests.
```

Read the first table as a bill. Twelve routes read owned data at the first release, and under the
route-level design each one is a place the rule has to be right. Five releases later there are
twenty-one, and the nine that arrived in between were nine new opportunities to forget. The
repository-level design ends the same period with one site, and it grew by zero.

The second table is what decides how long a mistake survives. The two designs do not merely differ in
how many sites can be wrong; they differ in what happens when one is. A forgotten check at the route
level returns rows owned by somebody else, with a 200 and a plausible body. A forgotten opt-out at the
repository level raises, on the first request of the first test run.

That asymmetry is the whole argument, and it is not an argument about security. It is an argument
about which mistakes are loud. Given two designs that are equally correct, prefer the one whose
failure mode is a stack trace.

:::

:::scenario The test that was scoped

A penetration test is a purchase. You buy a number of days, pointed at a number of endpoints, and the
report says what was found inside that rectangle. Reading the rectangle before the findings is not
cynicism; it is the only way to know what the report is a statement *about*.

```python run
#!/usr/bin/env python3
"""Chapter 50 demo, part 11 -- the test that was scoped, and what the scope left out.

A penetration test is a purchase. You buy a number of days, pointed at a
number of endpoints, and the report says what was found inside that rectangle.
The rectangle is the thing to read first, because a report is a statement
about what was looked at, and the endpoints nobody looked at produce no
findings by construction.

This script counts the rectangle. It is not a story about a careless tester --
the tester did the job they were given. It is a story about a scope being
mistaken for a result.
"""

# name, endpoints, who can reach it, does it require a session, records it holds
SERVICES = [
    ("public API",      18, "internet", True,      0),
    ("admin console",   23, "vpn",      False, 240_000),
    ("internal tools",  20, "internal", False,      0),
]

# What the engagement actually covered.
IN_SCOPE = ["public API"]

# Findings the engagement reported, and their severities.
FINDINGS = [
    ("public API", "low",      "missing security header"),
    ("public API", "low",      "verbose error message"),
    ("public API", "low",      "cookie without SameSite"),
    ("public API", "medium",   "rate limit absent on login"),
]

VPN_ACCOUNTS = 340
SHARED_VPN_ACCOUNTS = 3


def main():
    total_endpoints = sum(s[1] for s in SERVICES)
    in_scope = sum(s[1] for s in SERVICES if s[0] in IN_SCOPE)
    out_scope = total_endpoints - in_scope

    print("  the estate")
    print()
    print(f"    {'service':<16}{'endpoints':>11}{'reachable from':>16}"
          f"{'session required':>18}{'records':>10}")
    for name, eps, reach, auth, records in SERVICES:
        print(f"    {name:<16}{eps:>11}{reach:>16}"
              f"{('yes' if auth else 'NO'):>18}{records:>10,}")

    print()
    print(f"  endpoints in the estate              {total_endpoints:>3}")
    print(f"  endpoints in the engagement scope    {in_scope:>3}"
          f"   ({in_scope / total_endpoints:.1%})")
    print(f"  endpoints nobody looked at           {out_scope:>3}"
          f"   ({out_scope / total_endpoints:.1%})")

    print()
    print("  the report")
    print()
    by_sev = {}
    for service, sev, desc in FINDINGS:
        by_sev.setdefault(sev, []).append((service, desc))
    for sev in ("critical", "high", "medium", "low"):
        got = by_sev.get(sev, [])
        print(f"    {sev:<10}{len(got):>3}")
    print()
    print(f"    findings in scope                  {len(FINDINGS):>3}")
    print(f"    findings out of scope              {0:>3}"
          f"   (no endpoint out of scope was tested)")

    print()
    print("  what the rectangle left out")
    print()
    for name, eps, reach, auth, records in SERVICES:
        if name in IN_SCOPE:
            continue
        why = "no session required" if not auth else "session required"
        print(f"    {name:<16}{eps:>3} endpoints   reachable from {reach:<9}"
              f"{why:<20}{records:>9,} records")

    exposed = [s for s in SERVICES if not s[3] and s[0] not in IN_SCOPE]
    exposed_endpoints = sum(s[1] for s in exposed)
    exposed_records = sum(s[4] for s in exposed)
    print()
    print(f"  endpoints reachable with no session  {exposed_endpoints:>3}")
    print(f"  records behind them                  {exposed_records:>9,}")
    print(f"  reachable with one shared VPN login  {exposed_records:>9,}"
          f"   ({SHARED_VPN_ACCOUNTS} of {VPN_ACCOUNTS} accounts are shared)")

    print()
    print("  the fix")
    print("    one session middleware, applied to the two services that lack it")
    print(f"    covers {exposed_endpoints} endpoints, {exposed_records:,} records, "
          f"in one change")

    print()
    print(f"  the report said {len(FINDINGS)} findings, all in the {in_scope} endpoints"
          f" it was pointed at.")
    print(f"  the {out_scope} it was not pointed at held "
          f"{exposed_records:,} records and no session check.")


if __name__ == "__main__":
    main()
```

```text
  the estate

    service           endpoints  reachable from  session required   records
    public API               18        internet               yes         0
    admin console            23             vpn                NO   240,000
    internal tools           20        internal                NO         0

  endpoints in the estate               61
  endpoints in the engagement scope     18   (29.5%)
  endpoints nobody looked at            43   (70.5%)

  the report

    critical    0
    high        0
    medium      1
    low         3

    findings in scope                    4
    findings out of scope                0   (no endpoint out of scope was tested)

  what the rectangle left out

    admin console    23 endpoints   reachable from vpn      no session required   240,000 records
    internal tools   20 endpoints   reachable from internal no session required         0 records

  endpoints reachable with no session   43
  records behind them                    240,000
  reachable with one shared VPN login    240,000   (3 of 340 accounts are shared)

  the fix
    one session middleware, applied to the two services that lack it
    covers 43 endpoints, 240,000 records, in one change

  the report said 4 findings, all in the 18 endpoints it was pointed at.
  the 43 it was not pointed at held 240,000 records and no session check.
```

The estate has sixty-one endpoints across three services. The engagement covered eighteen of them --
the public API -- which is 29.5%. The other forty-three were not tested, and they produced no findings,
because an endpoint nobody looks at cannot produce one. That is not a criticism of the tester. It is
what a scope means.

The report was four findings: one medium, three low, all of them in the endpoints it was pointed at.
Meanwhile the two services nobody looked at require no session at all, and one of them holds 240,000
records. It is reachable from the VPN, and three of the 340 VPN accounts are shared, so "reachable
from the VPN" is a shorter sentence than it sounds.

The last paragraph is why this scenario belongs in a chapter about thinking rather than in a
post-mortem. One session middleware, applied to the two services that lack it, covers forty-three
endpoints and 240,000 records. The finding was large and the change was small, which is the usual
shape once somebody counts instead of guessing.

:::

## Key takeaways

- **Count the assets before defending them.** Eleven assets in the code, five in the design document.
  An asset in no document has no owner, and a control with no owner is a control nobody is failing.
- **Look at the distribution, not the total.** Exactly one of the eleven assets passes all four
  controls, and it is the one that had the most attention. The two that fail all four had none.
- **The log is an asset.** 200 of 500 request lines carried a credential and 101 carried a credential
  plus an email. Six of the fifteen request shapes were responsible, which makes it a fixable bug.
- **Anything that accumulates needs a retention policy.** 73,000 credential-bearing lines a year, in a
  file that is unencrypted, unrotated and unowned. Nothing in the system will tell you it grew.
- **Count boundaries, not boxes.** The same deployment gives 0.250 to 0.667 boundaries per component
  depending on the path. A diagram with more boxes is not a diagram with more risk.
- **The unguarded path is usually the outbound one.** `fetch image` touches two components, crosses one
  boundary, guards none of it -- and it is the only wholly unguarded path, because nobody drew the
  arrow pointing out.
- **The attack surface is the input count, not the endpoint count.** 19 routes, 47 inputs. Path
  parameters get a type check for free; the query string, the body and the `Authorization` header do
  not.
- **The input that decides who you are is the one nothing validates.** A session token is a lookup,
  not a type check, so no framework can check it for you.
- **STRIDE is a completeness device, not a ranking device.** 68 applicable threats out of 108 cells,
  and the count per category is a property of how many boxes you drew.
- **Redraw the diagram and the threat count moves.** Relabelling four data stores as processes takes
  the total from 68 to 76 and doubles elevation of privilege. Nothing was built.
- **The fix's location predicts whether a book like this has covered it.** Every category with a
  syntax-level fix is covered here; none with a design-level fix is.
- **"Internal" is a reachability claim, and reachability is computable.** Nine of thirteen components
  were reachable from the internet before the SSRF existed; five of the nine needed no credential.
- **Separate the reachability graph from the authentication graph.** They have different edges, and
  the difference between them is the exposure.
- **Two checks that fail on the same inputs are one check.** Independence predicted 4.6 inputs through;
  14 got through. The error is always in the direction that flatters the design.
- **A structural layer has no blind spot that scales.** Parameterisation and context-aware escaping
  caught 64 of 64, because they decide where input goes rather than what it says.
- **An error path is a decision made by default.** The failing-open and failing-closed sites were
  identical on 97.30% of traffic, which is why the 270 requests that distinguished them never came up.
- **Least privilege is a count, not a taste.** Three extra tables took the blast radius from 3
  resources to 17, a factor of 5.7, with no network path between the ends of the chain.
- **Where you enforce a rule decides how many rules you have.** The route-level design needed 21
  correct sites after five releases; the repository-level design needed one, and it grew by zero.

## Practice

- [ ] **Take an inventory.** For a project you have written, list every asset -- tables, config files,
  logs, caches, backups, uploads. For each, record whether it is documented, owned, encrypted and
  retained. Count the assets that fail all four, then count how many credential-bearing lines your
  logs would hold in a year at your real request rate.
- [ ] **Count the boundaries, not the boxes.** Draw the data flows for four request paths through a
  system you know. For each, count the components, the trust boundaries, and how many of those
  boundaries have a check on them. Find the path with the largest gap, then check whether it is also
  the path with the most components.
- [ ] **STRIDE one element.** Pick a single component and answer all six STRIDE questions about it in
  writing. Then run the same component through the applicability matrix. Report how many questions you
  had an answer for, which ones you left blank, and what the matrix says the count should have been.
- [ ] **Compute a blast radius.** Build a credential graph for a project you know: which account reads
  which table, which table holds which key, which key opens which store. Take the least privileged
  account you have and traverse it. Then add back the grants it has but does not obviously need, and
  report the factor by which the radius grows.

## Solutions

:::solution Exercise 1

A smaller inventory over a different application, and the same two counts.

```python run
#!/usr/bin/env python3
"""Exercise 1 -- an inventory, and a year of log lines.

A smaller version of the first block, over a different application: six
assets, three controls, and a request trace of three hundred lines.
"""
ASSETS = [
    # name, documented, owned, encrypted
    ("notes",         True,  True,  False),
    ("attachments",   True,  True,  False),
    ("accounts",      True,  True,  True),
    ("sessions",      False, False, False),
    ("api keys",      False, False, True),
    ("audit trail",   False, True,  False),
]

SHAPES = [
    "GET /notes",
    "GET /notes/12",
    "POST /notes title=groceries&body=milk",
    "POST /auth email=sam@example.com&password=correct-horse",
    "GET /me Authorization=Bearer eyJhbGciOiJIUzI1NiJ9",
    "POST /notes/12/attachment file=scan.pdf",
    "GET /share token=eyJhbGciOiJIUzI1NiJ9",
    "DELETE /notes/12",
    "GET /search q=holiday",
    "POST /auth/reset email=sam@example.com",
]

SECRET = ("password", "token", "authorization")
PII = ("@",)
REQUESTS = 300


def main():
    print(f"  assets                              {len(ASSETS):>3}")
    for name, doc, owned, enc in ASSETS:
        bad = sum(1 for v in (doc, owned, enc) if not v)
        print(f"    {name:<14} failing {bad} of 3")

    worst = [a[0] for a in ASSETS if not (a[1] and a[2] and a[3])]
    print(f"  failing at least one control        {len(worst)}")
    print(f"  passing all three                   "
          f"{len(ASSETS) - len(worst)}   "
          f"{[a[0] for a in ASSETS if a[1] and a[2] and a[3]]}")

    trace = [SHAPES[i % len(SHAPES)] for i in range(REQUESTS)]
    secrets = [t for t in trace if any(m in t.lower() for m in SECRET)]
    pii = [t for t in trace if any(m in t for m in PII)]

    print()
    print(f"  log lines                           {len(trace)}")
    print(f"  carrying a credential               {len(secrets)}"
          f"   ({len(secrets) / len(trace):.1%})")
    print(f"  carrying an email                   {len(pii)}"
          f"   ({len(pii) / len(trace):.1%})")

    leaky = [s for s in SHAPES if any(m in s.lower() for m in SECRET)]
    print(f"  shapes responsible                  {len(leaky)} of {len(SHAPES)}")
    for s in leaky:
        print(f"    {s}")

    print()
    print(f"  a year at {REQUESTS} a day: "
          f"{len(secrets) * 365:,} credential-bearing lines")


if __name__ == "__main__":
    main()
```

```text
  assets                                6
    notes          failing 1 of 3
    attachments    failing 1 of 3
    accounts       failing 0 of 3
    sessions       failing 3 of 3
    api keys       failing 2 of 3
    audit trail    failing 2 of 3
  failing at least one control        5
  passing all three                   1   ['accounts']

  log lines                           300
  carrying a credential               90   (30.0%)
  carrying an email                   60   (20.0%)
  shapes responsible                  3 of 10
    POST /auth email=sam@example.com&password=correct-horse
    GET /me Authorization=Bearer eyJhbGciOiJIUzI1NiJ9
    GET /share token=eyJhbGciOiJIUzI1NiJ9

  a year at 300 a day: 32,850 credential-bearing lines
```

:::

:::solution Exercise 2

Four paths, and the check that the two counts are not the same count.

```python run
#!/usr/bin/env python3
"""Exercise 2 -- count the boundaries, not the boxes.

Four request paths over the same small deployment. For each one, count the
components, the trust boundaries, and how many of those boundaries have a
check on them. Then find the path with the largest gap.
"""

ZONE = {
    "phone": "public",
    "gateway": "edge",
    "service": "app",
    "worker": "app",
    "primary": "data",
    "blobstore": "data",
    "ops_host": "admin",
}

PATHS = [
    ("read a note",     ["phone", "gateway", "service", "primary"],  ["gateway", "service"]),
    ("upload",          ["phone", "gateway", "service", "blobstore"], ["gateway", "service"]),
    ("nightly reindex", ["worker", "primary", "blobstore"],          ["primary"]),
    ("ops restore",     ["ops_host", "primary", "blobstore"],        []),
]


def crosses(u, v):
    return ZONE[u] != ZONE[v]


def main():
    print(f"  {'path':<18}{'components':>11}{'boundaries':>12}{'guarded':>9}{'gap':>6}")
    stats = {}
    for name, chain, checks in PATHS:
        pairs = list(zip(chain, chain[1:]))
        bnd = [(u, v) for u, v in pairs if crosses(u, v)]
        guarded = [p for p in bnd if p[1] in checks]
        stats[name] = (len(chain), len(bnd), len(guarded))
        print(f"  {name:<18}{len(chain):>11}{len(bnd):>12}{len(guarded):>9}"
              f"{len(bnd) - len(guarded):>6}")

    print()
    worst = max(stats, key=lambda n: (stats[n][1] - stats[n][2], -stats[n][0]))
    comp, bnd, guarded = stats[worst]
    plural = "" if bnd == 1 else "s"
    print(f"  largest gap: {worst} -- {comp} components, {bnd} boundary{plural}, "
          f"{guarded} guarded, gap {bnd - guarded}")

    deepest = max(stats, key=lambda n: stats[n][0])
    print(f"  most components: {deepest} ({stats[deepest][0]}) "
          f"-- {stats[deepest][1]} boundaries")

    print()
    print("  the path with the most components is not the path with the most")
    print("  boundaries, and neither is the path with the largest gap.")


if __name__ == "__main__":
    main()
```

```text
  path               components  boundaries  guarded   gap
  read a note                 4           3        2     1
  upload                      4           3        2     1
  nightly reindex             3           1        1     0
  ops restore                 3           1        0     1

  largest gap: ops restore -- 3 components, 1 boundary, 0 guarded, gap 1
  most components: read a note (4) -- 3 boundaries

  the path with the most components is not the path with the most
  boundaries, and neither is the path with the largest gap.
```

:::

:::solution Exercise 3

The six questions answered by hand, and the matrix's opinion of the same component.

```python run
#!/usr/bin/env python3
"""Exercise 3 -- STRIDE one element, and check it against the matrix.

The six questions applied to a single component of an upload service, then
the same component run through the applicability matrix. The two counts are
not the same number, and the difference is the point of the exercise.
"""
import itertools

STRIDE = (
    "Spoofing", "Tampering", "Repudiation",
    "Information disclosure", "Denial of service", "Elevation of privilege",
)

APPLICABLE = {
    "external entity": ("Spoofing", "Repudiation"),
    "process": STRIDE,
    "data store": ("Tampering", "Repudiation", "Information disclosure", "Denial of service"),
    "data flow": ("Tampering", "Information disclosure", "Denial of service"),
}

# The component under study, and the threats a person actually wrote down
# after thinking about it for ten minutes.
ELEMENT = "upload service"
KIND = "process"
WRITTEN = [
    ("Spoofing", "a forged session cookie reaches the handler"),
    ("Tampering", "the filename is used as a path"),
    ("Tampering", "the content type is trusted over the bytes"),
    ("Information disclosure", "uploaded files are served without a session check"),
    ("Denial of service", "no size limit before the body is buffered"),
]

OTHER_ELEMENTS = [
    ("browser", "external entity"),
    ("object store", "data store"),
    ("browser->upload service", "data flow"),
    ("upload service->object store", "data flow"),
]


def main():
    print(f"  element                             {ELEMENT} ({KIND})")
    print()
    print("  the six questions, answered by hand")
    answered = {cat for cat, _ in WRITTEN}
    for cat in STRIDE:
        hits = [d for c, d in WRITTEN if c == cat]
        mark = "x" if hits else "."
        detail = hits[0] if hits else ""
        print(f"    {mark} {cat:<26}{detail}")
    print()
    print(f"  questions with an answer            {len(answered)} of {len(STRIDE)}")
    print(f"  threats written down                {len(WRITTEN)}")
    print(f"  questions left blank                {len(STRIDE) - len(answered)}"
          f"   {sorted(set(STRIDE) - answered)}")

    print()
    print("  the same element against the matrix")
    applies = APPLICABLE[KIND]
    print(f"    a {KIND} attracts {len(applies)} of the {len(STRIDE)} questions")
    print(f"    all {len(STRIDE)} were asked here, which cost nothing extra")
    print(f"    and found {len(STRIDE) - len(answered)} question(s) nobody had an answer for")

    # The same arithmetic for the whole diagram, for comparison.
    cells = len(OTHER_ELEMENTS) * len(STRIDE)
    applicable = sum(len(APPLICABLE[k]) for _, k in OTHER_ELEMENTS)
    print()
    print("  the rest of the diagram, for scale")
    for name, kind in OTHER_ELEMENTS:
        print(f"    {name:<30}{kind:<18}{len(APPLICABLE[kind])} of {len(STRIDE)}")
    print(f"    cells {cells}, applicable {applicable}"
          f"   ({applicable / cells:.1%})")

    print()
    print("  the matrix is a checklist for completeness. It does not rank,")
    print("  and it does not know which of your answers are wrong.")


if __name__ == "__main__":
    main()
```

```text
  element                             upload service (process)

  the six questions, answered by hand
    x Spoofing                  a forged session cookie reaches the handler
    x Tampering                 the filename is used as a path
    . Repudiation               
    x Information disclosure    uploaded files are served without a session check
    x Denial of service         no size limit before the body is buffered
    . Elevation of privilege    

  questions with an answer            4 of 6
  threats written down                5
  questions left blank                2   ['Elevation of privilege', 'Repudiation']

  the same element against the matrix
    a process attracts 6 of the 6 questions
    all 6 were asked here, which cost nothing extra
    and found 2 question(s) nobody had an answer for

  the rest of the diagram, for scale
    browser                       external entity   2 of 6
    object store                  data store        4 of 6
    browser->upload service       data flow         3 of 6
    upload service->object store  data flow         3 of 6
    cells 24, applicable 12   (50.0%)

  the matrix is a checklist for completeness. It does not rank,
  and it does not know which of your answers are wrong.
```

:::

:::solution Exercise 4

Ten resources, one starting credential, and the factor.

```python run
#!/usr/bin/env python3
"""Exercise 4 -- a blast radius over a credential graph of your own.

Ten resources, one starting credential, and two grants. The traversal is the
same breadth-first search as the ninth block, on a different graph.
"""

LEAST = [
    ("reporting account", "orders table"),
    ("reporting account", "order lines table"),
]

DEFAULT = LEAST + [
    ("reporting account", "customers table"),
]

# resource -> what is stored inside it, and what that unlocks
CONTAINS = [
    ("customers table", "support api token"),
    ("support api token", "support console"),
    ("support console", "customer export tool"),
    ("customer export tool", "full customer export"),
    ("reporting account", "warehouse key"),
    ("warehouse key", "analytics bucket"),
    ("analytics bucket", "raw event stream"),
]

START = "reporting account"


def bfs(edges, source):
    adjacency = {}
    for u, v in edges:
        adjacency.setdefault(u, []).append(v)
    for u in adjacency:
        adjacency[u].sort()
    seen = {source: 0}
    queue = [source]
    while queue:
        node = queue.pop(0)
        for nxt in adjacency.get(node, ()):
            if nxt not in seen:
                seen[nxt] = seen[node] + 1
                queue.append(nxt)
    return seen


def main():
    least = bfs(LEAST + CONTAINS, START)
    default = bfs(DEFAULT + CONTAINS, START)

    print(f"  starting credential                 {START}")
    print()
    print("  least privilege")
    for node in sorted(least, key=lambda n: (least[n], n)):
        if node != START:
            h = least[node]
            print(f"    {h:>2} hop{'' if h == 1 else 's'}   {node}")
    print(f"    reachable                           {len(least) - 1}")

    print()
    print("  with one extra table")
    for node in sorted(default, key=lambda n: (default[n], n)):
        if node == START:
            continue
        h = default[node]
        mark = "" if node in least else "   <- only through the extra grant"
        print(f"    {h:>2} hop{'' if h == 1 else 's'}   {node:<26}{mark}")
    print(f"    reachable                           {len(default) - 1}")

    extra = sorted(set(default) - set(least), key=lambda n: (default[n], n))
    print()
    print(f"  one table added                     {len(extra)} resources to the radius")
    for node in extra:
        print(f"    {node}")
    print()
    print(f"  the radius grew from {len(least) - 1} to {len(default) - 1}, "
          f"a factor of {(len(default) - 1) / (len(least) - 1):.1f}.")
    print("  nobody would describe that grant as broad.")


if __name__ == "__main__":
    main()
```

```text
  starting credential                 reporting account

  least privilege
     1 hop   order lines table
     1 hop   orders table
     1 hop   warehouse key
     2 hops   analytics bucket
     3 hops   raw event stream
    reachable                           5

  with one extra table
     1 hop   customers table              <- only through the extra grant
     1 hop   order lines table         
     1 hop   orders table              
     1 hop   warehouse key             
     2 hops   analytics bucket          
     2 hops   support api token            <- only through the extra grant
     3 hops   raw event stream          
     3 hops   support console              <- only through the extra grant
     4 hops   customer export tool         <- only through the extra grant
     5 hops   full customer export         <- only through the extra grant
    reachable                           10

  one table added                     5 resources to the radius
    customers table
    support api token
    support console
    customer export tool
    full customer export

  the radius grew from 5 to 10, a factor of 2.0.
  nobody would describe that grant as broad.
```

:::
