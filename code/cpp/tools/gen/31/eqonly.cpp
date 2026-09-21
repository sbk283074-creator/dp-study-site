// C++17 does NOT derive != from ==. Defining one says nothing about the other.
#include <cstdio>

struct Point { int x; int y; };

bool operator==(Point a, Point b) { return a.x == b.x && a.y == b.y; }

int main() {
    Point p{1, 2};
    Point q{1, 2};
    std::printf("%s\n", (p != q) ? "different" : "same");
    return 0;
}
