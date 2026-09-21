// A move-only type passed as an lvalue through a forwarding wrapper: T deduces
// to unique_ptr<Task>&, forward yields an lvalue, and the copy constructor --
// which unique_ptr deletes -- is the one that gets selected.
#include <memory>
#include <utility>

struct Task { int id; };

void take(std::unique_ptr<Task> t) { (void)t; }

template <typename T> void relay(T &&t) { take(std::forward<T>(t)); }

int main() {
    auto p = std::make_unique<Task>(Task{7});
    relay(p);                  // lvalue: this cannot work
    return 0;
}
