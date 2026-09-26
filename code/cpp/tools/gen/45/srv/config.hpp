// ch45 generator project — config layer of the notes service.
#pragma once

#include <cctype>
#include <cstdlib>
#include <fstream>
#include <map>
#include <optional>
#include <set>
#include <string>
#include <vector>

// Four places can set the same value, and the operator needs to know which one won.
// Every layer is therefore recorded as provenance next to the value itself, because
// "why is it listening on 8080" is the first question anybody asks at 3am and the
// answer is never "the default".
struct Config {
    int port = 8080;
    int workers = 4;
    unsigned rounds = 100000;
    std::string db_path = "notes.db";
    std::string log_path;                 // empty means the log goes to stdout
    std::string level = "info";
    std::map<std::string, std::string> source;   // key -> "default", "file", "env", "argv"

    bool strict() const { return rounds >= 1000 && port >= 1 && port <= 65535 &&
                                  workers >= 1 && workers <= 64; }
};

inline const std::set<std::string> &config_keys() {
    static const std::set<std::string> keys = {"port", "workers", "rounds", "db", "log", "level"};
    return keys;
}

inline std::string upper_key(const std::string &key) {
    std::string out;
    for (char c : key) out += static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    return out;
}

// Returns false and fills `err` rather than throwing: configuration happens at startup,
// and the only useful thing a program can do with a bad configuration is refuse to start
// and say exactly which line was wrong.
inline bool apply_pair(Config &c, const std::string &key, const std::string &value,
                       const std::string &where, std::string &err) {
    if (!config_keys().count(key)) { err = "unknown key '" + key + "'"; return false; }
    try {
        if (key == "port") c.port = std::stoi(value);
        else if (key == "workers") c.workers = std::stoi(value);
        else if (key == "rounds") c.rounds = static_cast<unsigned>(std::stoul(value));
        else if (key == "db") c.db_path = value;
        else if (key == "log") c.log_path = value;
        else if (key == "level") c.level = value;
    } catch (const std::exception &) {
        err = "value '" + value + "' is not valid for key '" + key + "'";
        return false;
    }
    c.source[key] = where;
    return true;
}

inline bool load_file(Config &c, const std::string &path, std::string &err) {
    std::ifstream in(path);
    if (!in) { err = "cannot read configuration file '" + path + "'"; return false; }
    std::string line;
    int lineno = 0;
    while (std::getline(in, line)) {
        ++lineno;
        std::size_t start = line.find_first_not_of(" \t");
        if (start == std::string::npos || line[start] == '#') continue;
        const std::size_t eq = line.find('=', start);
        if (eq == std::string::npos) {
            err = path + ":" + std::to_string(lineno) + ": expected key=value";
            return false;
        }
        std::string key = line.substr(start, eq - start);
        std::string value = line.substr(eq + 1);
        while (!key.empty() && (key.back() == ' ' || key.back() == '\t')) key.pop_back();
        const std::size_t vs = value.find_first_not_of(" \t");
        if (vs != std::string::npos) value = value.substr(vs);
        while (!value.empty() && (value.back() == ' ' || value.back() == '\t')) value.pop_back();
        std::string pair_err;
        if (!apply_pair(c, key, value, "file", pair_err)) {
            err = path + ":" + std::to_string(lineno) + ": " + pair_err;
            return false;
        }
    }
    return true;
}

inline bool load_env(Config &c, std::string &err) {
    for (const std::string &key : config_keys()) {
        const char *raw = std::getenv(("NOTESD_" + upper_key(key)).c_str());
        if (raw && *raw) {
            if (!apply_pair(c, key, raw, "env", err)) return false;
        }
    }
    return true;
}

inline bool load_argv(Config &c, int argc, char **argv, std::string &err, bool &print_config) {
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--print-config") { print_config = true; continue; }
        if (arg.rfind("--", 0) != 0) { err = "unexpected argument '" + arg + "'"; return false; }
        const std::string body = arg.substr(2);
        // `--config=` is handled before this pass, when the file layer is applied. It
        // is not a setting, it is where the settings come from.
        if (body.rfind("config=", 0) == 0) continue;
        const std::size_t eq = body.find('=');
        if (eq == std::string::npos) { err = "expected --key=value, got '" + arg + "'"; return false; }
        if (!apply_pair(c, body.substr(0, eq), body.substr(eq + 1), "argv", err)) return false;
    }
    return true;
}

inline std::string validate(const Config &c) {
    if (c.port < 1 || c.port > 65535) return "port must be 1..65535, got " + std::to_string(c.port);
    if (c.workers < 1 || c.workers > 64) return "workers must be 1..64, got " + std::to_string(c.workers);
    if (c.rounds < 1) return "rounds must be >= 1";
    if (c.db_path.empty()) return "db must not be empty";
    static const std::set<std::string> levels = {"debug", "info", "warn", "error"};
    if (!levels.count(c.level)) return "level must be one of debug, info, warn, error";
    return {};
}

// Printed by `--print-config`, and deliberately including WHERE each value came from.
inline std::string to_json(const Config &c) {
    static auto quote = [](const std::string &s) {
        std::string out = "\"";
        for (char ch : s) {
            if (ch == '"' || ch == '\\') { out += '\\'; out += ch; }
            else if (ch == '\t') out += "\\t";
            else out += ch;
        }
        return out + "\"";
    };
    struct Row { const char *key; std::string value; };
    const std::vector<Row> rows = {
        {"db", quote(c.db_path)},
        {"level", quote(c.level)},
        {"log", quote(c.log_path)},
        {"port", std::to_string(c.port)},
        {"rounds", std::to_string(c.rounds)},
        {"workers", std::to_string(c.workers)},
    };
    std::string out = "{\n";
    for (std::size_t i = 0; i < rows.size(); ++i) {
        auto it = c.source.find(rows[i].key);
        out += "  " + quote(rows[i].key) + ": {\"value\": " + rows[i].value + ", \"from\": " +
               quote(it == c.source.end() ? "default" : it->second) + "}" +
               (i + 1 == rows.size() ? "\n" : ",\n");
    }
    return out + "}";
}
