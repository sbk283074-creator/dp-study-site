#include <atomic>
#include <chrono>
#include <cstdio>
#include <mutex>
#include <shared_mutex>
#include <thread>
#include <vector>

// One writer, many readers. A plain mutex would serialise the readers too,
// which is the entire thing shared_mutex buys.
std::shared_mutex mutex;
std::atomic<int> value{0};

std::atomic<int> holding{0};
std::atomic<int> recorded{0};
std::atomic<int> release{0};
std::vector<int> seen(3);

void reader(int id) {
    std::shared_lock<std::shared_mutex> lock(mutex);
    holding.fetch_add(1);
    // All three readers get in: shared locks do not exclude each other.
    while (holding.load() < 3) {
    }
    seen[static_cast<std::size_t>(id)] = holding.load();
    recorded.fetch_add(1);
    while (release.load() == 0) {
    }  // stay inside until main says go
}

void writer() {
    std::unique_lock<std::shared_mutex> lock(mutex);
    value.store(7);
}

int main() {
    std::vector<std::thread> readers;
    for (int i = 0; i < 3; ++i) readers.emplace_back(reader, i);

    while (holding.load() < 3) {
    }
    // Wait for the *writers* of `seen`, not merely for the count. Three threads
    // have incremented `holding` by the time the loop above ends, but printing
    // `seen` here would read a slot that no reader has stored into yet -- the
    // vector's initial value, which is exactly what "reader saw 0" means.
    while (recorded.load() < 3) {
    }
    for (int s : seen) std::printf("reader saw %d readers inside\n", s);

    // The writer starts while three shared locks are held, so it must wait.
    std::thread write(writer);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::printf("writer got in while they held it : %s\n", value.load() == 0 ? "no" : "yes");

    release.store(1);
    for (std::thread &r : readers) r.join();
    write.join();
    std::printf("value after the writer           : %d\n", value.load());
    return 0;
}
