#include <stdio.h>
#include <limits.h>

int main(void) {
    unsigned int u = UINT_MAX;
    printf("UINT_MAX     = %u\n", u);
    u = u + 1;                     /* defined: wraps modulo 2^32 */
    printf("UINT_MAX + 1 = %u\n", u);

    unsigned int z = 0;
    printf("0 - 1        = %u\n", z - 1);
    return 0;
}
