#include <cstdio>
#include <map>
#include <stdexcept>
#include <string>

std::string escape_html(const std::string &input) {
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

// `{{#if name}} ... {{/if}}` renders the body only when `name` was supplied.
// Recursion over the body is what keeps placeholders inside a conditional
// subject to the same rules as the ones outside it.
std::string render(const std::string &tpl, const std::map<std::string, std::string> &vars) {
    std::string out;
    std::size_t i = 0;
    while (i < tpl.size()) {
        const std::size_t open = tpl.find("{{", i);
        if (open == std::string::npos) {
            out += tpl.substr(i);
            break;
        }
        out += tpl.substr(i, open - i);

        if (tpl.compare(open, 6, "{{#if ") == 0) {
            const std::size_t name_end = tpl.find("}}", open);
            if (name_end == std::string::npos) throw std::runtime_error("unterminated {{#if");
            const std::string name = tpl.substr(open + 6, name_end - open - 6);
            const std::size_t close = tpl.find("{{/if}}", name_end);
            if (close == std::string::npos) {
                throw std::runtime_error("{{#if " + name + "}} has no {{/if}}");
            }
            if (vars.count(name) != 0) {
                out += render(tpl.substr(name_end + 2, close - name_end - 2), vars);
            }
            i = close + 7;
            continue;
        }

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
        "<h1>{{title}}</h1>\n"
        "{{#if subtitle}}<p class=\"sub\">{{subtitle}}</p>{{/if}}\n"
        "<p>{{body}}</p>\n";

    std::printf("--- with a subtitle ---\n");
    std::printf("%s", render(tpl, {{"title", "Post"},
                                   {"subtitle", "a <b>subtitle</b>"},
                                   {"body", "text"}})
                          .c_str());

    std::printf("--- without one ---\n");
    std::printf("%s", render(tpl, {{"title", "Post"}, {"body", "text"}}).c_str());

    std::printf("--- the rules still apply inside the block ---\n");
    try {
        render("{{#if title}}{{missing}}{{/if}}", {{"title", "Post"}});
    } catch (const std::runtime_error &e) {
        std::printf("  caught: %s\n", e.what());
    }
    try {
        render("{{#if title}}no end", {{"title", "Post"}});
    } catch (const std::runtime_error &e) {
        std::printf("  caught: %s\n", e.what());
    }
    return 0;
}
