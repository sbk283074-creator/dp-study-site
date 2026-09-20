#include "json.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <utility>

/* ------------------------------------------------------------------ writing */

std::string json_escape(const std::string &s) {
    std::string out;
    for (unsigned char c : s) {
        switch (c) {
        case '"':  out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\n': out += "\\n";  break;
        case '\r': out += "\\r";  break;
        case '\t': out += "\\t";  break;
        case '\b': out += "\\b";  break;
        case '\f': out += "\\f";  break;
        default:
            if (c < 0x20) {
                char buf[8];
                std::snprintf(buf, sizeof buf, "\\u%04x", c);
                out += buf;
            } else {
                out += static_cast<char>(c);
            }
        }
    }
    return out;
}

std::string json_number(double d) {
    /* JSON has no way to write NaN or Infinity, so neither may reach the wire. */
    if (!std::isfinite(d)) return "null";
    if (d == static_cast<double>(static_cast<long long>(d)) && std::fabs(d) < 1e15) {
        return std::to_string(static_cast<long long>(d));
    }
    char buf[32];
    std::snprintf(buf, sizeof buf, "%.15g", d);
    return buf;
}

Json::Json() : value_(nullptr) {}
Json::Json(std::nullptr_t) : value_(nullptr) {}
Json::Json(bool b) : value_(b) {}
Json::Json(int i) : value_(static_cast<double>(i)) {}
Json::Json(double d) : value_(d) {}
Json::Json(const char *s) : value_(std::string(s)) {}
Json::Json(std::string s) : value_(std::move(s)) {}
Json::Json(Array a) : value_(std::move(a)) {}
Json::Json(Object o) : value_(std::move(o)) {}

bool Json::is_null() const { return std::holds_alternative<std::nullptr_t>(value_); }
bool Json::is_bool() const { return std::holds_alternative<bool>(value_); }
bool Json::is_number() const { return std::holds_alternative<double>(value_); }
bool Json::is_string() const { return std::holds_alternative<std::string>(value_); }
bool Json::is_array() const { return std::holds_alternative<Array>(value_); }
bool Json::is_object() const { return std::holds_alternative<Object>(value_); }

bool Json::as_bool() const { return std::get<bool>(value_); }
double Json::as_number() const { return std::get<double>(value_); }
const std::string &Json::as_string() const { return std::get<std::string>(value_); }
const Json::Array &Json::as_array() const { return std::get<Array>(value_); }
const Json::Object &Json::as_object() const { return std::get<Object>(value_); }

void Json::dump_into(std::string &out) const {
    if (is_null())   { out += "null"; return; }
    if (is_bool())   { out += as_bool() ? "true" : "false"; return; }
    if (is_number()) { out += json_number(as_number()); return; }
    if (is_string()) { out += '"' + json_escape(as_string()) + '"'; return; }

    if (is_array()) {
        out += '[';
        bool first = true;
        for (const Json &item : as_array()) {
            if (!first) out += ',';
            first = false;
            item.dump_into(out);
        }
        out += ']';
        return;
    }

    out += '{';
    bool first = true;
    for (const auto &pair : as_object()) {
        if (!first) out += ',';
        first = false;
        out += '"' + json_escape(pair.first) + "\":";
        pair.second.dump_into(out);
    }
    out += '}';
}

std::string Json::dump() const {
    std::string out;
    dump_into(out);
    return out;
}

/* ------------------------------------------------------------------ reading */

namespace {

/* Turns a code point into the bytes UTF-8 writes for it. */
std::string utf8(unsigned cp) {
    std::string out;
    if (cp < 0x80) {
        out += static_cast<char>(cp);
    } else if (cp < 0x800) {
        out += static_cast<char>(0xC0 | (cp >> 6));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        out += static_cast<char>(0xE0 | (cp >> 12));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else {
        out += static_cast<char>(0xF0 | (cp >> 18));
        out += static_cast<char>(0x80 | ((cp >> 12) & 0x3F));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    }
    return out;
}

class Parser {
public:
    Parser(const std::string &text, std::size_t max_depth)
        : text_(text), max_depth_(max_depth) {}

    std::optional<Json> parse_document() {
        std::optional<Json> value = parse_value(0);
        if (!value) return std::nullopt;
        skip_ws();
        /* Anything left over means the text was not JSON, however good the start was. */
        if (pos_ != text_.size()) return std::nullopt;
        return value;
    }

private:
    const std::string &text_;
    std::size_t pos_ = 0;
    std::size_t max_depth_;

    bool eof() const { return pos_ >= text_.size(); }
    char peek() const { return eof() ? '\0' : text_[pos_]; }

    void skip_ws() {
        while (!eof()) {
            const char c = text_[pos_];
            if (c == ' ' || c == '\t' || c == '\n' || c == '\r') ++pos_;
            else break;
        }
    }

    bool literal(const char *word) {
        const std::size_t n = std::strlen(word);
        if (text_.compare(pos_, n, word) != 0) return false;
        pos_ += n;
        return true;
    }

    std::optional<Json> parse_value(std::size_t depth) {
        if (depth > max_depth_) return std::nullopt;
        skip_ws();
        if (eof()) return std::nullopt;

        const char c = peek();
        if (c == '{') return parse_object(depth);
        if (c == '[') return parse_array(depth);
        if (c == '"') {
            std::optional<std::string> s = parse_string();
            if (!s) return std::nullopt;
            return Json(std::move(*s));
        }
        if (literal("true"))  return Json(true);
        if (literal("false")) return Json(false);
        if (literal("null"))  return Json();
        return parse_number();
    }

    /* Four hex digits, or nothing. */
    std::optional<unsigned> hex4() {
        if (pos_ + 4 > text_.size()) return std::nullopt;
        unsigned value = 0;
        for (int i = 0; i < 4; ++i) {
            const char c = text_[pos_++];
            value <<= 4;
            if (c >= '0' && c <= '9')      value |= static_cast<unsigned>(c - '0');
            else if (c >= 'a' && c <= 'f') value |= static_cast<unsigned>(c - 'a' + 10);
            else if (c >= 'A' && c <= 'F') value |= static_cast<unsigned>(c - 'A' + 10);
            else return std::nullopt;
        }
        return value;
    }

    /* \uXXXX, including the case where one character is written as two escapes. */
    std::optional<std::string> parse_unicode() {
        std::optional<unsigned> first = hex4();
        if (!first) return std::nullopt;
        unsigned cp = *first;

        if (cp >= 0xD800 && cp <= 0xDBFF) {
            /* A high half. It is only a character once its low half arrives. */
            if (pos_ + 2 > text_.size() || text_[pos_] != '\\' || text_[pos_ + 1] != 'u') {
                return std::nullopt;
            }
            pos_ += 2;
            std::optional<unsigned> second = hex4();
            if (!second) return std::nullopt;
            if (*second < 0xDC00 || *second > 0xDFFF) return std::nullopt;
            cp = 0x10000u + ((cp - 0xD800u) << 10) + (*second - 0xDC00u);
        } else if (cp >= 0xDC00 && cp <= 0xDFFF) {
            return std::nullopt;      /* a low half with nothing in front of it */
        }
        return utf8(cp);
    }

    std::optional<std::string> parse_string() {
        if (peek() != '"') return std::nullopt;
        ++pos_;
        std::string out;
        while (true) {
            if (eof()) return std::nullopt;
            const unsigned char c = static_cast<unsigned char>(text_[pos_++]);
            if (c == '"') return out;
            if (c != '\\') {
                if (c < 0x20) return std::nullopt;    /* raw control character */
                out += static_cast<char>(c);
                continue;
            }
            if (eof()) return std::nullopt;
            switch (text_[pos_++]) {
            case '"':  out += '"';  break;
            case '\\': out += '\\'; break;
            case '/':  out += '/';  break;
            case 'b':  out += '\b'; break;
            case 'f':  out += '\f'; break;
            case 'n':  out += '\n'; break;
            case 'r':  out += '\r'; break;
            case 't':  out += '\t'; break;
            case 'u': {
                std::optional<std::string> encoded = parse_unicode();
                if (!encoded) return std::nullopt;
                out += *encoded;
                break;
            }
            default: return std::nullopt;             /* \x is not a JSON escape */
            }
        }
    }

    static bool is_digit(char c) { return c >= '0' && c <= '9'; }

    /* Scans the shape JSON allows first, then converts. Handing the whole
       remaining text to strtod would accept "nan", "0x10" and "1e999". */
    std::optional<Json> parse_number() {
        const std::size_t start = pos_;
        if (peek() == '-') ++pos_;
        if (!is_digit(peek())) return std::nullopt;
        if (peek() == '0') {
            ++pos_;                        /* a leading zero has to stand alone */
        } else {
            while (is_digit(peek())) ++pos_;
        }
        if (peek() == '.') {
            ++pos_;
            if (!is_digit(peek())) return std::nullopt;
            while (is_digit(peek())) ++pos_;
        }
        if (peek() == 'e' || peek() == 'E') {
            ++pos_;
            if (peek() == '+' || peek() == '-') ++pos_;
            if (!is_digit(peek())) return std::nullopt;
            while (is_digit(peek())) ++pos_;
        }
        const std::string digits = text_.substr(start, pos_ - start);
        return Json(std::strtod(digits.c_str(), nullptr));
    }

    std::optional<Json> parse_array(std::size_t depth) {
        ++pos_;                                   /* '[' */
        Json::Array items;
        skip_ws();
        if (peek() == ']') { ++pos_; return Json(std::move(items)); }
        while (true) {
            std::optional<Json> item = parse_value(depth + 1);
            if (!item) return std::nullopt;
            items.push_back(std::move(*item));
            skip_ws();
            if (peek() == ',') { ++pos_; continue; }
            if (peek() == ']') { ++pos_; return Json(std::move(items)); }
            return std::nullopt;
        }
    }

    std::optional<Json> parse_object(std::size_t depth) {
        ++pos_;                                   /* '{' */
        Json::Object fields;
        skip_ws();
        if (peek() == '}') { ++pos_; return Json(std::move(fields)); }
        while (true) {
            skip_ws();
            std::optional<std::string> key = parse_string();
            if (!key) return std::nullopt;
            skip_ws();
            if (peek() != ':') return std::nullopt;
            ++pos_;
            std::optional<Json> value = parse_value(depth + 1);
            if (!value) return std::nullopt;
            /* A repeated key keeps the last one, which is what JavaScript does. */
            fields.insert_or_assign(std::move(*key), std::move(*value));
            skip_ws();
            if (peek() == ',') { ++pos_; continue; }
            if (peek() == '}') { ++pos_; return Json(std::move(fields)); }
            return std::nullopt;
        }
    }
};

}  // namespace

std::optional<Json> Json::parse(const std::string &text, std::size_t max_depth) {
    Parser parser(text, max_depth);
    return parser.parse_document();
}
