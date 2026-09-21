// T&& in a deduced context is a *forwarding* reference, not an rvalue
// reference. What T deduces to is what decides -- and that is the trick.
#include <cstdio>
#include <type_traits>
#include <utility>

template <typename T>
void probe(T &&) {
    if      constexpr (std::is_same_v<T, int>)         std::printf("T = int          -> param is int&&\n");
    else if constexpr (std::is_same_v<T, int &>)       std::printf("T = int&         -> param is int&\n");
    else if constexpr (std::is_same_v<T, const int &>) std::printf("T = const int&   -> param is const int&\n");
    else                                               std::printf("T = something else\n");
}

void takes_rvalue(int &&) { std::printf("takes_rvalue(int&&)\n"); }

int main() {
    int i = 1;
    const int c = 2;

    probe(5);              // rvalue  -> T deduces to int        -> int&&
    probe(i);              // lvalue  -> T deduces to int&       -> int&  (collapse)
    probe(c);              // const lvalue -> T = const int&     -> const int&
    probe(std::move(i));   // xvalue  -> T = int                -> int&&

    // A concrete int&& is NOT a forwarding reference: nothing is deduced.
    takes_rvalue(5);
    // takes_rvalue(i);    // would not compile -- see the exercise
    return 0;
}
