#include <cstdint>
#include <cstdio>

static std::uint32_t swap_bytes(std::uint32_t value) {
    return ((value & 0x000000FFu) << 24) | ((value & 0x0000FF00u) << 8) |
           ((value & 0x00FF0000u) >> 8)  | ((value & 0xFF000000u) >> 24);
}

int main() {
    std::uint32_t host = 0x01020304u;
    std::uint32_t swapped = swap_bytes(host);

    std::printf("host    = 0x%08X\n", host);
    std::printf("swapped = 0x%08X\n", swapped);
    std::printf("round trip ok = %d\n", swap_bytes(swapped) == host);
    return 0;
}
