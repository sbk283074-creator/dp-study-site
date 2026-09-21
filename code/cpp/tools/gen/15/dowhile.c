#include <stdio.h>

#define BUMP(a) do { (a) += 1; printf("bumped to %d\n", (a)); } while (0)

int main(void) {
    int x = 0;
    if (x == 0)
        BUMP(x);
    else
        printf("skipped\n");
    printf("x = %d\n", x);
    return 0;
}
