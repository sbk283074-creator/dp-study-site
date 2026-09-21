// iterator_traits is where a container declares what its iterator can do. The
// algorithms read that answer and refuse the ones they cannot honour.
#include <cstdio>
#include <iterator>
#include <list>
#include <type_traits>
#include <vector>

template <typename It>
const char *category() {
    using Cat = typename std::iterator_traits<It>::iterator_category;
    if      constexpr (std::is_same_v<Cat, std::random_access_iterator_tag>) return "random access";
    else if constexpr (std::is_same_v<Cat, std::bidirectional_iterator_tag>) return "bidirectional";
    else if constexpr (std::is_same_v<Cat, std::forward_iterator_tag>)       return "forward";
    else if constexpr (std::is_same_v<Cat, std::input_iterator_tag>)         return "input";
    else return "other";
}

int main() {
    std::printf("vector<int>::iterator : %s\n", category<std::vector<int>::iterator>());
    std::printf("list<int>::iterator   : %s\n", category<std::list<int>::iterator>());
    std::printf("int*                  : %s\n", category<int *>());
    return 0;
}
