#include <chrono>
#include <cstdio>
#include <mutex>
#include <thread>
#include <vector>

// The mutex lives with the data it protects, and no code path outside this
// class can touch `value_` without going through it.
class Counter {
public:
    void add(int amount) {
        std::lock_guard<std::mutex> guard(mutex_);
        value_ += amount;
    }

    int value() const {
        std::lock_guard<std::mutex> guard(mutex_);
        return value_;
    }

    // try_lock never blocks: it is the right primitive when "someone else is
    // using this" is an answer rather than a reason to wait.
    bool try_add(int amount) {
        std::unique_lock<std::mutex> guard(mutex_, std::try_to_lock);
        if (!guard.owns_lock()) return false;
        value_ += amount;
        return true;
    }

    void hold_for(std::chrono::milliseconds how_long) {
        std::lock_guard<std::mutex> guard(mutex_);
        std::this_thread::sleep_for(how_long);
    }

private:
    mutable std::mutex mutex_;
    int value_ = 0;
};

int main() {
    Counter counter;
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&counter] {
            for (int n = 0; n < 50000; ++n) counter.add(1);
        });
    }
    for (std::thread &t : threads) t.join();
    std::printf("counter = %d (4 threads x 50000)\n", counter.value());

    std::thread holder([&counter] { counter.hold_for(std::chrono::milliseconds(300)); });
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    std::printf("try_add while held: %s\n", counter.try_add(1) ? "got the lock" : "refused");
    holder.join();

    std::printf("try_add when free : %s\n", counter.try_add(1) ? "got the lock" : "refused");
    std::printf("counter = %d\n", counter.value());
    return 0;
}
