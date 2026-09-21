#include <cstddef>
#include <cstdio>

struct Loose {
    char   tag;
    double value;
    int    count;
};

struct Tight {
    double value;
    int    count;
    char   tag;
};

int main() {
    std::printf("Loose size=%zu align=%zu  tag=%zu value=%zu count=%zu\n",
                sizeof(Loose), alignof(Loose),
                offsetof(Loose, tag), offsetof(Loose, value), offsetof(Loose, count));
    std::printf("Tight size=%zu align=%zu  value=%zu count=%zu tag=%zu\n",
                sizeof(Tight), alignof(Tight),
                offsetof(Tight, value), offsetof(Tight, count), offsetof(Tight, tag));
    return 0;
}
