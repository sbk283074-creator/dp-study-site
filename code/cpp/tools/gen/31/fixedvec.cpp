// The easiest iterator is one you already had: for contiguous storage, a
// pointer satisfies every requirement, so the container just hands one out.
#include <algorithm>
#include <cstdio>

template <typename T, int N>
struct FixedVec {
    T data[N];
    int n = 0;

    void push(const T &t) { data[n++] = t; }

    using iterator       = T *;
    using const_iterator = const T *;

    iterator       begin()       { return data; }
    iterator       end()         { return data + n; }
    const_iterator begin() const { return data; }
    const_iterator end()   const { return data + n; }
};

int main() {
    FixedVec<int, 8> f;
    for (int i : {5, 3, 9, 1}) f.push(i);

    for (int x : f) std::printf("%d ", x);
    std::printf("\n");

    auto it = std::find(f.begin(), f.end(), 9);
    std::printf("9 is at index %ld\n", it - f.begin());
    std::printf("count of 3: %ld\n",
                std::count(f.begin(), f.end(), 3));
    return 0;
}
