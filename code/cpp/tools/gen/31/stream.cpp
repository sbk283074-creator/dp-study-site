// operator<< has to be a non-member: the stream is the LEFT operand, and you do
// not own std::ostream.
#include <cstdio>
#include <sstream>

struct Vec2 { double x; double y; };

std::ostream &operator<<(std::ostream &os, Vec2 v) {
    return os << "(" << v.x << ", " << v.y << ")";
}

int main() {
    std::ostringstream out;
    out << Vec2{1.5, 2.5} << " and " << Vec2{-1.0, 0.0};
    std::printf("%s\n", out.str().c_str());
    return 0;
}
