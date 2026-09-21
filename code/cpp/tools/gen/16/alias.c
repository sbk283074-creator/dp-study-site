#include <stdio.h>
#include <string.h>

int main(void) {
    float f = 1.0f;
    unsigned int bits;
    memcpy(&bits, &f, sizeof bits);      /* the defined way to reinterpret bytes */
    printf("1.0f as bits = 0x%08x\n", bits);

    float g;
    memcpy(&g, &bits, sizeof g);
    printf("back to float = %.1f\n", g);
    return 0;
}
