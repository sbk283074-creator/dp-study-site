#include "page.h"

#include <cstdio>
#include <string>

namespace {

int failures = 0;

void check(const char *what, std::string_view got, std::string_view want) {
    const bool ok = got == want;
    if (!ok) ++failures;
    std::printf("  [%s] %-28s %.*s\n", ok ? "ok" : "FAIL", what,
                static_cast<int>(got.size()), got.data());
}

}  // namespace

int main() {
    std::printf("--- the page ---\n");
    const std::string layout =
        "<article>\n"
        "  <h1>{{title}}</h1>\n"
        "  <p>{{body}}</p>\n"
        "  <a href=\"{{{link}}}\">profile</a>\n"
        "  <footer>{{{footer}}}</footer>\n"
        "</article>\n";

    // Everything here came from a request. That is the assumption the types
    // enforce, not a comment someone has to remember.
    std::printf("%s", render(layout,
                             {{"title", escape(Untrusted("<script>alert(1)</script>"))},
                              {"body", escape(Untrusted("Tom & Jerry <3 \"quotes\""))},
                              {"link", safe_url(Untrusted("javascript:alert(1)"), "/")},
                              {"footer", trusted("<em>rendered by us</em>")}})
                          .c_str());

    std::printf("--- self-test ---\n");
    check("escapes a script tag", escape(Untrusted("<script>")).text(),
          std::string("&lt;script&gt;"));
    check("escapes an ampersand once", escape(Untrusted("a &amp; b")).text(),
          std::string("a &amp;amp; b"));
    check("escapes a quote", escape(Untrusted("\"")).text(), std::string("&quot;"));
    check("javascript: is replaced",
          safe_url(Untrusted("javascript:alert(1)"), "/").text(), std::string("/"));
    check("//host is replaced", safe_url(Untrusted("//evil.example"), "/").text(),
          std::string("/"));
    check("https survives", safe_url(Untrusted("https://example.com/a?b=1&c=2"), "/").text(),
          std::string("https://example.com/a?b=1&amp;c=2"));

    try {
        render("<p>{{typo}}</p>", {});
        std::printf("  [FAIL] unknown placeholder should throw\n");
        ++failures;
    } catch (const TemplateError &error) {
        std::printf("  [ok]   unknown placeholder throws: %s\n", error.what());
    }

    std::printf("failures: %d\n", failures);
    return failures == 0 ? 0 : 1;
}
