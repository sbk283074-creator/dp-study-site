# Feature-test macros: the honest way to ask "does this compiler have it?"
# instead of guessing from the version number. Language features are
# __cpp_<name>; library features are __cpp_lib_<name>.
cat > t.cpp <<'EOF'
#include <cstdio>
#include <version>

#define REPORT(x) std::printf("%-22s %ld\n", #x, (long)(x))

int main() {
    REPORT(__cplusplus);
    REPORT(__cpp_concepts);
    REPORT(__cpp_lib_ranges);
    REPORT(__cpp_lib_span);
    REPORT(__cpp_lib_format);
    REPORT(__cpp_lib_expected);
    return 0;
}
EOF
clang++ -std=c++23 -Wall -Wextra -Werror -o t t.cpp && ./t
