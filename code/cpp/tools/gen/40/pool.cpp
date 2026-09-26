#include "pool.h"

ThreadPool::ThreadPool(std::size_t threads) {
    for (std::size_t i = 0; i < threads; ++i) workers_.emplace_back(&ThreadPool::run, this);
}

ThreadPool::~ThreadPool() {
    {
        std::lock_guard<std::mutex> guard(mutex_);
        stopping_ = true;
    }
    // Every worker is blocked in wait(), so all of them have to be woken.
    ready_.notify_all();
    for (std::thread &worker : workers_) worker.join();
}

void ThreadPool::run() {
    for (;;) {
        std::function<void()> job;
        {
            std::unique_lock<std::mutex> guard(mutex_);
            // The predicate is not optional. wait() may wake spuriously, and
            // waking with an empty queue would pop from nothing.
            ready_.wait(guard, [this] { return stopping_ || !queue_.empty(); });
            if (queue_.empty()) return;  // stopping, and nothing left to do
            job = std::move(queue_.front());
            queue_.pop_front();
        }
        job();
        {
            std::lock_guard<std::mutex> guard(mutex_);
            ++completed_;
        }
    }
}

std::size_t ThreadPool::size() const { return workers_.size(); }

std::size_t ThreadPool::submitted() const {
    std::lock_guard<std::mutex> guard(mutex_);
    return submitted_;
}

std::size_t ThreadPool::completed() const {
    std::lock_guard<std::mutex> guard(mutex_);
    return completed_;
}
