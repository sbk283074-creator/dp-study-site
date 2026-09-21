// Where moves actually happen in ordinary code: growing a vector relocates its
// elements, and it moves them if it can.
#include <cstdio>
#include <utility>
#include <vector>

struct Tracked {
    int id;
    explicit Tracked(int i) : id(i) { std::printf("construct id=%d\n", id); }
    Tracked(const Tracked &o) : id(o.id) { std::printf("copy      id=%d\n", id); }
    Tracked(Tracked &&o) noexcept : id(o.id) { o.id = -1; std::printf("move      id=%d\n", id); }
    ~Tracked() { std::printf("destroy   id=%d\n", id); }
};

int main() {
    std::vector<Tracked> v;
    v.reserve(2);
    std::printf("-- two pushes, no reallocation --\n");
    v.emplace_back(1);
    v.emplace_back(2);

    std::printf("-- third push: must grow --\n");
    v.emplace_back(3);
    std::printf("-- done --\n");
    return 0;
}
