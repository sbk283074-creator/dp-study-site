// Reading .value() on an expected that holds an error is a checked operation:
// it throws, rather than handing back an uninitialised T.
#include <cstdio>
#include <expected>

std::expected<int, const char *> fails() { return std::unexpected("no value"); }

int main() {
    std::expected<int, const char *> r = fails();
    std::printf("%d\n", r.value());
    return 0;
}
