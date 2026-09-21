// operator[] in const and non-const flavours. The const overload is what lets a
// read-only caller still index -- without it, `const Row` would be unusable.
#include <cstdio>

struct Row {
    int cells[3] = {0, 0, 0};
    int       &operator[](int i)       { return cells[i]; }
    const int &operator[](int i) const { return cells[i]; }
};

int main() {
    Row r;
    r[1] = 7;                 // writes through the non-const overload
    const Row &cr = r;
    std::printf("%d %d\n", r[1], cr[1]);
    return 0;
}
