#include <cstdint>
#include <cstdio>

static const std::uint32_t READABLE   = 1u << 0;
static const std::uint32_t WRITABLE   = 1u << 1;
static const std::uint32_t EXECUTABLE = 1u << 2;
static const std::uint32_t HIDDEN     = 1u << 7;

int main() {
    std::uint32_t flags = 0;
    flags |= READABLE | EXECUTABLE;

    std::printf("flags      = 0x%02X\n", flags);
    std::printf("readable   = %s\n", (flags & READABLE)   ? "yes" : "no");
    std::printf("writable   = %s\n", (flags & WRITABLE)   ? "yes" : "no");
    std::printf("executable = %s\n", (flags & EXECUTABLE) ? "yes" : "no");
    std::printf("hidden     = %s\n", (flags & HIDDEN)     ? "yes" : "no");

    flags &= ~EXECUTABLE;
    flags |= HIDDEN;
    std::printf("after changes = 0x%02X\n", flags);
    return 0;
}
