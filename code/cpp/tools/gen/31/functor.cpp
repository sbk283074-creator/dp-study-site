// operator() makes an object callable. A "functor" carries state a free
// function cannot, which is why algorithms take one.
#include <algorithm>
#include <cstdio>
#include <vector>

struct DivisibleBy {
    int d;
    bool operator()(int n) const { return n % d == 0; }
};

int main() {
    std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    int threes = 0;
    for (int n : v) if (DivisibleBy{3}(n)) ++threes;
    std::printf("multiples of 3: %d\n", threes);

    long twos = std::count_if(v.begin(), v.end(), DivisibleBy{2});
    std::printf("multiples of 2: %ld\n", twos);
    return 0;
}
