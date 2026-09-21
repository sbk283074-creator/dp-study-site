#include <climits>
#include <cstdint>
#include <cstdio>

static_assert(CHAR_BIT == 8, "this book assumes a byte is 8 bits");

int main() {
    std::printf("int8_t   %zu\n", sizeof(std::int8_t));
    std::printf("int16_t  %zu\n", sizeof(std::int16_t));
    std::printf("int32_t  %zu\n", sizeof(std::int32_t));
    std::printf("int64_t  %zu\n", sizeof(std::int64_t));
    std::printf("size_t   %zu\n", sizeof(std::size_t));
    std::printf("intptr_t %zu\n", sizeof(std::intptr_t));
    std::printf("float    %zu\n", sizeof(float));
    std::printf("double   %zu\n", sizeof(double));
    std::printf("int      %zu\n", sizeof(int));
    std::printf("long     %zu\n", sizeof(long));
    return 0;
}
