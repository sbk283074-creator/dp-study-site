#include <cstdio>
#include <map>
#include <stdexcept>
#include <string>
#include <string_view>

std::string escape_html(std::string_view input) {
    std::string out;
    out.reserve(input.size());
    for (const char c : input) {
        switch (c) {
            case '&':  out += "&amp;";  break;
            case '<':  out += "&lt;";   break;
            case '>':  out += "&gt;";   break;
            case '"':  out += "&quot;"; break;
            case '\'': out += "&#39;";  break;
            default:   out += c;        break;
        }
    }
    return out;
}

// `{{name}}` is escaped, `{{{name}}}` is inserted verbatim. The extra brace is
// deliberate friction: raw insertion should look different at a glance.
std::string render(const std::string &tpl, const std::map<std::string, std::string> &vars) {
    std::string out;
    out.reserve(tpl.size());
    std::size_t i = 0;
    while (i < tpl.size()) {
        const std::size_t open = tpl.find("{{", i);
        if (open == std::string::npos) {
            out += tpl.substr(i);
            break;
        }
        out += tpl.substr(i, open - i);

        const bool raw = tpl.compare(open, 3, "{{{") == 0;
        const std::size_t name_at = open + (raw ? 3 : 2);
        const std::size_t close = tpl.find(raw ? "}}}" : "}}", name_at);
        if (close == std::string::npos) {
            throw std::runtime_error("unterminated placeholder at offset " + std::to_string(open));
        }
        const std::string name = tpl.substr(name_at, close - name_at);
        const auto found = vars.find(name);
        if (found == vars.end()) {
            throw std::runtime_error("no value supplied for {{" + name + "}}");
        }
        out += raw ? found->second : escape_html(found->second);
        i = close + (raw ? 3 : 2);
    }
    return out;
}

int main() {
    const std::string tpl =
        "<h1>Hello {{name}}</h1>\n"
        "<p>{{body}}</p>\n"
        "<p class=\"raw\">{{{body}}}</p>\n";

    const std::map<std::string, std::string> vars = {
        {"name", "Ada"},
        {"body", "<script>alert(1)</script>"},
    };

    std::printf("%s", render(tpl, vars).c_str());

    std::printf("--- a missing value is an error, not an empty string ---\n");
    try {
        render("<p>{{oops}}</p>", vars);
    } catch (const std::runtime_error &e) {
        std::printf("  caught: %s\n", e.what());
    }

    std::printf("--- an unterminated placeholder is an error too ---\n");
    try {
        render("<p>{{oops</p>", vars);
    } catch (const std::runtime_error &e) {
        std::printf("  caught: %s\n", e.what());
    }
    return 0;
}
