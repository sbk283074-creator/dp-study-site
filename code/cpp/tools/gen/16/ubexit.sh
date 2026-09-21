cat > ub.c <<'EOF'
#include <limits.h>
#include <stdio.h>
int main(void) {
    int x = INT_MAX;
    int y = x + 1;
    printf("x + 1 = %d\n", y);
    return 0;
}
EOF
clang -std=c17 -fsanitize=undefined -o ub ub.c
./ub 2>/dev/null
echo "exit=$?"
