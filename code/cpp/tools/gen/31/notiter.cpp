// A range-for needs begin/end, and it needs ++, * and != on what they return.
// This iterator has the first two but not the comparison, so the loop cannot be
// written -- the requirement is real, not a convention.
#include <cstdio>

struct Iter {
    int i;
    int  operator*() const { return i; }
    Iter &operator++() { ++i; return *this; }
};

struct Range {
    Iter begin() { return Iter{0}; }
    Iter end()   { return Iter{3}; }
};

int main() {
    for (int x : Range{}) std::printf("%d\n", x);
    return 0;
}
