#!/usr/bin/env python3
"""Exercise 2 -- eight member names, two archive readers, one table.

The same question as parts 4 and 5 over a longer list, with both modules side by
side so the comparison is in one place.

The two columns are measured differently and the difference is deliberate.
tarfile's filter is the function that decides, so it is called directly and the
name it returns is the answer. zipfile's decision is inside its extract path, so
the archive is built and extracted and the answer is where the bytes ended up.
"""
import os
import tarfile
import tempfile
import zipfile

NAMES = [
    "../escape.txt",
    "../../escape.txt",
    "../../../escape.txt",
    "a/../../escape.txt",
    "a/b/../../../escape.txt",
    "/abs/escape.txt",
    "..\\escape.txt",
    "normal.txt",
]

DEST = "/srv/app/uploads"


def zip_result(name):
    """Extract one member and report the path it landed on."""
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
        escaped = False
        for root, _dirs, files in os.walk(td):
            for f in files:
                full = os.path.realpath(os.path.join(root, f))
                if full == real_archive:
                    continue
                if not (full == real_dest or full.startswith(real_dest + os.sep)):
                    escaped = True
                landed.append(os.path.relpath(full, real_dest))
        return ", ".join(sorted(landed)), escaped


def tar_result(name):
    """Ask the strictest filter tarfile ships what it would do."""
    member = tarfile.TarInfo(name)
    member.mode, member.type = 0o644, tarfile.REGTYPE
    try:
        return tarfile.data_filter(member, DEST).name, False
    except tarfile.TarError:
        return "refused", False


def main():
    print(f"  member names                       {len(NAMES):>3}")
    print(f"  destination                        {DEST}")
    print()
    print(f"    {'member':<25}{'zipfile writes':<22}{'tarfile (data)':>15}")

    zip_rewritten = 0
    tar_refused = 0
    escaped_any = 0
    for name in NAMES:
        z, escaped = zip_result(name)
        t, _ = tar_result(name)
        if z != name:
            zip_rewritten += 1
        if t == "refused":
            tar_refused += 1
        if escaped:
            escaped_any += 1
        print(f"    {name:<25}{z:<22}{t:>15}")

    print()
    print(f"  names zipfile writes under a new one   {zip_rewritten:>2} of "
          f"{len(NAMES)}")
    print(f"  names the data filter refuses          {tar_refused:>2} of "
          f"{len(NAMES)}")
    print(f"  names that left the destination        {escaped_any:>2} of "
          f"{len(NAMES)}")
    print()
    print("  the two columns disagree on the five names that walk upward.")
    print("  zipfile never refuses a member -- it rewrites the name so that")
    print("  the write cannot leave -- so on those five it writes a file the")
    print("  filter would have stopped. the disagreement is not about where")
    print("  the file lands. it is about whether there is a file at all.")
    print()
    print("  they agree on the absolute one, and that agreement is worth a")
    print("  second look: both strip the leading slash and produce")
    print("  `abs/escape.txt`, so the member is written to a directory the")
    print("  archive never named. neither module calls that an escape,")
    print("  because it is not one.")
    print()
    print("  for an import feature the refusal is usually the behaviour you")
    print("  want. a member that asked to be written somewhere else is not a")
    print("  member you asked for, and silently writing it under a new name")
    print("  means the archive's own manifest no longer describes what was")
    print("  unpacked.")


if __name__ == "__main__":
    main()
