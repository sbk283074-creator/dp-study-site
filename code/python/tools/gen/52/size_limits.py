#!/usr/bin/env python3
"""Chapter 52 demo, part 8 -- the length you were told is not the length you get.

A stream of messages needs framing, and the cheap framing is to write the length
first. That puts a number from the sender into the reader's control flow: the
reader uses it to decide how many bytes belong to this message.

Seven messages. Four are honest, three declare a length that does not match the
bytes that follow, and one of those is honest-but-huge. Two readers: one that
believes the number, and one that reads to the delimiter and then checks the
number against what it actually got.
"""
LIMIT = 1024

# declared length, the bytes that actually follow
FRAMES = [
    (5, b"hello"),
    (2000, b"x" * 2000),
    (3, b"hello"),
    (9, b"hello"),
    (4, b"abcd"),
    (2, b"abcd"),
    (6, b"abcdef"),
]


def stream():
    return b"".join(f"{n}\n".encode() + body + b"\n" for n, body in FRAMES)


def read_trusting(data, frames):
    """Take the declared length as the number of bytes to read.

    Frames are appended as they are read, so a caller that catches the
    exception can still see how far this reader got before it died.
    """
    i = 0
    while i < len(data):
        j = data.index(b"\n", i)
        declared = int(data[i:j])
        i = j + 1
        body = data[i:i + declared]
        i += declared
        trailer = data[i:i + 1]
        i += 1
        frames.append((declared, body, trailer))


def read_bounded(data, limit):
    """Read to the delimiter, then check the declaration against it."""
    i = 0
    accepted, rejected = [], []
    while i < len(data):
        j = data.index(b"\n", i)
        declared = int(data[i:j])
        i = j + 1
        k = data.index(b"\n", i)
        body = data[i:k]
        i = k + 1
        if len(body) != declared:
            rejected.append((declared, len(body), "declared length"))
        elif declared > limit:
            rejected.append((declared, len(body), "over the limit"))
        else:
            accepted.append((declared, body))
    return accepted, rejected


def main():
    data = stream()
    print(f"  messages sent                      {len(FRAMES):>3}")
    print(f"  bytes on the wire                  {len(data):>3}")
    print(f"  declared length limit              {LIMIT:>3}")
    print()

    trusted = []
    stop = "-"
    try:
        read_trusting(data, trusted)
    except ValueError as exc:
        stop = f"ValueError: {exc}"

    accepted, rejected = read_bounded(data, LIMIT)

    print(f"    {'reader':<30}{'frames':>7}{'consistent':>12}"
          f"{'misaligned':>12}")
    good = sum(1 for _d, _b, trailer in trusted if trailer == b"\n")
    print(f"    {'trusts the declared length':<30}{len(trusted):>7}"
          f"{good:>12}{len(trusted) - good:>12}")
    print(f"    {'reads to the delimiter':<30}{len(accepted) + len(rejected):>7}"
          f"{len(accepted):>12}{0:>12}")

    print()
    print("  the reader that believes the number")
    for declared, body, trailer in trusted:
        mark = "consistent" if trailer == b"\n" else "MISALIGNED"
        print(f"    declared {declared:>5}  read {len(body):>5} bytes  "
              f"next byte {trailer!r:>6}  {mark}")
    print(f"    and then it stopped: {stop}")

    print()
    print("  the reader that reads to the delimiter")
    print(f"    accepted {len(accepted)} of {len(FRAMES)}")
    for declared, got, why in rejected:
        print(f"    rejected  declared {declared:>5}  got {got:>5} bytes"
              f"  {why}")

    print()
    print("  the first reader gets one message wrong and then cannot")
    print("  continue, because the bytes it did not read are now standing")
    print("  where a length is supposed to be. it read 'o' and tried to")
    print("  parse it as a number. that is the part worth carrying: a")
    print("  framing bug is not a wrong message, it is the end of the")
    print("  stream, and everything after the mistake is attributed to the")
    print("  wrong sender.")
    print()
    print("  the second reader never has that problem, because the")
    print("  delimiter decides where a message ends and the number is only")
    print("  ever a claim to be checked. it also gets the size limit for")
    print("  free, which the first reader has no way to apply: one")
    print("  consistent message of two thousand bytes is a perfectly")
    print("  well-formed frame, and it is still two thousand bytes.")


if __name__ == "__main__":
    main()
