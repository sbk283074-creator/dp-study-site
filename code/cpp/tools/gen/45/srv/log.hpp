// ch45 generator project — structured logging with provenance-safe fields.
#pragma once

#include <cstdarg>
#include <cstdio>
#include <ctime>
#include <mutex>
#include <string>
#include <utility>
#include <vector>

#include "config.hpp"

// A log line is a machine-readable record, so it is one line per event and every
// value is escaped. The escaping is not politeness: without it a request containing a
// newline can write a second, entirely fabricated line -- `GET /a%0Alevel=error%0Amsg=x`
// -- and whoever greps the file later believes it.
inline std::string json_escape(const std::string &in) {
    std::string out;
    for (unsigned char c : in) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if (c < 0x20) {
                    static const char *digits = "0123456789abcdef";
                    out += "\\u00";
                    out += digits[c >> 4];
                    out += digits[c & 15];
                } else {
                    out += static_cast<char>(c);
                }
        }
    }
    return out;
}

class Logger {
public:
    explicit Logger(const Config &c) : config_(c) {
        if (!c.log_path.empty()) file_ = std::fopen(c.log_path.c_str(), "a");
        if (!file_) file_ = stdout;
    }
    ~Logger() { if (file_ && file_ != stdout) std::fclose(file_); }
    Logger(const Logger &) = delete;
    Logger &operator=(const Logger &) = delete;

    static int rank(const std::string &level) {
        if (level == "debug") return 10;
        if (level == "info") return 20;
        if (level == "warn") return 30;
        if (level == "error") return 40;
        return 0;
    }

    void emit(const std::string &level, const std::string &msg,
              const std::vector<std::pair<std::string, std::string>> &fields = {}) {
        if (rank(level) < rank(config_.level)) return;
        std::lock_guard<std::mutex> guard(mutex_);
        std::string line = "{\"t\": " + std::to_string(static_cast<long long>(std::time(nullptr))) +
                           ", \"level\": \"" + json_escape(level) +
                           "\", \"msg\": \"" + json_escape(msg) + "\"";
        for (const auto &kv : fields)
            line += ", \"" + json_escape(kv.first) + "\": \"" + json_escape(kv.second) + "\"";
        line += "}\n";
        std::fwrite(line.data(), 1, line.size(), file_);
        // Flushed on every line: stdout sent to a file is BLOCK buffered, and a
        // redirection therefore changes how much of the log anybody can see.
        std::fflush(file_);
    }

    // The last line of defence, not the first. An allow-list of fields is what really
    // keeps secrets out of the log (see `access`); this exists so that even the one
    // place that handles a password can be read out loud in a review.
    static std::string redact(const std::string &) { return "<redacted>"; }

    void access(const std::string &method, const std::string &target, int status, long micros) {
        emit("info", "request", {{"method", method},
                                 {"target", target},
                                 {"status", std::to_string(status)},
                                 {"micros", std::to_string(micros)}});
    }

private:
    Config config_;
    std::FILE *file_ = nullptr;
    std::mutex mutex_;
};
