cat > greet.cpp <<'EOF'
#include <cstdio>

int main() {
#ifdef VERBOSE
    std::printf("verbose: hello\n");
#else
    std::printf("hello\n");
#endif
    return 0;
}
EOF
echo '$ clang++ -std=c++17 -o greet greet.cpp && ./greet'
clang++ -std=c++17 -o greet greet.cpp && ./greet
echo '$ clang++ -std=c++17 -DVERBOSE -o greet greet.cpp && ./greet'
clang++ -std=c++17 -DVERBOSE -o greet greet.cpp && ./greet
