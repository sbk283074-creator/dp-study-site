#include <stdio.h>

#define STRINGIFY(x) #x
#define CONCAT(a, b) a##b

int main(void) {
    printf("STRINGIFY(1 + 2)    = %s\n", STRINGIFY(1 + 2));
    printf("STRINGIFY(\"text\")   = %s\n", STRINGIFY("text"));

    int CONCAT(wa, ter) = 42;
    printf("water               = %d\n", water);
    return 0;
}
