#include <stdio.h>

int main(void) {
    unsigned int u = 1u;
    int n = 32;                    /* a variable: invisible to the compiler */
    printf("1u << %d = %u\n", n, u << n);
    return 0;
}
