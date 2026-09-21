#include <cstdio>
#include <map>
#include <string>
#include <string_view>
#include <utility>

// A value that has not been escaped yet. The only way out of this type is
// `escape`, so an unescaped string cannot reach the renderer by accident.
class Untrusted {
public:
    explicit Untrusted(std::string text) : text_(std::move(text)) {}
    std::string_view text() const { return text_; }

private:
    std::string text_;
};

// A value that is safe to place in HTML text or a quoted attribute.
class Html {
public:
    explicit Html(std::string text) : text_(std::move(text)) {}
    std::string_view text() const { return text_; }

private:
    std::string text_;
};

Html escape(const Untrusted &value) {
    std::string out;
    for (const char c : value.text()) {
        switch (c) {
            case '&':  out += "&amp;";  break;
            case '<':  out += "&lt;";   break;
            case '>':  out += "&gt;";   break;
            case '"':  out += "&quot;"; break;
            case '\'': out += "&#39;";  break;
            default:   out += c;        break;
        }
    }
    return Html(std::move(out));
}

// Markup the programmer wrote, not the user. Still explicit, still visible.
Html trusted(std::string markup) { return Html(std::move(markup)); }

std::string render(const std::string &tpl, const std::map<std::string, Html> &vars) {
    std::string out = tpl;
    for (const auto &[name, value] : vars) {
        const std::string needle = "{{" + name + "}}";
        std::size_t at = 0;
        while ((at = out.find(needle, at)) != std::string::npos) {
            out.replace(at, needle.size(), value.text());
            at += value.text().size();
        }
    }
    return out;
}

int main() {
    const std::string from_user = "<script>alert(1)</script>";
    const std::string tpl = "<p>{{greeting}}</p>\n<p>{{note}}</p>\n";

    // The type system refuses to let the raw value through; `escape` is the
    // only door, and `trusted` is the one you have to type out loud.
    std::printf("%s", render(tpl, {{"greeting", escape(Untrusted(from_user))},
                                   {"note", trusted("<em>written by us</em>")}})
                          .c_str());
    return 0;
}
