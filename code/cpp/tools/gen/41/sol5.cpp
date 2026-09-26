#include "common.hpp"

#include <cstdio>
#include <dirent.h>

// Counting the entries in /dev/fd is the only honest way to prove a descriptor
// was released. No sanitizer can see this leak: the descriptor belongs to the
// kernel, not to the heap, and macOS has no leak detector to ask anyway.
// Print the *difference*, never the absolute count -- the baseline depends on
// what the shell handed the process.
int open_descriptors() {
    DIR *dir = ::opendir("/dev/fd");
    if (dir == nullptr) return -1;
    int count = 0;
    while (::readdir(dir) != nullptr) ++count;
    ::closedir(dir);
    return count - 3;  // '.', '..' and the descriptor opendir itself used
}

// The Chapter 26 rule applied to a socket: if it is owned by an object, the
// destructor closes it on every path, including the one where an exception
// unwinds through the function.
class Descriptor {
public:
    explicit Descriptor(int fd) : fd_(fd) {}
    ~Descriptor() {
        if (fd_ >= 0) ::close(fd_);
    }
    Descriptor(const Descriptor &) = delete;
    Descriptor &operator=(const Descriptor &) = delete;
    int get() const { return fd_; }

private:
    int fd_;
};

int main() {
    const int baseline = open_descriptors();
    std::printf("baseline descriptor count differs per run; only the difference is printed\n");

    {
        int fds[2];
        if (!make_pair(fds)) return 1;
        Descriptor guard(fds[0]);
        ::send(fds[1], "x", 1, 0);
        ::close(fds[1]);  // the other end, closed by hand

        const int inside = open_descriptors();
        std::printf("while the guard is alive: %+d vs the baseline\n", inside - baseline);
    }

    const int after = open_descriptors();
    std::printf("after the guard's scope:  %+d vs the baseline\n", after - baseline);
    std::printf("the descriptor was released: %s\n", after == baseline ? "yes" : "NO");

    return 0;
}
