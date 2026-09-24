"""Chapter 28 -- a WebSocket starts as an HTTP request with one extra header.

Four client keys, each hashed with the protocol's fixed GUID to produce the accept
value the server must send back. The count is of keys that produce a distinct
value, and of keys that reproduce the documented example.
"""

import base64
import hashlib

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

KEYS = [
    ("the documented example", "dGhlIHNhbXBsZSBub25jZQ=="),
    ("a browser key", "x3JJHMbDL1EzLkh9GBhXDw=="),
    ("a short key", "aGVsbG8gd29ybGQ="),
    ("an all-zero key", "AAAAAAAAAAAAAAAAAAAAAA=="),
]

EXAMPLE_ACCEPT = "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="


def accept(key):
    digest = hashlib.sha1((key + GUID).encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")


def without_guid(key):
    digest = hashlib.sha1(key.encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")


rows = [(label, key, accept(key), without_guid(key)) for label, key in KEYS]

print(f"{len(rows)} client keys, hashed with the protocol's GUID")
print()
print(f"{'key':<24}{'accept value':<30}{'length':>7}")
print("-" * 61)
for label, _, value, _ in rows:
    print(f"{label:<24}{value:<30}{len(value):>7}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'keys tried':<46}{len(rows):>8}")
print(f"{'distinct accept values':<46}"
      f"{len({value for _, _, value, _ in rows}):>8}")
print(f"{'accept values of the same length':<46}"
      f"{len({len(value) for _, _, value, _ in rows}):>8}")
print(f"{'keys that reproduce the documented example':<46}"
      f"{sum(1 for _, _, value, _ in rows if value == EXAMPLE_ACCEPT):>8}")
print(f"{'keys whose value changes when the GUID is dropped':<46}"
      f"{sum(1 for _, _, value, naive in rows if value != naive):>8}")

print()
print("The handshake is ordinary HTTP until the last two headers, and that is")
print("the point of it: a GET with `Upgrade: websocket` and a random client key")
print("looks like any other request to a proxy, a load balancer or a log, so")
print("nothing in the path has to be taught a new protocol. The server answers")
print("101 and the connection stops being HTTP.")
print()
print("The accept value is the one piece of arithmetic in the exchange, and it")
print("is deliberately not an echo. The server hashes the client's key")
print("together with a constant defined by the specification, so the value it")
print("sends back proves it knows the protocol rather than proving it read the")
print("request. Drop the GUID and every value changes, which is the last row.")
print()
print("Every accept value is the same length, because it is base64 of a")
print("twenty-byte SHA-1 digest -- 28 characters, always. That makes it cheap")
print("to check and cheap to test: the documented example is a fixed pair, so")
print("a server that reproduces it is very likely correct, and one that does")
print("not is certainly wrong. It is the same shape of test as the CSRF token")
print("earlier in the chapter: a derived value with one known-good example.")
