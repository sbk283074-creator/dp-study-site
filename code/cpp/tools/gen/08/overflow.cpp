#include <cstdio>

int main() {
    int value = 2147483647;   /* INT_MAX on a 32-bit int */

    std::printf("%d\n", value + 1);
    return 0;
}
