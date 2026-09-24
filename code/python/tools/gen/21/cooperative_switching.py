"""Chapter 21 -- one thread, and the await is the only thing that shares it.

Four coroutines, each logging a start and an end, run twice: once with nothing
between the two events and once with a single await. The count is of coroutines
that reached their end before any other one had started.
"""

import asyncio

WORKERS = 4


async def no_await(name, log):
    log.append(f"{name}:start")
    log.append(f"{name}:end")


async def one_await(name, log):
    log.append(f"{name}:start")
    await asyncio.sleep(0)
    log.append(f"{name}:end")


async def run(worker, log):
    await asyncio.gather(*(worker(f"w{index}", log) for index in range(WORKERS)))


def uninterrupted(log):
    """Coroutines that got from start to end with no other worker in between."""
    count = 0
    index = 0
    while index < len(log) - 1:
        left, right = log[index], log[index + 1]
        if (left.endswith(":start") and right.endswith(":end")
                and left[:2] == right[:2]):
            count += 1
            index += 2
        else:
            index += 1
    return count


def switches(log):
    return sum(1 for index in range(1, len(log))
               if log[index][:2] != log[index - 1][:2])


plain_log = []
asyncio.run(run(no_await, plain_log))

yielding_log = []
asyncio.run(run(one_await, yielding_log))

print(f"{WORKERS} coroutines on one thread, each logging a start and an end")
print()
print(f"{'log':<40}{'no await':>10}{'one await':>11}")
print("-" * 61)
print(f"{'events recorded':<40}{len(plain_log):>10}{len(yielding_log):>11}")
print(f"{'times control moved coroutine':<40}{switches(plain_log):>10}"
      f"{switches(yielding_log):>11}")
print(f"{'ran start to end in one turn':<40}{uninterrupted(plain_log):>10}"
      f"{uninterrupted(yielding_log):>11}")
print(f"{'started but unfinished at the first end':<40}{0:>10}"
      f"{WORKERS - uninterrupted(yielding_log):>11}")

print()
print("no await      : " + " ".join(plain_log))
print("one await     : " + " ".join(yielding_log))

print()
print("The last row is the difference. With nothing between the two events,")
print("each coroutine ran its whole body before the next one began -- four")
print("starts, four ends, and at no point was more than one of them part-way")
print("through. Nothing was concurrent; the loop simply took them one at a")
print("time, and the word `async` bought nothing at all.")
print()
print("With a single `await asyncio.sleep(0)` in the middle, all four reached")
print("their start before any of them reached an end. That is what cooperative")
print("switching means: one thread, and the only moment another coroutine can")
print("run is the moment this one hands control back.")
print()
print("Which makes the blocking call the whole problem. `time.sleep`, a")
print("synchronous database driver, `requests.get` -- none of them contain an")
print("await, so none of them hand control back. Put one inside a coroutine")
print("and it behaves exactly like the first column: every other coroutine")
print("waits, because there is one thread and that thread is busy. A coroutine")
print("that never awaits is not concurrent code; it is an ordinary function")
print("written with `async def`, and it blocks the loop for as long as it runs.")
