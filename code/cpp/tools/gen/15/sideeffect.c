#include <stdio.h>

#define MAX_NAIVE(a, b) ((a) > (b) ? (a) : (b))

static int max_fn(int a, int b) { return a > b ? a : b; }

int main(void) {
    int i = 3;
    int r1 = MAX_NAIVE(i++, 2);
    printf("MAX_NAIVE(i++, 2) = %d   i is now %d\n", r1, i);

    int j = 3;
    int r2 = max_fn(j++, 2);
    printf("max_fn(j++, 2)    = %d   j is now %d\n", r2, j);
    return 0;
}
