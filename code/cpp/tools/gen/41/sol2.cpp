#include "common.hpp"

#include <arpa/inet.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <netinet/in.h>
#include <vector>

int main() {
    const int listener = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) return 1;

    struct sockaddr_in address;
    std::memset(&address, 0, sizeof address);
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = 0;  // port 0 asks the kernel to choose one
    if (::bind(listener, reinterpret_cast<struct sockaddr *>(&address), sizeof address) != 0)
        return 1;
    if (::listen(listener, 8) != 0) return 1;
    set_nonblocking(listener);

    // Ask which port we were given. Nothing here prints it: a port number is
    // not stable across runs, so it never belongs in a transcript.
    socklen_t length = sizeof address;
    if (::getsockname(listener, reinterpret_cast<struct sockaddr *>(&address), &length) != 0)
        return 1;

    std::vector<int> clients;
    for (int i = 0; i < 3; ++i) {
        const int client = ::socket(AF_INET, SOCK_STREAM, 0);
        if (client < 0) continue;
        if (::connect(client, reinterpret_cast<struct sockaddr *>(&address), sizeof address) == 0)
            clients.push_back(client);
    }
    std::printf("clients connected: %zu\n", clients.size());

    // Accepting once per turn is how a server falls behind: the backlog grows
    // while it serves one connection at a time. Draining the queue costs one
    // extra syscall when it is empty, which is a bargain.
    int accepted = 0;
    for (;;) {
        const int fd = ::accept(listener, nullptr, nullptr);
        if (fd < 0) break;  // EAGAIN: the queue is empty
        ++accepted;
        ::close(fd);
    }
    std::printf("accept() returned %d connections, then EAGAIN\n", accepted);
    std::printf("one accept per turn would have taken 3 turns; this took one\n");

    for (const int client : clients) ::close(client);
    ::close(listener);
    return 0;
}
