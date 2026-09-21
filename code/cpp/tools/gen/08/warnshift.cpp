#include <cstdio>

int main() {
    int value = 1 << 40;   /* 40 >= the 32 bits of `int` */

    std::printf("%d\n", value);
    return 0;
}
