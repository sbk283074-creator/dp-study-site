#include <climits>
#include <cstdio>

static void print_bits(unsigned value, int width) {
    for (int i = width - 1; i >= 0; --i) {
        std::putchar(((value >> (unsigned)i) & 1u) ? '1' : '0');
        if (i % 4 == 0 && i != 0) {
            std::putchar(' ');
        }
    }
}

int main() {
    unsigned char v = 0x9Cu;

    std::printf("CHAR_BIT   = %d\n", CHAR_BIT);
    std::printf("v          = 0x%02X  ", (unsigned)v);
    print_bits(v, 8);
    std::printf("\n");

    std::printf("v & 0x0F   = 0x%02X\n", (unsigned)(v & 0x0Fu));
    std::printf("v | 0x01   = 0x%02X\n", (unsigned)(v | 0x01u));
    std::printf("v ^ 0xFF   = 0x%02X\n", (unsigned)(v ^ 0xFFu));
    std::printf("~v         = 0x%02X\n", (unsigned)(unsigned char)~v);

    std::printf("v << 1     = 0x%02X\n", (unsigned)(unsigned char)(v << 1));
    std::printf("v >> 1     = 0x%02X\n", (unsigned)(unsigned char)(v >> 1));
    std::printf("bit 7 of v = %u\n", (v >> 7) & 1u);
    std::printf("bit 2 of v = %u\n", (v >> 2) & 1u);

    return 0;
}
