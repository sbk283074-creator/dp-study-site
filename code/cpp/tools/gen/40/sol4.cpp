#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <memory>
#include <deque>
#include <functional>
#include <future>
#include <mutex>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

// `wait()` blocks until every submitted job has finished, so a caller can hand
// over a batch and then collect it without sleeping and hoping.
class Pool {
public:
    explicit Pool(std::size_t workers) {
        for (std::size_t i = 0; i < workers; ++i) threads_.emplace_back(&Pool::run, this);
    }

    ~Pool() {
        {
            std::lock_guard<std::mutex> guard(mutex_);
            stopping_ = true;
        }
        work_.notify_all();
        for (std::thread &t : threads_) t.join();
    }

    template <class F>
    std::future<std::invoke_result_t<std::decay_t<F>>> submit(F &&job) {
        using Result = std::invoke_result_t<std::decay_t<F>>;
        auto task = std::make_shared<std::packaged_task<Result()>>(std::forward<F>(job));
        std::future<Result> outcome = task->get_future();
        {
            std::lock_guard<std::mutex> guard(mutex_);
            queue_.push_back([task] { (*task)(); });
            ++submitted_;
        }
        work_.notify_one();
        return outcome;
    }

    void wait() {
        std::unique_lock<std::mutex> guard(mutex_);
        // The predicate must cover *in flight* as well as queued: an empty
        // queue with four workers still running is not idle.
        idle_.wait(guard, [this] { return queue_.empty() && busy_ == 0; });
    }

    std::size_t submitted() const { return submitted_.load(); }
    std::size_t completed() const { return completed_.load(); }

private:
    void run() {
        for (;;) {
            std::function<void()> job;
            {
                std::unique_lock<std::mutex> guard(mutex_);
                work_.wait(guard, [this] { return stopping_ || !queue_.empty(); });
                if (queue_.empty()) return;
                job = std::move(queue_.front());
                queue_.pop_front();
                ++busy_;
            }
            job();
            {
                std::lock_guard<std::mutex> guard(mutex_);
                --busy_;
                ++completed_;
            }
            idle_.notify_all();
        }
    }

    std::vector<std::thread> threads_;
    std::deque<std::function<void()>> queue_;
    std::mutex mutex_;
    std::condition_variable work_;
    std::condition_variable idle_;
    bool stopping_ = false;
    std::size_t busy_ = 0;
    std::atomic<std::size_t> submitted_{0};
    std::atomic<std::size_t> completed_{0};
};

int main() {
    Pool pool(4);
    std::vector<std::future<int>> results;
    for (int i = 0; i < 20; ++i) {
        results.push_back(pool.submit([i] {
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
            return i * i;
        }));
    }

    pool.wait();  // every job has finished, but the workers stay alive
    std::printf("after wait(): submitted = %zu, completed = %zu\n", pool.submitted(),
                pool.completed());

    int total = 0;
    for (std::future<int> &f : results) total += f.get();
    std::printf("sum of squares 0..19 = %d\n", total);
    std::printf("batch is %s\n", pool.completed() == 20 ? "complete" : "INCOMPLETE");
    return 0;
}
