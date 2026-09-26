#ifndef COMMON_HPP
#define COMMON_HPP

#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

// A socketpair is two connected descriptors with no network in between:
// whatever is written to one end is readable at the other. It behaves like a
// connection in every way this chapter cares about -- it is non-blocking, it
// buffers, and it fills up -- without needing a port, a client or a listener.
inline bool make_pair(int fds[2]) {
    return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0;
}

inline bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

// The two errno values every event loop has to tell apart. "Nothing to read
// yet" is not an error -- it is the normal state of a connection you are not
// finished with, and treating it as one is how a loop turns into a spin.
inline bool would_block() { return errno == EAGAIN || errno == EWOULDBLOCK; }

#endif
