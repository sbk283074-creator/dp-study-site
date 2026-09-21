#include "stats.h"

int sum(const int *values, std::size_t count) {
    int total = 0;

    for (std::size_t i = 0; i < count; ++i) {
        total += values[i];
    }
    return total;
}

int maximum(const int *values, std::size_t count) {
    int best = values[0];

    for (std::size_t i = 1; i < count; ++i) {
        if (values[i] > best) {
            best = values[i];
        }
    }
    return best;
}
