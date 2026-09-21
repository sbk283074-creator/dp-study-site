// The same arithmetic, written with named functions. Nothing here is wrong --
// the point is what the reader has to hold in their head to read it.
#include <cstdio>

struct Vec2 { double x; double y; };

Vec2 add(Vec2 a, Vec2 b)   { return Vec2{a.x + b.x, a.y + b.y}; }
Vec2 scale(Vec2 a, double k) { return Vec2{a.x * k, a.y * k}; }

void print(Vec2 v) { std::printf("(%.1f, %.1f)\n", v.x, v.y); }

int main() {
    Vec2 a{1.0, 2.0};
    Vec2 b{3.0, 4.0};
    print(add(a, scale(b, 2.0)));
    return 0;
}
