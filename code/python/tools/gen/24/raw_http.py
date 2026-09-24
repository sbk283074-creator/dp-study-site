"""Chapter 24 -- an HTTP message is a line, some headers, a blank line, a body.

One request and one response, built from their parts and then taken apart again.
The count is of the headers, the bytes in the body, and whether the declared
length matches what actually arrived.
"""

SEPARATOR = "\r\n"
BOUNDARY = SEPARATOR * 2

request_body = '{"title": "write it down"}'
request_headers = [
    "Host: api.example.com",
    "Content-Type: application/json",
    f"Content-Length: {len(request_body.encode('utf-8'))}",
    "X-Request-Id: 7f3a91",
]
request_text = (f"POST /api/tasks?page=2 HTTP/1.1{SEPARATOR}"
                + SEPARATOR.join(request_headers) + BOUNDARY + request_body)

response_body = '{"error": "no such task"}'
response_headers = [
    "Content-Type: application/json",
    f"Content-Length: {len(response_body.encode('utf-8'))}",
    "Cache-Control: no-store",
]
response_text = (f"HTTP/1.1 404 Not Found{SEPARATOR}"
                 + SEPARATOR.join(response_headers) + BOUNDARY + response_body)


def parse(text):
    head, _, body = text.partition(BOUNDARY)
    lines = head.split(SEPARATOR)
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip()] = value.strip()
    return lines[0], headers, body


request_start, request_parsed, request_seen = parse(request_text)
response_start, response_parsed, response_seen = parse(response_text)


def agrees(headers, body):
    return int(headers.get("Content-Length", -1)) == len(body.encode("utf-8"))


def status_class(start):
    code = int(start.split()[1])
    return code, f"{code // 100}xx"


response_code, response_class = status_class(response_start)

print(f"{'what is counted':<42}{'request':>12}{'response':>12}")
print("-" * 66)
print(f"{'lines before the blank line':<42}"
      f"{1 + len(request_parsed):>12}{1 + len(response_parsed):>12}")
print(f"{'headers':<42}{len(request_parsed):>12}{len(response_parsed):>12}")
print(f"{'body bytes':<42}"
      f"{len(request_seen.encode('utf-8')):>12}"
      f"{len(response_seen.encode('utf-8')):>12}")
print(f"{'content-length declared':<42}"
      f"{request_parsed['Content-Length']:>12}"
      f"{response_parsed['Content-Length']:>12}")
print(f"{'declared length matches the body':<42}"
      f"{('yes' if agrees(request_parsed, request_seen) else 'no'):>12}"
      f"{('yes' if agrees(response_parsed, response_seen) else 'no'):>12}")

print()
print(f"the request line  : {request_start}")
print(f"the response line : {response_start}   (class {response_class})")
print()
print("request headers   : " + ", ".join(request_parsed))
print("response headers  : " + ", ".join(response_parsed))

print()
print("The blank line is the structure. Everything before it is lines of text")
print("that a person can read; everything after it is bytes with no shape at")
print("all, and the only thing that says where they end is Content-Length. That")
print("is why a body is not text: it can be an image, a zip file, or a string")
print("that happens to contain a blank line, and the receiver counts bytes")
print("rather than looking for a marker.")
print()
print("Which makes Content-Length a promise, and one the receiver can check --")
print("which is exactly what the last row does. Both messages here keep it, and")
print("the two ways of breaking it fail differently. A sender that declares")
print("more bytes than it sends leaves the receiver waiting for bytes that")
print("never arrive, so the download stalls and then times out. A sender that")
print("declares fewer leaves the surplus in the buffer, where the next message")
print("will be read from it. The first looks like a slow network and the")
print("second looks like corruption, and neither is a parsing mistake.")
print()
print(f"The status line is the other half. {response_class} is the class, and it is")
print("decided before the body is read: a failure carries a body, and the body")
print("here is JSON, because the error is data too. A client that checks the")
print("code and throws the body away has thrown away the only explanation it")
print("was given.")
