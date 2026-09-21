#include "config.h"

int clamp_to_max(int value) {
    if (value > MAX_ITEMS) {
        return MAX_ITEMS;
    }
    return value;
}
