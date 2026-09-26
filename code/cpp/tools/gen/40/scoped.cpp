#include <array>
#include <atomic>
#include <cstdio>
#include <mutex>
#include <thread>

struct Account {
    int balance = 0;
    std::mutex mutex;
};

Account alice;
Account bob;

// std::scoped_lock takes any number of mutexes and acquires them with
// std::lock's deadlock-avoiding algorithm, so the order does not matter.
void transfer(Account &from, Account &to, int amount) {
    std::scoped_lock lock(from.mutex, to.mutex);
    from.balance -= amount;
    to.balance += amount;
}

void churn(int who) {
    for (int i = 0; i < 2000; ++i) {
        if (who == 0) {
            transfer(alice, bob, 1);
        } else {
            transfer(bob, alice, 1);
        }
    }
}

int main() {
    alice.balance = 5000;
    bob.balance = 5000;

    std::array<std::thread, 4> threads;
    for (int i = 0; i < 4; ++i) threads[static_cast<std::size_t>(i)] = std::thread(churn, i % 2);
    for (std::thread &t : threads) t.join();

    std::printf("alice = %d, bob = %d\n", alice.balance, bob.balance);
    std::printf("sum   = %d (started at 10000)\n", alice.balance + bob.balance);
    std::printf("money is %s\n", alice.balance + bob.balance == 10000 ? "conserved" : "MISSING");
    return 0;
}
