#include <cstdio>
#include <string>
#include <string_view>

// One pass over the input. Each input byte maps to one output fragment, so the
// `&` inserted here is never re-examined -- which is the property the chained
// version below gets wrong.
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
    const std::string script = "<script>alert('x')</script>";
    const std::string attribute = "x\" onerror=\"alert(1)";
    const std::string ampersand = "Tom & Jerry <3";

    std::printf("script    : %s\n", escape_html(script).c_str());
    std::printf("attribute : %s\n", escape_html(attribute).c_str());
    std::printf("ampersand : %s\n", escape_html(ampersand).c_str());
    std::printf("plain     : %s\n", escape_html("nothing to do here").c_str());
    std::printf("grown from %zu to %zu bytes\n", script.size(), escape_html(script).size());
    return 0;
}
