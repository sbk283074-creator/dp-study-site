#include <cstdio>
#include <string>

/* One code point in, the bytes UTF-8 writes for it out. */
std::string utf8(unsigned cp) {
    std::string out;
    if (cp < 0x80) {
        out += static_cast<char>(cp);
    } else if (cp < 0x800) {
        out += static_cast<char>(0xC0 | (cp >> 6));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        out += static_cast<char>(0xE0 | (cp >> 12));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else {
        out += static_cast<char>(0xF0 | (cp >> 18));
        out += static_cast<char>(0x80 | ((cp >> 12) & 0x3F));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    }
    return out;
}

/* The arithmetic that turns \ud83d\ude00 into one character. */
unsigned from_surrogates(unsigned high, unsigned low) {
    return 0x10000u + ((high - 0xD800u) << 10) + (low - 0xDC00u);
}

int main() {
    const unsigned points[] = {0x41, 0xE9, 0x20AC, 0x1F600};
    std::printf("code point -> the bytes on the wire\n");
    std::printf("-----------------------------------\n");
    for (unsigned cp : points) {
        const std::string bytes = utf8(cp);
        std::printf("  U+%04X -> %zu byte(s):", cp, bytes.size());
        for (unsigned char b : bytes) std::printf(" %02x", b);
        std::printf("   %s\n", bytes.c_str());
    }

    std::printf("\ntwo escapes, one character\n");
    std::printf("--------------------------\n");
    const unsigned high = 0xD83D, low = 0xDE00;
    const unsigned cp = from_surrogates(high, low);
    std::printf("  U+%04X and U+%04X together are U+%05X\n", high, low, cp);
    std::printf("  which is %s\n", utf8(cp).c_str());
    std::printf("  and it needs %zu bytes, not 2\n", utf8(cp).size());
    return 0;
}
