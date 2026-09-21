#include <iostream>

constexpr int kMax = 64;                                  // replaces #define kMax 64
inline int square(int x) { return x * x; }                // replaces #define SQUARE(x) ((x)*(x))
template <typename T> T max_of(T a, T b) { return a > b ? a : b; }

int main() {
    std::cout << "kMax         = " << kMax << "\n";
    std::cout << "square(1+2)  = " << square(1 + 2) << "\n";
    std::cout << "max_of(3, 2) = " << max_of(3, 2) << "\n";
    return 0;
}
