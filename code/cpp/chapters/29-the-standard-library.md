---
chapter: 29
part: 4
title: The Standard Library
summary: Use vector, string, map and optional instead of hand-rolled memory, say what you want with algorithms and lambdas instead of writing loops, and learn where the containers quietly invalidate what you are holding.
minutes: 65
tags: [stl, vector, string, array, map, unordered_map, set, iterators, algorithms, lambda, optional, accumulate]
---

Chapter 28 explained how the standard library is possible: one template, instantiated per type. This
chapter is what it actually gives you, and it is the payoff for everything in Part IV. A `std::vector`
is a rule-of-zero type that owns its memory, so Chapter 25's double free cannot happen to it. A
`std::map` is a sorted container with `find` and `insert` already written. `std::sort` works on any
container you can hand it two iterators from. The vocabulary here is what makes the rest of this book
short: instead of writing a growable array, a hash table and a sort, you choose the container whose
shape matches your data and then say what you want done to it.

## Containers: choose the shape of your data

The standard library's containers are all templates, and the first decision is always which one:

| Container | Shape | Lookup | Use when |
|---|---|---|---|
| `std::vector<T>` | growable array, contiguous | O(n) scan, O(1) index | the default; use this unless you have a reason |
| `std::array<T, N>` | fixed size, on the stack | O(1) index | the size is known at compile time |
| `std::string` | growable array of characters | O(n) scan | text |
| `std::map<K, V>` | sorted balanced tree | O(log n) | you need keys in order, or range queries |
| `std::unordered_map<K, V>` | hash table | O(1) average | you only need lookup by key |
| `std::set<T>` | sorted unique values | O(log n) | membership and ordering |
| `std::deque<T>` | growable at both ends | O(1) index | push/pop at both ends |

`std::vector` is the default and it should be. It stores its elements contiguously, which means it is
cache-friendly, it can be passed to C APIs, and its iteration is as fast as an array. Reach for something
else when you have a specific reason — an ordered key, a hash lookup, fixed size — not in advance.

```cpp run
#include <array>
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> v = {10, 20, 30};
    v.push_back(40);
    std::printf("vector: size = %zu, v[3] = %d\n", v.size(), v[3]);

    std::array<int, 4> a = {4, 8, 15, 16};
    std::printf("array:  size = %zu, a[2] = %d, sizeof = %zu\n", a.size(), a[2], sizeof(a));

    int total = 0;
    for (int x : a) total += x;
    std::printf("total = %d\n", total);
    return 0;
}
```

```text
vector: size = 4, v[3] = 40
array:  size = 4, a[2] = 15, sizeof = 16
total = 43
```

Both have `size()`, both support `[]` and range-based `for`, and both were already worth using in
Chapter 10 for the same reason: `size()` is a stored number rather than a `sizeof` calculation that
forgets about decay. The difference is where the storage lives. `std::array<int, 4>` is `16` bytes of
stack with no indirection, exactly like the C array it replaces, and its size is part of its type.
`std::vector<int>` holds a pointer to heap memory and grows as needed.

`std::string` is the container you will use more than any other, and it is a `vector<char>` with text
operations bolted on:

```cpp run
#include <cstdio>
#include <string>

int main() {
    std::string s = "build-41.log";
    std::printf("size      = %zu\n", s.size());
    std::printf("find '-'  = %zu\n", s.find('-'));
    std::printf("stem      = %s\n", s.substr(0, s.find('-')).c_str());
    std::printf("extension = %s\n", s.substr(s.rfind('.') + 1).c_str());
    std::printf("shouted   = %s\n", (s + "!").c_str());
    std::printf("contains '41': %s\n", s.find("41") != std::string::npos ? "yes" : "no");
    return 0;
}
```

```text
size      = 12
find '-'  = 5
stem      = build
extension = log
shouted   = build-41.log!
contains '41': yes
```

Compare this to the `strlen`/`strcpy`/`strstr` work of Chapter 10. `s + "!"` allocates and returns a new
string; `substr` allocates and returns a new string; nothing needs a length argument because the string
knows its own length; and none of it can run past the end of a buffer, because the buffer is managed.
The one thing to know is that `find` returns `std::string::npos` rather than a pointer, and that is what
the last line is checking. **`std::string` and `std::vector` are why most modern C++ contains no
`malloc` at all.**

## Iterators and range-based for

An **iterator** is a position in a container. `v.begin()` is the first element and `v.end()` is **one
past** the last — a half-open range, `[begin, end)`. That is why the loop condition is `!=` and not
`<`, and why an empty container has `begin() == end()`:

```cpp
for (auto it = v.begin(); it != v.end(); ++it) {
    std::printf("%d\n", *it);       // *it is the element
}
```

You rarely write that loop, because range-based `for` from Chapter 10 does it for you:

```cpp
for (int x : v) { }                  // a copy of each element
for (const int &x : v) { }           // a reference: no copy, cannot modify
for (int &x : v) { x *= 2; }         // a reference: can modify in place
```

Iterators support arithmetic when the container is contiguous, which is how you get an index back out:
`it - v.begin()` is the position of `it` as a number, and it is a `long` on this 64-bit target. A `const
auto &` in a range-based `for` over a container of strings is the idiom you will write constantly,
because it avoids copying each string.

## Algorithms: say what, not how

`<algorithm>` contains around a hundred functions, all built on the same two-iterator interface, and all
usable on any container — including the C arrays from Part I, since a pointer is an iterator:

```cpp run
#include <algorithm>
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> v = {5, 3, 9, 1, 7, 8, 2};

    std::sort(v.begin(), v.end());
    std::printf("sorted:");
    for (int x : v) std::printf(" %d", x);
    std::printf("\n");

    auto it = std::find(v.begin(), v.end(), 7);
    std::printf("found 7 at index %ld\n", it - v.begin());

    int evens = (int)std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; });
    std::printf("evens = %d\n", evens);

    std::vector<int> doubled(v.size());
    std::transform(v.begin(), v.end(), doubled.begin(), [](int x) { return x * 2; });
    std::printf("doubled:");
    for (int x : doubled) std::printf(" %d", x);
    std::printf("\n");
    return 0;
}
```

```text
sorted: 1 2 3 5 7 8 9
found 7 at index 4
evens = 2
doubled: 2 4 6 10 14 16 18
```

Four algorithms, four lines, and none of them contains a loop. `std::sort` is a hybrid quicksort
(nothing here is a bubble sort written by hand, and the hand-written ones in every codebase are slower
than this one). `std::find` returns `end()` when the value is absent, which is the standard "not found"
convention and the reason the half-open range matters. `std::count_if` takes a predicate. `std::transform`
writes into a destination you provide, which is why `doubled` had to be sized first — `transform` writes
through an output iterator and does not grow the container for you.

## Lambdas

A **lambda** is an anonymous function written where it is used:

```cpp
[](int x) { return x % 2 == 0; }        // no capture
[limit](int t) { return t > limit; }    // captures limit by value
[&total](int t) { total += t; }         // captures total by reference
```

The brackets are the **capture list**, and they are what makes lambdas more than function pointers: a
lambda can carry values from the surrounding scope into itself. `[limit]` copies `limit` into the
lambda, so the lambda still works after `limit` changes. `[&total]` refers to the enclosing `total`, so
writes go to the original — and that is also how you get a dangling reference if the lambda outlives the
variable. Capture by value unless you have a reason, and never let a lambda that captures by reference
outlive the scope it was written in.

:::note A const local does not need capturing

If a local is `const` and initialised with a constant expression, a lambda can use it without capturing
it — the compiler treats it as a compile-time constant. So this:

```cpp
const int limit = 30;
auto f = [](int t) { return t > limit; };   // compiles, no capture needed
```

is legal, and `[limit]` in the same place produces `lambda capture 'limit' is not required to be
captured for this use [-Wunused-lambda-capture]` under `-Wall -Wextra -Werror`. It is a warning rather
than an error, so the code works either way; the reason to know it is that the diagnostic looks alarming
and the fix is to delete the capture. Make the local non-`const` if you want the capture to be
meaningful, or leave it out and enjoy the constant folding.

:::

## map and set: lookup by key

`std::map<K, V>` keeps its entries sorted by key, which gives you O(log n) lookup and iteration in key
order for free:

```cpp run
#include <cstdio>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> counts;
    counts["pear"] += 1;
    counts["apple"] += 1;
    counts["apple"] += 1;
    for (const auto &kv : counts) {
        std::printf("%-6s %d\n", kv.first.c_str(), kv.second);
    }
    std::printf("has pear: %s\n", counts.count("pear") ? "yes" : "no");
    std::printf("has plum: %s\n", counts.count("plum") ? "yes" : "no");
    return 0;
}
```

```text
apple  2
pear   1
has pear: yes
has plum: no
```

The iteration printed `apple` before `pear` even though `pear` was inserted first, because a `map` is
ordered by key. Each element is a `std::pair<const std::string, int>` with `.first` and `.second`, which
is why the loop binds `const auto &kv` rather than trying to name the pair type. `counts.count(k)` is
the membership test: it returns `0` or `1` for a map, and it does **not** insert.

`std::unordered_map<K, V>` has the same interface with a hash table underneath, so lookups are O(1)
average instead of O(log n) — but iteration order is unspecified and changes as the table grows, so
never write a program whose output depends on it. `std::set<T>` is the `map` idea with no value, for
membership and ordering.

## std::optional: a value that may not be there

Returning "not found" from a function is awkward in C: you either return a sentinel that might be a real
value, or a success flag plus an out-parameter. C++17 has a type for it:

```cpp run
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

static std::optional<std::size_t> index_of(const std::vector<std::string> &v,
                                           const std::string &want) {
    for (std::size_t i = 0; i < v.size(); i++) {
        if (v[i] == want) return i;
    }
    return std::nullopt;
}

int main() {
    std::vector<std::string> names = {"ana", "bo", "cy"};

    if (auto i = index_of(names, "cy")) std::printf("cy is at index %zu\n", *i);
    else std::printf("cy is not in the list\n");

    if (auto i = index_of(names, "di")) std::printf("di is at index %zu\n", *i);
    else std::printf("di is not in the list\n");
    return 0;
}
```

```text
cy is at index 2
di is not in the list
```

`std::optional<T>` holds either a `T` or nothing. It converts to `bool`, so `if (auto i = ...)` both
declares the result and tests it — and because the declaration is inside the condition, `i` is in scope
for both branches. `*i` reaches the value, and `std::nullopt` is the empty state.

The important detail is that **index `0` is still "found"**. `optional`'s boolean conversion asks
whether a value is present, not whether it is truthy, so a function returning `optional<size_t>` reports
success for index `0` — unlike the C habit of returning `-1` and making the caller remember that `0` is a
valid answer. That is the whole reason the type exists.

## accumulate, and the end of hand-written loops

`<numeric>` has the accumulation algorithms, and they take an optional starting value and operation:

```cpp run
#include <cstdio>
#include <numeric>
#include <string>
#include <vector>

int main() {
    std::vector<int> v = {1, 2, 3, 4};
    std::printf("sum  = %d\n", std::accumulate(v.begin(), v.end(), 0));
    std::printf("prod = %d\n", std::accumulate(v.begin(), v.end(), 1, [](int a, int b) { return a * b; }));

    std::vector<std::string> words = {"one", "two", "three"};
    std::string joined = std::accumulate(words.begin(), words.end(), std::string(),
                                         [](const std::string &a, const std::string &b) {
                                             return a.empty() ? b : a + "," + b;
                                         });
    std::printf("joined = %s\n", joined.c_str());
    return 0;
}
```

```text
sum  = 10
prod = 24
joined = one,two,three
```

The starting value is what sets the type: `0` makes the result an `int`, `1` makes the product an `int`,
and `std::string()` makes the result a string. That is the one trap here — `std::accumulate(v.begin(),
v.end(), 0)` on a vector of `double` truncates to `int`, and the fix is `0.0`.

## When a container moves, what you were holding stops being valid

Every container has rules about which operations invalidate iterators, pointers and references. For
`std::vector` the rule is simple and it is the one that catches people: **adding an element may
reallocate the array, and reallocation invalidates every pointer, reference and iterator into it.**

```cpp run-san-catch
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> v = {1, 2, 3};
    int *p = &v[0];
    for (int i = 0; i < 100; i++) v.push_back(i);
    std::printf("first = %d\n", *p);
    return 0;
}
```

```text
heap-use-after-free
```

`p` pointed at the first element of the original three-element allocation. `push_back` ran out of
capacity, allocated a larger block, copied the elements across, and freed the old one — so `p` is now
pointing at freed memory, and reading it is exactly the Chapter 7 use-after-free. Nothing in the code
looks wrong, and `-Wall -Wextra` says nothing; the sanitizer catches it because the memory really was
freed.

The habit that prevents this: **do not keep a pointer or iterator into a vector across an insertion.**
Use an index (`v[0]` re-reads the current allocation), or reserve the capacity up front with
`v.reserve(103)`, or hold the pointer only for the duration of a loop that does not modify the vector.
The same caution applies to `std::string`, and to `std::unordered_map` when it rehashes.

:::scenario The word count that scanned the list

A log summariser counts how often each word appears. The first version, written by someone coming from
C, keeps a vector of `{word, count}` pairs and searches it linearly for every word:

```cpp
struct Entry { std::string word; int count; };

std::vector<Entry> counts;
for (const std::string &w : words) {
    bool found = false;
    for (Entry &e : counts) {                 // scan the whole vector, every time
        if (e.word == w) { e.count++; found = true; break; }
    }
    if (!found) counts.push_back({w, 0});
}
```

It is correct, and it is O(n·m) — for each of the *n* words it scans up to *m* distinct words. On a log
with a million lines and a hundred thousand distinct words that is 10¹¹ comparisons, and it is the
reason the summariser takes minutes instead of seconds. The rewrite uses the container whose shape
matches the problem:

```cpp run
#include <cstdio>
#include <map>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words = {"pear", "apple", "pear", "plum", "apple", "pear"};

    std::map<std::string, int> counts;
    for (const std::string &w : words) counts[w] += 1;

    std::printf("distinct = %zu\n", counts.size());
    for (const auto &kv : counts) {
        std::printf("%-6s %d\n", kv.first.c_str(), kv.second);
    }
    return 0;
}
```

```text
distinct = 3
apple  2
pear   3
plum   1
```

Two lines replaced the search: `counts[w] += 1` looks the key up in O(log n) and increments it. The
whole loop is now O(n log n), and the output is **already sorted** — the sorted-by-key iteration of a
`map` is free, and the vector version would have needed an explicit `std::sort` to get the same output.

If ordering does not matter, `std::unordered_map<std::string, int>` makes the lookup O(1) average and the
whole loop O(n). That is usually the right choice for a pure frequency count, and the reason the version
above uses `map` is that the sorted output is part of the requirement. **Choose the container from the
operations you need** — ordered iteration, or fastest lookup, or both — and the complexity follows from
the choice rather than from tuning.

:::

:::pitfall map::operator[] inserts the key when you only meant to look

`counts[k]` is documented as "the value for `k`, inserting a default-constructed one if `k` is absent."
That insertion is easy to forget, because the expression reads like a lookup:

```cpp run
#include <cstdio>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> counts;
    counts["apple"] = 2;
    std::printf("size before = %zu\n", counts.size());

    if (counts["plum"] == 0) {
        std::printf("plum is absent\n");
    }
    std::printf("size after  = %zu\n", counts.size());
    return 0;
}
```

```text
size before = 1
plum is absent
size after  = 2
```

The program asked whether `plum` was absent, printed that it was, and then reported a container with
**two** entries. The lookup created the very key it was testing for. In a word counter this is
invisible, because the new entry has a count of `0` and the totals still add up — until someone iterates
the map and finds words that never appeared in the input.

Use `find` or `count` to test without inserting:

```cpp run
#include <cstdio>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> counts;
    counts["apple"] = 2;
    std::printf("size before = %zu\n", counts.size());

    auto it = counts.find("plum");
    if (it == counts.end()) {
        std::printf("plum is absent\n");
    }
    std::printf("size after  = %zu\n", counts.size());
    return 0;
}
```

```text
size before = 1
plum is absent
size after  = 1
```

`find` returns `end()` when the key is missing and changes nothing. `count` does the same job when you
only need a yes/no. `operator[]` is for the case where you genuinely want to create-on-demand, which is
why it is the right thing in `counts[w] += 1` and the wrong thing in a membership test. The same applies
to `std::unordered_map`.

:::

## Key takeaways

- `std::vector` is the default container: contiguous, cache-friendly, growable, and a rule-of-zero type
  so it cannot leak or double-free; `std::array<T, N>` is the fixed-size version with the size in the
  type and no allocation.
- `std::string` owns its buffer and provides `size`, `find`, `substr` and `+`, replacing the
  `strlen`/`strcpy`/`strstr` work of Part I and the buffer overruns that come with it.
- Iterators are positions, and a container's range is half-open `[begin(), end())`, which is why
  comparisons are `!=` and why `it - v.begin()` gives an index.
- `<algorithm>` gives you `sort`, `find`, `count_if`, `transform` and around a hundred more, all on the
  two-iterator interface, so they work on vectors, arrays, strings and raw C arrays alike.
- A lambda is an anonymous function with a capture list; capture by value unless you need to write back,
  and never let a lambda that captures by reference outlive its scope.
- `std::map` is sorted by key with O(log n) lookup and ordered iteration; `std::unordered_map` is a hash
  table with O(1) average lookup and unspecified iteration order — never depend on that order.
- `std::optional<T>` returns "a value or nothing" without a sentinel, and its `bool` conversion asks
  whether a value is present, so index `0` is correctly reported as found.
- `std::accumulate`'s starting value sets the result type, so `0` on a vector of `double` truncates.
- Adding to a `std::vector` may reallocate and free the old array, invalidating every pointer, reference
  and iterator into it; do not hold one across an insertion.

## Practice

- [ ] Build a `std::vector<int>`, sort it with `std::sort`, print it, and use `std::find` to print the
  index of a value.
- [ ] Use `std::count_if` and `std::find_if` with a lambda that captures a threshold by value, and
  report both the count above the threshold and the index of the first one.
- [ ] Build a `std::map<std::string, int>` word counter from a vector of words and print the distinct
  count followed by each word and its count.
- [ ] Write a function returning `std::optional<std::size_t>` that finds a value, and handle both the
  found and the not-found branch at the call site.
- [ ] Use `std::accumulate` for a sum, a product with a lambda, and a string join with a `std::string`
  starting value.
- [ ] Save a pointer to a vector's first element, add enough elements to force a reallocation, then read
  through the pointer and show what the sanitizer says.

## Solutions

:::solution Exercise 1

```cpp run
#include <algorithm>
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> v = {42, 7, 19, 3, 88, 21};

    std::sort(v.begin(), v.end());
    std::printf("sorted:");
    for (int x : v) std::printf(" %d", x);
    std::printf("\n");

    auto it = std::find(v.begin(), v.end(), 19);
    std::printf("19 is at index %ld\n", it - v.begin());
    return 0;
}
```

```text
sorted: 3 7 19 21 42 88
19 is at index 2
```

`std::sort` takes the two-iterator range and sorts in place, so no new container is needed. `std::find`
returns an iterator, and subtracting `v.begin()` converts it to an index — `2` for `19`, which is the
third element. The `%ld` matches `long`, which is what `it - v.begin()` is on this 64-bit target. If the
value were absent, `it` would equal `v.end()` and the subtraction would report the size rather than a
valid index, which is why real code checks `it != v.end()` first.

:::

:::solution Exercise 2

```cpp run
#include <algorithm>
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> temps = {12, 31, 7, 25, 40, 19, 33};
    int limit = 30;

    int hot = (int)std::count_if(temps.begin(), temps.end(),
                                 [limit](int t) { return t > limit; });
    std::printf("above %d: %d days\n", limit, hot);

    auto first_hot = std::find_if(temps.begin(), temps.end(),
                                  [limit](int t) { return t > limit; });
    if (first_hot != temps.end()) {
        std::printf("first hot day is index %ld\n", first_hot - temps.begin());
    }
    return 0;
}
```

```text
above 30: 3 days
first hot day is index 1
```

Both algorithms take the same predicate, so the "above 30" test is written once and used twice. `limit`
is captured by value, which means the lambda carries its own copy and would still work if `limit` changed
afterwards. Note that `limit` is deliberately **not** `const` here: a `const` local with a constant
initialiser does not need capturing at all, and the capture would then be reported as
`-Wunused-lambda-capture`.

:::

:::solution Exercise 3

```cpp run
#include <cstdio>
#include <map>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words = {"red", "blue", "red", "green", "blue", "red"};

    std::map<std::string, int> counts;
    for (const std::string &w : words) counts[w] += 1;

    std::printf("distinct = %zu\n", counts.size());
    for (const auto &kv : counts) std::printf("%-6s %d\n", kv.first.c_str(), kv.second);
    return 0;
}
```

```text
distinct = 3
blue   2
green  1
red    3
```

Six words, three distinct, and the output is in key order because that is what a `map` guarantees —
`blue`, `green`, `red`, which is alphabetical and not insertion order. `counts[w] += 1` uses
`operator[]` deliberately: the key should be created if it is new, which is exactly the behaviour the
pitfall warns about when it happens by accident. Each element is a pair, so `kv.first` is the word and
`kv.second` is the count.

:::

:::solution Exercise 4

```cpp run
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

static std::optional<std::size_t> index_of(const std::vector<std::string> &v,
                                           const std::string &want) {
    for (std::size_t i = 0; i < v.size(); i++) {
        if (v[i] == want) return i;
    }
    return std::nullopt;
}

int main() {
    std::vector<std::string> names = {"ana", "bo", "cy"};

    if (auto i = index_of(names, "cy")) std::printf("cy is at index %zu\n", *i);
    else std::printf("cy is not in the list\n");

    if (auto i = index_of(names, "di")) std::printf("di is at index %zu\n", *i);
    else std::printf("di is not in the list\n");
    return 0;
}
```

```text
cy is at index 2
di is not in the list
```

The function has one return for the found case and one for the not-found case, and the caller handles
both without a sentinel. The important property is that a result of index `0` would still take the
`if` branch, because `optional`'s boolean conversion tests presence rather than the value — a function
using `-1` as "not found" would be wrong here, since `std::size_t` cannot hold `-1` and the caller would
have to remember which values are valid. `*i` reaches the value and is only safe inside the branch that
proved it exists.

:::

:::solution Exercise 5

```cpp run
#include <cstdio>
#include <numeric>
#include <string>
#include <vector>

int main() {
    std::vector<int> v = {2, 3, 4};

    std::printf("sum  = %d\n", std::accumulate(v.begin(), v.end(), 0));
    std::printf("prod = %d\n", std::accumulate(v.begin(), v.end(), 1,
                                              [](int a, int b) { return a * b; }));

    std::vector<std::string> parts = {"GET", "/index.html", "HTTP/1.0"};
    std::string line = std::accumulate(parts.begin(), parts.end(), std::string(),
                                       [](const std::string &a, const std::string &b) {
                                           return a.empty() ? b : a + " " + b;
                                       });
    std::printf("request = %s\n", line.c_str());
    return 0;
}
```

```text
sum  = 9
prod = 24
request = GET /index.html HTTP/1.0
```

Three different operations through one algorithm, and the starting value is what distinguishes them: `0`
for a sum, `1` for a product, and `std::string()` for a join. The string version needs the
`a.empty() ? b : a + " " + b` test because the accumulator starts empty and there is no separator before
the first element. Note also that the product uses `1` and not `0` — starting a product at `0` makes
every result `0`, which is the classic version of this mistake. Changing `0` to `0.0` would give a
`double` sum, which is the fix when the vector holds floating-point values.

:::

:::solution Exercise 6

```cpp run-san-catch
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> v = {1, 2, 3};
    int *p = &v[0];
    for (int i = 0; i < 100; i++) v.push_back(i);
    std::printf("first = %d\n", *p);
    return 0;
}
```

```text
heap-use-after-free
```

`v` was created with capacity for three elements. The `push_back` calls ran out of capacity, so the
vector allocated a larger block, copied the three elements into it, and freed the original — leaving `p`
pointing at freed memory. The sanitizer reports `READ of size 4` at that address, which is the same
use-after-free Chapter 7 taught, arriving through a container instead of a `free`. The fixes are to hold
an index instead of a pointer (`v[0]` re-reads the current allocation every time), to call
`v.reserve(103)` before the loop so no reallocation happens, or to finish using the pointer before
modifying the vector. Re-reading the address after the loop, as in `&v[0]`, would also be correct — it
is holding the *old* address across the insertion that is the bug.

:::
