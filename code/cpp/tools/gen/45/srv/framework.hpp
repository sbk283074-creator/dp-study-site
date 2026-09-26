// ch45 generator project — the smallest framework that can be automated.
#pragma once

#include <algorithm>
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

struct TestCase {
    std::string name;
    std::function<void()> body;
};

inline std::vector<TestCase> &registry() { static std::vector<TestCase> all; return all; }
inline int &failures() { static int n = 0; return n; }
inline int &checks() { static int n = 0; return n; }
inline std::string &current() { static std::string s; return s; }

struct Registrar {
    Registrar(const char *name, std::function<void()> body) {
        registry().push_back({name, body});
    }
};

#define TEST(name)                                  \
    static void name();                             \
    static Registrar registrar_##name(#name, name); \
    static void name()

// Counted, not aborted: one run must report every problem it can find, because the
// expensive part is starting the process, not running the checks.
#define CHECK(expr)                                                            \
    do {                                                                       \
        ++checks();                                                            \
        if (!(expr)) {                                                         \
            ++failures();                                                      \
            std::fprintf(stderr, "FAIL %s check %d: %s\n", current().c_str(),  \
                         checks(), #expr);                                     \
        }                                                                      \
    } while (0)

inline int run_all() {
    // Sorted by name, not registration order. Registration order is decided by static
    // initialisation across translation units, which the standard leaves unspecified --
    // two toolchains can print the same results in a different order, and a report that
    // is not byte-stable cannot be diffed or compared against a transcript.
    std::vector<TestCase> all = registry();
    std::sort(all.begin(), all.end(),
              [](const TestCase &a, const TestCase &b) { return a.name < b.name; });
    for (const TestCase &t : all) {
        current() = t.name;
        const int before = failures();
        t.body();
        std::printf("%-44s %s\n", t.name.c_str(), failures() == before ? "ok" : "FAIL");
    }
    std::printf("%zu test(s), %d check(s), %d failure(s)\n", all.size(), checks(), failures());
    return failures() == 0 ? 0 : 1;
}
