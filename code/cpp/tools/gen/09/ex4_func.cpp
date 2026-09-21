#include <cstdio>

static int calls = 0;

static int next(void) {
    ++calls;
    return 3;
}

static int square(int value) {
    return value * value;
}

int main() {
    std::printf("result = %d\n", square(next()));
    std::printf("calls  = %d\n", calls);
    return 0;
}
