#include <atomic>
#include <cstdio>
#include <thread>
#include <vector>

// `[&]` captures the loop variable by reference. The loop is over by the time
// any thread runs, so every thread reads the same `i` -- and that `i` is 4,
// one past the end of the vector.
int main() {
    std::atomic<bool> go{false};
    std::vector<int> results(4, -1);
    std::vector<std::thread> threads;

    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&] {
            while (!go.load()) {
            }
            results[static_cast<std::size_t>(i)] = i;
        });
    }

    go.store(true);
    for (std::thread &t : threads) t.join();
    for (int v : results) std::printf("%d ", v);
    std::printf("\n");
    return 0;
}
