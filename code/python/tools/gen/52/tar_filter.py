#!/usr/bin/env python3
"""Chapter 52 demo, part 5 -- the archive format that asks you to choose.

zipfile sanitises member names on the way out and has done for a long time.
tarfile does not, because tar has to be able to represent the archives that
already exist -- absolute paths, links that point out of the tree, device nodes
-- and refusing them would make the module unable to read its own format.

So tarfile asks. Each member is offered to a filter, and the filter returns a
possibly-rewritten member or raises. Three filters ship with the module, and
this script runs the same seven members through all three.

The filters are called directly here rather than through extractall, so nothing
is written to the filesystem and the result is a property of the filter alone.
"""
import tarfile

DEST = "/srv/app/uploads"

# member name, mode, type
MEMBERS = [
    ("../escape.txt", 0o644, tarfile.REGTYPE),
    ("../../escape.txt", 0o644, tarfile.REGTYPE),
    ("a/../../escape.txt", 0o644, tarfile.REGTYPE),
    ("/abs/escape.txt", 0o644, tarfile.REGTYPE),
    ("normal.txt", 0o644, tarfile.REGTYPE),
    ("setuid", 0o4755, tarfile.REGTYPE),
    ("device", 0o644, tarfile.CHRTYPE),
]

FILTERS = [
    ("fully_trusted", tarfile.fully_trusted_filter),
    ("tar", tarfile.tar_filter),
    ("data", tarfile.data_filter),
]


def main():
    print(f"  members                            {len(MEMBERS):>3}")
    print(f"  destination                        {DEST}")
    print(f"  filters                            {len(FILTERS)}")
    print()
    print(f"    {'member':<20}{'fully_trusted':>15}{'tar':>10}{'data':>10}")

    rejected = {name: 0 for name, _ in FILTERS}
    rewritten = []
    survivors = []
    for mname, mode, mtype in MEMBERS:
        cells = []
        for fname, fn in FILTERS:
            member = tarfile.TarInfo(mname)
            member.mode, member.type = mode, mtype
            try:
                out = fn(member, DEST)
                cells.append("accepted")
                if out.name != mname:
                    rewritten.append((fname, mname, out.name))
                if fname == FILTERS[-1][0] and mname != "normal.txt":
                    survivors.append(mname)
            except tarfile.TarError:
                cells.append("rejected")
                rejected[fname] += 1
        print(f"    {mname:<20}{cells[0]:>15}{cells[1]:>10}{cells[2]:>10}")

    print()
    for name, _ in FILTERS:
        print(f"  {name:<14} rejected {rejected[name]:>2} of {len(MEMBERS)}")

    print()
    print("  members a filter accepted under a different name")
    for fname, was, now in rewritten:
        print(f"    {fname:<14} {was} -> {now}")
    if not rewritten:
        print("    (none)")

    print()
    print("  members the strictest filter still accepts, other than the")
    print("  ordinary one")
    for mname in survivors:
        print(f"    {mname}")

    print()
    print("  read the third column against the fourth. the two filters")
    print("  reject the same three traversals, and the difference between")
    print("  them is one member: the character device, which the strictest")
    print("  filter refuses because a device node is not a file you can")
    print("  write a payload into -- it is a handle to something else.")
    print()
    print("  two things neither filter does. the absolute path is not")
    print("  rejected, it is rewritten into a relative one, so the member")
    print("  lands somewhere -- just not where it asked. and the setuid")
    print("  member passes both, because a permission bit is not a path")
    print("  and neither filter is looking at permissions.")
    print()
    print("  the safe option is not the default. `extractall` without a")
    print("  filter uses fully_trusted, which is named for what it does,")
    print("  and the caller is the one who has to say otherwise.")


if __name__ == "__main__":
    main()
