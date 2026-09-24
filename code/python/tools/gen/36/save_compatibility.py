"""Chapter 36 -- a save file is a format, and JSON is a format with opinions.

A game state of ten entries saved two ways. The count is of entries whose type
survives the round trip, of entries whose type changes, and of entries that
cannot be written at all.
"""

import json


class Player:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __eq__(self, other):
        return (isinstance(other, Player)
                and (self.name, self.level) == (other.name, other.level))


STATE = [
    ("score", 4200, int),
    ("time", 91.5, float),
    ("name", "ada", str),
    ("finished", False, bool),
    ("last_boss", None, type(None)),
    ("inventory", ["rope", "torch"], list),
    ("settings", {"volume": 7}, dict),
    ("position", (12, 4), tuple),
    ("visited", {1, 2, 3}, set),
    ("player", Player("ada", 12), Player),
]


def as_json(value):
    return json.loads(json.dumps(value))


rows = []
for key, value, expected in STATE:
    try:
        back = as_json(value)
    except TypeError:
        rows.append((key, expected.__name__, "not writable", "raised"))
        continue
    if type(back) is expected:
        rows.append((key, expected.__name__, type(back).__name__, "kept"))
    else:
        rows.append((key, expected.__name__, type(back).__name__, "changed"))

kept = sum(1 for _, _, _, verdict in rows if verdict == "kept")
changed = sum(1 for _, _, _, verdict in rows if verdict == "changed")
raised = sum(1 for _, _, _, verdict in rows if verdict == "raised")

print(f"{len(STATE)} entries in a game state, saved through json")
print()
print(f"{'entry':<14}{'written as':<14}{'read back as':<16}{'verdict':>10}")
print("-" * 54)
for key, wrote, back, verdict in rows:
    print(f"{key:<14}{wrote:<14}{back:<16}{verdict:>10}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'entries in the state':<46}{len(STATE):>8}")
print(f"{'entries whose type survives':<46}{kept:>8}")
print(f"{'entries whose type changes':<46}{changed:>8}")
print(f"{'entries json refuses to write':<46}{raised:>8}")
print(f"{'entries a typed loader would need rules for':<46}"
      f"{len(STATE) - kept:>8}")

print()
print("Seven of the ten come back as what they were, which is why JSON is the")
print("right default and why it is easy to stop thinking about. The other three")
print("are the whole subject of a save format. The position was a tuple and is")
print("now a list -- equal to nothing that compares types, and the kind of bug")
print("that appears as a coordinate that will not index. The set of visited")
print("rooms and the player object are not JSON at all: one has no object")
print("notation and the other has no way to know which class to rebuild.")
print()
print("None of that is a defect in the library. JSON has six types and a game")
print("has more, so a save format is a decision about how to represent the")
print("difference -- and the decision has to be written down, because a save")
print("file outlives the code that wrote it. A player who comes back in two")
print("years is loading a file your program no longer exists to explain.")
print()
print("So the shape of a good save format is a version number, a plain")
print("dictionary of JSON-safe values, and a loader that knows the schema. The")
print("version is what lets the loader do something other than crash when it")
print("meets a file from an older build, and the schema is what turns the list")
print("back into a tuple and the name back into a Player. Pickle does all of")
print("that in one line and takes the decision away from you, which is the")
print("trade: convenient until the class moves, and unreadable to anyone who")
print("wants to fix a save by hand.")
