#include <cstdio>
#include <map>
#include <string>
#include <string_view>

// Three different claims get three different names. "escaped" and "sanitised"
// are not the same trust level, and collapsing them is how a sanitiser's output
// ends up reviewed as if it were markup the team wrote.
enum class Provenance { escaped, sanitised, authored };

const char *name(Provenance p) {
    switch (p) {
        case Provenance::escaped:  return "escaped";
        case Provenance::sanitised: return "sanitised";
        case Provenance::authored: return "authored";
    }
    return "unknown";
}

class Html {
public:
    Html(std::string text, Provenance origin) : text_(std::move(text)), origin_(origin) {}
    std::string_view text() const { return text_; }
    Provenance provenance() const { return origin_; }

private:
    std::string text_;
    Provenance origin_;
};

Html escape(const std::string &raw) {
    std::string out;
    for (const char c : raw) {
        switch (c) {
            case '&':  out += "&amp;";  break;
            case '<':  out += "&lt;";   break;
            case '>':  out += "&gt;";   break;
            case '"':  out += "&quot;"; break;
            case '\'': out += "&#39;";  break;
            default:   out += c;        break;
        }
    }
    return Html(std::move(out), Provenance::escaped);
}

// Stand-ins for a sanitiser and for markup in the source tree.
Html sanitised(std::string markup) { return Html(std::move(markup), Provenance::sanitised); }
Html authored(std::string markup) { return Html(std::move(markup), Provenance::authored); }

std::string render(const std::string &tpl, const std::map<std::string, Html> &vars) {
    std::string out;
    std::size_t i = 0;
    while (i < tpl.size()) {
        const std::size_t open = tpl.find("{{", i);
        if (open == std::string::npos) {
            out += tpl.substr(i);
            break;
        }
        out += tpl.substr(i, open - i);
        const std::size_t close = tpl.find("}}", open + 2);
        const std::string key = tpl.substr(open + 2, close - open - 2);
        const Html &value = vars.at(key);
        out += value.text();
        // The provenance travels with the value, so a reviewer reading the
        // generated page can see where each hole was filled from.
        out += "<!-- " + key + ": " + name(value.provenance()) + " -->";
        i = close + 2;
    }
    return out;
}

int main() {
    std::printf("%s", render("<h1>{{title}}</h1>\n<p>{{body}}</p>\n<footer>{{note}}</footer>\n",
                             {{"title", escape("<script>alert(1)</script>")},
                              {"body", sanitised("<em>from markdown</em>")},
                              {"note", authored("<small>we wrote this</small>")}})
                          .c_str());
    return 0;
}
