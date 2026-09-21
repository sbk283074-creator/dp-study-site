#include <cstdint>
#include <cstdio>

static std::uint32_t set_bit(std::uint32_t reg, unsigned n) {
    return reg | (1u << n);
}

static std::uint32_t clear_bit(std::uint32_t reg, unsigned n) {
    return reg & ~(1u << n);
}

static std::uint32_t toggle_bit(std::uint32_t reg, unsigned n) {
    return reg ^ (1u << n);
}

static unsigned test_bit(std::uint32_t reg, unsigned n) {
    return (reg >> n) & 1u;
}

static unsigned extract(std::uint32_t reg, unsigned hi, unsigned lo) {
    unsigned width = hi - lo + 1;
    return (reg >> lo) & ((1u << width) - 1u);
}

static std::uint32_t insert(std::uint32_t reg, unsigned hi, unsigned lo, std::uint32_t value) {
    unsigned width = hi - lo + 1;
    std::uint32_t mask = ((1u << width) - 1u) << lo;
    return (reg & ~mask) | ((value << lo) & mask);
}

int main() {
    std::uint32_t instr = 0;
    instr = insert(instr, 31, 26, 0x23u);   /* opcode */
    instr = insert(instr, 25, 21, 8u);      /* rs     */
    instr = insert(instr, 20, 16, 9u);      /* rt     */
    instr = insert(instr, 15, 0, 0x0010u);  /* immediate */

    std::printf("instruction = 0x%08X\n", instr);
    std::printf("opcode=%u rs=%u rt=%u imm=%u\n",
                extract(instr, 31, 26), extract(instr, 25, 21),
                extract(instr, 20, 16), extract(instr, 15, 0));

    std::uint32_t reg = 0;
    reg = set_bit(reg, 3);
    reg = set_bit(reg, 7);
    std::printf("after set 3,7 = 0x%02X\n", reg);
    reg = toggle_bit(reg, 3);
    std::printf("after toggle 3 = 0x%02X\n", reg);
    reg = clear_bit(reg, 7);
    std::printf("after clear 7  = 0x%02X\n", reg);
    std::printf("bit 3 = %u, bit 7 = %u\n", test_bit(reg, 3), test_bit(reg, 7));
    return 0;
}
