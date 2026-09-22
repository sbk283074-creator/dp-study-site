"""Chapter 54 -- the observer pattern, and the two questions it raises.

A list of callbacks is the whole pattern. What it does not answer is
what happens when one of them raises, and whether the order they run in
is part of the contract.
"""

import itertools


def make_subscribers():
    """Six subscribers, the third of which raises."""
    ran = []

    def first(event):
        ran.append("first")

    def second(event):
        ran.append("second")

    def third(event):
        raise RuntimeError("third")

    def fourth(event):
        ran.append("fourth")

    def fifth(event):
        ran.append("fifth")

    def sixth(event):
        ran.append("sixth")

    return ran, [first, second, third, fourth, fifth, sixth]


def notify_naive(subscribers, event):
    """What the first version of this always looks like."""
    for subscriber in subscribers:
        subscriber(event)


def notify_isolated(subscribers, event):
    """The same loop, with each subscriber's failure kept to itself."""
    failures = []
    for subscriber in subscribers:
        try:
            subscriber(event)
        except Exception as exc:
            failures.append((subscriber.__name__, type(exc).__name__))
    return failures


FACTORS = [2, 3, 5]


def run_order(order):
    """Three subscribers that each fold the shared value, so the result
    is a function of the order they run in."""
    state = [0]
    for factor in order:
        state[0] = state[0] * factor + 1
    return state[0]


def main():
    print(f"  subscribers                         {len(make_subscribers()[1])}")
    print()

    ran, subscribers = make_subscribers()
    try:
        notify_naive(subscribers, "order placed")
        outcome = "no failure"
    except RuntimeError:
        outcome = "raised"
    print(f"  the loop that does not isolate failures: {outcome} after "
          f"{len(ran)} of the")
    print(f"  {len(subscribers)} subscribers ran. the three after the failure never")
    print("  hear about the event, and the caller never gets a return value,")
    print("  so the list of who did run is not available either.")
    print()

    ran, subscribers = make_subscribers()
    failures = notify_isolated(subscribers, "order placed")
    print(f"  the loop that isolates failures: {len(ran)} of the "
          f"{len(subscribers)} ran, and")
    print("  the failures are returned:")
    for name, kind in failures:
        print(f"    {name}  {kind}")
    print()
    print("  both loops are three lines. the difference is that the second")
    print("  one treats a subscriber as something that can be wrong, which is")
    print("  the only assumption a list of callbacks needs and the one the")
    print("  first version does not make.")
    print()

    orders = list(itertools.permutations(FACTORS))
    outcomes = {}
    for order in orders:
        outcomes.setdefault(run_order(order), []).append(order)
    print(f"  the order the subscribers run in")
    print()
    print("    order        the value it leaves")
    for order in orders:
        print("    {:<12}{}".format(
            ",".join(str(f) for f in order), run_order(order)))
    print()
    print(f"  {len(outcomes)} of the {len(orders)} orderings leave a different value.")
    print("  three subscribers that each fold a shared value commute with")
    print("  nothing, so the order is not an implementation detail -- it is")
    print("  part of the result, and nothing in the pattern says what it is.")
    print()
    print("  that is the question a subscriber list raises and does not")
    print("  answer. if the subscribers only report, any order will do and the")
    print("  isolation is the whole fix. if any of them can change the value")
    print("  the others see, the order is a contract, and a contract that is")
    print("  not written down is one that a later refactor will change.")


main()
