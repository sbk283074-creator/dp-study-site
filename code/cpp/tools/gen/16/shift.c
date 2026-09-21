#include <stdio.h>

int main(void) {
    unsigned int u = 1u;
    printf("1u << 31 = %u\n", u << 31);
    printf("1u << 32 = %u\n", u << 32);   /* undefined: exponent == width */
    return 0;
}
