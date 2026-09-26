#include <chrono>
#include <cstdio>
#include <exception>
#include <future>
#include <stdexcept>
#include <thread>

int main() {
    // A promise is the writing end of a future you create yourself. It is how
    // a worker reports one result -- or one failure -- to whoever is waiting.
    std::promise<int> done;
    std::future<int> answer = done.get_future();

    std::thread worker([&done] {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        done.set_value(42);  // move-only: a promise can be fulfilled once
    });

    std::printf("waiting...\n");
    std::printf("worker answered: %d\n", answer.get());
    worker.join();

    // The failure path matters more. Without set_exception, an exception that
    // escapes a thread function calls std::terminate and the process dies.
    std::promise<int> failing;
    std::future<int> outcome = failing.get_future();
    std::thread risky([&failing] {
        try {
            throw std::runtime_error("connection reset by peer");
        } catch (...) {
            failing.set_exception(std::current_exception());
        }
    });
    try {
        outcome.get();
    } catch (const std::runtime_error &error) {
        std::printf("delivered through the future: %s\n", error.what());
    }
    risky.join();

    // A promise that is destroyed unfulfilled breaks its future with
    // std::future_error, which is the third case a caller has to handle.
    std::future<int> orphan;
    {
        std::promise<int> abandoned;
        orphan = abandoned.get_future();
    }
    try {
        orphan.get();
    } catch (const std::future_error &error) {
        std::printf("broken promise: %s\n", error.what());
    }
    return 0;
}
