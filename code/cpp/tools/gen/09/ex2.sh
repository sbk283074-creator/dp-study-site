cat > level.cpp <<'EOF'
#include <cstdio>

#ifndef LEVEL
#define LEVEL 1
#endif

int main() {
#if LEVEL >= 2
    std::printf("level %d: detailed\n", LEVEL);
#else
    std::printf("level %d: quiet\n", LEVEL);
#endif
    return 0;
}
EOF
echo '$ clang++ -std=c++17 -o level level.cpp && ./level'
clang++ -std=c++17 -o level level.cpp && ./level
echo '$ clang++ -std=c++17 -DLEVEL=2 -o level level.cpp && ./level'
clang++ -std=c++17 -DLEVEL=2 -o level level.cpp && ./level
echo '$ clang++ -std=c++17 -DLEVEL=9 -o level level.cpp && ./level'
clang++ -std=c++17 -DLEVEL=9 -o level level.cpp && ./level
