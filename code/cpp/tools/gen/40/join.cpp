#include <cstdio>
#include <thread>
#include <utility>
#include <vector>

// Each thread writes into its own slot, so the printed order is the order the
// results were requested in -- not the order the threads happened to run.
int main() {
    std::vector<int> squares(4);
    std::vector<std::thread> threads;

    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([i, &squares] { squares[static_cast<std::size_t>(i)] = i * i; });
    }

    std::printf("before join, main is still running\n");
    for (std::thread &t : threads) t.join();
    std::printf("after join, every thread has finished\n");

    for (int v : squares) std::printf("%d ", v);
    std::printf("\n");
    return 0;
}
