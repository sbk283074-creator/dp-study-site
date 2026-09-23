"""Chapter 9 -- how wide an except clause is, counted in exception types.

Three application errors, four built-in errors, and the two exceptions that are
not errors at all. Each handler is asked how many of the nine it catches, and
the count is the answer. The result is that the broadest clause that is still
safe catches seven of nine, and the two it misses are the ones that matter.
"""


class AppError(Exception):
    """The base class this program's own errors share."""


class NotFound(AppError):
    """A thing that was asked for does not exist."""


class Conflict(AppError):
    """A thing that exists when it should not."""


class Timeout(AppError):
    """A thing took longer than the caller allowed."""


def raiser(error):
    """A callable that raises this exception when it is called."""

    def raise_it():
        raise error

    return raise_it


RAISERS = [
    ("NotFound", raiser(NotFound("no such row"))),
    ("Conflict", raiser(Conflict("already there"))),
    ("Timeout", raiser(Timeout("too slow"))),
    ("ValueError", raiser(ValueError("bad literal"))),
    ("KeyError", raiser(KeyError("missing key"))),
    ("OSError", raiser(OSError("disk went away"))),
    ("RuntimeError", raiser(RuntimeError("gave up"))),
    ("KeyboardInterrupt", raiser(KeyboardInterrupt())),
    ("SystemExit", raiser(SystemExit(2))),
]

HANDLERS = [
    ("except NotFound", (NotFound,)),
    ("except AppError", (AppError,)),
    ("except Exception", (Exception,)),
    ("except BaseException", (BaseException,)),
]

print(f"{'handler':<22}{'catches':>9}{'of':>4}{'misses':>8}")
print("-" * 43)
misses_by_handler = {}
for label, caught in HANDLERS:
    hits = []
    misses = []
    for name, raiser in RAISERS:
        try:
            raiser()
        except caught:
            hits.append(name)
        except BaseException:
            misses.append(name)
    misses_by_handler[label] = misses
    print(f"{label:<22}{len(hits):>9}{len(RAISERS):>4}{len(misses):>8}")

print()
print(f"The first two handlers catch one and {len(RAISERS) - len(misses_by_handler['except AppError'])} of")
print(f"the {len(RAISERS)}. They are the two you want: they name the failures the caller is")
print("prepared to handle, and everything else keeps travelling up the stack to")
print("somebody who can.")
print()
print(f"The third catches {len(RAISERS) - len(misses_by_handler['except Exception'])} of the {len(RAISERS)}, and the two it misses are")
print(f"{' and '.join(misses_by_handler['except Exception'])}. Neither is a failure of the")
print("program: one is the operator asking it to stop and the other is the")
print("interpreter unwinding. That is why `except Exception` is the broadest")
print("clause a library should ever write.")
print()
print(f"The fourth catches all {len(RAISERS)}. A handler that swallows a KeyboardInterrupt")
print("is a program you cannot stop with Ctrl-C, and the count is the reason:")
print("it is not one mistake, it is every mistake at once, including the two")
print("that were never errors.")
