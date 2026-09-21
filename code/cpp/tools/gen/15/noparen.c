#include <stdio.h>

#define SQUARE_NAIVE(x) x * x
#define SQUARE_SAFE(x)  ((x) * (x))

int main(void) {
    printf("SQUARE_NAIVE(1 + 2) = %d\n", SQUARE_NAIVE(1 + 2));
    printf("SQUARE_SAFE(1 + 2)  = %d\n", SQUARE_SAFE(1 + 2));

    int n = 1 + 2;
    printf("SQUARE_NAIVE(n)     = %d   (n = %d)\n", SQUARE_NAIVE(n), n);
    return 0;
}
