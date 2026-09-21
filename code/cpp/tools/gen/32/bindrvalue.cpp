// An rvalue reference is a reference that BINDS to rvalues. It is not a
// promise that the thing it names is one -- and it will not bind to an lvalue.
#include <cstdio>

int main() {
    int i = 1;
    int &&r = i;                 // i is an lvalue
    std::printf("%d\n", r);
    return 0;
}
