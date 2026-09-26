#include "common.hpp"

#include <cstddef>
#include <cstdio>
#include <vector>

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    set_nonblocking(fds[0]);
    set_nonblocking(fds[1]);

    const std::size_t wanted = 1024 * 1024;
    std::vector<char> payload(wanted, 'a');

    // One send() is not one delivery. A socket has a finite send buffer, so a
    // non-blocking send() fills what it can and returns -- with a *count*, not
    // an error. Code that assumes the count equals the request loses the rest.
    const ssize_t first = ::send(fds[1], payload.data(), payload.size(), 0);
    std::printf("asked to send %zu bytes in a single call\n", wanted);
    std::printf("the call accepted fewer: %s\n",
                (first > 0 && static_cast<std::size_t>(first) < wanted) ? "yes" : "no");

    // The pattern that works: keep sending what is left, and drain the other
    // end as you go, because the reason you cannot send is that the buffer is
    // full and nothing is emptying it.
    std::size_t sent = first > 0 ? static_cast<std::size_t>(first) : 0;
    std::vector<char> sink(64 * 1024);
    while (sent < wanted) {
        while (::recv(fds[0], sink.data(), sink.size(), 0) > 0) {
        }
        const ssize_t n = ::send(fds[1], payload.data() + sent, wanted - sent, 0);
        if (n > 0) {
            sent += static_cast<std::size_t>(n);
        } else if (!would_block()) {
            std::printf("send failed at %zu bytes\n", sent);
            return 1;
        }
    }
    std::printf("after the loop: %zu of %zu\n", sent, wanted);
    std::printf("the message is %s\n", sent == wanted ? "complete" : "TRUNCATED");

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
