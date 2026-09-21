// An iterator is a position, not a value. Growing a vector past its capacity
// moves the elements, and every iterator into the old storage dies with it.
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> v;
    v.reserve(4);                       // exactly four slots
    for (int i = 0; i < 4; ++i) v.push_back(i);

    auto it = v.begin();                // points into the current storage
    v.push_back(4);                     // fifth element: must reallocate
    std::printf("first = %d\n", *it);   // that storage has been freed
    return 0;
}
