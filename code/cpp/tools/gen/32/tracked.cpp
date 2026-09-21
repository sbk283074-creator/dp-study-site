// std::move does not move anything. It is a cast. This type logs every
// constructor so you can see which one actually ran.
#include <cstdio>
#include <utility>

struct Tracked {
    int id;
    explicit Tracked(int i) : id(i) { std::printf("construct id=%d\n", id); }
    Tracked(const Tracked &o) : id(o.id) { std::printf("copy      id=%d\n", id); }
    Tracked(Tracked &&o) noexcept : id(o.id) { o.id = -1; std::printf("move      id=%d\n", id); }
    ~Tracked() { std::printf("destroy   id=%d\n", id); }
};

int main() {
    Tracked a{1};
    Tracked b{a};                 // copy constructor
    Tracked c{std::move(a)};      // move constructor -- a's id becomes -1
    std::printf("a.id=%d\n", a.id);
    return 0;
}
