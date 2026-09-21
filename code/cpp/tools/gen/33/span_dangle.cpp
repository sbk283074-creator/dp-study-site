// A span owns nothing, so it dangles exactly as a pointer would. This one
// refers to a vector that dies when the function returns -- and here the
// compiler can see it, which is the good case.
#include <cstdio>
#include <span>
#include <vector>

std::span<int> dangling() {
    std::vector<int> v{1, 2, 3};
    return std::span<int>(v);          // v's storage dies here
}

int main() {
    std::span<int> s = dangling();
    std::printf("first=%d\n", s[0]);   // reads storage that no longer exists
    return 0;
}
