#include <cstdio>
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

// Escaping HTML syntax does nothing about a URL's *scheme*. A link is executed,
// not displayed, so the only safe answer is an allow-list of schemes.
std::string safe_url(std::string_view input, std::string_view base) {
    const auto has = [&](std::string_view prefix) {
        return input.size() >= prefix.size() && input.compare(0, prefix.size(), prefix) == 0;
    };
    if (has("http://") || has("https://") || has("mailto:")) return std::string(input);
    if (!input.empty() && input.front() == '/' && input.size() > 1 && input[1] != '/') {
        return std::string(input);  // a site-relative path
    }
    if (input.empty()) return std::string(base);
    return std::string(base);  // anything else is not a URL we will emit
}

int main() {
    const std::string attack = "javascript:alert(document.cookie)";

    std::printf("--- text context ---\n");
    std::printf("  %s\n", escape_html("<script>alert(1)</script>").c_str());

    std::printf("--- URL context ---\n");
    std::printf("  escaped : %s\n", escape_html(attack).c_str());
    std::printf("  allowed : %s\n", safe_url(attack, "/").c_str());
    std::printf("  https   : %s\n", safe_url("https://example.com/a", "/").c_str());
    std::printf("  relative: %s\n", safe_url("/profile/ada", "/").c_str());
    std::printf("  protocol-relative: %s\n", safe_url("//evil.example", "/").c_str());
    std::printf("  empty   : %s\n", safe_url("", "/").c_str());

    std::printf("--- JavaScript context ---\n");
    // Neither of the two fixes above applies here. Data going into a script
    // block needs JSON encoding, not HTML escaping.
    const std::string payload = "</script><script>alert(1)</script>";
    std::printf("  html-escaped still breaks out: %s\n", escape_html(payload).c_str());
    return 0;
}
