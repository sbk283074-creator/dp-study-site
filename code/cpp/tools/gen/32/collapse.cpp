// Reference collapsing: the four rules the whole forwarding mechanism rests on.
// You cannot write `int & &` yourself -- collapse only happens through a
// template parameter or a typedef, which is why these are expressed as aliases.
#include <cstdio>
#include <type_traits>

template <typename T> using Lref = T &;
template <typename T> using Rref = T &&;

int main() {
    static_assert(std::is_same_v<Lref<int &>, int &>);
    static_assert(std::is_same_v<Lref<int &&>, int &>);
    static_assert(std::is_same_v<Rref<int &>, int &>);
    static_assert(std::is_same_v<Rref<int &&>, int &&>);

    std::printf("T&  &  -> T&\n");
    std::printf("T&& &  -> T&\n");
    std::printf("T&  && -> T&\n");
    std::printf("T&& && -> T&&\n");
    std::printf("one rule: an lvalue reference anywhere wins\n");
    return 0;
}
