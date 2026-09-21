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

static std::string truncate_utf8(const std::string &s, std::size_t limit) {
    if (s.size() <= limit) return s;
    std::size_t end = limit;
    if (is_continuation(static_cast<unsigned char>(s[end]))) {
        while (end > 0 && is_continuation(static_cast<unsigned char>(s[end]))) --end;
    }
    return s.substr(0, end);
}

// Order matters: cut to a character boundary FIRST, then walk back to a word
// boundary inside what is already valid text. Doing it the other way round puts
// you back at an arbitrary byte.
std::string truncate_words(const std::string &s, std::size_t limit) {
    std::string cut = truncate_utf8(s, limit);
    if (cut.size() < s.size()) {
        const std::size_t space = cut.find_last_of(' ');
        if (space != std::string::npos && space > 0) cut.erase(space);
    }
    return cut;
}

int main() {
    // Spaces between the multi-byte words, so that cutting at different offsets
    // lands in different places and the word boundary actually moves.
    const std::string text = "the quick brown fox 你好 世界 再见 朋友 jumps over";
    std::printf("full: %zu bytes\n", text.size());

    for (std::size_t limit = 21; limit <= 42; limit += 3) {
        const std::string naive = text.substr(0, limit);
        const std::string safe = truncate_words(text, limit);
        std::printf("limit %2zu  naive valid=%-3s | safe valid=%-3s  \"%s\"\n", limit,
                    valid_utf8(naive) ? "yes" : "NO", valid_utf8(safe) ? "yes" : "NO",
                    safe.c_str());
    }
    return 0;
}
