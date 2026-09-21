// Views are lazy: building the pipeline does no work, and each element is
// pulled through the whole chain one at a time. A counting predicate proves it.
#include <cstdio>
#include <ranges>
#include <vector>

int main() {
    std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    int filter_calls = 0;
    int transform_calls = 0;

    auto pipeline = v
        | std::views::filter([&](int n) { ++filter_calls; return n % 3 == 0; })
        | std::views::transform([&](int n) { ++transform_calls; return n * 100; });

    std::printf("after building: filter=%d transform=%d\n",
                filter_calls, transform_calls);

    auto first_two = pipeline | std::views::take(2);
    std::printf("result:");
    for (int x : first_two) std::printf(" %d", x);
    std::printf("\n");

    std::printf("after two elements: filter=%d transform=%d\n",
                filter_calls, transform_calls);
    return 0;
}
