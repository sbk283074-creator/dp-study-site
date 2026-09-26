#include "common.hpp"

#include <cstddef>
#include <cstdio>
#include <functional>
#include <map>
#include <poll.h>
#include <utility>
#include <vector>

// A reactor: a table mapping "this descriptor is readable" to "do this". The
// loop knows nothing about sockets, HTTP or connections -- it watches, and it
// dispatches. That separation is the whole difference between this chapter's
// server and Chapter 20's, which accepted, served and closed in one function.
class Reactor {
public:
    void on_readable(int fd, std::function<void()> handler) {
        handlers_[fd] = std::move(handler);
    }

    // One turn of the loop. Returns how many handlers ran, 0 if nothing was
    // ready, or -1 if poll() itself failed.
    int turn(int timeout_ms) {
        std::vector<struct pollfd> watched;
        watched.reserve(handlers_.size());
        for (const auto &entry : handlers_) {
            struct pollfd item;
            item.fd = entry.first;
            item.events = POLLIN;
            item.revents = 0;
            watched.push_back(item);
        }
        const int ready = ::poll(watched.data(), watched.size(), timeout_ms);
        if (ready <= 0) return ready;

        int dispatched = 0;
        for (const struct pollfd &item : watched) {
            if (item.revents & POLLIN) {
                handlers_[item.fd]();
                ++dispatched;
            }
        }
        return dispatched;
    }

private:
    std::map<int, std::function<void()>> handlers_;
};

// A handler that reads what is there. Reading is not optional: a level-triggered
// poll() keeps reporting a descriptor as readable until the bytes are consumed,
// so a handler that only looks at `revents` makes the loop run forever.
std::function<void()> reader(int fd, const char *name) {
    return [fd, name] {
        char buffer[8];
        const ssize_t n = ::recv(fd, buffer, sizeof buffer, 0);
        std::printf("handler %s consumed %zd byte(s)\n", name, n);
    };
}

int main() {
    int first_pair[2];
    int second_pair[2];
    if (!make_pair(first_pair) || !make_pair(second_pair)) return 1;

    Reactor reactor;
    // Each handler closes over the name it should print, so the transcript
    // never depends on a descriptor number.
    reactor.on_readable(first_pair[0], reader(first_pair[0], "A"));
    reactor.on_readable(second_pair[0], reader(second_pair[0], "B"));

    ::send(first_pair[1], "a", 1, 0);
    ::send(second_pair[1], "b", 1, 0);

    std::printf("one byte queued on each connection\n");
    const int first_turn = reactor.turn(0);
    std::printf("turn() dispatched %d handler(s)\n", first_turn);
    const int second_turn = reactor.turn(0);
    std::printf("turn() again dispatched %d handler(s), because both were drained\n",
                second_turn);

    ::close(first_pair[0]);
    ::close(first_pair[1]);
    ::close(second_pair[0]);
    ::close(second_pair[1]);
    return 0;
}
