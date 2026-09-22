#!/usr/bin/env python3
"""Chapter 52 demo, part 10 -- the import feature that takes four formats.

An "import your data" feature is the place where this chapter stops being
theoretical, because it is the one feature whose entire job is to accept a file
from a user and act on what is inside it. This one accepts four formats, and the
validation is an extension check and a size check, which are the two checks that
are about the file rather than about the content.

Eight uploads, two per format. Each one is offered to the feature's validation
and then to three detectors, one per capability the chapter has been counting: a
member name that is a path, an opcode that names a callable, and a declaration
that expands.
"""
import io
import pickle
import pickletools
import tarfile
import xml.etree.ElementTree as ET

ALLOWED_EXT = {".json", ".xml", ".tar", ".pkl"}
MAX_BYTES = 64 * 1024


class Export:
    def __init__(self, rows):
        self.rows = rows


def json_upload():
    return [b'{"rows": [1, 2, 3]}', b'[{"id": 1}, {"id": 2}]']


def xml_upload():
    def doc(depth):
        lines = ['<!ENTITY e0 "lol">']
        for level in range(1, depth + 1):
            lines.append(f'<!ENTITY e{level} "'
                         + "".join(f"&e{level - 1};" for _ in range(10)) + '">')
        return ('<?xml version="1.0"?>\n<!DOCTYPE r [\n' + "\n".join(lines)
                + "\n]>\n" + f"<r>&e{depth};</r>")
    return [doc(3).encode(), doc(4).encode()]


def tar_upload():
    out = []
    for name in ("../rows.csv", "a/../../rows.csv"):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            data = b"1,2,3"
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
        out.append(buf.getvalue())
    return out


def pickle_upload():
    return [pickle.dumps(Export([1, 2, 3])), pickle.dumps(Export([]))]


def carries_a_path(data, ext):
    if ext != ".tar":
        return False
    try:
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            return any(n.startswith("/") or ".." in n.split("/")
                       for n in tf.getnames())
    except tarfile.TarError:
        return False


def carries_a_callable(data, ext):
    if ext != ".pkl":
        return False
    try:
        return any(op.name in ("GLOBAL", "STACK_GLOBAL")
                   for op, _arg, _pos in pickletools.genops(data))
    except (ValueError, pickle.UnpicklingError):
        return False


def carries_an_expansion(data, ext):
    return ext == ".xml" and b"<!ENTITY" in data


def main():
    groups = [
        (".json", json_upload()),
        (".xml", xml_upload()),
        (".tar", tar_upload()),
        (".pkl", pickle_upload()),
    ]
    uploads = [(ext, data) for ext, datas in groups for data in datas]

    print(f"  formats accepted                   {len(groups):>3}")
    print(f"  uploads                            {len(uploads):>3}")
    print(f"  the feature's checks               extension, "
          f"{MAX_BYTES // 1024} KB")
    print()
    print(f"    {'upload':<12}{'bytes':>7}{'accepted':>10}{'path':>7}"
          f"{'callable':>10}{'expands':>9}")

    accepted = 0
    dangerous = 0
    for i, (ext, data) in enumerate(uploads, start=1):
        ok = ext in ALLOWED_EXT and len(data) <= MAX_BYTES
        path = carries_a_path(data, ext)
        call = carries_a_callable(data, ext)
        exp = carries_an_expansion(data, ext)
        accepted += ok
        if path or call or exp:
            dangerous += 1
        label = f"import-{i}{ext}"
        print(f"    {label:<12}{len(data):>7}{'yes' if ok else 'no':>10}"
              f"{'yes' if path else '-':>7}{'yes' if call else '-':>10}"
              f"{'yes' if exp else '-':>9}")

    print()
    print(f"  uploads the feature accepts         {accepted:>3} of "
          f"{len(uploads)}")
    print(f"  uploads whose content decides       {dangerous:>3} of "
          f"{len(uploads)}")
    biggest = max(len(d) for _e, d in uploads)
    print(f"  the largest upload                 {biggest:>3} bytes, "
          f"limit {MAX_BYTES}")

    print()
    print("  the extension check and the size check are correct and they")
    print("  pass every upload, because both of them are statements about the")
    print("  file and all three of the capabilities are statements about the")
    print("  content. a .tar well under the limit is still a well-formed tar")
    print("  that is well under the limit.")
    print()
    print("  the three detectors are not filters and they are not a")
    print("  sanitiser. each one asks a question the feature never asked: is")
    print("  any member name a path, does the pickle stream contain an opcode")
    print("  that names something, does the document declare its own")
    print("  entities. answering those three is the difference between a")
    print("  format that is accepted and a format that is understood.")
    print()
    print("  the fix is one reader per format, and none of the four uses the")
    print("  format's own constructor for the part that decides: json for the")
    print("  data, an allow-list for the type name, a member filter for the")
    print("  archive, and no entity declarations for the document.")


if __name__ == "__main__":
    main()
