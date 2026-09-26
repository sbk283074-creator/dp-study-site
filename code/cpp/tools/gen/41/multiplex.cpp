#include "common.hpp"

#include <cstddef>
#include <cstdio>
#include <poll.h>
#include <vector>

int main() {
    const std::size_t count = 3;
    int pairs[3][2];
    std::vector<struct pollfd> watched;

    for (std::size_t i = 0; i < count; ++i) {
        if (!make_pair(pairs[i])) return 1;
        set_nonblocking(pairs[i][0]);
        struct pollfd entry;
        entry.fd = pairs[i][0];
        entry.events = POLLIN;
        entry.revents = 0;
        watched.push_back(entry);
    }

    // One byte, into the middle connection only.
    ::send(pairs[1][1], "?", 1, 0);

    const int ready = ::poll(watched.data(), watched.size(), 0);
    std::printf("poll() reports %d of %zu connections ready\n", ready, watched.size());
    for (std::size_t i = 0; i < watched.size(); ++i) {
        // The index is what is stable. The descriptor number is not: it
        // depends on what else the process has open, so never quote it.
        if (watched[i].revents & POLLIN) std::printf("connection %zu is readable\n", i);
    }

    for (std::size_t i = 0; i < count; ++i) {
        ::close(pairs[i][0]);
        ::close(pairs[i][1]);
    }
    return 0;
}
