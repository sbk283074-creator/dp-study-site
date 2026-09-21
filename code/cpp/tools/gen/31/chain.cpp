// `+` returns a temporary. Calling += on it is legal -- member functions may be
// called on rvalues -- so this compiles, runs, and quietly achieves nothing.
#include <cstdio>

struct Counter {
    int n = 0;
    Counter &operator+=(int k) { n += k; return *this; }
};

Counter operator+(Counter c, int k) { c += k; return c; }

int main() {
    Counter a{10};
    (a + 3) += 5;                 // modifies the temporary, then drops it
    std::printf("a=%d\n", a.n);   // a never changed
    return 0;
}
