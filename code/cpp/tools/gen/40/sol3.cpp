#include <cstdio>
#include <mutex>
#include <thread>
#include <utility>
#include <vector>

struct Account {
    int balance = 0;
    std::mutex mutex;
};

// Impose one global order on the two locks, using the only ordering every
// thread can agree on: the addresses. If every thread locks low-then-high,
// no thread can hold high and wait for low, so no cycle can form.
void transfer(Account &from, Account &to, int amount) {
    Account *low = &from;
    Account *high = &to;
    if (low > high) std::swap(low, high);

    std::unique_lock<std::mutex> first(low->mutex);
    std::unique_lock<std::mutex> second(high->mutex);
    from.balance -= amount;
    to.balance += amount;
}

int main() {
    std::vector<Account> accounts(4);
    for (Account &a : accounts) a.balance = 1000;

    std::vector<std::thread> threads;
    for (int i = 0; i < 8; ++i) {
        threads.emplace_back([&accounts, i] {
            for (int n = 0; n < 500; ++n) {
                const std::size_t a = static_cast<std::size_t>(i) % accounts.size();
                const std::size_t b = (static_cast<std::size_t>(i) + 1) % accounts.size();
                transfer(accounts[a], accounts[b], 1);
            }
        });
    }
    for (std::thread &t : threads) t.join();

    int total = 0;
    for (std::size_t i = 0; i < accounts.size(); ++i) {
        std::printf("account %zu = %d\n", i, accounts[i].balance);
        total += accounts[i].balance;
    }
    std::printf("total = %d (started at 4000)\n", total);
    std::printf("no thread deadlocked, money is %s\n", total == 4000 ? "conserved" : "MISSING");
    return 0;
}
