#include <stdio.h>

#define GREET  "hello"
#define PI     3.14159
#define DBL(x) ((x) * 2)

int main(void) {
    printf("GREET        = %s\n", GREET);
    printf("PI           = %.5f\n", PI);
    printf("DBL(21)      = %d\n", DBL(21));
    printf("this is line %d\n", __LINE__);
    return 0;
}
