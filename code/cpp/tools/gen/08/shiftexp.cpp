#include <cstdio>

int main() {
    unsigned value = 1u;
    int shift = 32;   /* the width of `unsigned` on this target */

    std::printf("%u\n", value << shift);
    return 0;
}
