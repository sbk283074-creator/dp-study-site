// A ring buffer: the elements are NOT in storage order once it has wrapped, so
// the iterator has to do arithmetic. That is the whole job of an iterator --
// present a logical sequence over whatever layout you actually chose.
#include <algorithm>
#include <cstddef>
#include <cstdio>
#include <iterator>
#include <numeric>

template <typename T, std::size_t N>
class Ring {
    T buf[N];
    std::size_t head = 0;    // next slot to write
    std::size_t count = 0;   // how many are live

public:
    void push(T v) {
        buf[head] = v;
        head = (head + 1) % N;
        if (count < N) ++count;
    }
    std::size_t size() const { return count; }

    class iterator {
        Ring *owner;
        std::size_t index;                 // logical position, 0 .. count
    public:
        // The five typedefs are how the standard library asks what this is.
        using iterator_category = std::forward_iterator_tag;
        using value_type        = T;
        using difference_type   = std::ptrdiff_t;
        using pointer           = T *;
        using reference         = T &;

        iterator(Ring *o, std::size_t i) : owner(o), index(i) {}

        reference operator*() const {
            std::size_t start = (owner->head + N - owner->count) % N;
            return owner->buf[(start + index) % N];
        }
        iterator &operator++() { ++index; return *this; }
        iterator  operator++(int) { iterator tmp = *this; ++index; return tmp; }
        bool operator==(const iterator &o) const {
            return owner == o.owner && index == o.index;
        }
        bool operator!=(const iterator &o) const { return !(*this == o); }
    };

    iterator begin() { return iterator(this, 0); }
    iterator end()   { return iterator(this, count); }
};

int main() {
    Ring<int, 3> r;
    for (int i = 1; i <= 5; ++i) r.push(i);   // 1 and 2 are overwritten

    std::printf("size=%zu contents:", r.size());
    for (int x : r) std::printf(" %d", x);
    std::printf("\n");

    auto it = std::find(r.begin(), r.end(), 4);
    std::printf("found 4: %s\n", it != r.end() ? "yes" : "no");
    std::printf("sum=%d\n", std::accumulate(r.begin(), r.end(), 0));
    return 0;
}
