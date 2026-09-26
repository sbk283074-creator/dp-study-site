// ch45 generator project — the HTTP layer, kept free of every other dependency so it
// can be unit tested without a socket, without a database and without a clock.
#pragma once

#include <sys/socket.h>
#include <unistd.h>

#include <cctype>
#include <cstddef>
#include <string>
#include <utility>
#include <vector>

struct Request {
    std::string method, target, body;
    std::vector<std::pair<std::string, std::string>> headers;

    std::string header(const std::string &name) const {
        for (const auto &h : headers) if (h.first == name) return h.second;
        return {};
    }

    // Cookie parsing has to tolerate ` theme=dark ; sid=abc `, which means trimming
    // both ends of every pair and not stopping at the first space.
    std::string cookie(const std::string &name) const {
        const std::string all = header("cookie");
        std::size_t i = 0;
        while (i < all.size()) {
            const std::size_t semi = all.find(';', i);
            std::string part = all.substr(i, semi == std::string::npos ? std::string::npos : semi - i);
            while (!part.empty() && (part.front() == ' ' || part.front() == '\t')) part.erase(part.begin());
            while (!part.empty() && (part.back() == ' ' || part.back() == '\t')) part.pop_back();
            const std::size_t eq = part.find('=');
            if (eq != std::string::npos && part.substr(0, eq) == name) return part.substr(eq + 1);
            if (semi == std::string::npos) break;
            i = semi + 1;
        }
        return {};
    }
};

struct Response {
    int status = 200;
    std::string body;
    std::string content_type = "text/html; charset=utf-8";
    std::string set_cookie;
    std::string location;
};

inline const char *reason_phrase(int code) {
    switch (code) {
        case 200: return "OK";
        case 201: return "Created";
        case 303: return "See Other";
        case 400: return "Bad Request";
        case 401: return "Unauthorized";
        case 404: return "Not Found";
        case 409: return "Conflict";
        case 500: return "Internal Server Error";
        default:  return "Status";
    }
}

inline std::string render_response(const Response &r) {
    std::string out = "HTTP/1.1 " + std::to_string(r.status) + " " + reason_phrase(r.status) + "\r\n";
    out += "Content-Type: " + r.content_type + "\r\n";
    out += "Content-Length: " + std::to_string(r.body.size()) + "\r\n";
    if (!r.location.empty()) out += "Location: " + r.location + "\r\n";
    if (!r.set_cookie.empty()) out += "Set-Cookie: " + r.set_cookie + "\r\n";
    out += "Connection: close\r\n\r\n";
    out += r.body;
    return out;
}

inline int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

// `+` means space only in a form body; `%xx` is the escape that matters, because a
// body that is not decoded is a body that silently truncates at the first space.
inline std::string url_decode(const std::string &in) {
    std::string out;
    for (std::size_t i = 0; i < in.size(); ++i) {
        if (in[i] == '+') { out += ' '; continue; }
        if (in[i] == '%' && i + 2 < in.size()) {
            const int hi = hex_value(in[i + 1]), lo = hex_value(in[i + 2]);
            if (hi >= 0 && lo >= 0) {
                out += static_cast<char>((hi << 4) | lo);
                i += 2;
                continue;
            }
        }
        out += in[i];
    }
    return out;
}

inline std::string form_value(const std::string &body, const std::string &key) {
    std::size_t i = 0;
    while (i < body.size()) {
        const std::size_t amp = body.find('&', i);
        const std::string pair = body.substr(i, amp == std::string::npos ? std::string::npos : amp - i);
        const std::size_t eq = pair.find('=');
        if (eq != std::string::npos && pair.substr(0, eq) == key) return url_decode(pair.substr(eq + 1));
        if (amp == std::string::npos) break;
        i = amp + 1;
    }
    return {};
}

inline void send_all(int fd, const std::string &data) {
    std::size_t sent = 0;
    while (sent < data.size()) {
        const ssize_t n = ::send(fd, data.data() + sent, data.size() - sent, 0);
        if (n <= 0) return;
        sent += static_cast<std::size_t>(n);
    }
}

// Reads exactly one request. Two limits are load-bearing: an unbounded header would
// let one client occupy the whole heap, and a body read that trusts Content-Length to
// be present would hang waiting for bytes that will never arrive.
inline bool read_request(int fd, Request &req) {
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
                std::string name = line.substr(0, colon);
                std::string value = line.substr(colon + 1);
                while (!value.empty() && (value.front() == ' ' || value.front() == '\t'))
                    value.erase(value.begin());
                while (!value.empty() && (value.back() == ' ' || value.back() == '\t'))
                    value.pop_back();
                for (char &c : name) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
                req.headers.emplace_back(name, value);
                if (name == "content-length")
                    content_length = static_cast<std::size_t>(std::stoul(value));
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
