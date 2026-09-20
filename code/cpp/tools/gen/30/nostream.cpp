/* fsync() needs a file descriptor. A std::ofstream does not give you one. */
#include <fstream>

int main() {
    std::ofstream out("store.json");
    out << "{\"version\":1}";
    const int fd = out.native_handle();
    (void)fd;
    return 0;
}
