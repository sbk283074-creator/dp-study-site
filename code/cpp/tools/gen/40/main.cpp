#include "pool.h"

#include <cstdio>
#include <vector>

namespace {

bool is_prime(int n) {
    if (n < 2) return false;
    for (int d = 2; d * d <= n; ++d) {
        if (n % d == 0) return false;
    }
    return true;
}

int count_primes(int low, int high) {
    int found = 0;
    for (int n = low; n < high; ++n) {
        if (is_prime(n)) ++found;
    }
    return found;
}

}  // namespace

int main() {
    ThreadPool pool(4);
    std::printf("workers = %zu\n", pool.size());

    std::vector<std::future<int>> results;
    for (int slice = 0; slice < 8; ++slice) {
        const int low = slice * 50000 + 1;
        results.push_back(pool.submit(count_primes, low, low + 50000));
    }

    // The futures are collected in submission order even though the slices
    // finish in whatever order the workers get to them.
    int total = 0;
    for (std::size_t i = 0; i < results.size(); ++i) {
        const int found = results[i].get();
        total += found;
        std::printf("slice %zu: %d primes\n", i, found);
    }
    std::printf("total: %d primes below 400001\n", total);

    std::printf("submitted = %zu, completed = %zu\n", pool.submitted(), pool.completed());
    return 0;
}
