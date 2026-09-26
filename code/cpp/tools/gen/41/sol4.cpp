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

    // A timeout is what turns a blocking wait into a scheduler. With a deadline
    // the loop wakes up even when nothing happened, which is the only way a
    // single-threaded server can notice an idle or slow client.
    const int quiet = ::poll(&watch, 1, 50);
    std::printf("silent connection, 50 ms timeout -> poll() = %d\n", quiet);
    std::printf("that is %s\n", quiet == 0 ? "a timeout, not an error" : "unexpected");
    std::printf("revents after a timeout: %s\n", watch.revents == 0 ? "no events set" : "set");

    ::send(fds[1], "x", 1, 0);
    watch.revents = 0;
    const int ready = ::poll(&watch, 1, 50);
    std::printf("after one byte, same timeout  -> poll() = %d, immediately\n", ready);
    std::printf("readable: %s\n", (watch.revents & POLLIN) ? "yes" : "no");

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
