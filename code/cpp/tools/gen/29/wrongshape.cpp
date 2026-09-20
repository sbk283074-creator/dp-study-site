#include <cstdio>
#include <string>
#include <variant>

int main() {
    std::variant<int, std::string> value = std::string("hello");

    /* The value holds a string. std::get<int> does not convert it, and does not
       return zero. It throws. */
    std::printf("the number is %d\n", std::get<int>(value));
    return 0;
}
