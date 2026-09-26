#include <atomic>
#include <cstddef>
#include <cstdio>
#include <mutex>
#include <thread>
#include <vector>

// Two pieces of state, two different tools. A single number is an atomic; a
// container is a structure, and a structure has an invariant that a single
// instruction cannot preserve.
class Stats {
public:
    void record(int ms) {
        ++requests_;
        std::lock_guard<std::mutex> guard(mutex_);
        latencies_.push_back(ms);
    }

    long requests() const { return requests_.load(); }

    long total_ms() const {
        std::lock_guard<std::mutex> guard(mutex_);
        long total = 0;
        for (int ms : latencies_) total += ms;
        return total;
    }

    std::size_t samples() const {
        std::lock_guard<std::mutex> guard(mutex_);
        return latencies_.size();
    }

private:
    std::atomic<long> requests_{0};
    mutable std::mutex mutex_;
    std::vector<int> latencies_;
};

int main() {
    Stats stats;
    std::vector<std::thread> workers;

    for (int w = 0; w < 4; ++w) {
        workers.emplace_back([&stats, w] {
            for (int i = 0; i < 10000; ++i) stats.record(w + 1);
        });
    }
    for (std::thread &t : workers) t.join();

    std::printf("requests   = %ld (4 workers x 10000)\n", stats.requests());
    std::printf("samples    = %zu\n", stats.samples());
    std::printf("total ms   = %ld (1+2+3+4 per round x 10000)\n", stats.total_ms());
    std::printf("counts agree: %s\n",
                stats.requests() == static_cast<long>(stats.samples()) ? "yes" : "NO");
    return 0;
}
