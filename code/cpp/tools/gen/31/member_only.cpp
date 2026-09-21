// operator* as a MEMBER: the left operand must be a Vec2, because a member
// operator is a call with the left operand as `this`.
#include <cstdio>

struct Vec2 {
    double x;
    double y;
    Vec2 operator*(double k) const { return Vec2{x * k, y * k}; }
};

int main() {
    Vec2 a{1.0, 2.0};
    Vec2 b = 2.0 * a;                 // scalar on the left
    std::printf("%.1f %.1f\n", b.x, b.y);
    return 0;
}
