#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char *buf = malloc(8);
    if (!buf) return 1;
    memcpy(buf, "hello", 6);
    printf("buf = %s\n", buf);
    free(buf);
    return 0;
}
