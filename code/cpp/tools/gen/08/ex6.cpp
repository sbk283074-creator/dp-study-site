#include <cstdint>
#include <cstdio>

static void put_u32_le(std::uint8_t *out, std::uint32_t value) {
    out[0] = (std::uint8_t)value;
    out[1] = (std::uint8_t)(value >> 8);
    out[2] = (std::uint8_t)(value >> 16);
    out[3] = (std::uint8_t)(value >> 24);
}

static std::uint32_t get_u32_le(const std::uint8_t *in) {
    return (std::uint32_t)in[0] | ((std::uint32_t)in[1] << 8) |
           ((std::uint32_t)in[2] << 16) | ((std::uint32_t)in[3] << 24);
}

int main() {
    std::uint32_t value = 0x01020304u;

    std::uint8_t le[4];
    std::uint8_t be[4];
    put_u32_le(le, value);
    be[0] = (std::uint8_t)(value >> 24);
    be[1] = (std::uint8_t)(value >> 16);
    be[2] = (std::uint8_t)(value >> 8);
    be[3] = (std::uint8_t)value;

    std::printf("le = %02X %02X %02X %02X\n",
                (unsigned)le[0], (unsigned)le[1], (unsigned)le[2], (unsigned)le[3]);
    std::printf("be = %02X %02X %02X %02X\n",
                (unsigned)be[0], (unsigned)be[1], (unsigned)be[2], (unsigned)be[3]);
    std::printf("byte-reverse of each other = %d\n",
                le[0] == be[3] && le[1] == be[2] && le[2] == be[1] && le[3] == be[0]);
    std::printf("round trip = 0x%08X\n", get_u32_le(le));
    return 0;
}
