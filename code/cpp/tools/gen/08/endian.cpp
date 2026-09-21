#include <cstdint>
#include <cstdio>
#include <cstring>

int main() {
    std::uint32_t value = 0x01020304u;

    unsigned char raw[4];
    std::memcpy(raw, &value, sizeof value);
    std::printf("value = 0x%08X\n", value);
    std::printf("raw   = %02X %02X %02X %02X\n",
                (unsigned)raw[0], (unsigned)raw[1], (unsigned)raw[2], (unsigned)raw[3]);

    std::uint16_t one = 1;
    unsigned char probe[2];
    std::memcpy(probe, &one, sizeof one);
    std::printf("order = %s\n", probe[0] ? "little-endian" : "big-endian");

    unsigned char wire[4] = {
        (unsigned char)(value >> 24), (unsigned char)(value >> 16),
        (unsigned char)(value >> 8),  (unsigned char)value,
    };
    std::printf("be    = %02X %02X %02X %02X\n",
                (unsigned)wire[0], (unsigned)wire[1], (unsigned)wire[2], (unsigned)wire[3]);

    std::uint32_t back = ((std::uint32_t)wire[0] << 24) | ((std::uint32_t)wire[1] << 16) |
                         ((std::uint32_t)wire[2] << 8)  |  (std::uint32_t)wire[3];
    std::printf("back  = 0x%08X\n", back);
    return 0;
}
