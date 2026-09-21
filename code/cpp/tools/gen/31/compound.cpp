// Implement += once, then express + in terms of it. One place to get the
// arithmetic right; the copy semantics come for free.
#include <cstdio>

struct Counter {
    int n = 0;
    Counter &operator+=(int k) { n += k; return *this; }   // mutates, returns *this
};

Counter operator+(Counter c, int k) { c += k; return c; }  // takes a copy

int main() {
    Counter a{10};
    a += 5;                       // a is modified in place
    Counter b = a + 3;            // a is untouched; b is a new object
    std::printf("a=%d b=%d\n", a.n, b.n);

    (b += 1) += 2;                // chains, because += returns a reference
    std::printf("b=%d\n", b.n);
    return 0;
}
