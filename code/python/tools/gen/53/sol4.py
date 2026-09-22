"""Chapter 53 -- practice 4.

The constructive half of the logging block: a recorder with a field
allow-list and a list of events that must always produce a line, checked
against each other. Nothing here writes a value out, which is also what
the recorder is for.
"""

CORE = {"actor": "u1", "action": "read", "resource": "note 12",
        "outcome": "ok"}

FROM_BODY = "(from the request body)"

# The names the request body uses for the three fields that must never
# reach a log line. They are held as data rather than written as keyword
# arguments, so that this file is a list of names and not a set of
# assignments.
BODY_NAMES = ("password", "token", "card")

# the fields a log line is allowed to contain
ALLOWED = ("actor", "action", "resource", "outcome", "reason", "address")

# the events that must produce a line, whether or not anyone thought to
# add a call for them
REQUIRED = [
    "permission denied",
    "role changed",
    "account locked",
    "export downloaded",
    "password changed",
]


def fields(**extra):
    out = dict(CORE)
    out.update(extra)
    return out


def from_body(**extra):
    """A handler that hands the recorder the whole request rather than
    the fields it needs."""
    out = fields(**extra)
    for name in BODY_NAMES:
        out[name] = FROM_BODY
    return out


# name, the fields offered to the recorder, and whether it is required
EVENTS = [
    ("login success",
     from_body(action="login", resource="session"), False),
    ("login failure",
     from_body(action="login", resource="session", outcome="refused",
               reason="bad password"), False),
    ("password reset",
     from_body(action="reset", resource="session"), False),
    ("token refresh",
     from_body(action="refresh", resource="session"), False),
    ("page view", fields(resource="note 12", trace="a4f1"), False),
    ("note created", fields(action="create", trace="a4f1"), False),
    ("permission denied",
     fields(action="read", outcome="refused", reason="not the owner"), True),
    ("role changed",
     from_body(action="grant", resource="account"), True),
    ("account locked",
     fields(action="lock", resource="account", outcome="refused",
            reason="too many attempts"), True),
    ("export downloaded",
     fields(action="export", resource="all notes", trace="a4f1"), True),
]


def record(offered):
    """The allow-list is the whole of the first fix: the line is built
    from named fields rather than from the request."""
    kept = {k: v for k, v in offered.items() if k in ALLOWED}
    dropped = [k for k in offered if k not in ALLOWED]
    return kept, dropped


def main():
    print(f"  events                              {len(EVENTS)}")
    print(f"  events that must produce a line     {len(REQUIRED)}")
    print(f"  fields a line may contain           {len(ALLOWED)}")
    print()

    print("    {:<22}{:>9}{:>9}{:>11}{:>14}".format(
        "event", "offered", "written", "dropped", "from the body"))
    written_records = []
    offered = written = dropped = body = 0
    for name, offered_fields, _ in EVENTS:
        kept, lost = record(offered_fields)
        written_records.append((name, kept))
        offered += len(offered_fields)
        written += len(kept)
        dropped += len(lost)
        body += sum(1 for k in lost if k in BODY_NAMES)
        print("    {:<22}{:>9}{:>9}{:>11}{:>14}".format(
            name, len(offered_fields), len(kept), len(lost),
            sum(1 for k in lost if k in BODY_NAMES)))
    print()

    print(f"  fields offered                      {offered}")
    print(f"  fields written                      {written}")
    print(f"  fields dropped                      {dropped}")
    print(f"  of the dropped, from the request body   {body}")
    print(f"  lines written                       "
          f"{len(written_records)} of {len(EVENTS)}")
    with_line = [r for r in REQUIRED if any(n == r for n, _ in written_records)]
    missing = [r for r in REQUIRED if not any(n == r for n, _ in written_records)]
    print(f"  required events with a line         "
          f"{len(with_line)} of {len(REQUIRED)}")
    print()

    questions = [
        ("who acted", lambda r: "actor" in r),
        ("on what", lambda r: "resource" in r),
        ("what happened", lambda r: "outcome" in r),
        ("why it was refused",
         lambda r: r.get("outcome") != "refused" or "reason" in r),
    ]
    print("    the questions the written lines answer")
    for label, ok in questions:
        answerable = all(ok(kept) for _, kept in written_records)
        print("    {:<28}{}".format(label, "yes" if answerable else "no"))
    carried = sum(1 for _, kept in written_records
                  if any(k in BODY_NAMES for k in kept))
    print("    {:<28}{}".format("what the credential was",
                                "yes" if carried else "no"))
    print()
    print(f"  {body} of the {dropped} dropped fields came from the request body, and")
    print("  the rest are the ones somebody will want during the incident.")
    print("  that is the cost of an allow-list, and it is the right trade: a")
    print("  field that is missing from a log can be added, and a credential")
    print("  that was written into one cannot be unwritten.")
    print()
    print(f"  the required list has {len(REQUIRED)} entries and "
          f"{len(with_line)} of them produced a line.")
    print(f"  the one that did not is `{missing[0]}`, which is a gap the field")
    print("  allow-list cannot see and the event list found. nothing in this")
    print("  service writes a line when a credential changes, and that is the")
    print("  same missing event the session block could not find either -- a")
    print("  password change is a route, and nothing about it looks like a")
    print("  session event until you write the list of events that have to")
    print("  leave a trace.")
    print()
    print("  that list is the only part of this recorder that is a")
    print("  requirement rather than an implementation. the allow-list can be")
    print("  reviewed by reading it. the list of events cannot, because what")
    print("  is missing from it is missing from the output too, and the")
    print("  output is what you would check it against.")
    print()
    print("  the last row of the questions table is the whole argument. the")
    print("  only question the request body would have answered is the one")
    print("  nobody should be asking, and every question an incident review")
    print("  actually asks is answered by a named field that was there")
    print("  before the request arrived.")


main()
