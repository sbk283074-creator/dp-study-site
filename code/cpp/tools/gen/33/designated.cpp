// Designated initialisers: name the fields at the call site. The declaration
// order is enforced, so you cannot accidentally swap two members of the same
// type -- which is the bug this feature exists to prevent.
#include <cstdio>

struct Config {
    const char *host;
    int port;
    bool tls;
    int timeout_ms;
};

int main() {
    Config c{.host = "example.com", .port = 443, .tls = true, .timeout_ms = 5000};
    std::printf("%s:%d tls=%d timeout=%d\n",
                c.host, c.port, (int)c.tls, c.timeout_ms);

    Config d{.host = "localhost", .port = 8080};   // the rest are zero
    std::printf("%s:%d tls=%d timeout=%d\n",
                d.host, d.port, (int)d.tls, d.timeout_ms);
    return 0;
}
