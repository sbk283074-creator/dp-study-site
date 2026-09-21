cat > a.c <<'EOF'
#include <assert.h>
#include <stdio.h>
int main(void) {
    int x = 0;
    assert(x != 0);
    printf("survived\n");
    return 0;
}
EOF
clang -std=c17 -o with_assert a.c
./with_assert 2>&1
echo "exit=$?"
clang -std=c17 -DNDEBUG -o no_assert a.c
./no_assert 2>&1
echo "exit=$?"
