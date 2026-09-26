#include "common.hpp"

#include <cstddef>
#include <cstdio>
#include <poll.h>
#include <string>
#include <utility>
#include <vector>

// A writer that never loses bytes: what cannot be sent now is kept, and the
// caller is told to come back when the descriptor is writable.
class Writer {
public:
    explicit Writer(int fd) : fd_(fd) {}

    void queue(std::string text) { pending_ += std::move(text); }

    // Returns true when the queue is empty, false when the socket is full.
    bool flush() {
        while (!pending_.empty()) {
            const ssize_t n = ::send(fd_, pending_.data(), pending_.size(), 0);
            if (n > 0) {
                pending_.erase(0, static_cast<std::size_t>(n));
                continue;
            }
            return false;  // EAGAIN (or a dead peer) -- either way, stop
        }
        return true;
    }

    std::size_t pending() const { return pending_.size(); }

private:
    int fd_;
    std::string pending_;
};

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    // Both ends. If the reading end blocks, a single-threaded program that
    // fills the socket and then tries to drain it waits forever for data only
    // it could have produced.
    set_nonblocking(fds[0]);
    set_nonblocking(fds[1]);

    Writer writer(fds[1]);
    const std::string big(1024 * 1024, 'z');
    writer.queue(big);

    const bool finished = writer.flush();
    std::printf("queued %zu bytes\n", big.size());
    std::printf("the first flush emptied the queue: %s\n", finished ? "yes" : "no");

    struct pollfd watch;
    watch.fd = fds[1];
    watch.events = POLLOUT;
    watch.revents = 0;

    std::vector<char> sink(256 * 1024);
    std::size_t received = 0;
    const auto drain_peer = [&] {
        for (;;) {
            const ssize_t n = ::recv(fds[0], sink.data(), sink.size(), 0);
            if (n <= 0) break;
            received += static_cast<std::size_t>(n);
        }
    };

    while (!writer.flush()) {
        drain_peer();  // the socket is full because nobody is emptying it
        watch.revents = 0;
        if (::poll(&watch, 1, 2000) <= 0) break;
    }
    drain_peer();

    std::printf("queue empty at the end: %s\n", writer.pending() == 0 ? "yes" : "no");
    std::printf("sent %zu bytes, the peer received %zu\n", big.size(), received);
    std::printf("nothing was lost: %s\n", received == big.size() ? "yes" : "NO");

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
