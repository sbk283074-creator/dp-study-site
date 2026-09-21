#include <cstdio>

struct Vec2 { double x; double y; };

// Non-member: neither operand is privileged, which is what lets `2.0 * b`
// work later on.
Vec2 operator+(Vec2 a, Vec2 b)    { return Vec2{a.x + b.x, a.y + b.y}; }
Vec2 operator*(Vec2 a, double k)  { return Vec2{a.x * k, a.y * k}; }
Vec2 operator*(double k, Vec2 a)  { return a * k; }

void print(Vec2 v) { std::printf("(%.1f, %.1f)\n", v.x, v.y); }

int main() {
    Vec2 a{1.0, 2.0};
    Vec2 b{3.0, 4.0};
    print(a + b * 2.0);   // * still binds tighter than +: a + (b * 2)
    print(2.0 * a + b);
    return 0;
}
