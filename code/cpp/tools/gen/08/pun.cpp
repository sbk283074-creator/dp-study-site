#include <cstdint>
#include <cstdio>
#include <cstring>

static std::uint32_t bits_of(float value) {
    std::uint32_t bits = 0;
    std::memcpy(&bits, &value, sizeof bits);
    return bits;
}

static void describe(float value) {
    std::uint32_t bits = bits_of(value);
    unsigned sign = (bits >> 31) & 1u;
    unsigned biased = (bits >> 23) & 0xFFu;
    unsigned mantissa = bits & 0x7FFFFFu;

    std::printf("%-5g bits=0x%08X sign=%u exponent=%u (2^%d) mantissa=0x%06X\n",
                (double)value, bits, sign, biased, (int)biased - 127, mantissa);
}

int main() {
    describe(1.0f);
    describe(0.5f);
    describe(-2.0f);
    describe(0.1f);
    return 0;
}
