// A range pipeline reads left to right and composes, instead of nesting
// temporary containers. Nothing is copied and nothing is materialised.
#include <algorithm>
#include <cstdio>
#include <numeric>
#include <ranges>
#include <string>
#include <vector>

int main() {
    std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    auto evens_doubled = v
        | std::views::filter([](int n) { return n % 2 == 0; })
        | std::views::transform([](int n) { return n * 10; });

    std::printf("evens doubled:");
    for (int x : evens_doubled) std::printf(" %d", x);
    std::printf("\n");

    std::printf("first three:");
    for (int x : evens_doubled | std::views::take(3)) std::printf(" %d", x);
    std::printf("\n");

    // std::ranges:: algorithms take the range directly -- no begin/end pair.
    std::printf("sum=%d\n", std::ranges::fold_left(v, 0, std::plus<int>{}));
    std::printf("any > 9: %s\n", std::ranges::any_of(v, [](int n) { return n > 9; })
                                 ? "yes" : "no");

    // Projection: sort by a member instead of writing a comparator.
    std::vector<std::string> words{"pear", "fig", "apple"};
    std::ranges::sort(words, {}, [](const std::string &s) { return s.size(); });
    std::printf("by length:");
    for (const auto &w : words) std::printf(" %s", w.c_str());
    std::printf("\n");
    return 0;
}
