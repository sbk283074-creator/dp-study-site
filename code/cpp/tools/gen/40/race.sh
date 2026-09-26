cat > counter.cpp <<'EOF'
#include <atomic>
#include <cstdio>
#include <thread>

int plain = 0;
std::atomic<int> guarded{0};

void bump_plain()   { for (int i = 0; i < 50000; ++i) plain++; }
void bump_guarded() { for (int i = 0; i < 50000; ++i) guarded.fetch_add(1); }

int main(int argc, char **) {
    if (argc > 1) {
        std::thread a(bump_guarded), b(bump_guarded);
        a.join(); b.join();
        std::printf("guarded = %d\n", guarded.load());
        return 0;
    }
    std::thread a(bump_plain), b(bump_plain);
    a.join(); b.join();
    std::printf("plain   = %d\n", plain);
    return 0;
}
EOF

clang++ -std=c++17 -fsanitize=thread -g -o counter_tsan counter.cpp

echo "--- plain int, built with -fsanitize=thread ---"
./counter_tsan > /dev/null 2> racy.txt
if grep -q "WARNING: ThreadSanitizer" racy.txt; then
  echo "ThreadSanitizer: data race reported"
else
  echo "ThreadSanitizer reported nothing"
fi

echo "--- std::atomic<int>, built with -fsanitize=thread ---"
./counter_tsan atomic 2> safe.txt
if grep -q "WARNING: ThreadSanitizer" safe.txt; then
  echo "ThreadSanitizer: data race reported"
else
  echo "ThreadSanitizer reported nothing"
fi
