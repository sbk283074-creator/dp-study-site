#include <cstdio>

/* Declared, never defined in this translation unit. */
const char *greeting();

int main() {
    std::printf("%s\n", greeting());
    return 0;
}
