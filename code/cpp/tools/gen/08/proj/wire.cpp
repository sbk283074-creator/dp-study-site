#include "wire.h"

void put_u16_be(std::uint8_t *out, std::uint16_t value) {
    out[0] = (std::uint8_t)(value >> 8);
    out[1] = (std::uint8_t)value;
}

void put_u32_be(std::uint8_t *out, std::uint32_t value) {
    out[0] = (std::uint8_t)(value >> 24);
    out[1] = (std::uint8_t)(value >> 16);
    out[2] = (std::uint8_t)(value >> 8);
    out[3] = (std::uint8_t)value;
}

std::uint16_t get_u16_be(const std::uint8_t *in) {
    return (std::uint16_t)(((std::uint16_t)in[0] << 8) | (std::uint16_t)in[1]);
}

std::uint32_t get_u32_be(const std::uint8_t *in) {
    return ((std::uint32_t)in[0] << 24) | ((std::uint32_t)in[1] << 16) |
           ((std::uint32_t)in[2] << 8)  |  (std::uint32_t)in[3];
}

unsigned popcount32(std::uint32_t value) {
    unsigned count = 0;

    while (value != 0u) {
        count += value & 1u;
        value >>= 1;
    }
    return count;
}
