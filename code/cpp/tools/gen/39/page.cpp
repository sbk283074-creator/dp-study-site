#include "page.h"

#include <utility>

namespace {

std::string escaped(std::string_view input) {
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

bool starts_with(std::string_view text, std::string_view prefix) {
    return text.size() >= prefix.size() && text.compare(0, prefix.size(), prefix) == 0;
}

}  // namespace

Html escape(const Untrusted value) { return Html(escaped(value.text())); }

Html trusted(std::string markup) { return Html(std::move(markup)); }

Html safe_url(const Untrusted value, const std::string_view fallback) {
    const std::string_view url = value.text();
    if (starts_with(url, "http://") || starts_with(url, "https://") ||
        starts_with(url, "mailto:")) {
        return Html(escaped(url));
    }
    // A site-relative path is fine; `//host` is not, it means another host.
    if (url.size() > 1 && url.front() == '/' && url[1] != '/') {
        return Html(escaped(url));
    }
    return Html(escaped(fallback));
}

std::string render(const std::string_view tpl, const std::map<std::string, Html> &vars) {
    std::string out;
    out.reserve(tpl.size());
    std::size_t i = 0;
    while (i < tpl.size()) {
        const std::size_t open = tpl.find("{{", i);
        if (open == std::string_view::npos) {
            out += tpl.substr(i);
            break;
        }
        out += tpl.substr(i, open - i);

        const bool raw = tpl.compare(open, 3, "{{{") == 0;
        const std::size_t name_at = open + (raw ? 3 : 2);
        const std::size_t close = tpl.find(raw ? "}}}" : "}}", name_at);
        if (close == std::string_view::npos) {
            throw TemplateError("unterminated placeholder at offset " + std::to_string(open));
        }
        const std::string name(tpl.substr(name_at, close - name_at));
        const auto found = vars.find(name);
        if (found == vars.end()) {
            throw TemplateError("no value supplied for {{" + name + "}}");
        }
        out += found->second.text();
        i = close + (raw ? 3 : 2);
    }
    return out;
}
