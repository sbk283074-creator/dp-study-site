// Adding std::move here is not a no-op and not an optimisation: it forces the
// object to be materialised in the callee's frame and then moved out, and it
// makes the elision impossible. The compiler says so.
#include <utility>

struct Tracked {
    int id;
    explicit Tracked(int i) : id(i) {}
    Tracked(const Tracked &o) : id(o.id) {}
    Tracked(Tracked &&o) noexcept : id(o.id) { o.id = -1; }
};

Tracked spelled_out() {
    Tracked local{8};
    return std::move(local);      // -Wpessimizing-move
}

int main() {
    Tracked b = spelled_out();
    return b.id;
}
