#ifndef POOL_H
#define POOL_H

#include <condition_variable>
#include <cstddef>
#include <deque>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

// A fixed set of workers pulling from one queue. The point of the pool is not
// speed, it is a bound: a service that spawns a thread per request eventually
// runs out of memory, and long before that it runs out of scheduler.
class ThreadPool {
public:
    explicit ThreadPool(std::size_t threads);
    ~ThreadPool();

    ThreadPool(const ThreadPool &) = delete;
    ThreadPool &operator=(const ThreadPool &) = delete;

    // Returns a future, so the caller decides when to wait and what to do with
    // an exception -- see the futures section of this chapter.
    template <class F, class... Args>
    std::future<std::invoke_result_t<std::decay_t<F>, std::decay_t<Args>...>> submit(
        F &&work, Args &&...args) {
        using Result = std::invoke_result_t<std::decay_t<F>, std::decay_t<Args>...>;
        auto bound = std::bind(std::forward<F>(work), std::forward<Args>(args)...);
        auto task = std::make_shared<std::packaged_task<Result()>>(std::move(bound));
        std::future<Result> outcome = task->get_future();
        {
            std::lock_guard<std::mutex> guard(mutex_);
            if (stopping_) throw std::runtime_error("submit() on a pool that is shutting down");
            queue_.push_back([task] { (*task)(); });
            ++submitted_;
        }
        // notify_one, not notify_all: one job arrived, one worker should wake.
        ready_.notify_one();
        return outcome;
    }

    std::size_t size() const;
    std::size_t submitted() const;
    std::size_t completed() const;

private:
    void run();

    std::vector<std::thread> workers_;
    std::deque<std::function<void()>> queue_;
    mutable std::mutex mutex_;
    std::condition_variable ready_;
    bool stopping_ = false;
    std::size_t submitted_ = 0;
    std::size_t completed_ = 0;
};

#endif
