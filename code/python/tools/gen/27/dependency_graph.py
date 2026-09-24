"""Chapter 27 -- a dependency is built once per request, unless you say otherwise.

A graph of four dependencies and two endpoints that both ask for the bottom of it.
The count is of constructions per request, with the cache on and off.
"""

GRAPH = {
    "settings": [],
    "database": ["settings"],
    "repository": ["database"],
    "service": ["repository"],
}

ENDPOINTS = [
    ("list items", "service"),
    ("create item", "service"),
]


def construct(name, cache, built):
    if cache and name in built:
        return
    for parent in GRAPH[name]:
        construct(parent, cache, built)
    built[name] = built.get(name, 0) + 1


def resolve(cache):
    built = {}
    for _, wanted in ENDPOINTS:
        construct(wanted, cache, built)
    return built


with_cache = resolve(True)
without_cache = resolve(False)
NAMES = list(GRAPH)

print(f"{len(NAMES)} dependencies, {len(ENDPOINTS)} endpoints, one request each")
print()
print(f"{'dependency':<16}{'with cache':>12}{'without cache':>15}")
print("-" * 43)
for name in NAMES:
    print(f"{name:<16}{with_cache.get(name, 0):>12}{without_cache.get(name, 0):>15}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'dependencies in the graph':<46}{len(NAMES):>8}")
print(f"{'endpoints asking for the same dependency':<46}{len(ENDPOINTS):>8}")
print(f"{'constructions with the cache on':<46}"
      f"{sum(with_cache.values()):>8}")
print(f"{'constructions with the cache off':<46}"
      f"{sum(without_cache.values()):>8}")
print(f"{'constructions the cache removed':<46}"
      f"{sum(without_cache.values()) - sum(with_cache.values()):>8}")

print()
print("The first column is the default. A dependency declared with `Depends` is")
print("built once per request, however many places ask for it, so the chain")
print("here costs four constructions rather than eight. That is not an")
print("optimisation you switch on -- it is the behaviour, and the reason two")
print("handlers can both depend on the current user and get the same object.")
print()
print("The second column is what happens without it, and the shape of the")
print("number is the point: every dependency is built twice, once for each")
print("endpoint that asked. Settings are parsed twice, the database handle is")
print("opened twice, and the repository is created twice. On one request that")
print("is four wasted objects; across a service it is the difference between a")
print("connection pool and a connection per call.")
print()
print("Which leads to the rule about what a dependency may hold. The cache is")
print("scoped to a single request, so a dependency is the right place for the")
print("current user, the request id, or a parsed body -- and the wrong place")
print("for anything you want shared across requests. A connection pool belongs")
print("to the process, created at startup and closed at shutdown; a per-request")
print("dependency that opens a connection is a pool you did not build.")
