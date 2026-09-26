#include "common.hpp"

#include <algorithm>
#include <arpa/inet.h>
#include <csignal>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <netinet/in.h>
#include <poll.h>
#include <string>
#include <vector>

namespace {

// "GET /hello HTTP/1.1" -> "/hello". A real parser is Chapter 18's job; this
// chapter is about when the bytes arrive, not what they mean.
std::string request_path(const std::string &head) {
    const std::size_t first = head.find(' ');
    if (first == std::string::npos) return "/";
    const std::size_t second = head.find(' ', first + 1);
    if (second == std::string::npos) return "/";
    return head.substr(first + 1, second - first - 1);
}

void forget(std::vector<int> &clients, int fd) {
    clients.erase(std::remove(clients.begin(), clients.end(), fd), clients.end());
}

}  // namespace

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: prog <port>\n");
        return 2;
    }
    const int port = std::atoi(argv[1]);

    // Writing to a socket whose peer has gone does not return an error: it
    // raises SIGPIPE, whose default action is to kill the process. Every
    // network program ignores it and checks the return value instead.
    std::signal(SIGPIPE, SIG_IGN);

    const int listener = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) return 1;

    int reuse = 1;
    ::setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof reuse);

    struct sockaddr_in address;
    std::memset(&address, 0, sizeof address);
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons(static_cast<std::uint16_t>(port));
    if (::bind(listener, reinterpret_cast<struct sockaddr *>(&address), sizeof address) != 0) {
        std::fprintf(stderr, "bind failed\n");
        return 1;
    }
    if (::listen(listener, 16) != 0) return 1;
    set_nonblocking(listener);

    // No port number in this line on purpose: it changes every run, and a
    // transcript that quotes it cannot be verified.
    std::printf("listening on 127.0.0.1\n");
    std::fflush(stdout);

    std::vector<int> clients;
    int served = 0;

    for (;;) {
        std::vector<struct pollfd> watched;
        struct pollfd listener_entry;
        listener_entry.fd = listener;
        listener_entry.events = POLLIN;
        listener_entry.revents = 0;
        watched.push_back(listener_entry);
        for (const int fd : clients) {
            struct pollfd entry;
            entry.fd = fd;
            entry.events = POLLIN;
            entry.revents = 0;
            watched.push_back(entry);
        }

        // -1 means "wait as long as it takes". This is the line that makes the
        // loop cost nothing while it is idle: no spinning, no polling timer.
        const int ready = ::poll(watched.data(), watched.size(), -1);
        if (ready < 0) {
            if (errno == EINTR) continue;  // a signal arrived; the loop survives
            break;
        }

        if (watched[0].revents & POLLIN) {
            for (;;) {
                const int fd = ::accept(listener, nullptr, nullptr);
                if (fd < 0) break;  // EAGAIN: every pending connection is taken
                set_nonblocking(fd);
                clients.push_back(fd);
            }
        }

        for (std::size_t i = 1; i < watched.size(); ++i) {
            if (!(watched[i].revents & POLLIN)) continue;
            const int fd = watched[i].fd;

            char buffer[1024];
            const ssize_t n = ::recv(fd, buffer, sizeof buffer - 1, 0);
            if (n <= 0) {
                ::close(fd);
                forget(clients, fd);
                break;
            }
            buffer[n] = '\0';
            const std::string path = request_path(buffer);
            ++served;
            std::printf("served #%d GET %s\n", served, path.c_str());
            std::fflush(stdout);

            const std::string body = "you asked for " + path + "\n";
            char head[160];
            std::snprintf(head, sizeof head,
                          "HTTP/1.1 200 OK\r\n"
                          "Content-Type: text/plain\r\n"
                          "Content-Length: %zu\r\n"
                          "Connection: close\r\n\r\n",
                          body.size());
            const std::string response = std::string(head) + body;

            std::size_t sent = 0;
            while (sent < response.size()) {
                const ssize_t written =
                    ::send(fd, response.data() + sent, response.size() - sent, 0);
                // A real server keeps what it could not send and waits for
                // POLLOUT. This one has no write queue, so it gives up -- and
                // that limitation is the exercise at the end of the chapter.
                if (written <= 0) break;
                sent += static_cast<std::size_t>(written);
            }

            ::close(fd);
            forget(clients, fd);
            break;  // the descriptor list changed; rebuild it on the next turn
        }
    }

    for (const int fd : clients) ::close(fd);
    ::close(listener);
    return 0;
}
