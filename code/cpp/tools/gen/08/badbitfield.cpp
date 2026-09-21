#include <cstdio>

struct Flags {
    unsigned readable : 1;
    unsigned writable : 1;
};

int main() {
    Flags flags{1, 0};

    std::printf("%zu\n", sizeof(flags.readable));
    return 0;
}
