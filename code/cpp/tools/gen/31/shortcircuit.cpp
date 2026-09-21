// Overloaded && and || are ordinary function calls, and a function call
// evaluates all of its arguments. Short-circuit evaluation is gone.
#include <cstdio>

struct Bool { bool v; };

Bool operator&&(Bool a, Bool b) { return Bool{a.v && b.v}; }

Bool note(const char *name, bool v) {
    std::printf("evaluated %s\n", name);
    return Bool{v};
}

int main() {
    Bool r = note("left", false) && note("right", true);
    std::printf("result=%d\n", static_cast<int>(r.v));
    return 0;
}
