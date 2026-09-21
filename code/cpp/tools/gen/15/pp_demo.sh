cat > demo.c <<'EOF'
#define GREET "hi"
#define DBL(x) ((x) * 2)
int main(void) { return DBL(3); }
EOF
clang -E -P demo.c
