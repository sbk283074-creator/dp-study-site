// The format string is checked at compile time when it is a literal, so a
// mismatch is a compile error rather than garbage at run time.
#include <format>

int main() {
    auto s = std::format("{:d}\n", 3.5);   // :d is for integers
    return static_cast<int>(s.size());
}
