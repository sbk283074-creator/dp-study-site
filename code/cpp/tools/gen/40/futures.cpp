#include <chrono>
#include <cstdio>
#include <future>
#include <stdexcept>
#include <thread>
#include <utility>
#include <vector>

static int work(int n) {
    int total = 0;
    for (int i = 1; i <= n; ++i) total += i;
    return total;
}

int main() {
    // std::async hands back a future immediately; get() waits for the value.
    std::vector<std::future<int>> futures;
    for (int n : {10, 100, 1000}) {
        futures.push_back(std::async(std::launch::async, work, n));
    }
    for (std::size_t i = 0; i < futures.size(); ++i) {
        std::printf("result %zu = %d\n", i, futures[i].get());
    }

    // An exception thrown inside the task is stored in the future and rethrown
    // by get(). Without get(), it is swallowed silently.
    std::future<int> broken = std::async(std::launch::async, []() -> int {
        throw std::runtime_error("the worker could not reach the database");
    });
    try {
        broken.get();
    } catch (const std::runtime_error &error) {
        std::printf("caught from the future: %s\n", error.what());
    }

    // wait_for lets a caller give up instead of blocking forever.
    std::future<int> slow = std::async(std::launch::async, [] {
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
        return 1;
    });
    const auto state = slow.wait_for(std::chrono::milliseconds(10));
    std::printf("after 10ms the slow task is %s\n",
                state == std::future_status::ready      ? "ready"
                : state == std::future_status::timeout  ? "still running"
                                                        : "deferred");
    std::printf("eventually: %d\n", slow.get());
    return 0;
}
