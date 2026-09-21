#include <cstdio>

#include "config.h"

int main() {
    std::printf("clamped 1 -> %d\n", clamp_to_max(1));
    std::printf("clamped 5 -> %d\n", clamp_to_max(5));
    std::printf("SQUARE(MAX_ITEMS) = %d\n", SQUARE(MAX_ITEMS));
    return 0;
}
