#include <stdio.h>

#define BUMP_BAD(a) (a) += 1; printf("bumped to %d\n", (a))

int main(void) {
    int x = 0;
    if (x == 0)
        BUMP_BAD(x);
    else
        printf("skipped\n");
    printf("x = %d\n", x);
    return 0;
}
