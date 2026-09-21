#include <cstdint>
#include <cstdio>

int main() {
    std::uint8_t byte = 0xB5u;   /* 1011 0101 */

    std::printf("bits:");
    unsigned set = 0;
    for (int i = 7; i >= 0; --i) {
        unsigned bit = ((unsigned)byte >> (unsigned)i) & 1u;
        std::printf(" %u", bit);
        set += bit;
    }
    std::printf("\nset bits = %u\n", set);
    return 0;
}
