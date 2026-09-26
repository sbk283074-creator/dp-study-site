#include <cstdio>
#include <thread>
#include <vector>

// One object per thread, with static storage duration inside that thread.
// Not shared, so not racy -- which is the whole point.
thread_local int calls = 0;
thread_local int worker_id = -1;

int record_call() {
    ++calls;
    return calls;
}

void work(int id) {
    worker_id = id;
    for (int i = 0; i < 3; ++i) record_call();
}

int main() {
    std::vector<int> seen(3);
    std::vector<std::thread> threads;
    for (int id = 0; id < 3; ++id) {
        threads.emplace_back([id, &seen] {
            work(id);
            seen[static_cast<std::size_t>(id)] = calls;   // each thread's own
        });
    }
    for (std::thread &t : threads) t.join();

    // The main thread never called record_call, so its own counter is 0.
    std::printf("main thread calls   = %d\n", calls);
    for (std::size_t i = 0; i < seen.size(); ++i) {
        std::printf("worker %zu saw       = %d\n", i, seen[i]);
    }
    return 0;
}
