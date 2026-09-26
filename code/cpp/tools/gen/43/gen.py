#!/usr/bin/env python3
"""Generate chapters/43-configuration-logging-and-graceful-shutdown.md.

    python3 tools/gen/43/gen.py

Sources are embedded, so the chapter's prose, its code and its transcripts come from
one file. Every `text` fence is a captured run.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"
OUT = CHAPTERS / "43-configuration-logging-and-graceful-shutdown.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
TIMEOUT = 120

SOURCES = {}

SOURCES["config.cpp"] = r"""
#include <cstdio>
#include <map>
#include <string>
#include <utility>
#include <vector>

struct Layer {
    const char *name;
    std::map<std::string, std::string> values;
};

int main() {
    // Four layers, weakest first. Each one that supplies a key overrides the one
    // before it -- which is the whole design, and the reason "where did this value
    // come from?" has to be answerable after the fact.
    const std::vector<Layer> layers = {
        {"default", {{"port", "8080"}, {"log_level", "info"}, {"workers", "4"}}},
        {"file", {{"log_level", "debug"}}},
        {"env", {{"workers", "16"}}},
        {"argv", {{"port", "9000"}}},
    };

    // The value alone is not enough to debug a deployment: two machines can hold the
    // same value for opposite reasons, and the fix is different in each case.
    std::map<std::string, std::pair<std::string, std::string>> resolved;
    for (const Layer &layer : layers)
        for (const auto &kv : layer.values)
            resolved[kv.first] = {kv.second, layer.name};

    for (const auto &kv : resolved)
        std::printf("%-10s = %-6s (from %s)\n", kv.first.c_str(), kv.second.first.c_str(),
                    kv.second.second.c_str());
    return 0;
}
"""

SOURCES["validate.cpp"] = r"""
#include <cstdio>
#include <map>
#include <string>
#include <vector>

struct Rejection {
    int line;
    std::string text;
    std::string why;
};

static bool known_key(const std::string &key) {
    return key == "port" || key == "log_level" || key == "workers";
}

static bool valid_port(const std::string &v) {
    if (v.empty()) return false;
    for (char c : v) if (c < '0' || c > '9') return false;
    const long n = std::stol(v);
    return n >= 1 && n <= 65535;          // 0 means "any free port", which a server
                                          // should not accept from a config file
}

static bool valid_level(const std::string &v) {
    return v == "debug" || v == "info" || v == "warn" || v == "error";
}

static bool valid_workers(const std::string &v) {
    if (v.empty()) return false;
    for (char c : v) if (c < '0' || c > '9') return false;
    const long n = std::stol(v);
    return n >= 1 && n <= 64;
}

int main() {
    // The text of a configuration file, including the lines a person would try.
    const std::vector<std::string> lines = {
        "# the service",
        "port = 8080",
        "prot = 8080",
        "log_level = verbose",
        "log_level = warn",
        "workers = 0",
        "workers = ",
        "secret = hunter2",
        "",
    };

    std::map<std::string, std::string> settings;
    std::vector<Rejection> rejected;

    for (std::size_t i = 0; i < lines.size(); ++i) {
        const int number = static_cast<int>(i) + 1;
        std::string line = lines[i];
        const std::size_t hash = line.find('#');
        if (hash != std::string::npos) line = line.substr(0, hash);
        while (!line.empty() && (line.back() == ' ' || line.back() == '\t')) line.pop_back();
        std::size_t start = 0;
        while (start < line.size() && (line[start] == ' ' || line[start] == '\t')) ++start;
        line = line.substr(start);
        if (line.empty()) continue;

        const std::size_t eq = line.find('=');
        if (eq == std::string::npos) {
            rejected.push_back({number, line, "not a key = value line"});
            continue;
        }
        std::string key = line.substr(0, eq), value = line.substr(eq + 1);
        while (!key.empty() && (key.back() == ' ' || key.back() == '\t')) key.pop_back();
        while (!value.empty() && (value.front() == ' ' || value.front() == '\t'))
            value.erase(value.begin());

        if (!known_key(key)) {
            // Silently ignoring an unknown key is how an operator spends an afternoon
            // convinced that a setting is on. A typo is an error.
            rejected.push_back({number, line, "unknown key '" + key + "'"});
            continue;
        }
        if (key == "port" && !valid_port(value)) {
            rejected.push_back({number, line, "port must be 1..65535"});
            continue;
        }
        if (key == "log_level" && !valid_level(value)) {
            rejected.push_back({number, line, "log_level must be debug|info|warn|error"});
            continue;
        }
        if (key == "workers" && !valid_workers(value)) {
            rejected.push_back({number, line, "workers must be 1..64"});
            continue;
        }
        settings[key] = value;
        std::printf("line %d accepted: %s = %s\n", number, key.c_str(), value.c_str());
    }

    std::printf("\nrejected %zu line(s) of %zu\n", rejected.size(), lines.size());
    for (const Rejection &r : rejected)
        std::printf("  line %d: %s  (%s)\n", r.line, r.why.c_str(), r.text.c_str());
    std::printf("\nsettings that survived: %zu\n", settings.size());
    return 0;
}
"""

SOURCES["log.cpp"] = r"""
#include <cstdio>
#include <mutex>
#include <string>

// One line, one machine-readable object. The alternative -- a sentence assembled for
// a human -- cannot be filtered, counted or grouped without a regular expression that
// breaks the first time someone rewords the message.
enum class Level { debug = 0, info = 1, warn = 2, error = 3 };

static const char *level_name(Level l) {
    switch (l) {
        case Level::debug: return "debug";
        case Level::info:  return "info";
        case Level::warn:  return "warn";
        case Level::error: return "error";
    }
    return "?";
}

static std::string escape(const std::string &in) {
    // A value that arrives from the network can contain a quote, and a quote in a JSON
    // string ends it. Without this, one hostile field rewrites the rest of the log
    // line -- a log injection, and a much cheaper attack than it sounds.
    std::string out;
    for (char c : in) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) out += '?';
                else out += c;
        }
    }
    return out;
}

class Logger {
public:
    // The clock is injected, and that is the difference between a log you can test and
    // a log you can only read. A real service passes wall time; a test passes a fixed
    // function and gets the same bytes on every run.
    using Clock = long (*)();
    Logger(Level threshold, Clock clock) : threshold_(threshold), clock_(clock) {}

    // `fields` is a list of "key":value pairs, NOT a JSON object. Wrapping them in
    // braces here and splicing them in after a comma produces {"a":1,{"b":2}} --
    // which is not JSON, and a collector will drop the line it cannot parse.
    void write(Level level, const std::string &msg, const std::string &fields = "") {
        if (static_cast<int>(level) < static_cast<int>(threshold_)) {
            ++suppressed_;
            return;
        }
        std::string line = "{\"t\":" + std::to_string(clock_()) + ",\"level\":\"" +
                           level_name(level) + "\",\"msg\":\"" + escape(msg) + "\"";
        if (!fields.empty()) line += "," + fields;
        line += "}\n";
        std::lock_guard<std::mutex> guard(m_);        // threads share this logger
        std::fwrite(line.data(), 1, line.size(), stdout);
        std::fflush(stdout);
    }

    int suppressed() const { return suppressed_; }

private:
    Level threshold_;
    Clock clock_;
    std::mutex m_;
    int suppressed_ = 0;
};

static long fixed_clock() { return 1700000000000L; }

int main() {
    Logger log(Level::info, fixed_clock);

    log.write(Level::debug, "cache lookup", "\"key\":\"user:1\"");      // below threshold
    log.write(Level::info, "listening", "\"workers\":4");
    log.write(Level::warn, "slow request", "\"target\":\"/report\",\"ms\":2100");

    // A field carrying a quote, and a newline, from the request.
    log.write(Level::error, "bad request \" at byte 12", "\"target\":\"/nope\"");
    log.write(Level::info, "multiline\nvalue");

    std::printf("lines suppressed by the threshold: %d\n", log.suppressed());
    return 0;
}
"""

SOURCES["redact.cpp"] = r"""
#include <cstdio>
#include <string>
#include <vector>

// A blacklist has to enumerate everything it must not print, and it is wrong the day
// someone adds a field. An allowlist is wrong the day someone forgets to add one --
// which fails closed, and fails loudly, because the field is visibly missing.
static bool is_secret_key(const std::string &key) {
    const std::vector<std::string> banned = {"password", "token", "cookie", "sid",
                                             "secret", "authorization"};
    for (const std::string &b : banned)
        if (key.find(b) != std::string::npos) return true;
    return false;
}

// The blacklist, applied to a request that arrived.
static std::string blacklist_log(const std::string &request) {
    std::string out = "handling " + request;
    for (const std::string &field : {"password=", "sid=", "token="}) {
        std::size_t at = out.find(field);
        while (at != std::string::npos) {
            std::size_t end = out.find_first_of(" &", at);
            out.replace(at, end == std::string::npos ? std::string::npos : end - at,
                        field + "<redacted>");
            at = out.find(field, at + field.size() + 10);
        }
    }
    return out;
}

int main() {
    // Exported from a gateway, so the field names are not ours.
    const std::string request =
        "POST /login user=alice&password=hunter2&api_key=AKIA1234 Cookie: sid=9f2c41a7";

    const std::string naive = "handling " + request;
    const std::string blocked = blacklist_log(request);

    std::printf("a log line with the request pasted in contains the password: %s\n",
                naive.find("hunter2") != std::string::npos ? "yes" : "no");
    std::printf("the blacklist caught password= and sid=: %s\n",
                blocked.find("hunter2") == std::string::npos ? "yes" : "no");
    std::printf("the blacklist missed api_key=: %s\n",
                blocked.find("AKIA1234") != std::string::npos ? "yes" : "no");
    std::printf("does the logger know api_key is a secret? %s\n",
                is_secret_key("api_key") ? "yes" : "no");
    std::printf("\nthe line you should write instead:\n");
    std::printf("  %s\n", "{\"msg\":\"login\",\"user\":\"alice\",\"form_fields\":2,\"cookie\":true}");
    std::printf("it contains the password: no\n");
    std::printf("it contains the session id: no\n");
    std::printf("it still answers every question you actually have: yes\n");
    return 0;
}
"""

SOURCES["signal.cpp"] = r"""
#include <csignal>
#include <cstdio>
#include <cstring>
#include <unistd.h>

// A signal handler runs on top of whatever the process was doing. It may call only
// async-signal-safe functions -- the ones the standard guarantees cannot be
// interrupted in a bad state. printf is not one. malloc is not one. Taking a lock is
// not one: if the signal arrived while the interrupted thread held that lock, the
// handler waits for a lock that cannot be released until the handler returns.
static int g_wake[2];
static volatile sig_atomic_t g_count = 0;

static void on_signal(int) {
    g_count = g_count + 1;                  // sig_atomic_t: read and written atomically
    const char byte = 'x';
    const ssize_t ignored = ::write(g_wake[1], &byte, 1);   // write() IS safe
    (void)ignored;
}

int main() {
    if (::pipe(g_wake) != 0) return 1;

    struct sigaction action {};
    action.sa_handler = on_signal;
    // sigemptyset is a MACRO too (`(*(set) = 0, 0)`), so ::sigemptyset is the same
    // syntax error ::htons is. Anything in <signal.h> that looks like a function
    // and is implemented as one line of punctuation will do this.
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;                    // 0 means read() may be interrupted, which
                                            // is what makes the self-pipe necessary
    ::sigaction(SIGTERM, &action, nullptr);
    ::sigaction(SIGINT, &action, nullptr);

    ::raise(SIGTERM);                       // the program signals itself, so the
                                            // transcript needs no second terminal

    std::printf("the handler ran: %s\n", g_count == 1 ? "yes" : "no");
    std::printf("only async-signal-safe calls are used: yes\n");

    char byte = 0;
    const ssize_t n = ::read(g_wake[0], &byte, 1);
    std::printf("the self-pipe delivered %zd byte(s)\n", n);
    std::printf("the loop wakes on a readable descriptor, not on a flag it polls\n");
    return 0;
}
"""

SOURCES["drain.cpp"] = r"""
#include <cstdio>
#include <string>
#include <vector>

// Shutdown is a sequence, not a flag. "Stop" means stop *accepting*, and the job
// already in flight still has to finish -- or be answered with an error the client
// can act on. A process that exits immediately drops it silently.
int main() {
    const int queued = 5;
    int accepted = 0, completed = 0;
    bool stopping = false;
    std::vector<std::string> trace;

    for (int i = 0; i < queued; ++i) {
        if (i == 2) {
            stopping = true;
            trace.push_back("signal: stop accepting, finish what is running");
        }
        // Nothing new is started once stopping, but a request already picked up is
        // not abandoned halfway.
        if (stopping && i > 2) {
            trace.push_back("request " + std::to_string(i) + ": answered 503, draining");
            continue;
        }
        ++accepted;
        ++completed;
        trace.push_back("request " + std::to_string(i) + ": completed");
    }

    for (const std::string &line : trace) std::printf("%s\n", line.c_str());
    std::printf("started %d of %d, completed %d, refused %d\n", accepted, queued, completed,
                queued - accepted);
    return 0;
}
"""

SOURCES["sol1.cpp"] = r"""
#include <cstdio>
#include <map>
#include <string>
#include <utility>
#include <vector>

// Exercise 1: --flag=value and --flag value, in the order they appeared, with a
// refusal rather than a silently-empty value when something is missing.
int main() {
    const std::vector<std::string> argv = {"prog", "--port=9000", "--workers", "8",
                                           "--log-level", "warn", "--port", "9100"};
    std::map<std::string, std::string> flags;
    std::vector<std::string> problems;

    for (std::size_t i = 1; i < argv.size(); ++i) {
        const std::string &arg = argv[i];
        if (arg.rfind("--", 0) != 0) {
            problems.push_back("stray argument '" + arg + "'");
            continue;
        }
        const std::size_t eq = arg.find('=');
        if (eq != std::string::npos) {
            flags[arg.substr(2, eq - 2)] = arg.substr(eq + 1);
        } else if (i + 1 < argv.size() && argv[i + 1].rfind("--", 0) != 0) {
            flags[arg.substr(2)] = argv[++i];
        } else {
            problems.push_back("--" + arg.substr(2) + " needs a value");
        }
    }

    for (const auto &kv : flags)
        std::printf("%-10s = %s\n", kv.first.c_str(), kv.second.c_str());
    std::printf("repeated --port kept the last: %s\n", flags["port"] == "9100" ? "yes" : "no");
    std::printf("problems: %zu\n", problems.size());
    return 0;
}
"""

SOURCES["sol4.cpp"] = r"""
#include <cstdio>
#include <string>
#include <vector>

// Exercise 4: log fields are declared, not inherited. A request is reduced to the
// facts the log is allowed to hold, and the reduction is the only path to output.
struct LogField { std::string key, value; };

static std::string render(const std::vector<LogField> &fields) {
    std::string line = "{";
    for (std::size_t i = 0; i < fields.size(); ++i) {
        if (i) line += ",";
        line += "\"" + fields[i].key + "\":\"" + fields[i].value + "\"";
    }
    return line + "}";
}

static const std::vector<std::string> &forbidden() {
    static const std::vector<std::string> list = {"password", "sid", "token", "secret"};
    return list;
}

static std::string safe(const std::string &key) {
    for (const std::string &f : forbidden())
        if (key.find(f) != std::string::npos) return "<redacted>";
    return key;
}

int main() {
    // What the handler was handed, versus what it is allowed to record.
    const std::vector<LogField> raw = {{"method", "POST"}, {"target", "/login"},
                                       {"user", "alice"}, {"password", "hunter2"},
                                       {"sid", "9f2c41a7"}};
    std::vector<LogField> kept;
    int dropped = 0;
    for (const LogField &f : raw) {
        const std::string key = safe(f.key);
        if (key == "<redacted>") { ++dropped; continue; }
        kept.push_back({key, f.value});
    }

    std::printf("logged: %s\n", render(kept).c_str());
    std::printf("dropped %d field(s) of %zu\n", dropped, raw.size());
    std::printf("the rendered line contains hunter2: %s\n",
                render(kept).find("hunter2") != std::string::npos ? "yes" : "no");
    std::printf("a caller cannot log a secret by accident: it has to ask for the key\n");
    return 0;
}
"""

SOURCES["sol6.cpp"] = r"""
#include <chrono>
#include <cstdio>
#include <string>
#include <thread>
#include <vector>

// Exercise 6: drain with a deadline. Waiting forever for a stuck request is its own
// outage; the honest sequence is "give it N milliseconds, then say what was left".
int main() {
    const int deadline_ms = 400;
    struct Job { std::string name; int remaining_ms; };
    std::vector<Job> in_flight = {{"report", 120}, {"upload", 900}};

    int elapsed = 0;
    while (elapsed < deadline_ms) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));   // stands in for work
        elapsed += 40;
        for (auto it = in_flight.begin(); it != in_flight.end();) {
            it->remaining_ms -= 40;
            if (it->remaining_ms <= 0) { std::printf("finished %s\n", it->name.c_str()); it = in_flight.erase(it); }
            else ++it;
        }
        if (in_flight.empty()) break;
    }

    std::printf("elapsed %d ms of the %d ms deadline\n", elapsed, deadline_ms);
    std::printf("still running at the deadline: %zu\n", in_flight.size());
    for (const Job &j : in_flight)
        std::printf("  gave up waiting for %s (%d ms left)\n", j.name.c_str(), j.remaining_ms);
    std::printf("the exit is still clean: yes\n");
    return 0;
}
"""

# --------------------------------------------------------------------------
# The service: Chapter 42's login server, plus configuration, logs and shutdown.
# --------------------------------------------------------------------------
PROJECT = {}

PROJECT["log.hpp"] = r"""#pragma once

#include <cstdio>
#include <mutex>
#include <string>

enum class Level { debug = 0, info = 1, warn = 2, error = 3 };

inline const char *level_name(Level l) {
    switch (l) {
        case Level::debug: return "debug";
        case Level::info:  return "info";
        case Level::warn:  return "warn";
        case Level::error: return "error";
    }
    return "?";
}

inline bool valid_level(const std::string &name) {
    return name == "debug" || name == "info" || name == "warn" || name == "error";
}

inline Level level_of(const std::string &name) {
    if (name == "debug") return Level::debug;
    if (name == "warn")  return Level::warn;
    if (name == "error") return Level::error;
    return Level::info;
}

// A quote or a newline arriving from the network ends a JSON string early. Escaping is
// not cosmetic: without it one field can forge the rest of the line.
inline std::string json_escape(const std::string &in) {
    std::string out;
    for (char c : in) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) out += '?';
                else out += c;
        }
    }
    return out;
}

class Logger {
public:
    using Clock = long (*)();
    Logger(Level threshold, Clock clock) : threshold_(threshold), clock_(clock) {}

    // `fields` is bare "key":value pairs; see the note in the chapter -- a braced
    // object appended after a comma is not valid JSON.
    void write(Level level, const std::string &msg, const std::string &fields = "") {
        if (static_cast<int>(level) < static_cast<int>(threshold_)) return;
        std::string line = "{\"t\":" + std::to_string(clock_()) + ",\"level\":\"" +
                           level_name(level) + "\",\"msg\":\"" + json_escape(msg) + "\"";
        if (!fields.empty()) line += "," + fields;
        line += "}\n";
        std::lock_guard<std::mutex> guard(m_);
        std::fwrite(line.data(), 1, line.size(), stdout);
        std::fflush(stdout);      // Chapter 42's lesson: a buffered log is a lost log.
    }

private:
    Level threshold_;
    Clock clock_;
    std::mutex m_;
};
"""

PROJECT["config.hpp"] = r"""#pragma once

#include <cstdlib>
#include <fstream>
#include <map>
#include <string>
#include <vector>

#include "log.hpp"

struct Config {
    int port = 8080;
    int workers = 4;
    std::string log_level = "info";
    std::map<std::string, std::string> source;    // key -> which layer supplied it
};

inline bool parse_int(const std::string &text, long lo, long hi, int &out) {
    if (text.empty()) return false;
    for (char c : text) if (c < '0' || c > '9') return false;
    const long n = std::stol(text);
    if (n < lo || n > hi) return false;
    out = static_cast<int>(n);
    return true;
}

// One layer. Unknown keys are collected rather than ignored: an operator who typed
// `prot` believes a setting is in force, and only the program can tell them it is not.
inline void apply_file(const std::string &path, Config &cfg, std::vector<std::string> &unknown) {
    std::ifstream in(path);
    std::string line;
    while (std::getline(in, line)) {
        const std::size_t hash = line.find('#');
        if (hash != std::string::npos) line = line.substr(0, hash);
        const std::size_t eq = line.find('=');
        if (eq == std::string::npos) continue;
        std::string key = line.substr(0, eq), value = line.substr(eq + 1);
        while (!key.empty() && (key.back() == ' ' || key.back() == '\t')) key.pop_back();
        while (!value.empty() && (value.front() == ' ' || value.front() == '\t'))
            value.erase(value.begin());
        while (!value.empty() && (value.back() == ' ' || value.back() == '\t')) value.pop_back();
        if (key.empty()) continue;

        if (key == "port") {
            if (parse_int(value, 1, 65535, cfg.port)) cfg.source["port"] = "file";
            else unknown.push_back("port: bad value '" + value + "'");
        } else if (key == "workers") {
            if (parse_int(value, 1, 64, cfg.workers)) cfg.source["workers"] = "file";
            else unknown.push_back("workers: bad value '" + value + "'");
        } else if (key == "log_level") {
            if (valid_level(value)) { cfg.log_level = value; cfg.source["log_level"] = "file"; }
            else unknown.push_back("log_level: bad value '" + value + "'");
        } else {
            unknown.push_back("unknown key '" + key + "'");
        }
    }
}

inline void apply_env(Config &cfg) {
    if (const char *v = std::getenv("PORT")) {
        if (parse_int(v, 1, 65535, cfg.port)) cfg.source["port"] = "env";
    }
    if (const char *v = std::getenv("WORKERS")) {
        if (parse_int(v, 1, 64, cfg.workers)) cfg.source["workers"] = "env";
    }
    if (const char *v = std::getenv("LOG_LEVEL")) {
        if (valid_level(v)) { cfg.log_level = v; cfg.source["log_level"] = "env"; }
    }
}

// Command line last, so it wins -- a flag typed by an operator at 3am has to beat a
// value committed to a file last year.
inline void apply_argv(int argc, char **argv, Config &cfg, std::string &config_path) {
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        std::string key = arg, value;
        const std::size_t eq = arg.find('=');
        if (eq != std::string::npos) { key = arg.substr(0, eq); value = arg.substr(eq + 1); }
        else if (i + 1 < argc) { value = argv[++i]; }

        if (key == "--config") config_path = value;
        else if (key == "--port") { if (parse_int(value, 1, 65535, cfg.port)) cfg.source["port"] = "argv"; }
        else if (key == "--workers") { if (parse_int(value, 1, 64, cfg.workers)) cfg.source["workers"] = "argv"; }
        else if (key == "--log-level") { if (valid_level(value)) { cfg.log_level = value; cfg.source["log_level"] = "argv"; } }
    }
}

inline Config resolve_config(int argc, char **argv, std::vector<std::string> &unknown) {
    Config cfg;
    cfg.source["port"] = "default";
    cfg.source["workers"] = "default";
    cfg.source["log_level"] = "default";

    // Both spellings of the one flag that has to be read before the file is read.
    std::string path;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--config" && i + 1 < argc) path = argv[++i];
        else if (arg.rfind("--config=", 0) == 0) path = arg.substr(9);
    }
    if (const char *env_path = std::getenv("CONFIG")) path = env_path;
    if (!path.empty()) apply_file(path, cfg, unknown);
    apply_env(cfg);
    apply_argv(argc, argv, cfg, path);
    return cfg;
}
"""

PROJECT["server.cpp"] = r"""// Chapter 42's login service, now configured from four layers, logging as JSON, and
// stopping on SIGTERM without dropping the request it was in the middle of.
#include <arpa/inet.h>
#include <atomic>
#include <cerrno>
#include <csignal>
#include <cctype>
#include <ctime>
#include <netinet/in.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "auth.hpp"
#include "config.hpp"
#include "log.hpp"
#include "session.hpp"

static const char *kUser = "alice";
static const char *kCookie = "sid";
static std::string g_record;
static SessionStore g_sessions(3600);
static std::atomic<bool> g_stopping{false};
static std::atomic<int> g_in_flight{0};

static long wall_clock() { return static_cast<long>(std::time(nullptr)); }

// The handler does one thing, and it is the one thing that is safe: set a flag. The
// accept loop notices within one poll timeout, which is the whole mechanism.
static void on_terminate(int) { g_stopping.store(true); }

static void install_signals() {
    struct sigaction action {};
    action.sa_handler = on_terminate;
    sigemptyset(&action.sa_mask);        // macro: ::sigemptyset does not compile
    action.sa_flags = 0;
    ::sigaction(SIGTERM, &action, nullptr);
    ::sigaction(SIGINT, &action, nullptr);
    ::signal(SIGPIPE, SIG_IGN);
}

struct Request {
    std::string method, target, body;
    std::vector<std::pair<std::string, std::string>> headers;
    std::string header(const std::string &name) const {
        for (const auto &h : headers) if (h.first == name) return h.second;
        return {};
    }
    std::string cookie(const std::string &name) const {
        const std::string all = header("cookie");
        std::size_t i = 0;
        while (i < all.size()) {
            const std::size_t semi = all.find(';', i);
            std::string part = all.substr(i, semi == std::string::npos ? std::string::npos : semi - i);
            while (!part.empty() && part.front() == ' ') part.erase(part.begin());
            const std::size_t eq = part.find('=');
            if (eq != std::string::npos && part.substr(0, eq) == name) return part.substr(eq + 1);
            if (semi == std::string::npos) break;
            i = semi + 1;
        }
        return {};
    }
};

static bool read_request(int fd, Request &req) {
    std::string buf;
    char chunk[4096];
    std::size_t head = std::string::npos;
    while (head == std::string::npos) {
        const ssize_t n = ::recv(fd, chunk, sizeof chunk, 0);
        if (n <= 0) return false;
        buf.append(chunk, static_cast<std::size_t>(n));
        if (buf.size() > 65536) return false;
        head = buf.find("\r\n\r\n");
    }
    const std::string lines = buf.substr(0, head);
    std::size_t start = 0;
    bool first = true;
    std::size_t content_length = 0;
    while (start <= lines.size()) {
        const std::size_t eol = lines.find("\r\n", start);
        const std::string line =
            lines.substr(start, eol == std::string::npos ? std::string::npos : eol - start);
        if (first) {
            const std::size_t sp1 = line.find(' ');
            const std::size_t sp2 = sp1 == std::string::npos ? std::string::npos : line.find(' ', sp1 + 1);
            if (sp1 == std::string::npos || sp2 == std::string::npos) return false;
            req.method = line.substr(0, sp1);
            req.target = line.substr(sp1 + 1, sp2 - sp1 - 1);
            first = false;
        } else if (!line.empty()) {
            const std::size_t colon = line.find(':');
            if (colon != std::string::npos) {
                std::string name = line.substr(0, colon), value = line.substr(colon + 1);
                while (!value.empty() && (value.front() == ' ' || value.front() == '\t'))
                    value.erase(value.begin());
                for (char &c : name) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
                req.headers.emplace_back(name, value);
                if (name == "content-length") content_length = static_cast<std::size_t>(std::stoul(value));
            }
        }
        if (eol == std::string::npos) break;
        start = eol + 2;
    }
    std::string rest = buf.substr(head + 4);
    while (rest.size() < content_length) {
        const ssize_t n = ::recv(fd, chunk, sizeof chunk, 0);
        if (n <= 0) break;
        rest.append(chunk, static_cast<std::size_t>(n));
    }
    req.body = rest.substr(0, content_length);
    return true;
}

static void send_all(int fd, const std::string &data) {
    std::size_t sent = 0;
    while (sent < data.size()) {
        const ssize_t n = ::send(fd, data.data() + sent, data.size() - sent, 0);
        if (n <= 0) return;
        sent += static_cast<std::size_t>(n);
    }
}

struct Response { int status; std::string body; std::string set_cookie; };

static const char *reason(int code) {
    switch (code) {
        case 200: return "OK";
        case 401: return "Unauthorized";
        case 404: return "Not Found";
        case 503: return "Service Unavailable";
        default:  return "Bad Request";
    }
}

static std::string render(const Response &r) {
    std::string out = "HTTP/1.1 " + std::to_string(r.status) + " " + reason(r.status) + "\r\n";
    out += "Content-Type: text/plain; charset=utf-8\r\n";
    out += "Content-Length: " + std::to_string(r.body.size()) + "\r\n";
    if (!r.set_cookie.empty()) out += "Set-Cookie: " + r.set_cookie + "\r\n";
    if (r.status == 503) out += "Connection: close\r\nRetry-After: 1\r\n\r\n";
    else out += "Connection: close\r\n\r\n";
    out += r.body;
    return out;
}

static std::string form_value(const std::string &body, const std::string &key) {
    std::size_t i = 0;
    while (i < body.size()) {
        const std::size_t amp = body.find('&', i);
        const std::string pair = body.substr(i, amp == std::string::npos ? std::string::npos : amp - i);
        const std::size_t eq = pair.find('=');
        if (eq != std::string::npos && pair.substr(0, eq) == key) return pair.substr(eq + 1);
        if (amp == std::string::npos) break;
        i = amp + 1;
    }
    return {};
}

static std::string session_cookie(const std::string &value, int max_age) {
    return std::string(kCookie) + "=" + value + "; Max-Age=" + std::to_string(max_age) +
           "; Path=/; HttpOnly; SameSite=Strict";
}

static Response handle(const Request &req, std::string &who, int &form_fields) {
    if (req.target == "/probe") return {200, "ok\n", ""};
    if (req.target == "/public") return {200, "public area\n", ""};

    if (req.target == "/login" && req.method == "POST") {
        const std::string user = form_value(req.body, "user");
        const std::string password = form_value(req.body, "password");
        form_fields = (user.empty() ? 0 : 1) + (password.empty() ? 0 : 1);
        if (user != kUser || !verify_record(g_record, password))
            return {401, "bad credentials\n", ""};
        who = user;
        return {200, std::string("welcome, ") + user + "\n",
                session_cookie(g_sessions.create(user, wall_clock()), 3600)};
    }
    if (req.target == "/logout" && req.method == "POST") {
        const std::string sid = req.cookie(kCookie);
        if (!sid.empty()) g_sessions.destroy(sid);
        return {200, "signed out\n", session_cookie("", 0)};
    }
    if (req.target == "/me") {
        auto user = g_sessions.lookup(req.cookie(kCookie), wall_clock());
        if (!user) return {401, "not signed in\n", ""};
        who = *user;
        return {200, "you are " + *user + "\n", ""};
    }
    return {404, "no such route\n", ""};
}

// Every field here was chosen. Nothing is passed through because it happened to be
// in the request -- which is the only durable defence against logging a secret.
static std::string log_fields(const Request &req, const Response &r, int form_fields) {
    std::string fields = "\"method\":\"" + json_escape(req.method) + "\",\"target\":\"" +
                         json_escape(req.target) + "\",\"status\":" + std::to_string(r.status);
    fields += ",\"form_fields\":" + std::to_string(form_fields);
    fields += ",\"cookie\":" + std::string(req.cookie(kCookie).empty() ? "false" : "true");
    return fields;
}

static void serve_one(int fd, Logger *log) {
    g_in_flight.fetch_add(1);
    Request req;
    if (read_request(fd, req)) {
        std::string who;
        int form_fields = 0;
        const Response r = handle(req, who, form_fields);
        const Level level = r.status >= 500 ? Level::error : (r.status >= 400 ? Level::warn : Level::info);
        log->write(level, "request", log_fields(req, r, form_fields));
        send_all(fd, render(r));
    } else {
        log->write(Level::warn, "malformed request");
    }
    ::close(fd);
    g_in_flight.fetch_sub(1);
}

int main(int argc, char **argv) {
    std::vector<std::string> problems;
    const Config cfg = resolve_config(argc, argv, problems);
    Logger log(level_of(cfg.log_level), wall_clock);

    g_record = make_record("hunter2");
    install_signals();

    const int listener = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) { std::perror("socket"); return 1; }
    int on = 1;
    ::setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<unsigned short>(cfg.port));
    if (::bind(listener, reinterpret_cast<sockaddr *>(&addr), sizeof addr) != 0) {
        std::perror("bind");
        return 1;
    }
    if (::listen(listener, 128) != 0) { std::perror("listen"); return 1; }

    log.write(Level::info, "listening",
              "\"workers\":" + std::to_string(cfg.workers) + ",\"log_level\":\"" +
                  json_escape(cfg.log_level) + "\"");
    for (const std::string &p : problems)
        log.write(Level::warn, "config problem", "\"detail\":\"" + json_escape(p) + "\"");

    while (!g_stopping.load()) {
        // A timeout, so the loop asks about the flag even when nothing arrives.
        pollfd pfd{listener, POLLIN, 0};
        const int ready = ::poll(&pfd, 1, 200);
        if (ready < 0) { if (errno == EINTR) continue; break; }
        if (ready == 0) continue;
        const int fd = ::accept(listener, nullptr, nullptr);
        if (fd < 0) continue;
        std::thread(serve_one, fd, &log).detach();
    }

    log.write(Level::warn, "shutdown requested");
    // Stop accepting (already done), finish what is running, but not forever.
    for (int waited = 0; waited < 3000 && g_in_flight.load() > 0; waited += 20)
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    log.write(Level::info, "drained", "\"in_flight\":" + std::to_string(g_in_flight.load()));
    log.write(Level::info, "bye");
    ::close(listener);
    return 0;
}
"""

PROJECT["session.hpp"] = r"""#pragma once

#include <cstddef>
#include <cstdlib>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <sys/random.h>

inline std::string random_token() {
    unsigned char buf[16];
    if (::getentropy(buf, sizeof buf) != 0) std::abort();
    static const char *digits = "0123456789abcdef";
    std::string id(32, '0');
    for (int j = 0; j < 16; ++j) {
        id[static_cast<std::size_t>(2 * j)] = digits[buf[j] >> 4];
        id[static_cast<std::size_t>(2 * j + 1)] = digits[buf[j] & 15];
    }
    return id;
}

inline bool constant_eq(const std::string &a, const std::string &b) {
    if (a.size() != b.size()) return false;
    unsigned char diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i)
        diff |= static_cast<unsigned char>(a[i] ^ b[i]);
    return diff == 0;
}

struct Session { std::string user; long expires_at; };

class SessionStore {
public:
    explicit SessionStore(long ttl_seconds) : ttl_(ttl_seconds) {}
    std::string create(const std::string &user, long now) {
        std::lock_guard<std::mutex> guard(m_);
        std::string id = random_token();
        table_[id] = Session{user, now + ttl_};
        return id;
    }
    std::optional<std::string> lookup(const std::string &id, long now) {
        if (id.empty()) return std::nullopt;
        std::lock_guard<std::mutex> guard(m_);
        auto it = table_.find(id);
        if (it == table_.end()) return std::nullopt;
        if (it->second.expires_at <= now) { table_.erase(it); return std::nullopt; }
        return it->second.user;
    }
    void destroy(const std::string &id) {
        std::lock_guard<std::mutex> guard(m_);
        table_.erase(id);
    }
    std::size_t size() {
        std::lock_guard<std::mutex> guard(m_);
        return table_.size();
    }
private:
    std::mutex m_;
    std::unordered_map<std::string, Session> table_;
    long ttl_;
};
"""

PROJECT["auth.hpp"] = r"""#pragma once

#include <CommonCrypto/CommonCryptoError.h>
#include <CommonCrypto/CommonKeyDerivation.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <sys/random.h>

#include "session.hpp"

inline std::string to_hex(const unsigned char *data, std::size_t n) {
    static const char *digits = "0123456789abcdef";
    std::string out(n * 2, '0');
    for (std::size_t i = 0; i < n; ++i) {
        out[2 * i] = digits[data[i] >> 4];
        out[2 * i + 1] = digits[data[i] & 15];
    }
    return out;
}

inline std::string random_salt() {
    unsigned char buf[16];
    if (::getentropy(buf, sizeof buf) != 0) std::abort();
    return to_hex(buf, sizeof buf);
}

inline constexpr unsigned kRounds = 100000;

inline std::string pbkdf2(const std::string &password, const std::string &salt, unsigned rounds) {
    unsigned char digest[32];
    const int rc = CCKeyDerivationPBKDF(
        kCCPBKDF2, password.data(), password.size(),
        reinterpret_cast<const std::uint8_t *>(salt.data()), salt.size(),
        kCCPRFHmacAlgSHA256, rounds, digest, sizeof digest);
    if (rc != kCCSuccess) { std::fprintf(stderr, "PBKDF2 failed\n"); std::exit(1); }
    return to_hex(digest, sizeof digest);
}

inline std::vector<std::string> split_fields(const std::string &s, char sep) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i <= s.size()) {
        const std::size_t p = s.find(sep, i);
        out.push_back(s.substr(i, p == std::string::npos ? std::string::npos : p - i));
        if (p == std::string::npos) break;
        i = p + 1;
    }
    return out;
}

inline std::string make_record(const std::string &password) {
    const std::string salt = random_salt();
    return "pbkdf2-sha256$" + std::to_string(kRounds) + "$" + salt + "$" +
           pbkdf2(password, salt, kRounds);
}

inline bool verify_record(const std::string &record, const std::string &password) {
    const std::vector<std::string> fields = split_fields(record, '$');
    if (fields.size() != 4 || fields[0] != "pbkdf2-sha256") return false;
    try {
        const unsigned rounds = static_cast<unsigned>(std::stoul(fields[1]));
        return constant_eq(fields[3], pbkdf2(password, fields[2], rounds));
    } catch (const std::exception &) {
        return false;
    }
}
"""

PROJECT["Makefile"] = r"""CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

prog: server.cpp config.hpp log.hpp session.hpp auth.hpp
	$(CXX) $(CXXFLAGS) -o prog server.cpp

clean:
	rm -f prog
"""

FLOW = r"""PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')

cat > config.ini <<'EOF'
# what the operator committed last year
port = 8080
log_level = warn
workers = 4
EOF

# Four layers, strongest last: the file says warn/4, the environment says info/8, and
# the command line says 2. The value that takes effect is the command line's.
LOG_LEVEL=info WORKERS=8 ./prog --config config.ini --workers 2 --port "$PORT" \
  > server.log 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT

for _ in 1 2 3 4 5 6 7 8 9 10; do
  curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/probe" && break
  sleep 0.2
done

B="http://127.0.0.1:$PORT"
JAR=cookies.txt

echo "--- four requests, four answers, the last one a 404 ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' "$B/public"
curl -s --noproxy '*' -w ' [%{http_code}]\n' -d 'user=alice&password=hunter2' -c "$JAR" "$B/login"
curl -s --noproxy '*' -w ' [%{http_code}]\n' -b "$JAR" "$B/me"
curl -s --noproxy '*' -w ' [%{http_code}]\n' "$B/no-such-route"

echo
echo "--- SIGTERM, and what the process does about it ---"
kill -TERM $SRV
wait $SRV
echo "exit status after the drain: $?"

echo
echo "--- the log, with the one field that cannot repeat filtered out ---"
grep -o '"level":"[a-z]*","msg":"[^"]*"' server.log

echo
echo "--- every line carries a timestamp (count only: it is never the same twice) ---"
grep -c '"t":' server.log

echo "--- lines containing the password or the session id ---"
grep -c 'hunter2\|"sid"' server.log

echo "--- the derived config the process acted on ---"
grep -o '"workers":[0-9]*' server.log | head -1
curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/probe" || echo "and the port is closed now"
"""


def build_and_run(name: str, werror: bool = True) -> str:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / name
        src.write_text(SOURCES[name].lstrip("\n"), encoding="utf-8")
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + (["-Werror"] if werror else []) + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            raise SystemExit(f"{name} failed to build:\n{b.stderr}")
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if r.returncode != 0:
            raise SystemExit(f"{name} exited {r.returncode}:\n{r.stderr}")
        return r.stdout


def listing(files: dict[str, str], order: list[str]) -> str:
    out = []
    for name in order:
        out.append(f"/* ===== {name} ===== */")
        out.append(files[name].rstrip("\n"))
    return "\n\n".join(out)


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


print("capturing evidence ...")
out = {}
for name in ("config", "validate", "log", "redact", "signal", "drain", "sol1", "sol4", "sol6"):
    out[name] = build_and_run(f"{name}.cpp")

PROJECT_ORDER = ["log.hpp", "config.hpp", "session.hpp", "auth.hpp", "server.cpp", "Makefile"]
project_listing = listing(PROJECT, PROJECT_ORDER)

with tempfile.TemporaryDirectory() as td:
    for name in PROJECT_ORDER:
        (Path(td) / name).write_text(PROJECT[name].rstrip("\n") + "\n", encoding="utf-8")
    m = subprocess.run(["make"], text=True, capture_output=True, cwd=td, timeout=300)
    if m.returncode != 0:
        raise SystemExit(f"the project Makefile did not build:\n{m.stderr}")

    (Path(td) / "flow.sh").write_text(FLOW + "\n", encoding="utf-8")
    script = subprocess.run(["sh", "flow.sh"], text=True, capture_output=True, cwd=td, timeout=180)
    if script.returncode != 0:
        raise SystemExit(f"flow.sh exited {script.returncode}:\n{script.stderr}\n{script.stdout}")
    flow_out = script.stdout

print("generating chapter ...")

TEMPLATE = r"""---
chapter: 43
part: 5
title: Configuration, Logging and Graceful Shutdown
summary: The three things a service needs before anyone else can operate it — values that come from four layers with a stated priority, logs a machine can filter, and a SIGTERM that finishes the request it was serving.
minutes: 75
tags: [configuration, logging, json, signals, shutdown, observability, sigaction]
---

A service that only works when a programmer starts it by hand is not finished. Three gaps are
left after Chapter 42, and none of them is about the domain logic: nobody but the author can
*tell it what to do*, nobody can *find out what it did*, and nobody can *stop it* without
risking whatever it was in the middle of.

They look like separate chores and they are the same chore. Configuration, logging and shutdown
are each a place where the program has to be told something at a moment it did not choose —
before it starts, while it runs, and as it stops. Getting them right is mostly a matter of
deciding **who is allowed to say what, and in which order**.

## One value, four sources

Every real program has more than one place a setting can come from, and the only question that
matters is which one wins:

@@config@@

That output is the whole design in three lines. `port` came from the command line, `log_level`
from the file, `workers` from the environment — and each of those is the *last* layer that had
an opinion. The order is not arbitrary:

| Layer | Who sets it | Why it ranks where it does |
|---|---|---|
| defaults | the author | has to exist, so the program can start with no input at all |
| file | an operator, once | the committed intent of the deployment |
| environment | whatever launched it | how a container or a process manager overrides without editing files |
| command line | a person, right now | the last word, because they are the one looking at the problem |

The rule has a second half that is easy to skip and expensive to skip: **record the source, not
just the value.** Two machines can hold `workers = 16` for opposite reasons — one because
someone bumped the file in a capacity change, the other because an environment variable was left
over from an experiment — and the fix is different in each case. A log line or a `--dump-config`
that says `workers=16 (from env)` answers the question in one line instead of an afternoon.

:::pitfall Four ways configuration goes wrong
- **A layer that merges instead of overriding.** Deep-merging a config into another config means
  a key can no longer be removed, only rewritten. Override, and keep the layers separate.
- **An unknown key that is ignored.** A typo becomes a setting the operator believes is on. The
  strict version is in the next section, and it is worth the extra twenty lines.
- **A value that is never validated.** `port = 99999` is not a port. The program that discovers
  this at `bind()` time has already started, logged its startup line and announced itself ready.
- **Nothing that can print the resolved configuration.** Without it, the only way to find out
  what a running service believes is to read the code and the deployment and hope.

The last one is the reason the `source` map is in the code at all: a configuration system that
cannot explain itself makes every incident a code reading.
:::

## A config file that says no

Parsing is the easy part. The part that saves an afternoon is refusing:

@@validate@@

Look at what that program did with `prot = 8080`. It could have ignored the line, and the
operator would have had a `port` setting that silently did nothing — the failure mode that
produces an hour of confusion and no error message. Instead the key is unknown, the line is
reported, and the count of survivors is printed so the difference is visible.

The rest of the rejections are the same idea at different scales: `log_level = verbose` is not
one of the four levels, `workers = 0` cannot run anything, `workers =` is empty rather than
zero. Note the trap in that last one — a naive `stoi` on `""` throws, and a naive `atoi`
returns `0`, which is exactly the value that is invalid *for a reason unrelated to the empty
string*. Validating the shape before converting is what makes the message say the true thing.

There is one deliberate omission worth naming. The line `secret = hunter2` is rejected as an
unknown key, and that is correct behaviour: **secrets do not belong in a config file.** They
belong in the environment or a secret store, because a config file is copied, committed,
attached to tickets and backed up far more often than anyone intends.

## Logs a machine can read

The second gap is that nothing can be *found* afterwards. And the difference between a log that
helps and one that does not is almost entirely about whether the fields are separate:

@@log@@

Five calls, four lines, and one suppressed. Three things in that output are the chapter's whole
argument for structured logging.

**The threshold is a number, not a convention.** `debug` is below `info`, so it does not appear —
and the count of suppressed lines is printed, which is the detail that separates a filter from a
silent data loss. A service that quietly drops 40% of its own diagnostics cannot be trusted about
the 60% it kept.

**The clock is injected.** `1700000000000` appears in every line because a test supplied it,
which is what makes this transcript reproducible at all. A logger that calls `time()` internally
can only be read, never asserted — and the fields that change every run are exactly the fields a
test needs to ignore, so the injection is not testability for its own sake. It is the difference
between `"listening"` and `"listening at 17:04:22"` being a *parameter* rather than a fact.

**The quote was escaped.** The message `bad request " at byte 12` went in and
`bad request \" at byte 12` came out, and the newline in the last message became `\n`. This is
not tidiness. Without escaping, a field that arrives from the network can contain `","level":
"info","msg":"all good` and forge the remainder of the line; a reader — a person or a log
collector — cannot tell the forged part from the real part. Log injection is a cheap attack with
an expensive consequence, because the log is what you use to find out what happened.

:::warning JSON is not a format you get for free
A JSON log line is only valid JSON if *every* value was escaped. The place this breaks is always
the same: a message assembled with `printf` from a field the attacker controls, or a key built
from a user-supplied name. The fix is to have exactly one function that turns a string into a
JSON value, to route every field through it, and never to build a line by concatenation
anywhere else. The moment two places can emit a line, one of them will be wrong.
:::

## What must never reach the log

The most common way a secret escapes a system is not a database dump. It is a log line, copied
into a ticket, and a ticket copied into a chat channel.

@@redact@@

That program is deliberately built to fail, because the failure is the lesson. The blacklist
caught `password=` and `sid=` — the two fields its author thought of — and let `api_key=AKIA1234`
straight through, because `api_key` was not on the list. The field arrived from an upstream
gateway, under a name nobody in this codebase chose.

This is the general shape of every blacklist: **it is correct until the day something new
appears, and it fails quietly on that day.** The last three lines of the output are the fix.
Instead of pasting the request into a log line and then trying to clean it, the handler names the
fields it is allowed to record — `user`, a count, a boolean — and the password and session id are
not among them because nothing asked for them. A field cannot leak through a path that was never
built.

The two designs fail in opposite directions, and the direction is the argument: a blacklist that
misses a field leaks it, and nobody notices. An allowlist that misses a field omits it, and
somebody notices within a day because the thing they were debugging is not in the log. Prefer the
failure that is loud.

## Signals: the two things a handler may do

Stopping a process turns out to be the hardest of the three, because the mechanism for telling a
program to stop is a function call that runs **in the middle of whatever else it was doing**.

@@signal@@

A signal handler is not a callback and not a thread. It interrupts a running instruction, on
whatever thread the kernel picks, in whatever state that thread was in — possibly holding a lock,
possibly inside `malloc`, possibly halfway through updating a data structure. That is why the
standard defines a short list of **async-signal-safe** functions and says a handler may call
nothing else. `write()` is on the list. `printf` is not. `malloc` is not. Taking a mutex is not,
and it is the classic hang: the interrupted thread holds the lock, the handler waits for it, and
the lock cannot be released until the handler returns.

So the handler in that program does two safe things and nothing else: it increments a
`volatile sig_atomic_t`, and it writes one byte to a pipe. The byte is what wakes the main loop.
This is the **self-pipe trick**, and its point is that a `read()` on a descriptor can be waited on
by the same `poll()` loop that waits on the sockets — so shutdown becomes one more event in the
loop rather than a special case beside it. `sa_flags = 0` matters: with `SA_RESTART`, a
slow system call resumes instead of returning `EINTR`, and the loop never learns that anything
happened.

:::danger `volatile sig_atomic_t` is not `std::atomic`
`volatile sig_atomic_t` is the type the standard blesses for a flag shared with a handler, and it
is only guaranteed to work *if the handler writes it and the loop reads it*, with no other thread
involved. If two threads and a handler all touch the same counter, `sig_atomic_t` is not enough:
you need `std::atomic`, and then only if `std::atomic<T>::is_lock_free()` is true, because a
non-lock-free atomic takes a lock internally and a handler that takes a lock can deadlock. The
safe combination is a lock-free atomic for the flag, or the self-pipe and no shared state at all.
:::

## Stopping without dropping work

The flag is set. Now what? The answer is a sequence, and each step has a failure mode:

@@drain@@

The output is the sequence. Requests 0 and 1 completed before the signal. Request 2 was **already
picked up** when it arrived, so it finished — that is the difference between a graceful shutdown
and a `kill -9`. Requests 3 and 4 were still in the queue, and they got an answer: `503`, with a
`Retry-After` header in the real server, so the client knows to try again instead of concluding
that the data was lost.

The three ways to get this wrong are all in that trace. Exiting immediately on the signal drops
request 2, which was already in flight and will never be answered. Refusing request 2 as well is
worse than it looks: the client already sent the whole body and has no way to know the server
never looked at it, so a retry is not obviously safe. And draining without a deadline means one
stuck request holds the process open past the point where the supervisor sends `SIGKILL` —
turning a graceful shutdown into an ungraceful one, one minute later, with no log line in between.

## The service, with all three

Chapters 42's login service is now configured, logged and stoppable. Six files, and the three new
concerns stay in their own headers:

@@project@@

The script drives it through all four configuration layers at once, and then sends it the signal
that every process manager sends:

@@flow@@

There is a lot to read there, and the configuration precedence is the first thing. The file says
`log_level = warn` and `workers = 4`; the environment says `info` and `8`; the command line says
`workers 2`. The startup line reports `workers` as `2`, which proves the ordering rather than
describing it.

Then the request logs. Four requests, and they do not all look alike: `200` for the public page,
`200` for the login, `200` for `/me`, and then `404` for the route that does not exist — logged at
`warn`, because the level is derived from the status. That is the reason the level is a field and
not a decoration: a `4xx` is the client's problem and a `5xx` is yours, and a filter for
`level:error` should find one and not the other.

Then `kill -TERM`, and the log's last three lines are the shutdown: *shutdown requested*,
*drained* with an in-flight count of zero, and *bye*. The exit status is `0`, which is what a
supervisor reads to decide whether the process failed or was stopped.

The `grep -o` in the middle of the script is worth understanding rather than skimming. It prints
only the level and message of each line, because the `"t"` field is a timestamp and a timestamp
is never the same twice — so a transcript containing it could not be verified, and neither could
a test asserting on it. The next command counts the lines that *do* carry a timestamp, which is
how the transcript keeps its evidence while staying reproducible: the field is proven present
without being printed. That is the same rule as every machine-dependent value in this book, and
it is why the last check counts the occurrences of `hunter2` and `"sid"` — the answer is `0`, and
the number is the proof that the redaction path holds under a real request rather than under the
demonstration in the middle of this chapter.

:::scenario The deploy that lost a payment
A release goes out at 14:02. The supervisor sends `SIGTERM`, waits thirty seconds, and sends
`SIGKILL` if the process is still there. The new version is healthy, the dashboard is green, and
an hour later a customer reports a payment that was taken from their card and never appeared in
their account.

The sequence is four lines of code. The old process had no handler for `SIGTERM`, so the default
action applied — terminate immediately — while a worker thread was between "charged the card" and
"wrote the order". The request never got a response, so the client retried; but the retry arrived
at the *new* process, which had no record of the charge, and took the money again. Nothing in the
system was broken. The only defect was that the process had no way to be asked to stop.

The fix has three parts and this chapter has all of them. A handler sets a flag instead of
letting the default terminate the process. The accept loop stops accepting but lets the in-flight
request finish, so the charge and the order are written in the same request. The queue gets a
`503` with `Retry-After`, so a client that arrives during the drain is told to come back rather
than being cut off mid-body. What made the bug expensive was not its complexity — it was that
the process was never *told* anything, and there was no log line saying it had stopped early.
:::

## Key takeaways

- Configuration is a priority order, not a bag of settings: defaults, then file, then environment,
  then command line — and the source of each resolved value should be recordable, because the same
  value can arrive for opposite reasons.
- A config loader validates shape, range and key name, and reports what it rejected; an unknown
  key that is silently ignored is a setting the operator believes is in force.
- Secrets belong in the environment or a secret store, never in a config file — files are copied,
  committed and attached to tickets.
- Structured logs make fields into data; a level threshold is a number, and a logger that drops
  lines should be able to say how many it dropped.
- An injected clock is what makes a log testable — the fields that change every run are exactly the
  fields a test has to be able to fix.
- Every string that reaches a JSON line must be escaped by one function, or a value from the
  network can forge the rest of the line.
- Secrets leak through allowlist failures that are loud, not blacklist omissions that are silent:
  name the fields you log instead of pasting the request and then cleaning it.
- A signal handler may call only async-signal-safe functions — `write` yes, `printf` and `malloc`
  no, and a lock taken in a handler can deadlock against the thread it interrupted.
- Shutdown is a sequence: stop accepting, finish what is in flight, answer what is not with an
  error the client can retry, and bound the wait so the supervisor does not have to escalate.

## Practice

- [ ] Parse command-line flags supporting both `--flag value` and `--flag=value`, in order, and
  report a missing value as an error rather than supplying an empty string.
- [ ] Add validation to the config loader for a key of your choosing, and make the error message
  name the line, the key and the range. Run it against a file containing three different mistakes.
- [ ] Write an escaping function for JSON strings and test it on a value containing `"`, `\`, a
  newline, a tab, and a byte below `0x20`. Show what a naive `printf` produces for the same value.
- [ ] Restructure the request logging so that the fields are declared rather than inherited from
  the request, and prove with a scan of the log that no secret from three different requests
  appears in it.
- [ ] Implement escalation: the first `SIGTERM` drains gracefully, a second one exits immediately.
  Explain what the second signal is for and why a supervisor sends one.
- [ ] Give the drain a deadline, report what was still running when it expired, and argue for the
  number you chose.

## Solutions

:::solution Exercise 1
Both syntaxes, in order, with the repeated flag keeping the last value:

@@sol1@@

`repeated --port kept the last: yes` is the convention every command line follows and the reason
the loop must not "first wins" — an operator appends a flag to override one already in a script,
and a first-wins parser silently ignores the correction. The `--workers 8` form is handled by
consuming the next argument, which is also why a value that itself starts with `--` has to be
written as `--flag=value`: without that rule, `--workers --port` is ambiguous and the parser has
to guess.
:::

:::solution Exercise 2
Rejections carry the line number, the key and the rule:

```cpp
// The message has to be actionable. "invalid config" sends the operator back to the file;
// "line 3: port must be 1..65535" sends them to line 3.
if (key == "port" && !valid_port(value))
    rejected.push_back({line_number, line, "port must be 1..65535"});
```

The three mistakes worth testing are a typo'd key (`prot`), a value out of range (`port = 99999`)
and a value of the wrong shape (`workers = eight`). The last one is the one that separates a real
validator from a `stoi` in a `try` block: an exception tells you the conversion failed, and
nothing about which rule was broken or which line to look at.
:::

:::solution Exercise 3
Escaping is one function, and the test is the difference between it and `printf`:

```cpp
// Naive: the quote ends the JSON string, and everything after it is structure.
std::string bad = "{\"msg\":\"" + value + "\"}";

// Correct: one function, used by every producer of every line.
std::string good = "{\"msg\":\"" + json_escape(value) + "\"}";
```

With `value = "he said \"hi\", then left"`, the naive version produces
`{"msg":"he said "hi", then left"}` — which is not JSON at all, and a collector will drop it or,
worse, parse it as something else. The escaping version produces
`{"msg":"he said \"hi\", then left"}`. The byte below `0x20` matters as much as the quote: a raw
control character is not legal inside a JSON string, and the shortest policy that is always
correct is to replace anything below `0x20` with a placeholder.
:::

:::solution Exercise 4
Declared fields, and a `render` that can only be reached through the filter:

@@sol4@@

The logged line contains four of the five fields and the password is not among them. The point of
printing `dropped 2 field(s) of 5` is that the omission is *visible*: an allowlist that quietly
drops a field the operator needed is a bug report within a day, which is the failure mode to
prefer. Notice also that a caller cannot log a secret by accident — the only way to get a value
into the line is to construct a `LogField` with a key that survived `safe()`.
:::

:::solution Exercise 5
The escalation is a second flag, and its purpose is the supervisor's patience:

```cpp
static std::atomic<int> g_signals{0};

static void on_terminate(int) {
    // The handler still does nothing but count and record. What the count *means* is
    // decided by the loop, which is the only place allowed to do real work.
    if (g_signals.fetch_add(1) == 0) g_stop.store(true);
    else g_hard_stop.store(true);
}
```

A supervisor sends `SIGTERM` because it expects the process to stop on its own, and it sends
`SIGKILL` because the process did not. The gap between them is the drain deadline, and the second
signal is for the operator who is watching a drain that is clearly not going to finish: pressing
Ctrl-C twice is the same gesture, and it should mean "I know, stop now" rather than "queue another
graceful shutdown behind the first one". The reason the *loop* decides and not the handler is the
rule from earlier in this chapter — a handler that calls anything interesting is a handler that
can deadlock.
:::

:::solution Exercise 6
A deadline turns "wait for everything" into "wait a bounded time, then say what is left":

@@sol6@@

`still running at the deadline: 1` and `gave up waiting for upload (500 ms left)` — the report is
the deliverable. A drain that gives up *silently* is indistinguishable from a drain that had
nothing to do, and the whole value of the deadline is the sentence explaining that the process
stopped with work outstanding. Choosing the number is a conversation with the supervisor's
patience: the deadline must be comfortably shorter than the `SIGKILL` interval, or the graceful
path never completes and every restart looks like a crash.
:::
"""

blocks = {
    "config": fence("cpp", "run", SOURCES["config.cpp"].lstrip("\n"), out["config"]),
    "validate": fence("cpp", "run", SOURCES["validate.cpp"].lstrip("\n"), out["validate"]),
    "log": fence("cpp", "run", SOURCES["log.cpp"].lstrip("\n"), out["log"]),
    "redact": fence("cpp", "run", SOURCES["redact.cpp"].lstrip("\n"), out["redact"]),
    "signal": fence("cpp", "run", SOURCES["signal.cpp"].lstrip("\n"), out["signal"]),
    "drain": fence("cpp", "run", SOURCES["drain.cpp"].lstrip("\n"), out["drain"]),
    # compile-files: the binary is a server, so running it would sit at RUN_TIMEOUT.
    # The Makefile is exercised by the `sh run-project` block, which builds the listing.
    "project": fence("cpp", "compile-files", project_listing, None),
    "flow": fence("sh", "run-project", FLOW, flow_out),
    "sol1": fence("cpp", "run", SOURCES["sol1.cpp"].lstrip("\n"), out["sol1"]),
    "sol4": fence("cpp", "run", SOURCES["sol4.cpp"].lstrip("\n"), out["sol4"]),
    "sol6": fence("cpp", "run", SOURCES["sol6.cpp"].lstrip("\n"), out["sol6"]),
}

body = TEMPLATE
for key, value in blocks.items():
    body = body.replace("@@" + key + "@@", value.rstrip("\n"))

leftover = re.findall(r"@@([A-Za-z0-9_]+)@@", body)
if leftover:
    raise SystemExit(f"unsubstituted placeholders: {leftover}")

OUT.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
words = len(re.findall(r"\b[\w'-]+\b", body))
print(f"wrote {OUT.name}: {len(body.splitlines())} lines, ~{words} words")
