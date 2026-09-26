// ch45 generator project — the server: configuration, a pool, a self-pipe, a drain.
#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cerrno>
#include <csignal>
#include <cstdio>
#include <cstring>
#include <deque>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include "app.hpp"
#include "config.hpp"
#include "http.hpp"
#include "log.hpp"

// The self-pipe. A signal handler may call only async-signal-safe functions, and
// `write` is one of them while `std::printf` is not -- so instead of doing the work in
// the handler we make one end of a pipe readable and let the normal loop handle it,
// with the mutexes and the logging it already has.
static int g_signal_pipe[2] = {-1, -1};

static void on_signal(int sig) {
    const char byte = static_cast<char>(sig == SIGTERM ? 'T' : 'I');
    ssize_t ignored = ::write(g_signal_pipe[1], &byte, 1);
    (void)ignored;
}

struct Pool {
    std::mutex mutex;
    std::condition_variable ready;
    std::deque<int> queue;
    bool stopping = false;
    std::vector<std::thread> workers;
};

static Pool g_pool;
static std::atomic<long long> g_served{0};
static std::atomic<int> g_in_flight{0};

static void serve(App &app, int fd) {
    Request req;
    const std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
    if (read_request(fd, req)) {
        Response res;
        try {
            res = handle(app, req);
        } catch (const std::exception &e) {
            res = text_response(500, std::string("internal error\n"));
            app.log.emit("error", "handler threw", {{"what", e.what()}});
        }
        send_all(fd, render_response(res));
        const long micros = static_cast<long>(
            std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::steady_clock::now() - start).count());
        app.log.access(req.method, req.target, res.status, micros);
        g_served.fetch_add(1);
    }
    ::close(fd);
    g_in_flight.fetch_sub(1);
}

static void worker_main(App &app) {
    for (;;) {
        int fd = -1;
        {
            std::unique_lock<std::mutex> lock(g_pool.mutex);
            g_pool.ready.wait(lock, [] { return !g_pool.queue.empty() || g_pool.stopping; });
            if (g_pool.queue.empty()) {
                // Empty AND stopping: every accepted connection has been answered, so
                // this worker may go. Anything else would drop work already delivered
                // to us by the kernel.
                if (g_pool.stopping) return;
                continue;
            }
            fd = g_pool.queue.front();
            g_pool.queue.pop_front();
        }
        serve(app, fd);
    }
}

static bool build_config(Config &config, int argc, char **argv, std::string &err,
                         bool &print_config) {
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg.rfind("--config=", 0) == 0 && !load_file(config, arg.substr(9), err)) return false;
    }
    if (!load_env(config, err)) return false;
    return load_argv(config, argc, argv, err, print_config);
}

int main(int argc, char **argv) {
    Config config;
    std::string err;
    bool print_config = false;
    if (!build_config(config, argc, argv, err, print_config)) {
        std::fprintf(stderr, "configuration: %s\n", err.c_str());
        return 2;
    }
    err = validate(config);
    if (!err.empty()) {
        std::fprintf(stderr, "configuration: %s\n", err.c_str());
        return 2;
    }
    if (print_config) {
        std::printf("%s\n", to_json(config).c_str());
        return 0;
    }

    // Constructing the App opens the database and migrates it; if either fails there is
    // nothing useful the service can serve, so it says why and stops before listening.
    App app(config);
    app.log.emit("info", "startup", {{"db", config.db_path},
                                     {"workers", std::to_string(config.workers)}});

    if (::pipe(g_signal_pipe) != 0) return 4;
    for (int fd : g_signal_pipe) {
        const int flags = ::fcntl(fd, F_GETFL, 0);
        ::fcntl(fd, F_SETFL, flags | O_NONBLOCK);
    }
    struct sigaction action {};
    action.sa_handler = on_signal;
    sigemptyset(&action.sa_mask);
    if (::sigaction(SIGTERM, &action, nullptr) != 0) return 4;
    if (::sigaction(SIGINT, &action, nullptr) != 0) return 4;
    ::signal(SIGPIPE, SIG_IGN);

    const int listener = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) return 4;
    int on = 1;
    ::setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<unsigned short>(config.port));
    if (::bind(listener, reinterpret_cast<sockaddr *>(&addr), sizeof addr) != 0) {
        std::fprintf(stderr, "bind port %d: %s\n", config.port, strerror(errno));
        return 4;
    }
    if (::listen(listener, 128) != 0) return 4;

    // Port 0 means "give me one", which is how the suite avoids collisions and how an
    // operator finds the real port later. The number is logged, so anything that can
    // read the log can find the service.
    sockaddr_in bound{};
    socklen_t bound_len = sizeof bound;
    if (::getsockname(listener, reinterpret_cast<sockaddr *>(&bound), &bound_len) == 0)
        app.log.emit("info", "listening", {{"port", std::to_string(ntohs(bound.sin_port))}});
    else
        app.log.emit("info", "listening", {{"port", std::to_string(config.port)}});

    for (int i = 0; i < config.workers; ++i)
        g_pool.workers.emplace_back(worker_main, std::ref(app));

    for (;;) {
        pollfd fds[2]{};
        fds[0].fd = listener;
        fds[0].events = POLLIN;
        fds[1].fd = g_signal_pipe[0];
        fds[1].events = POLLIN;
        const int ready = ::poll(fds, 2, -1);
        if (ready < 0) {
            if (errno == EINTR) continue;
            break;
        }
        if (fds[1].revents & POLLIN) {
            char buf[64];
            while (::read(g_signal_pipe[0], buf, sizeof buf) > 0) { }
            break;
        }
        if (fds[0].revents & POLLIN) {
            const int fd = ::accept(listener, nullptr, nullptr);
            if (fd < 0) continue;
            g_in_flight.fetch_add(1);
            std::lock_guard<std::mutex> lock(g_pool.mutex);
            g_pool.queue.push_back(fd);
            g_pool.ready.notify_one();
        }
    }

    // Stop accepting first, then let the workers finish what the kernel already handed
    // us, then wait for them. Those three steps in that order are the whole of
    // "graceful"; skipping the middle one is how a restart loses requests.
    ::close(listener);
    {
        std::lock_guard<std::mutex> lock(g_pool.mutex);
        g_pool.stopping = true;
    }
    g_pool.ready.notify_all();
    for (std::thread &worker : g_pool.workers) worker.join();
    app.log.emit("info", "shutdown", {{"requests", std::to_string(g_served.load())},
                                      {"workers", std::to_string(config.workers)}});
    ::close(g_signal_pipe[0]);
    ::close(g_signal_pipe[1]);
    return 0;
}
