// Value categories are not syntax trivia: they are what overload resolution
// reads to decide which function you meant. Three overloads, five expressions.
#include <cstdio>
#include <utility>

void f(int &)       { std::printf("f(int&)\n"); }
void f(const int &) { std::printf("f(const int&)\n"); }
void f(int &&)      { std::printf("f(int&&)\n"); }

int main() {
    int i = 1;
    const int c = 2;

    f(i);              // a named variable: lvalue
    f(c);              // a named const:    lvalue, but const
    f(3);              // a literal:        prvalue
    f(i + 1);          // the result of +:  prvalue
    f(std::move(i));   // std::move makes:  xvalue
    return 0;
}
