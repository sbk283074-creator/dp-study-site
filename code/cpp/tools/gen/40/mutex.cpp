#include <cstdio>
#include <map>
#include <mutex>
#include <thread>
#include <vector>

std::vector<int> entries;
std::mutex log_mutex;

void record(int id, int times) {
    for (int i = 0; i < times; ++i) {
        // lock_guard unlocks on every exit path, including an exception thrown
        // by push_back. A manual lock()/unlock() pair would leave it held.
        std::lock_guard<std::mutex> guard(log_mutex);
        entries.push_back(id);
    }
}

int main() {
    std::vector<std::thread> threads;
    for (int id = 0; id < 4; ++id) threads.emplace_back(record, id, 1000);
    for (std::thread &t : threads) t.join();

    std::printf("entries = %zu\n", entries.size());
    std::map<int, int> per_thread;
    for (int id : entries) ++per_thread[id];
    for (const auto &[id, count] : per_thread) std::printf("  thread %d wrote %d\n", id, count);
    return 0;
}
