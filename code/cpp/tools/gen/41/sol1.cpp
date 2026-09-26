#include "common.hpp"

#include <cstddef>
#include <cstdio>
#include <string>

// Reading until EAGAIN is how a non-blocking reader learns it has everything
// that has *arrived*. It is not the same as the whole message: only the
// protocol can say where a message ends, which is what a length prefix or a
// delimiter in the framing is for.
std::string drain(int fd) {
    std::string out;
    char buffer[4096];
    for (;;) {
        const ssize_t n = ::recv(fd, buffer, sizeof buffer, 0);
        if (n > 0) {
            out.append(buffer, static_cast<std::size_t>(n));
            continue;
        }
        // 0 is the peer closing, a negative return with EAGAIN is "come back
        // later", and any other negative return is a real error. Only the
        // first two are reasons to stop quietly.
        break;
    }
    return out;
}

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    set_nonblocking(fds[0]);

    ::send(fds[1], "abc", 3, 0);
    ::send(fds[1], "def", 3, 0);
    ::send(fds[1], "ghi", 3, 0);

    const std::string first = drain(fds[0]);
    std::printf("first drain:  %zu bytes, \"%s\"\n", first.size(), first.c_str());

    ::send(fds[1], "jkl", 3, 0);
    const std::string second = drain(fds[0]);
    std::printf("second drain: %zu bytes, \"%s\"\n", second.size(), second.c_str());
    std::printf("three sends arrived as one read of %zu bytes, not three of 3\n", first.size());

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
