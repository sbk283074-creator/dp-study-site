#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

int main() {
    float value = -6.0f;

    std::uint32_t bits = 0;
    std::memcpy(&bits, &value, sizeof bits);

    unsigned sign = (bits >> 31) & 1u;
    unsigned exponent = (bits >> 23) & 0xFFu;
    unsigned mantissa = bits & 0x7FFFFFu;

    /* value = (-1)^sign * (1 + mantissa / 2^23) * 2^(exponent - 127) */
    double fraction = 1.0 + (double)mantissa / 8388608.0;
    double rebuilt = std::ldexp(fraction, (int)exponent - 127);
    if (sign != 0u) {
        rebuilt = -rebuilt;
    }

    std::printf("value   = %g\n", (double)value);
    std::printf("bits    = 0x%08X\n", bits);
    std::printf("rebuilt = %g\n", rebuilt);
    return 0;
}
