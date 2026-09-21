// Four operators must be members, because they act on an object that already
// exists. operator= is one of them; a free function cannot be it.
struct Vec2 { double x; double y; };

Vec2 &operator=(Vec2 &a, const Vec2 &b) {
    a.x = b.x;
    a.y = b.y;
    return a;
}

int main() { return 0; }
