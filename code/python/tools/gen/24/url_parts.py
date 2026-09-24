"""Chapter 24 -- a URL is five parts, and the scheme supplies the rest.

Eight URLs a client meets, split into their components. The count is of the
parts the text does not contain and the scheme fills in, and of the URLs that
are not absolute at all.
"""

from urllib.parse import urlsplit

DEFAULT_PORTS = {"http": 80, "https": 443}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}

URLS = [
    "https://api.example.com/items?page=2",
    "http://localhost:8000/health",
    "https://example.com",
    "https://user@example.com/path",
    "https://example.com:8443/a?x=1#f",
    "mailto:ada@example.com",
    "/relative/path",
    "http://127.0.0.1:8000/docs",
]


def port_of(parts):
    if parts.port is not None:
        return str(parts.port), "explicit"
    if parts.scheme in DEFAULT_PORTS:
        return str(DEFAULT_PORTS[parts.scheme]), "implied"
    return "-", "none"


rows = []
for url in URLS:
    parts = urlsplit(url)
    port, how = port_of(parts)
    rows.append({
        "url": url,
        "scheme": parts.scheme or "-",
        "host": parts.hostname or "-",
        "port": port,
        "how": how,
        "userinfo": parts.username is not None,
        "local": parts.hostname in LOCAL_HOSTS,
        "query": parts.query != "",
        "fragment": parts.fragment != "",
    })

print(f"{len(rows)} URLs, split into their parts")
print()
print(f"{'url':<38}{'scheme':>8}{'host':>17}{'port':>6}{'how':>10}{'local':>7}")
print("-" * 86)
for row in rows:
    print(f"{row['url']:<38}{row['scheme']:>8}{row['host']:>17}"
          f"{row['port']:>6}{row['how']:>10}"
          f"{('yes' if row['local'] else 'no'):>7}")

print()
print(f"{'what is counted':<44}{'count':>8}")
print("-" * 52)
print(f"{'urls parsed':<44}{len(rows):>8}")
print(f"{'urls with no scheme':<44}"
      f"{sum(1 for r in rows if r['scheme'] == '-'):>8}")
print(f"{'urls with an explicit port':<44}"
      f"{sum(1 for r in rows if r['how'] == 'explicit'):>8}")
print(f"{'urls whose port the scheme implied':<44}"
      f"{sum(1 for r in rows if r['how'] == 'implied'):>8}")
print(f"{'urls with no port at all':<44}"
      f"{sum(1 for r in rows if r['how'] == 'none'):>8}")
print(f"{'urls carrying userinfo before the host':<44}"
      f"{sum(1 for r in rows if r['userinfo']):>8}")
print(f"{'urls resolving to a local host':<44}"
      f"{sum(1 for r in rows if r['local']):>8}")
print(f"{'urls with a query string':<44}"
      f"{sum(1 for r in rows if r['query']):>8}")

print()
print("The 'how' column is the first thing the text does not tell you. Three of")
print("these URLs contain no port, and the request still goes to one -- 443 for")
print("https and 80 for http, chosen by the scheme. So `https://example.com`")
print("and `https://example.com:443` are the same request written two ways,")
print("and a check that compares the strings rather than the parts will call")
print("them different.")
print()
print("The userinfo column is the one to slow down on. A URL of the form")
print("`https://user@example.com/path` sends the request to example.com;")
print("everything before the @ is a credential, not a destination. That is the")
print("whole mechanism of the link that reads as one host and resolves to")
print("another, and it is why the host is the part after the last @ and not")
print("the part after the slashes.")
print()
print("And one URL here is not absolute at all. A path with no scheme and no")
print("host is resolved against a base, so `/relative/path` means something")
print("different in every context it appears in -- which is fine for an href")
print("inside a page and useless to a client with nothing to resolve it")
print("against.")
