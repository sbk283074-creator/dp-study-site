#include <atomic>
#include <cstdio>
#include <string>
#include <thread>

std::atomic<bool> go{false};

// A detached thread that outlives what it captured. The thread is still
// runnable when the enclosing scope ends, and it reads a string that no longer
// exists.
int main() {
    std::thread worker;
    {
        std::string request(64, 'x');
        worker = std::thread([&] {
            while (!go.load()) {
            }
            std::printf("worker read %zu bytes\n", request.size());
        });
    }  // `request` is destroyed here

    go.store(true);
    worker.join();
    return 0;
}
