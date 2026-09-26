#include "common.hpp"

#include <cstdio>

int main() {
    int fds[2];
    if (!make_pair(fds)) {
        std::printf("socketpair failed\n");
        return 1;
    }

    // A descriptor is blocking by default: recv() waits until there is
    // something to hand you. The flag below is what makes it answer instead.
    std::printf("non-blocking mode: %s\n", set_nonblocking(fds[0]) ? "set" : "FAILED");

    char buffer[16];
    ssize_t n = ::recv(fds[0], buffer, sizeof buffer, 0);
    std::printf("recv before any data: n = %zd, errno says \"not yet\": %s\n", n,
                would_block() ? "yes" : "no");

    const char message[] = "hello";
    ::send(fds[1], message, sizeof message - 1, 0);

    n = ::recv(fds[0], buffer, sizeof buffer, 0);
    std::printf("recv after one send:  n = %zd, data = %.*s\n", n, static_cast<int>(n), buffer);

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
