import dis

LIMIT = 100
WATCHED = {"LOAD_GLOBAL", "LOAD_FAST", "LOAD_FAST_LOAD_FAST", "LOAD_ATTR", "COMPARE_OP"}

def uses_global(xs):
    out = []
    for x in xs:
        if x < LIMIT:
            out.append(x)
    return out

def uses_local(xs):
    limit = LIMIT
    out = []
    for x in xs:
        if x < limit:
            out.append(x)
    return out

def show(fn):
    print(f"{fn.__name__}:")
    for ins in dis.get_instructions(fn):
        if ins.opname in WATCHED:
            print(f"    {ins.opname:<20} {ins.argrepr}")
    print()

show(uses_global)
show(uses_local)
