// A concept is a named requirement, checked at the call site and reported as
// such. Two concepts, one that composes them, and a static_assert.
#include <concepts>
#include <cstdio>

template <typename T>
concept Number = std::integral<T> || std::floating_point<T>;

template <typename T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
};

template <typename T>
concept Arithmetic = Number<T> && Addable<T>;

template <Arithmetic T>
T twice(T n) { return n + n; }

static_assert(Arithmetic<int>);
static_assert(Arithmetic<double>);
static_assert(!Arithmetic<const char *>);

int main() {
    std::printf("%d\n", twice(21));
    std::printf("%.1f\n", twice(1.5));
    return 0;
}
