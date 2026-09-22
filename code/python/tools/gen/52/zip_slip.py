#!/usr/bin/env python3
"""Chapter 52 demo, part 4 -- the archive member that is a path.

An archive is a list of names and the bytes to write at each one. If the writer
chooses the names and the reader writes them, the writer is choosing paths in
your filesystem. Six member names, extracted one at a time into a directory,
and the question is where each one lands.

This measures zipfile, which sanitises. The next block measures tarfile, which
takes an argument.
"""
import os
import tempfile
import zipfile

# member name, what it is trying to be
MEMBERS = [
    ("../escape.txt", "one level up"),
    ("../../escape.txt", "two levels up"),
    ("a/../../escape.txt", "up through a subdirectory"),
    ("/abs/escape.txt", "an absolute path"),
    ("..\\escape.txt", "a backslash, on POSIX"),
    ("normal.txt", "an ordinary name"),
]


def main():
    print(f"  member names                       {len(MEMBERS):>3}")
    print()
    print(f"    {'member':<22}{'lands at':<26}{'outside?':>9}")

    escaped = 0
    renamed = 0
    for name, _intent in MEMBERS:
        with tempfile.TemporaryDirectory() as td:
            archive = os.path.join(td, "x.zip")
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr(name, "owned")

            dest = os.path.join(td, "out")
            os.makedirs(dest)
            with zipfile.ZipFile(archive) as zf:
                zf.extract(name, dest)

            real_dest = os.path.realpath(dest)
            real_archive = os.path.realpath(archive)
            landed = []
            outside = False
            for root, _dirs, files in os.walk(td):
                for f in files:
                    full = os.path.realpath(os.path.join(root, f))
                    if full == real_archive:
                        continue
                    # the test is on resolved paths, not on string prefixes:
                    # a name may contain ".." and still be inside
                    inside = full == real_dest or full.startswith(
                        real_dest + os.sep)
                    if not inside:
                        outside = True
                    landed.append(os.path.relpath(full, real_dest))

            if outside:
                escaped += 1
            if landed and sorted(landed)[0] != name:
                renamed += 1

            shown = ", ".join(sorted(landed)) if landed else "(nothing written)"
            print(f"    {name:<22}{shown:<26}"
                  f"{'YES' if outside else 'no':>9}")

    print()
    print(f"  members that escaped the destination   {escaped} of "
          f"{len(MEMBERS)}")
    print(f"  members that landed under a new name   {renamed} of "
          f"{len(MEMBERS)}")
    print()
    print("  zipfile.extract sanitises the name before it writes: it drops")
    print("  the path parts that would move the write, so nothing leaves the")
    print("  destination. that is a real fix and it has been in the standard")
    print("  library for a long time.")
    print()
    print("  read the second column anyway. four of the six landed somewhere")
    print("  other than where they asked to, and two of them created a")
    print("  directory the member never named -- the absolute path became a")
    print("  relative subdirectory called 'abs'. and the backslash survived")
    print("  as a literal character in a filename, which is not an escape on")
    print("  this platform and is an escape on another. a sanitiser removes")
    print("  the traversal; it does not promise that the name you get is the")
    print("  name you asked for.")


if __name__ == "__main__":
    main()
