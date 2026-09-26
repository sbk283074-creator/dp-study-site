#include <array>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <mutex>
#include <string>
#include <thread>

std::timed_mutex first;
std::timed_mutex second;

std::atomic<int> holding{0};
std::atomic<int> tried{0};
std::array<std::string, 2> outcome;

// Two threads, two locks, opposite orders. The barriers make this observation
// rather than a race: both threads hold their first lock before either asks for
// the second, and neither releases it until both have finished asking.
void take_both(int who) {
    std::timed_mutex &mine = who == 0 ? first : second;
    std::timed_mutex &theirs = who == 0 ? second : first;
    {
        std::unique_lock<std::timed_mutex> held(mine);
        holding.fetch_add(1);
        while (holding.load() < 2) {
        }

        const bool got = theirs.try_lock_for(std::chrono::milliseconds(300));
        outcome[static_cast<std::size_t>(who)] = got ? "acquired" : "TIMED OUT";
        if (got) theirs.unlock();

        tried.fetch_add(1);
        while (tried.load() < 2) {
        }
    }
}

int main() {
    std::thread a(take_both, 0);
    std::thread b(take_both, 1);
    a.join();
    b.join();
    std::printf("thread 0 second lock: %s\n", outcome[0].c_str());
    std::printf("thread 1 second lock: %s\n", outcome[1].c_str());
    return 0;
}
