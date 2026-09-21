// A named rvalue reference IS an lvalue. So inside a wrapper, `x` has lost the
// information about what was passed in -- unless std::forward restores it from T.
#include <cstdio>
#include <utility>

void sink(int &)       { std::printf("sink(int&)\n"); }
void sink(const int &) { std::printf("sink(const int&)\n"); }
void sink(int &&)      { std::printf("sink(int&&)\n"); }

template <typename T> void forwarded(T &&x)      { sink(std::forward<T>(x)); }
template <typename T> void unforwarded(T &&x)    { sink(x); }

int main() {
    int i = 1;
    const int c = 2;

    std::printf("forwarded:      lvalue  -> "); forwarded(i);
    std::printf("forwarded:      const   -> "); forwarded(c);
    std::printf("forwarded:      rvalue  -> "); forwarded(5);

    std::printf("unforwarded:    lvalue  -> "); unforwarded(i);
    std::printf("unforwarded:    const   -> "); unforwarded(c);
    std::printf("unforwarded:    rvalue  -> "); unforwarded(5);
    return 0;
}
