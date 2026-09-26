#include <mutex>

int main() {
    std::mutex original;

    // A mutex is a movable, non-copyable resource: two objects cannot both own
    // the same lock. The compiler refuses rather than letting two threads
    // believe they hold it.
    std::mutex copy = original;
    return 0;
}
