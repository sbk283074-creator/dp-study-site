#!/usr/bin/env python3
"""Chapter 52 demo, part 7 -- reviving an object, the safe way.

The goal that gets people to pickle is legitimate: a record in a stream names a
type, and something has to turn that record back into an object of that type.
The unsafe way to do it is to let the record choose the type. The safe way is to
let the record name a type and then look that name up in a dictionary you wrote.

Eight records. Four name a type the application has, three name a builtin
function, and one names something that does not exist. Two resolvers: an
allow-list, and the dynamic one that looks the name up in the builtins module.

Nothing hostile is called. The question is only whether the name resolves, which
is the step that decides whether it would be.
"""
import builtins
import json


class User:
    def __init__(self, name):
        self.name = name


class Note:
    def __init__(self, body):
        self.body = body


class Tag:
    def __init__(self, label):
        self.label = label


class Setting:
    def __init__(self, key):
        self.key = key


REGISTRY = {"User": User, "Note": Note, "Tag": Tag, "Setting": Setting}

RECORDS = [
    {"__type__": "User", "name": "ada"},
    {"__type__": "Note", "body": "milk"},
    {"__type__": "Tag", "label": "home"},
    {"__type__": "Setting", "key": "theme"},
    {"__type__": "eval", "expr": "1 + 1"},
    {"__type__": "open", "path": "/etc/hosts"},
    {"__type__": "exec", "code": "pass"},
    {"__type__": "Widget", "size": 3},
]


def build(record):
    """Construct from an allow-list. The name is a key, not a decision."""
    cls = REGISTRY.get(record["__type__"])
    if cls is None:
        raise KeyError(record["__type__"])
    return cls(**{k: v for k, v in record.items() if k != "__type__"})


def main():
    print(f"  records                            {len(RECORDS):>3}")
    print(f"  types in the allow-list            {len(REGISTRY):>3}")
    print()
    print(f"    {'type named':<14}{'allow-list':>13}{'getattr(builtins)':>20}")

    allow_resolved, dynamic_resolved, off_list = 0, 0, 0
    for record in RECORDS:
        name = record["__type__"]
        on_list = name in REGISTRY
        # resolution only: the question is whether the name is reachable,
        # not whether the call that follows it would have succeeded
        in_builtins = hasattr(builtins, name)
        if on_list:
            allow_resolved += 1
        if in_builtins:
            dynamic_resolved += 1
            if not on_list:
                off_list += 1
        print(f"    {name:<14}{'resolves' if on_list else 'no such name':>13}"
              f"{'RESOLVES' if in_builtins else 'no such name':>20}")

    built = sum(1 for r in RECORDS if r["__type__"] in REGISTRY
                and build(r) is not None)

    print()
    print(f"  allow-list resolves                 {allow_resolved:>3} of "
          f"{len(RECORDS)}   ({len(REGISTRY) - allow_resolved} not in the list)")
    print(f"  getattr(builtins, ...) resolves     {dynamic_resolved:>3} of "
          f"{len(RECORDS)}   ({off_list} of them not in the list)")
    print(f"  objects the allow-list built        {built:>3} of {len(RECORDS)}")

    print()
    print("  the allow-list resolves the four the application has and none")
    print("  of the others, so the names it can reach are the names you")
    print("  wrote down. it also builds all four, because a record whose")
    print("  fields match the constructor is a record the constructor can")
    print("  use.")
    print()
    print("  the dynamic resolver resolves none of the application's types")
    print("  -- none of them is a builtin -- and all three of the ones that")
    print("  are. it is worse than the allow-list in both directions at")
    print("  once, which is the usual shape of a resolver that trusts the")
    print("  input to name its own type. nothing hostile was called here;")
    print("  resolution is the step that decides whether it would be.")
    print()
    print("  this is the constructive half of the chapter. the record may")
    print("  carry a name; it may not carry a decision. the name is a key")
    print("  into a dictionary you wrote, which is the same fix as the sort")
    print("  key in the previous chapter.")


if __name__ == "__main__":
    main()
