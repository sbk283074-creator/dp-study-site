#include <cstdio>
#include <string>
#include <string_view>

// One function, because the five characters are the complete set for both
// contexts. The difference between text and attribute is not the escaper.
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

int main() {
    // A payload with no HTML metacharacter at all. It does not need one, if the
    // attribute is not quoted.
    const std::string value = "x onerror=alert(document.cookie)";

    std::printf("--- text context ---\n");
    std::printf("  <p>%s</p>\n", escape_html(value).c_str());

    std::printf("--- quoted attribute, escaped ---\n");
    std::printf("  <img src=\"%s\">\n", escape_html(value).c_str());

    std::printf("--- unquoted attribute, escaped ---\n");
    std::printf("  <img src=%s>\n", escape_html(value).c_str());
    std::printf("  -> escaping changed nothing here: a space still ends the attribute\n");

    std::printf("--- unquoted attribute, payload WITH a quote ---\n");
    const std::string quoted = "x\" onerror=\"alert(1)";
    std::printf("  <img src=%s>\n", escape_html(quoted).c_str());
    std::printf("  -> &quot; is inert inside an unquoted attribute value, and the\n");
    std::printf("     space still splits it: escaping is not a substitute for quotes\n");

    std::printf("--- the value that proves the escaper is context-blind ---\n");
    std::printf("  escaped == original ? %s\n",
                escape_html(value) == value ? "yes (no metacharacters)" : "no");
    return 0;
}
