#include <atomic>
#include <cstdio>
#include <thread>
#include <vector>

// `[&, i]` captures the loop variable by value. Every thread gets its own copy,
// taken at the moment the lambda was created.
int main() {
    std::atomic<bool> go{false};
    std::vector<int> results(4, -1);
    std::vector<std::thread> threads;

    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&, i] {
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
