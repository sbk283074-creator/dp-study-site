#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(4 * sizeof(int));
    if (!p) return 1;
    p[0] = 10;
    p[1] = 20;
    p[2] = 30;
    p[3] = 40;
    printf("p[3] = %d\n", p[3]);
    printf("p[4] = %d\n", p[4]);   /* one past the end of the block */
    free(p);
    return 0;
}
