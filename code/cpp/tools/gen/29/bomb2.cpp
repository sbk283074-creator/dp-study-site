#include <cstdio>
#include <string>

/* The shape of the bug on its own: one frame per bracket, and no limit. */
std::size_t depth_of(const std::string &s, std::size_t i) {
    if (i >= s.size()) return 0;
    if (s[i] == '[') return 1 + depth_of(s, i + 1);
    return 0;
}

int main() {
    const std::string bomb(200000, '[');
    std::printf("nesting = %zu\n", depth_of(bomb, 0));
    return 0;
}
