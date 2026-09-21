# The same source under two standards. The standard is a compiler switch, not a
# property of the library -- and a C++20 feature under -std=c++17 is just a
# syntax error.
cat > t.cpp <<'EOF'
#include <concepts>
#include <cstdio>

template <typename T>
requires std::integral<T>
T twice(T n) { return n + n; }

int main() { std::printf("%d\n", twice(21)); }
EOF

echo "--- c++17 ---"
if clang++ -std=c++17 -fsyntax-only t.cpp 2>err.txt; then
    echo "compiled"
else
    echo "rejected:"
    grep -E "^t.cpp.*error" err.txt | head -2
fi

echo "--- c++20 ---"
if clang++ -std=c++20 -Wall -Wextra -Werror -o t t.cpp 2>err.txt; then
    ./t
else
    echo "rejected"
fi
