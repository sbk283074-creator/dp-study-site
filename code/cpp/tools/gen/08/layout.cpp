#include <cstddef>
#include <cstdio>

struct Loose {
    char a;
    int  b;
    char c;
};

struct Tight {
    int  b;
    char a;
    char c;
};

int main() {
    std::printf("Loose size=%zu align=%zu  a=%zu b=%zu c=%zu\n",
                sizeof(Loose), alignof(Loose),
                offsetof(Loose, a), offsetof(Loose, b), offsetof(Loose, c));
    std::printf("Tight size=%zu align=%zu  b=%zu a=%zu c=%zu\n",
                sizeof(Tight), alignof(Tight),
                offsetof(Tight, b), offsetof(Tight, a), offsetof(Tight, c));
    std::printf("members alone = %zu bytes\n",
                sizeof(char) + sizeof(int) + sizeof(char));
    return 0;
}
