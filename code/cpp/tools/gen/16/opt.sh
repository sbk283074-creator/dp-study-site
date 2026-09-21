cat > opt.c <<'EOF'
#include <stdio.h>
#include <limits.h>
int main(void) {
    volatile int v = INT_MAX;
    int x = v;
    if (x + 1 > x) printf("overflow assumed impossible\n");
    else printf("no overflow\n");
    return 0;
}
EOF
clang -std=c17 -O0 -o o0 opt.c && printf "at -O0: " && ./o0
clang -std=c17 -O2 -o o2 opt.c && printf "at -O2: " && ./o2
