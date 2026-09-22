#!/usr/bin/env python3
"""Exercise 4 -- five messages, two readers, and the bytes nobody read.

The same framing question as part 8 over a shorter stream, with one addition:
when the trusting reader dies, the number of bytes it never consumed. Those
bytes are the ones that get attributed to the next sender, and the count is the
size of the mistake.
"""
LIMIT = 64

# declared length, the bytes that actually follow
FRAMES = [
    (4, b"abcd"),
    (2, b"abcd"),
    (64, b"y" * 64),
    (100, b"z"),
    (3, b"xyz"),
]


def stream():
    return b"".join(f"{n}\n".encode() + body + b"\n" for n, body in FRAMES)


def read_trusting(data, frames):
    i = 0
    while i < len(data):
        j = data.index(b"\n", i)
        declared = int(data[i:j])
        i = j + 1
        body = data[i:i + declared]
        i += declared
        trailer = data[i:i + 1]
        i += 1
        frames.append((declared, body, trailer, i))
    return i


def read_bounded(data, limit):
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

    frames = []
    stop = "-"
    try:
        read_trusting(data, frames)
    except ValueError as exc:
        stop = f"ValueError: {exc}"
    # how far the reader got before it died: the offset after the last
    # frame it managed to read
    consumed = frames[-1][3] if frames else 0

    accepted, rejected = read_bounded(data, LIMIT)

    print()
    print("  the reader that believes the number")
    for declared, body, trailer, at in frames:
        mark = "consistent" if trailer == b"\n" else "MISALIGNED"
        print(f"    declared {declared:>4}  read {len(body):>4} bytes  "
              f"next byte {trailer!r:>6}  {mark}")
    print(f"    stopped: {stop}")

    print()
    print(f"  frames it read                     {len(frames):>3} of "
          f"{len(FRAMES)}")
    print(f"  bytes it consumed                  {consumed:>3} of {len(data)}")
    print(f"  bytes it never read                {len(data) - consumed:>3}")

    print()
    print("  the reader that reads to the delimiter")
    print(f"    accepted {len(accepted)} of {len(FRAMES)}")
    for declared, got, why in rejected:
        print(f"    rejected  declared {declared:>4}  got {got:>4} bytes"
              f"  {why}")

    print()
    print("  the first reader is not merely wrong about one message. it read")
    print("  a length of two, took two bytes, and left the rest of that")
    print("  message standing where the next length should be -- so the next")
    print("  thing it tries to parse as a number is a letter.")
    print()
    print("  the number worth carrying is the last one. those bytes are not")
    print("  lost, they are misattributed: whatever is downstream of this")
    print("  reader will see them as part of something else, and the")
    print("  messages after the mistake will be attributed to the wrong")
    print("  sender. a framing bug is a misattribution bug.")


if __name__ == "__main__":
    main()
