// Forwarding is not an academic exercise: a move-only type cannot be copied, so
// the only way to hand one through a wrapper is to preserve its rvalue-ness.
#include <cstdio>
#include <memory>
#include <utility>

struct Task { int id; };

void take(std::unique_ptr<Task> t) { std::printf("took task %d\n", t->id); }

template <typename T> void relay(T &&t) { take(std::forward<T>(t)); }

int main() {
    auto p = std::make_unique<Task>(Task{7});
    relay(std::move(p));                       // T = unique_ptr<Task>
    std::printf("p is now %s\n", p ? "alive" : "null");
    return 0;
}
