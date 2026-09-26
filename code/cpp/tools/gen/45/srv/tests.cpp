// ch45 generator project — integration tests: real process, real socket, real exit code.
#include "framework.hpp"

#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

#include <chrono>
#include <cstdio>
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include "app.hpp"
#include "auth.hpp"
#include "config.hpp"
#include "http.hpp"

// ---------------------------------------------------------------------------
// Against App directly: everything except the socket, in microseconds.
// ---------------------------------------------------------------------------

static Config test_config(const std::string &db) {
    Config c;
    c.db_path = db;
    c.rounds = 1000;               // the work factor is a knob; the suite turns it down
    c.log_path = "/dev/null";
    c.level = "error";
    return c;
}

static std::unique_ptr<App> fresh_app(const std::string &db) {
    std::remove(db.c_str());
    return std::unique_ptr<App>(new App(test_config(db)));
}

static Request make_request(const std::string &method, const std::string &target,
                            const std::string &body = "", const std::string &sid = "") {
    Request r;
    r.method = method;
    r.target = target;
    r.body = body;
    if (!sid.empty()) r.headers.push_back({"cookie", "sid=" + sid});
    return r;
}

TEST(app_signup_login_and_notes) {
    auto app = fresh_app("it-flow.db");
    CHECK(handle(*app, make_request("POST", "/signup", "user=alice&password=hunter22")).status == 201);
    CHECK(handle(*app, make_request("POST", "/signup", "user=alice&password=hunter22")).status == 409);
    CHECK(handle(*app, make_request("POST", "/signup", "user=bob&password=short")).status == 400);
    CHECK(handle(*app, make_request("POST", "/login", "user=alice&password=wrongpass")).status == 401);

    const Response signed_in = handle(*app, make_request("POST", "/login", "user=alice&password=hunter22"));
    CHECK(signed_in.status == 200);
    CHECK(signed_in.set_cookie.find("HttpOnly") != std::string::npos);
    const std::string sid = signed_in.set_cookie.substr(4, 32);

    CHECK(handle(*app, make_request("GET", "/", "", sid)).body.find("0 note(s)") != std::string::npos);
    CHECK(handle(*app, make_request("POST", "/notes", "title=Hello&body=first", sid)).status == 303);
    const Response page = handle(*app, make_request("GET", "/", "", sid));
    CHECK(page.body.find("1 note(s)") != std::string::npos);
    CHECK(page.body.find("Hello") != std::string::npos);

    // The XSS pair, asserted together: the payload must appear escaped and must NOT
    // appear as markup. Checking only the first half is how XSS tests pass with the
    // hole still open.
    CHECK(handle(*app, make_request("POST", "/notes",
                                    "title=%3Cscript%3E&body=alert%281%29", sid)).status == 303);
    const Response after = handle(*app, make_request("GET", "/", "", sid));
    CHECK(after.body.find("&lt;script&gt;") != std::string::npos);
    CHECK(after.body.find("<script>") == std::string::npos);

    const Response one = handle(*app, make_request("GET", "/notes/1", "", sid));
    CHECK(one.status == 200);
    CHECK(one.body.find("first") != std::string::npos);
    std::remove("it-flow.db");
}

TEST(app_notes_are_private) {
    auto app = fresh_app("it-private.db");
    CHECK(handle(*app, make_request("POST", "/signup", "user=alice&password=hunter22")).status == 201);
    CHECK(handle(*app, make_request("POST", "/signup", "user=bob&password=swordfish1")).status == 201);
    const std::string alice =
        handle(*app, make_request("POST", "/login", "user=alice&password=hunter22")).set_cookie.substr(4, 32);
    const std::string bob =
        handle(*app, make_request("POST", "/login", "user=bob&password=swordfish1")).set_cookie.substr(4, 32);
    CHECK(handle(*app, make_request("POST", "/notes", "title=secret&body=hush", alice)).status == 303);

    CHECK(handle(*app, make_request("GET", "/notes/1", "", alice)).status == 200);
    CHECK(handle(*app, make_request("GET", "/notes/1", "", bob)).status == 404);
    CHECK(handle(*app, make_request("GET", "/notes/1", "")).status == 401);
    CHECK(handle(*app, make_request("GET", "/notes/1", "", std::string(32, '0'))).status == 401);
    CHECK(handle(*app, make_request("POST", "/notes", "title=mine&body=bobs+own", bob)).status ==
          303);
    CHECK(handle(*app, make_request("GET", "/", "", bob)).body.find("secret") == std::string::npos);
    std::remove("it-private.db");
}

TEST(app_write_concurrently_and_count) {
    auto app = fresh_app("it-race.db");
    CHECK(handle(*app, make_request("POST", "/signup", "user=alice&password=hunter22")).status == 201);
    const std::string sid =
        handle(*app, make_request("POST", "/login", "user=alice&password=hunter22")).set_cookie.substr(4, 32);

    std::vector<std::thread> writers;
    for (int worker = 0; worker < 8; ++worker) {
        writers.emplace_back([&app, &sid, worker] {
            for (int i = 0; i < 5; ++i) {
                const std::string body = "title=w" + std::to_string(worker) + "n" +
                                         std::to_string(i) + "&body=x";
                const Response r = handle(*app, make_request("POST", "/notes", body, sid));
                if (r.status != 303) std::fprintf(stderr, "unexpected status %d\n", r.status);
            }
        });
    }
    for (std::thread &t : writers) t.join();
    const Response page = handle(*app, make_request("GET", "/", "", sid));
    CHECK(page.body.find("40 note(s)") != std::string::npos);
    std::remove("it-race.db");
}

TEST(app_data_survives_closing_the_database) {
    std::string sid;
    {
        auto app = fresh_app("it-reopen.db");
        CHECK(handle(*app, make_request("POST", "/signup", "user=alice&password=hunter22")).status == 201);
        sid = handle(*app, make_request("POST", "/login", "user=alice&password=hunter22"))
                  .set_cookie.substr(4, 32);
        CHECK(handle(*app, make_request("POST", "/notes", "title=kept&body=still+here", sid)).status ==
              303);
    }
    auto reopened = std::unique_ptr<App>(new App(test_config("it-reopen.db")));
    // Re-opening runs migrate() again; a migration that is not idempotent destroys the
    // data it was written to protect.
    reopened->db.migrate();
    const Response page = handle(*reopened, make_request("GET", "/", "", sid));
    CHECK(page.status == 200);
    CHECK(page.body.find("1 note(s)") != std::string::npos);
    CHECK(page.body.find("kept") != std::string::npos);
    std::remove("it-reopen.db");
}

// ---------------------------------------------------------------------------
// Against the real binary: what the socket does is not what the handler does.
// ---------------------------------------------------------------------------

static int free_port() {
    const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return 0;
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = 0;
    if (::bind(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) != 0) { ::close(fd); return 0; }
    socklen_t len = sizeof addr;
    if (::getsockname(fd, reinterpret_cast<sockaddr *>(&addr), &len) != 0) { ::close(fd); return 0; }
    const int port = ntohs(addr.sin_port);
    ::close(fd);
    return port;
}

static pid_t spawn_server(const char *db_path, int port) {
    const pid_t pid = ::fork();
    if (pid != 0) return pid;
    const int devnull = ::open("/dev/null", O_WRONLY);
    if (devnull >= 0) { ::dup2(devnull, 1); ::dup2(devnull, 2); }
    const std::string arg_port = "--port=" + std::to_string(port);
    const std::string arg_db = std::string("--db=") + db_path;
    ::execl("./server", "./server", arg_port.c_str(), arg_db.c_str(), "--rounds=1000",
            "--log=/dev/null", static_cast<char *>(nullptr));
    ::_exit(127);
}

static bool wait_ready(int port, int tries) {
    for (int i = 0; i < tries; ++i) {
        const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd >= 0) {
            sockaddr_in addr{};
            addr.sin_family = AF_INET;
            addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
            addr.sin_port = htons(static_cast<unsigned short>(port));
            const bool up = ::connect(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) == 0;
            ::close(fd);
            if (up) return true;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
    return false;
}

static std::string http_exchange(int port, const std::string &request) {
    const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return "";
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<unsigned short>(port));
    if (::connect(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) != 0) { ::close(fd); return ""; }
    ::send(fd, request.data(), request.size(), 0);
    std::string response;
    char buf[4096];
    for (;;) {
        const ssize_t n = ::recv(fd, buf, sizeof buf, 0);
        if (n <= 0) break;
        response.append(buf, static_cast<std::size_t>(n));
    }
    ::close(fd);
    return response;
}

static std::string get(int port, const std::string &target, const std::string &sid = "") {
    return http_exchange(port, "GET " + target + " HTTP/1.1\r\nHost: t\r\n" +
                                   (sid.empty() ? "" : "Cookie: sid=" + sid + "\r\n") + "\r\n");
}

static std::string post(int port, const std::string &target, const std::string &body,
                        const std::string &sid = "") {
    const std::string head = "POST " + target + " HTTP/1.1\r\nHost: t\r\n" +
                             (sid.empty() ? "" : "Cookie: sid=" + sid + "\r\n") +
                             "Content-Length: " + std::to_string(body.size()) + "\r\n\r\n";
    return http_exchange(port, head + body);
}

static std::string session_of(const std::string &response) {
    const std::size_t at = response.find("sid=");
    if (at == std::string::npos) return "";
    const std::size_t end = response.find(';', at);
    return response.substr(at + 4, end == std::string::npos ? std::string::npos : end - (at + 4));
}

// Bounded, because an unbounded wait turns a broken test into a job that never ends.
static bool exit_zero_within(pid_t pid, int seconds) {
    for (int i = 0; i < seconds * 100; ++i) {
        int status = 0;
        const pid_t done = ::waitpid(pid, &status, WNOHANG);
        if (done == pid) return WIFEXITED(status) && WEXITSTATUS(status) == 0;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    ::kill(pid, SIGKILL);
    int status = 0;
    ::waitpid(pid, &status, 0);
    return false;
}

TEST(server_answers_a_real_client) {
    const char *db = "it-socket.db";
    std::remove(db);
    const int port = free_port();
    CHECK(port > 0);
    const pid_t pid = spawn_server(db, port);
    CHECK(pid > 0);
    CHECK(wait_ready(port, 100));

    CHECK(get(port, "/healthz").find(" 200 ") != std::string::npos);
    CHECK(post(port, "/signup", "user=alice&password=hunter22").find(" 201 ") != std::string::npos);
    CHECK(post(port, "/login", "user=alice&password=wrongpass").find(" 401 ") != std::string::npos);

    const std::string signed_in = post(port, "/login", "user=alice&password=hunter22");
    CHECK(signed_in.find(" 200 ") != std::string::npos);
    const std::string sid = session_of(signed_in);
    CHECK(sid.size() == 32);
    CHECK(get(port, "/", sid).find("0 note(s)") != std::string::npos);
    CHECK(post(port, "/notes", "title=From curl&body=over+a+socket", sid).find(" 303 ") !=
          std::string::npos);
    CHECK(get(port, "/", sid).find("From curl") != std::string::npos);
    CHECK(get(port, "/nope").find(" 404 ") != std::string::npos);

    const std::string out = post(port, "/logout", "", sid);
    CHECK(out.find(" 200 ") != std::string::npos);
    CHECK(get(port, "/", sid).find("<form method=\"post\" action=\"/login\">") != std::string::npos);

    ::kill(pid, SIGTERM);
    CHECK(exit_zero_within(pid, 5));
    std::remove(db);
}

TEST(server_keeps_the_session_across_a_restart) {
    const char *db = "it-restart.db";
    std::remove(db);
    const int port = free_port();
    const pid_t first = spawn_server(db, port);
    CHECK(wait_ready(port, 100));
    CHECK(post(port, "/signup", "user=alice&password=hunter22").find(" 201 ") != std::string::npos);
    const std::string sid = session_of(post(port, "/login", "user=alice&password=hunter22"));
    CHECK(post(port, "/notes", "title=survivor&body=restarted", sid).find(" 303 ") != std::string::npos);
    ::kill(first, SIGTERM);
    CHECK(exit_zero_within(first, 5));

    // Same file, different process: the note AND the session were both in the database,
    // so neither of them belonged to the process that has now stopped existing.
    const pid_t second = spawn_server(db, port);
    CHECK(wait_ready(port, 100));
    const std::string page = get(port, "/", sid);
    CHECK(page.find(" 200 ") != std::string::npos);
    CHECK(page.find("1 note(s)") != std::string::npos);
    CHECK(page.find("survivor") != std::string::npos);
    ::kill(second, SIGTERM);
    CHECK(exit_zero_within(second, 5));
    std::remove(db);
}

TEST(shutdown_waits_for_the_request_in_flight) {
    const char *db = "it-drain.db";
    std::remove(db);
    const int port = free_port();
    const pid_t pid = spawn_server(db, port);
    CHECK(wait_ready(port, 100));

    const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<unsigned short>(port));
    CHECK(::connect(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) == 0);
    // A request that promises 100 bytes and sends 9. The server is now genuinely busy
    // waiting for the rest, which is the only state worth testing a shutdown against.
    const std::string slow = "POST /notes HTTP/1.1\r\nHost: t\r\nContent-Length: 100\r\n\r\ntitle=x";
    ::send(fd, slow.data(), slow.size(), 0);

    ::kill(pid, SIGTERM);
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    int status = 0;
    CHECK(::waitpid(pid, &status, WNOHANG) == 0);   // still running: it has work to finish
    ::close(fd);                                     // the client goes away
    CHECK(exit_zero_within(pid, 5));                 // and only now is it allowed to stop
    std::remove(db);
}

int main() {
    return run_all();
}
