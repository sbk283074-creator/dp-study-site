"""Chapter 55 -- scopes, and the bug a singleton causes.

Three requests, three scopes, and one cache that captured a per-request
object. The count is of the distinct objects handed out over three
requests, and of the requests that get the wrong one.
"""


class Session:
    def __init__(self, request_id):
        self.request_id = request_id


SINGLETON = Session(0)


def per_request(request_id):
    return Session(request_id)


def transient(request_id):
    return Session(request_id)


class CapturedCache:
    """A singleton that took a session when it was built, which is the
    mistake. It keeps request 1's session for ever."""

    def __init__(self, session):
        self.session = session

    def owner(self):
        return self.session.request_id


class PassedCache:
    """The same cache, told which session to use on each call."""

    def owner(self, session):
        return session.request_id


REQUESTS = [1, 2, 3]

SCOPES = [
    ("singleton", [SINGLETON for _ in REQUESTS]),
    ("per request", [per_request(i) for i in REQUESTS]),
    ("transient", [transient(i) for i in REQUESTS for _ in (0, 1)]),
]


def main():
    print(f"  requests                            {len(REQUESTS)}")
    print()
    print("    scope          instances   the same object every time")
    for label, made in SCOPES:
        distinct = len(set(id(item) for item in made))
        print("    {:<15}{:>9}   {}".format(
            label, distinct, "yes" if distinct == 1 else "no"))
    print()

    print("    who each request thinks it is talking to")
    print("    {:<24}{:<18}{}".format("", "captured cache", "passed cache"))
    captured = CapturedCache(per_request(REQUESTS[0]))
    rows = []
    for request_id in REQUESTS:
        session = per_request(request_id)
        rows.append((request_id, captured.owner(),
                     PassedCache().owner(session)))
    for request_id, got, want in rows:
        print("    {:<24}{:<18}{}".format(
            "request %d" % request_id,
            "request %d" % got,
            "request %d" % want))
    print()

    stale = sum(1 for request_id, got, _ in rows if got != request_id)
    print(f"  the captured cache gives {stale} of the {len(REQUESTS)} requests the")
    print("  wrong session, and the one it gets right is the request that")
    print("  built it. nothing raises: every call returns a session, and a")
    print("  session from the wrong request is a value of the right shape.")
    print()
    print("  that is why the scope is part of the wiring and not an")
    print("  implementation detail. a singleton may hold a singleton; a")
    print("  singleton may not hold something that is rebuilt per request,")
    print("  because the container builds the singleton once and there is no")
    print("  later moment at which it could be given a new one.")
    print()
    print("  the fix in the second column is not a longer lifetime. it is")
    print("  that the per-request object stops being held at all: it is")
    print("  passed to the method that needs it, so the object that outlives")
    print("  the request holds no reference to anything that should not.")
    print()
    print("  the three scopes are three different answers to one question,")
    print("  and the question is how long the thing is allowed to live. a")
    print("  container that lets you answer it per dependency is useful for")
    print("  exactly this reason, and a container that picks one answer for")
    print("  everything is the bug above waiting to happen.")


main()
