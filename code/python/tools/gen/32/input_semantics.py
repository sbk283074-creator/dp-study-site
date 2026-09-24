"""Chapter 32 -- a key that is held is not the same as a key that was pressed.

Two ways to read the keyboard over the same twelve frames of input, and five
taps placed in the gaps between the frames. The count is of taps a per-frame poll
can see and of presses it reports.
"""

FRAMES = 12

# The key is down on frames 3..8 inclusive -- six frames, one press.
DOWN = {3, 4, 5, 6, 7, 8}

# Each tap is a pair of times on a continuous clock. A frame samples at the
# whole numbers, so a tap that begins and ends between two samples is never
# observed by anything that polls.
TAPS = [
    ("begins and ends between frames 5 and 6", [(5.2, 5.8)]),
    ("two taps inside frame 7", [(7.1, 7.3), (7.5, 7.7)]),
    ("two taps, still down at the sample", [(6.9, 7.4), (7.6, 7.9)]),
]


def sampled_down(intervals):
    """The frames at which a poll would see this key as down."""
    return {frame for frame in range(FRAMES)
            if any(low <= frame <= high for low, high in intervals)}


def presses(down_frames):
    """Edges: a frame where the key is down and the frame before was not."""
    return sum(1 for frame in down_frames if frame - 1 not in down_frames)


held = [frame in DOWN for frame in range(FRAMES)]
pressed = [held[frame] and not held[frame - 1] for frame in range(FRAMES)]
released = [not held[frame] and held[frame - 1] for frame in range(FRAMES)]

rows = []
for label, intervals in TAPS:
    down = sampled_down(intervals)
    seen = sum(1 for low, high in intervals
               if any(low <= frame <= high for frame in range(FRAMES)))
    rows.append((label, len(intervals), seen, presses(down)))

print(f"{FRAMES} frames of input, the key down on {len(DOWN)} of them")
print()
print(f"{'frame':>5}{'down':>7}{'pressed':>9}{'released':>10}")
print("-" * 31)
for frame in range(FRAMES):
    print(f"{frame:>5}{str(held[frame]):>7}{str(pressed[frame]):>9}"
          f"{str(released[frame]):>10}")

print()
print(f"{'taps placed in the gaps':<46}{'taps':>7}{'seen':>7}{'presses':>9}")
print("-" * 69)
for label, taps, seen, count in rows:
    print(f"{label:<46}{taps:>7}{seen:>7}{count:>9}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'frames sampled':<46}{FRAMES:>8}")
print(f"{'frames the key is down':<46}{sum(held):>8}")
print(f"{'frames held reports true':<46}{sum(held):>8}")
print(f"{'frames pressed reports true':<46}{sum(pressed):>8}")
print(f"{'frames released reports true':<46}{sum(released):>8}")
print(f"{'taps placed across the scenarios':<46}"
      f"{sum(t for _, t, _, _ in rows):>8}")
print(f"{'of those, taps a per-frame poll sees':<46}"
      f"{sum(s for _, _, s, _ in rows):>8}")
print(f"{'presses reported for those taps':<46}"
      f"{sum(c for _, _, _, c in rows):>8}")

print()
print("The first block is the whole difference between the two functions. The")
print("key is down for six frames, and `held` reports true on all six while")
print("`pressed` reports true once. Both are correct; they answer different")
print("questions. Anything that should happen once per press -- a jump, a shot,")
print("a menu selection -- must read the edge, and reading the level instead")
print("turns one jump into six.")
print()
print("The second table is the part that no amount of care in the reading can")
print("fix, because it is a limit of polling rather than a bug in the code. A")
print("tap that begins and ends between two samples is invisible: the key was")
print("never down when a frame was sampled, so there is nothing for either")
print("function to report, and the player presses a button that the game never")
print("hears.")
print()
print("The last row is the worse case, and it is the one that looks like it")
print("works. When the key is still down at the sample, the poll sees the taps --")
print("but as one. Two presses produce one jump, and the second one is gone,")
print("which is why a fighting game with a combo system cannot be built on a")
print("per-frame poll no matter how fast the frame rate is.")
print()
print("That is the argument for the event queue. Polling samples a state and is")
print("the right tool for continuous input -- movement, aiming, a held")
print("accelerator. Events are the right tool for discrete input, because the")
print("queue keeps every transition and a frame can drain all of them. Use the")
print("state for what is true now and the queue for what happened.")
