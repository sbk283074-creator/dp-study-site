#include <cstdio>

#include "wire.h"

int main() {
    /* An 8-byte header: a 2-byte magic, a version, a flag byte, a 4-byte length. */
    std::uint8_t header[8];
    put_u16_be(header + 0, 0xCAFEu);
    header[2] = 2;
    header[3] = 0x05;
    put_u32_be(header + 4, 300u);

    std::printf("header:");
    for (std::size_t i = 0; i < sizeof header; ++i) {
        std::printf(" %02X", (unsigned)header[i]);
    }
    std::printf("\n");

    std::printf("magic  = 0x%04X\n", (unsigned)get_u16_be(header + 0));
    std::printf("length = %u\n", get_u32_be(header + 4));
    std::printf("set bits in length = %u\n", popcount32(get_u32_be(header + 4)));
    return 0;
}
