// `auto &&` in a range-for deduces too: it binds to whatever the container
// yields, so `auto &&` mutates the elements in place while `auto` copies them.
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> v{1, 2, 3};

    std::printf("inside `auto`   :");
    for (auto x : v) { x *= 2; std::printf(" %d", x); }
    std::printf("\n");

    std::printf("vector after    :");
    for (int x : v) std::printf(" %d", x);
    std::printf("\n");

    for (auto &&x : v) x *= 2;       // x is int& bound to the element
    std::printf("after `auto&&`  :");
    for (int x : v) std::printf(" %d", x);
    std::printf("\n");
    return 0;
}
