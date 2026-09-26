#include "common.hpp"

#include <cstdio>
#include <poll.h>

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    set_nonblocking(fds[0]);

    struct pollfd watch;
    watch.fd = fds[0];
    watch.events = POLLIN;
    watch.revents = 0;

    // A zero timeout turns poll() from a wait into a question: "is anything
    // ready right now?" That is the primitive an event loop is built on.
    int ready = ::poll(&watch, 1, 0);
    std::printf("nothing written yet: poll() = %d, readable = %s\n", ready,
                (watch.revents & POLLIN) ? "yes" : "no");

    ::send(fds[1], "x", 1, 0);

    watch.revents = 0;
    ready = ::poll(&watch, 1, 0);
    std::printf("after one byte:      poll() = %d, readable = %s\n", ready,
                (watch.revents & POLLIN) ? "yes" : "no");

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
