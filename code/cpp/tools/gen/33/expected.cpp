// std::expected<T, E>: either a value or a reason. Unlike an exception it is a
// return value, and unlike an error code the value and the reason are in one
// object and cannot be silently ignored.
#include <cstdio>
#include <expected>
#include <string>
#include <string_view>

std::expected<int, std::string> parse_positive(std::string_view text) {
    if (text.empty()) return std::unexpected("empty input");
    int n = 0;
    for (char c : text) {
        if (c < '0' || c > '9') return std::unexpected("not a number");
        n = n * 10 + (c - '0');
    }
    if (n == 0) return std::unexpected("must be positive");
    return n;
}

int main() {
    for (std::string_view in : {"42", "abc", "", "0", "7"}) {
        std::expected<int, std::string> r = parse_positive(in);
        if (r) std::printf("%s -> %d\n", std::string(in).c_str(), *r);
        else   std::printf("%s -> error: %s\n", std::string(in).c_str(), r.error().c_str());
    }

    int doubled = parse_positive("21").value_or(0) * 2;
    std::printf("value_or fallback: %d\n", doubled);

    auto chained = parse_positive("10").and_then([](int n) -> std::expected<int, std::string> {
        return n * 3;
    });
    std::printf("and_then: %d\n", chained.value_or(-1));
    return 0;
}
