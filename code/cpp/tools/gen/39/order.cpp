#include <cstdio>
#include <string>

static std::string replace_all(std::string subject, const std::string &from,
                               const std::string &to) {
    std::size_t at = 0;
    while ((at = subject.find(from, at)) != std::string::npos) {
        subject.replace(at, from.size(), to);
        at += to.size();
    }
    return subject;
}

// Escaping with a chain of string replacements. The order decides whether the
// ampersands the replacements themselves introduce get escaped a second time.
std::string escape_order_bad(std::string value) {
    value = replace_all(value, "<", "&lt;");
    value = replace_all(value, ">", "&gt;");
    value = replace_all(value, "\"", "&quot;");
    value = replace_all(value, "'", "&#39;");
    value = replace_all(value, "&", "&amp;");  // too late
    return value;
}

std::string escape_order_good(std::string value) {
    value = replace_all(value, "&", "&amp;");  // first, for once
    value = replace_all(value, "<", "&lt;");
    value = replace_all(value, ">", "&gt;");
    value = replace_all(value, "\"", "&quot;");
    value = replace_all(value, "'", "&#39;");
    return value;
}

int main() {
    const std::string input = "a < b & c > d";
    std::printf("input          : %s\n", input.c_str());
    std::printf("& last         : %s\n", escape_order_bad(input).c_str());
    std::printf("& first        : %s\n", escape_order_good(input).c_str());
    std::printf("browser shows, & last  : a &lt; b & c &gt; d\n");
    std::printf("browser shows, & first : a < b & c > d\n");
    return 0;
}
