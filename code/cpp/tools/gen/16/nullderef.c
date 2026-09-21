#include <stdio.h>

int main(void) {
    int *p = NULL;
    printf("about to write through a null pointer\n");
    *p = 1;
    printf("wrote %d\n", *p);
    return 0;
}
