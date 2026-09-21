// std::sort needs to jump around (it computes `it + n`), so it demands random
// access. A list iterator is bidirectional, and the refusal happens at compile
// time rather than by producing a wrong answer at run time.
#include <algorithm>
#include <list>

int main() {
    std::list<int> l{3, 1, 2};
    std::sort(l.begin(), l.end());
    return 0;
}
