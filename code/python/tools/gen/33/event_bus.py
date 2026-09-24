"""Chapter 33 -- an event bus decouples the sender, and then surprises it.

Five subscribers, one of which unsubscribes during the dispatch and one of which
raises. The count is of deliveries each subscriber receives.
"""

SUBSCRIBERS = ["hud", "sound", "achievements", "analytics", "logger"]


def dispatch(listeners, order, *, snapshot, isolate, unsubscriber=None, raiser=None):
    """Deliver one event and report who received it.

    `snapshot` copies the listener list before iterating, so a subscriber that
    leaves during the dispatch still receives this event. `isolate` catches a
    subscriber's exception so the ones after it still run.
    """
    delivered = []
    live = list(order)
    for name in (list(live) if snapshot else live):
        if name not in live:
            continue
        if name == unsubscriber:
            live.remove(name)
        if name == raiser:
            if isolate:
                continue
            break
        delivered.append(name)
    return delivered


order = list(SUBSCRIBERS)
leaver = "achievements"
raiser = "analytics"

configs = [
    ("plain", dict(snapshot=False, isolate=False)),
    ("snapshot only", dict(snapshot=True, isolate=False)),
    ("isolation only", dict(snapshot=False, isolate=True)),
    ("snapshot and isolation", dict(snapshot=True, isolate=True)),
]

rows = []
for label, kwargs in configs:
    got = dispatch(None, order, unsubscriber=leaver, raiser=raiser, **kwargs)
    rows.append((label, got))

print(f"{len(SUBSCRIBERS)} subscribers, {leaver} leaves during the dispatch, "
      f"{raiser} raises")
print()
print(f"{'bus':<24}{'delivered to':>14}   missing")
print("-" * 66)
for label, got in rows:
    missing = [name for name in SUBSCRIBERS if name not in got]
    print(f"{label:<24}{len(got):>14}   {', '.join(missing) or '-'}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'subscribers':<46}{len(SUBSCRIBERS):>8}")
print(f"{'subscribers that leave mid-dispatch':<46}"
      f"{int(leaver is not None):>8}")
print(f"{'subscribers that raise':<46}{int(raiser is not None):>8}")
for label, got in rows:
    print(f"{'delivered, ' + label:<46}{len(got):>8}")
print(f"{'buses that deliver to the leaver':<46}"
      f"{sum(1 for _, got in rows if leaver in got):>8}")
print(f"{'buses that deliver to the raiser':<46}"
      f"{sum(1 for _, got in rows if raiser in got):>8}")
print(f"{'buses that deliver to the last subscriber':<46}"
      f"{sum(1 for _, got in rows if SUBSCRIBERS[-1] in got):>8}")

print()
print("The plain row delivers to four of the five and the one it misses is not")
print("the subscriber that left. The leaver hears the event -- it is removed from")
print("the list after it has been called, which is what 'I want this one and then")
print("stop' means -- and the subscriber that is skipped is the one that did")
print("nothing at all. Removing an item from a list while a loop is walking it")
print("advances the iterator past the next item, and the victim is whoever")
print("happened to be sitting there.")
print()
print("The second row is the one to think about, because it is what happens when")
print("you fix the first bug. Taking a copy before iterating removes the skip, so")
print("the raising subscriber is finally reached -- and the dispatch ends there,")
print("and the logger after it hears nothing. Fixing the silent bug exposed the")
print("loud one, which is the usual order in which these things are found.")
print()
print("The last two rows deliver the same four subscribers and they get there")
print("for different reasons. Taking a copy means a subscriber can leave without")
print("disturbing anyone else; catching each exception means one broken listener")
print("cannot silence the rest. Neither fixes the other, and a bus with only one")
print("of them still has a way for an unrelated subscriber to lose an event.")
print()
print("That is the price of decoupling. The sender does not know who is")
print("listening, so the bus must not let the listeners know about each other")
print("either -- and the only way to promise that is to give each delivery its")
print("own scope, on a list that cannot change underneath it.")
