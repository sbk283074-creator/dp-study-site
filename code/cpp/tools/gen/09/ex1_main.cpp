#include <cstdio>

#include "stats.h"

int main() {
    const int readings[5] = {4, 9, 2, 7, 5};
    const std::size_t count = sizeof(readings) / sizeof(readings[0]);

    std::printf("sum     = %d\n", sum(readings, count));
    std::printf("maximum = %d\n", maximum(readings, count));
    return 0;
}
