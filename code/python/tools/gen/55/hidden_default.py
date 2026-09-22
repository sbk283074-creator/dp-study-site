"""Chapter 55 -- the default that wires the real dependency.

A sender whose dependency is optional, and the same sender where it is
required. The count is of the call sites that build the real thing
without saying so.
"""

REAL_MADE = []


class RealMailer:
    kind = "real"

    def __init__(self):
        REAL_MADE.append(self)

    def send(self, message):
        return "sent by the real one"


class FakeMailer:
    kind = "fake"

    def __init__(self):
        self.sent = []

    def send(self, message):
        self.sent.append(message)
        return "captured"


# --- optional
def send_report(message, mailer=None):
    if mailer is None:
        mailer = RealMailer()
    return mailer.send(message)
# --- end


# --- required
def send_required(message, mailer):
    return mailer.send(message)
# --- end


CALL_SITES = ["the nightly job", "the webhook handler", "the admin button"]


def run_optional():
    """Three production call sites and one test, against the optional
    version."""
    REAL_MADE.clear()
    outcomes = []
    for label in CALL_SITES:
        outcomes.append((label, send_report("the report")))
    outcomes.append(("a test", send_report("the report", FakeMailer())))
    return outcomes


def run_required():
    """The same four sites, against the required version. Each one now
    has to say what it wants."""
    REAL_MADE.clear()
    outcomes = []
    for label in CALL_SITES:
        outcomes.append((label, send_required("the report", RealMailer())))
    outcomes.append(("a test", send_required("the report", FakeMailer())))
    return outcomes


def main():
    print(f"  call sites                          {len(CALL_SITES) + 1}")
    print()

    print("    the optional parameter")
    outcomes = run_optional()
    for label, result in outcomes:
        print("    {:<24}{}".format(label, result))
    implicit = len(REAL_MADE)
    print("    {:<24}{}".format("", "%d real mailer(s) built" % implicit))
    print()

    print("    the required parameter")
    outcomes = run_required()
    for label, result in outcomes:
        print("    {:<24}{}".format(label, result))
    print("    {:<24}{}".format("", "%d real mailer(s) built" % len(REAL_MADE)))
    print()

    sites = len(CALL_SITES) + 1
    print(f"  {implicit} of the {sites} call sites build the real mailer without")
    print("  naming it, and the one that does name one is the test. so the")
    print("  default did not save the three production sites any work -- they")
    print("  still construct a real mailer, on the line inside the function")
    print("  instead of the line at the call site.")
    print()
    print("  what it changed is who can see the choice. with the default, the")
    print("  decision is inside `send_report`, one copy of it for every")
    print("  caller, and the call site that wanted something else is")
    print("  indistinguishable from the three that did not. with a required")
    print("  parameter there is no hidden copy, and the count of places the")
    print("  choice appears is the count of call sites.")
    print()
    print("  this is the same shape as the resolver and the registry in the")
    print("  earlier chapters: a default that produces a working object makes")
    print("  the wrong call site look exactly like the right one. the")
    print("  difference here is that it is one keyword argument, so it gets")
    print("  written by people who would never write a global.")


main()
