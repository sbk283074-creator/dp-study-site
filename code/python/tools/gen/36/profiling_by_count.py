"""Chapter 36 -- profiling by call count finds the wrong function.

One frame of a game, instrumented. The count is of calls per function and of the
work each call actually does.
"""

calls = {}
work = {}


def counted(name, per_call):
    def decorate(function):
        def wrapper(*args, **kwargs):
            calls[name] = calls.get(name, 0) + 1
            work[name] = work.get(name, 0) + per_call
            return function(*args, **kwargs)
        return wrapper
    return decorate


@counted("draw_text", 30)
def draw_text(label):
    return len(label)


@counted("update_enemies", 40)
def update_enemies(index):
    return index * 2


@counted("check_collisions", 19900)
def check_collisions():
    return 0


@counted("render_tiles", 320)
def render_tiles():
    return 0


# One frame: every label is drawn, every enemy is updated, and the two
# whole-scene passes happen once.
for index in range(240):
    draw_text(f"enemy {index}")
for index in range(60):
    update_enemies(index)
check_collisions()
render_tiles()

names = sorted(calls, key=lambda name: (-calls[name], name))
by_calls = names[0]
by_work = max(work, key=lambda name: work[name])
total = sum(work.values())

print(f"one frame, {len(calls)} instrumented functions")
print()
print(f"{'function':<22}{'calls':>8}{'work per call':>15}{'total work':>12}"
      f"{'share':>9}")
print("-" * 66)
for name in names:
    share = 100.0 * work[name] / total
    print(f"{name:<22}{calls[name]:>8}{work[name] // calls[name]:>15}"
          f"{work[name]:>12}{f'{share:.1f}%':>9}")
print("-" * 66)
print(f"{'total':<22}{sum(calls.values()):>8}{'':>15}{total:>12}{'100.0%':>9}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'functions instrumented':<46}{len(calls):>8}")
print(f"{'calls in one frame':<46}{sum(calls.values()):>8}")
print(f"{'total work in one frame':<46}{total:>8}")
print(f"{'the two answers agree':<46}{int(by_calls == by_work):>8}")
print(f"{'calls the busiest caller makes':<46}{calls[by_calls]:>8}")
print(f"{'work the busiest caller does':<46}{work[by_calls]:>8}")
print(f"{'work the hottest function does':<46}{work[by_work]:>8}")
print(f"{'calls the hottest function makes':<46}{calls[by_work]:>8}")

print()
print(f"The two answers disagree, and that is the lesson. Counting calls says")
print(f"{by_calls} is the hot function: it is called {calls[by_calls]} times, which is")
print(f"{calls[by_calls] // calls[by_work]} times more often than {by_work}. Counting work says")
print(f"{by_work}, which is called {calls[by_work]} time and does {work[by_work]:,} operations --")
print(f"{100.0 * work[by_work] / total:.0f}% of the frame on its own.")
print()
print("A call counter is the cheapest profiler there is and it is almost never")
print("the one you want. The functions that are called in a loop are cheap by")
print("construction, because a loop that calls something expensive per")
print("iteration is a loop nobody writes twice. The expensive calls are the ones")
print("made once, at the top of the frame, over the whole world.")
print()
print("So the number to sort by is the product of the two columns, and the way")
print("to get it is to count operations rather than seconds. An operation count")
print("is the same on every machine, it can be compared between two versions of")
print("the code in a test, and it does not change when the laptop is warm --")
print("which is exactly why it can be committed to a chapter like this one.")
