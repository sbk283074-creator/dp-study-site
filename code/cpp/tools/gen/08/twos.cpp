#include <cstdint>
#include <cstdio>

int main() {
    std::uint8_t byte = 0xFFu;
    std::int8_t signed_byte = (std::int8_t)byte;

    std::printf("0xFF as uint8_t = %u\n", (unsigned)byte);
    std::printf("0xFF as int8_t  = %d\n", (int)signed_byte);

    std::uint8_t wrapped = (std::uint8_t)(byte + 1u);
    std::printf("0xFF + 1 in uint8_t = %u\n", (unsigned)wrapped);

    std::int32_t negative = -8;
    std::uint32_t bits = (std::uint32_t)negative;
    std::printf("-8 as uint32_t  = %u\n", bits);

    std::printf("~0u             = %u\n", ~0u);
    std::printf("~0              = %d\n", ~0);
    return 0;
}
