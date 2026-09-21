// The same operator written as a member. It compiles -- and it is unusable,
// because `os << v` has the stream on the left, where `this` is not.
#include <sstream>

struct Vec2 {
    double x;
    double y;
    std::ostream &operator<<(std::ostream &os) const { return os << x; }
};

int main() {
    std::ostringstream out;
    out << Vec2{1.5, 2.5};
    return 0;
}
