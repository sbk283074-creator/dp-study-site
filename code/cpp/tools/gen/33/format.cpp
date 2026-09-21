// std::format: the type is taken from the argument, not declared in the format
// string -- so there is no %lld to get wrong, and a literal format string is
// checked at compile time.
#include <cstdio>
#include <format>
#include <string>

int main() {
    std::string s = std::format("{} + {} = {}", 1, 2, 3);
    std::printf("%s\n", s.c_str());

    std::printf("%s", std::format("padded |{:>8}| left |{:<8}|\n", "ab", "cd").c_str());
    std::printf("%s", std::format("hex {:#x}  binary {:#b}\n", 255, 5).c_str());
    std::printf("%s", std::format("pi {:.3f}  sci {:.2e}\n", 3.14159, 12345.678).c_str());

    long long big = 9'000'000'000LL;
    std::printf("%s", std::format("no width guesswork: {}\n", big).c_str());
    std::printf("%s", std::format("indexed: {1} before {0}\n", "zero", "one").c_str());
    return 0;
}
