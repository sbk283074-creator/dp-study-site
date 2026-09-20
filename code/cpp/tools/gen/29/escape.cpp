#include <cstdio>
#include <string>

/* ---------- the version that "works" until the data has a newline in it ---------- */
std::string naive(const std::string &s) {
    return "{\"msg\":\"" + s + "\"}";
}

/* ---------- the version that is actually JSON ---------- */
std::string escape(const std::string &s) {
    std::string out;
    for (unsigned char c : s) {
        switch (c) {
        case '"':  out += "\\\"";  break;
        case '\\': out += "\\\\";  break;
        case '\n': out += "\\n";   break;
        case '\r': out += "\\r";   break;
        case '\t': out += "\\t";   break;
        case '\b': out += "\\b";   break;
        case '\f': out += "\\f";   break;
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

std::string proper(const std::string &s) {
    return "{\"msg\":\"" + escape(s) + "\"}";
}

/* Count the bytes a JSON parser is not allowed to find inside a string. */
std::size_t raw_controls(const std::string &s) {
    std::size_t n = 0;
    for (unsigned char c : s) {
        if (c < 0x20) ++n;
    }
    return n;
}

struct Case {
    const char *label;
    const char *raw;
};

int main() {
    std::printf("what happens to each character\n");
    std::printf("-----------------------------\n");
    const Case cases[] = {
        {"plain letters", "hello"},
        {"a double quote", "he said \"hi\""},
        {"a backslash", "C:\\temp"},
        {"a forward slash", "a/b"},
        {"a tab", "a\tb"},
        {"a newline", "a\nb"},
        {"a bell", "a\ab"},
    };
    for (const Case &c : cases) {
        std::printf("  %-16s -> %s\n", c.label, escape(c.raw).c_str());
    }

    std::printf("\nwhat the client actually receives\n");
    std::printf("--------------------------------\n");
    const std::string msg = "line one\nline two";
    const std::string a = naive(msg);
    const std::string b = proper(msg);
    std::printf("  naive  output : %zu bytes, %zu raw control character(s)\n",
                a.size(), raw_controls(a));
    std::printf("  proper output : %zu bytes, %zu raw control character(s)\n",
                b.size(), raw_controls(b));
    std::printf("  a string in JSON may contain no raw control character at all\n");
    return 0;
}
