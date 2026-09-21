#include <stdio.h>

#define LEVEL 2

int main(void) {
#if !defined(LEVEL)
#error "LEVEL must be defined"
#endif

#if LEVEL >= 3
    printf("level 3: verbose diagnostics\n");
#elif LEVEL == 2
    printf("level 2: normal diagnostics\n");
#else
    printf("level 1: quiet\n");
#endif

#ifdef __clang__
    printf("built with clang\n");
#else
    printf("built with something else\n");
#endif
    return 0;
}
