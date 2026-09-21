// Both of these are one line each. std::move is a cast to an rvalue reference;
// std::forward is a cast that recovers the category recorded in T.
#include <cstdio>
#include <type_traits>
#include <utility>

template <typename T>
constexpr std::remove_reference_t<T> &&my_move(T &&t) noexcept {
    return static_cast<std::remove_reference_t<T> &&>(t);
}

template <typename T>
constexpr T &&my_forward(std::remove_reference_t<T> &t) noexcept {
    return static_cast<T &&>(t);
}

void sink(int &)  { std::printf("sink(int&)\n"); }
void sink(int &&) { std::printf("sink(int&&)\n"); }

template <typename T> void relay(T &&x) { sink(my_forward<T>(x)); }

int main() {
    int i = 1;
    static_assert(std::is_same_v<decltype(my_move(i)), int &&>);
    static_assert(std::is_same_v<decltype(my_forward<int>(i)), int &&>);
    static_assert(std::is_same_v<decltype(my_forward<int &>(i)), int &>);
    static_assert(std::is_same_v<decltype(std::move(i)), int &&>);

    relay(i);            // T = int&  -> my_forward returns int&  -> sink(int&)
    relay(5);            // T = int   -> my_forward returns int&& -> sink(int&&)
    int &&r = my_move(i);
    std::printf("r=%d\n", r);
    return 0;
}
