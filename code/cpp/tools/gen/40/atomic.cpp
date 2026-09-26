#include <atomic>
#include <cstdio>
#include <thread>
#include <vector>

std::atomic<int> counter{0};
std::atomic<bool> ready{false};

void bump(int times) {
    for (int i = 0; i < times; ++i) counter.fetch_add(1);
}

int main() {
    std::printf("atomic<int>  lock free: %s\n", counter.is_lock_free() ? "yes" : "no");
    std::printf("atomic<bool> lock free: %s\n", ready.is_lock_free() ? "yes" : "no");

    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) threads.emplace_back(bump, 50000);
    for (std::thread &t : threads) t.join();
    std::printf("counter = %d (4 threads x 50000)\n", counter.load());

    // exchange swaps and hands back the old value.
    std::printf("exchange(99) returned %d, now %d\n", counter.exchange(99), counter.load());

    // compare_exchange_weak is the primitive every lock-free structure is
    // built from: "if it is still `expected`, write `desired`; otherwise tell
    // me what it really is".
    int expected = 99;
    const bool won = counter.compare_exchange_weak(expected, 100);
    std::printf("cas(99 -> 100) = %s, value now %d\n", won ? "won" : "lost", counter.load());

    int stale = 0;
    const bool lost = counter.compare_exchange_weak(stale, 777);
    std::printf("cas(0 -> 777)  = %s, expected updated to %d\n", lost ? "won" : "lost", stale);
    std::printf("value unchanged: %d\n", counter.load());
    return 0;
}
