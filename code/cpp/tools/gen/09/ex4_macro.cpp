#include <cstdio>

#define SQUARE(x) ((x) * (x))

static int calls = 0;

static int next(void) {
    ++calls;
    return 3;
}

int main() {
    std::printf("result = %d\n", SQUARE(next()));
    std::printf("calls  = %d\n", calls);
    return 0;
}
