// Returning a named local: the language already knows the object is about to
// die, so the compiler may build it directly in the caller's slot. No copy and
// no move runs -- the log says so.
#include <cstdio>

struct Tracked {
    int id;
    explicit Tracked(int i) : id(i) { std::printf("construct id=%d\n", id); }
    Tracked(const Tracked &o) : id(o.id) { std::printf("copy      id=%d\n", id); }
    Tracked(Tracked &&o) noexcept : id(o.id) { o.id = -1; std::printf("move      id=%d\n", id); }
    ~Tracked() { std::printf("destroy   id=%d\n", id); }
};

Tracked plain() {
    Tracked local{7};
    return local;                 // NRVO: one construct, zero transfers
}

int main() {
    Tracked a = plain();
    std::printf("a.id=%d\n", a.id);
    return 0;
}
