// Defaulting operator<=> asks the compiler to generate all six comparisons
// from one declaration. Ordering becomes a one-liner instead of six functions
// that can disagree with each other (Chapter 31 wrote them by hand).
#include <compare>
#include <cstdio>
#include <string>
#include <vector>
#include <algorithm>

struct Version {
    int major;
    int minor;
    auto operator<=>(const Version &) const = default;
    bool operator==(const Version &) const = default;
};

int main() {
    Version a{1, 2};
    Version b{1, 3};
    Version c{1, 2};

    std::printf("a < b : %d\n", (int)(a < b));
    std::printf("a == c: %d\n", (int)(a == c));
    std::printf("a >= b: %d\n", (int)(a >= b));

    auto order = a <=> b;
    std::printf("a<=>b is less: %d\n", (int)(order == std::strong_ordering::less));

    std::vector<Version> vs{{2, 0}, {1, 5}, {1, 2}};
    std::sort(vs.begin(), vs.end());
    std::printf("sorted:");
    for (const auto &v : vs) std::printf(" %d.%d", v.major, v.minor);
    std::printf("\n");
    return 0;
}
