/* write() tells you how much it wrote. Ignoring the answer is how a short
   write becomes silent data loss. */
#include <cstdio>

#include <fcntl.h>
#include <unistd.h>

int main() {
    const char *payload = "{\"version\":1}";
    const int fd = ::open("store.json", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    const ssize_t n = ::write(fd, payload, 13);
    ::close(fd);
    std::printf("done\n");
    return 0;
}
