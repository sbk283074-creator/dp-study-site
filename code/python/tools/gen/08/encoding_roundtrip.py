"""Chapter 8 -- text is not bytes, and the length of one is not the length of the other.

Six strings, each counted as characters and as UTF-8 bytes. The result is that
`len()` of a string and `len()` of its encoding agree only for the first 128
code points, and that the last row is the one that catches people out.
"""

SAMPLES = [
    ("ascii", "hello"),
    ("latin-1", "caf\u00e9"),
    ("greek", "\u03b1\u03b2\u03b3"),
    ("cjk", "\u65e5\u672c\u8a9e"),
    ("emoji", "\U0001f642"),
    ("combining", "e\u0301"),
]

print(f"{'label':<12}{'characters':>11}{'utf-8 bytes':>12}{'bytes each':>11}"
      f"{'latin-1':>10}")
print("-" * 56)
utf8_ok = 0
latin_ok = 0
for label, text in SAMPLES:
    encoded = text.encode("utf-8")
    if encoded.decode("utf-8") == text:
        utf8_ok += 1
    try:
        latin = text.encode("latin-1")
        latin_ok += 1 if latin.decode("latin-1") == text else 0
        shown = str(len(latin))
    except UnicodeEncodeError:
        shown = "fails"
    print(f"{label:<12}{len(text):>11}{len(encoded):>12}"
          f"{len(encoded) / len(text):>11.1f}{shown:>10}")

print()
print(f"Only the first row has the same number of characters and bytes. Every")
print(f"other row is longer as bytes, by a factor that depends on which code")
print(f"points the text uses: one for ascii, two for most of the Latin and Greek")
print(f"ranges, three for CJK, four for emoji.")
print()
print(f"UTF-8 round-trips {utf8_ok} of {len(SAMPLES)} of these strings, and latin-1 round-trips")
print(f"{latin_ok} of {len(SAMPLES)}. That is the whole reason UTF-8 is the default: it can hold")
print("every code point, and the strings that are cheap in it are the ones that")
print("were already cheap.")
print()
print(f"The last row is the one worth reading twice. It is {len(SAMPLES[-1][1])} code points")
print("long and a reader sees one, because the second code point is a mark that")
print("goes on the first. Counting characters is counting code points, and a")
print("code point is not what a person sees.")
