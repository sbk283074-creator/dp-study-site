// operator-> must return something that itself has -> (or is a pointer).
// The language then applies -> again, which is what makes the chain work.
#include <cstdio>

struct Point {
    int x;
    int y;
    void show() const { std::printf("(%d, %d)\n", x, y); }
};

struct Handle {
    Point *p;
    Point *operator->() { return p; }
};

int main() {
    Point pt{3, 4};
    Handle h{&pt};
    h->show();
    std::printf("x=%d\n", h->x);
    return 0;
}
