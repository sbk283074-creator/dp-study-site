#include <cstddef>
#include <cstdio>
#include <string>

static bool is_continuation(unsigned char byte) { return (byte & 0xC0) == 0x80; }

static bool valid_utf8(const std::string &s) {
    std::size_t i = 0;
    while (i < s.size()) {
        const unsigned char lead = static_cast<unsigned char>(s[i]);
        std::size_t extra = 0;
        if (lead < 0x80) extra = 0;
        else if ((lead & 0xE0) == 0xC0) extra = 1;
        else if ((lead & 0xF0) == 0xE0) extra = 2;
        else if ((lead & 0xF8) == 0xF0) extra = 3;
        else return false;
        if (i + extra >= s.size()) return false;
        for (std::size_t k = 1; k <= extra; ++k) {
            if (!is_continuation(static_cast<unsigned char>(s[i + k]))) return false;
        }
        i += extra + 1;
    }
    return true;
}

// Cutting UTF-8 at an arbitrary byte offset can land inside a character. The
// result is not a shorter string, it is an invalid one.
std::string truncate_utf8(const std::string &s, std::size_t limit) {
    if (s.size() <= limit) return s;
    std::size_t end = limit;
    if (is_continuation(static_cast<unsigned char>(s[end]))) {
        // Walk back to the lead byte, then cut before it: a lead byte on its
        // own is just as invalid as a dangling continuation.
        while (end > 0 && is_continuation(static_cast<unsigned char>(s[end]))) --end;
    }
    return s.substr(0, end);
}

static void show(const char *label, const std::string &s) {
    std::printf("%-14s", label);
    for (const char c : s) std::printf(" %02x", static_cast<unsigned char>(c));
    // Only print the text when it is valid: an invalid sequence is the point of
    // the example, and printing it would make this captured transcript
    // unreadable rather than instructive.
    std::printf("   valid=%-3s  text=%s\n", valid_utf8(s) ? "yes" : "NO",
                valid_utf8(s) ? s.c_str() : "(not printable)");
}

int main() {
    // Built from code points so the byte sequence is explicit:
    // c a f é(2 bytes) space 你(3) 好(3) 世(3) 界(3)  ->  17 bytes
    const std::string text = "café 你好世界";
    std::printf("full (%zu bytes)\n", text.size());
    show("full", text);
    std::printf("\n");

    for (const std::size_t limit : {std::size_t{7}, std::size_t{8}}) {
        std::printf("limit %zu\n", limit);
        show("  naive", text.substr(0, limit));
        show("  safe", truncate_utf8(text, limit));
        std::printf("\n");
    }
    return 0;
}
