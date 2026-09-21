// std::move on a const object is a request the compiler cannot honour: the
// result is `const T&&`, and a move constructor taking `T&&` cannot bind to
// something const. The copy constructor can, so it runs -- silently.
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
    const Tracked a{1};
    Tracked b{std::move(a)};      // says "move"; gets a copy
    std::printf("a.id=%d (unchanged: it was copied, not moved)\n", a.id);
    return 0;
}
