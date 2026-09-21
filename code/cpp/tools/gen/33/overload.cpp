// Constrained overloads: the concept selects the function, which is the clean
// way to write "this version for integers, that one for everything else".
#include <concepts>
#include <cstdio>
#include <string>

void describe(std::integral auto n) { std::printf("integer %lld\n", (long long)n); }
void describe(std::floating_point auto x) { std::printf("float %.2f\n", (double)x); }
void describe(const std::string &s) { std::printf("string %s\n", s.c_str()); }

int main() {
    describe(42);
    describe(2.5);
    describe(std::string("hi"));
    return 0;
}
