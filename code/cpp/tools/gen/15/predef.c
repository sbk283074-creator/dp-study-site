#include <stdio.h>

int main(void) {
    printf("__LINE__         = %d\n", __LINE__);
    printf("__STDC__         = %d\n", __STDC__);
    printf("__STDC_VERSION__ = %ldL\n", (long)__STDC_VERSION__);
    printf("__func__         = %s\n", __func__);
    return 0;
}
