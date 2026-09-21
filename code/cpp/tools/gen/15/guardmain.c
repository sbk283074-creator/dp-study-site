#include <stdio.h>

#include "settings.h"
#include "settings.h"   /* deliberately twice: the guard makes this a no-op */

int main(void) {
    printf("app = %s\n", APP_NAME);
    printf("max = %d\n", max_connections());
    return 0;
}
