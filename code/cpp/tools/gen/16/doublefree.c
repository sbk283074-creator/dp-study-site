#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));
    if (!p) return 1;
    *p = 1;
    free(p);
    free(p);       /* double free */
    return 0;
}
