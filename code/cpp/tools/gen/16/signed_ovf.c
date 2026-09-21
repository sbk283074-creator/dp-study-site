#include <stdio.h>
#include <limits.h>

int main(void) {
    int x = INT_MAX;
    printf("x      = %d\n", x);
    int y = x + 1;                /* undefined behaviour: signed overflow */
    printf("x + 1  = %d\n", y);
    return 0;
}
