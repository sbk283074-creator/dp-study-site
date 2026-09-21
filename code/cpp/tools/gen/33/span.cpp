// std::span is a (pointer, length) pair with an interface. It owns nothing --
// which is the point: a function that only reads can take a span and stop
// caring whether the caller used a vector, an array or a malloc'd block.
#include <algorithm>
#include <array>
#include <cstdio>
#include <numeric>
#include <span>
#include <vector>

int sum(std::span<const int> s) {
    return std::accumulate(s.begin(), s.end(), 0);
}

int main() {
    std::vector<int> v{1, 2, 3, 4, 5};
    std::array<int, 3> a{10, 20, 30};

    std::printf("vector: %d\n", sum(v));
    std::printf("array:  %d\n", sum(a));

    std::span<int> s{v};
    std::printf("first=%d last=%d size=%zu\n", s.front(), s.back(), s.size());

    std::span<int> middle = s.subspan(1, 3);        // elements 1,2,3
    std::printf("middle: %d\n", sum(middle));

    std::fill(s.begin(), s.end(), 0);               // writes through the span
    std::printf("after fill: %d\n", sum(v));        // v itself changed
    return 0;
}
