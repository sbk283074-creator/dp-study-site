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

static std::string lower(std::string_view s) {
    std::string out(s);
    for (char &c : out) {
        if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
    }
    return out;
}

// The scheme is everything before the FIRST colon. Searching the whole string
// for "data:" would reject a perfectly ordinary URL that merely mentions it.
std::string safe_url(std::string_view raw, std::string_view fallback) {
    const std::size_t colon = raw.find(':');
    if (colon != std::string_view::npos) {
        bool scheme_shaped = true;
        for (std::size_t i = 0; i < colon; ++i) {
            const char c = raw[i];
            const bool ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                            (c >= '0' && c <= '9') || c == '+' || c == '-' || c == '.';
            if (!ok) scheme_shaped = false;
        }
        if (scheme_shaped) {
            const std::string scheme = lower(raw.substr(0, colon));
            if (scheme == "http" || scheme == "https" || scheme == "mailto") {
                return escape_html(raw);
            }
            return std::string(fallback);  // data:, vbscript:, javascript:, ...
        }
    }
    if (raw.size() > 1 && raw.front() == '/' && raw[1] == '/') {
        return std::string(fallback);  // protocol-relative means "another host"
    }
    if (!raw.empty() && raw.front() == '#') {
        return std::string(fallback);  // a fragment is not a destination
    }
    return escape_html(raw);  // no scheme: a relative path
}

static void check(std::string_view url) {
    std::printf("  %-46s -> %s\n", std::string(url).c_str(), safe_url(url, "/").c_str());
}

int main() {
    std::printf("rejected:\n");
    check("data:text/html;base64,PHNjcmlwdD4=");
    check("vbscript:msgbox(1)");
    check("javascript:alert(1)");
    check("JaVaScRiPt:alert(1)");
    check("//evil.example");
    check("#section");

    std::printf("accepted:\n");
    check("https://example.com/page?ref=data:text/html");
    check("mailto:ada@example.com");
    check("/profile/ada");
    check("about/team");
    return 0;
}
