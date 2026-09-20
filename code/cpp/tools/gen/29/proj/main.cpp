#include "api.h"
#include "json.h"

#include <cstdio>
#include <cstring>
#include <string>

namespace {

/* Print a response the way a terminal would show it, with the carriage returns
   spelled out. Without this, the \r is invisible and the output is a claim. */
void dump(const std::string &label, const std::string &data) {
    std::printf("=== %s ===\n", label.c_str());
    for (char ch : data) {
        if (ch == '\r')      std::fputs("\\r", stdout);
        else if (ch == '\n') std::fputs("\\n\n", stdout);
        else                 std::putchar(ch);
    }
    if (data.empty() || data.back() != '\n') std::putchar('\n');
}

/* One line per input, so the table fits on a screen. */
void show(const char *label, const std::string &text) {
    const std::optional<Json> value = Json::parse(text);
    if (!value) {
        std::printf("  %-32s -> refused\n", label);
        return;
    }
    std::printf("  %-32s -> %s\n", label, value->dump().c_str());
}

void selftest() {
    std::printf("what the parser accepts\n");
    std::printf("-----------------------\n");
    show("\"hello\"",              "\"hello\"");
    show("42",                     "42");
    show("-3.5",                   "-3.5");
    show("2e3",                    "2e3");
    show("[]",                     "[]");
    show("{}",                     "{}");
    show("{\"a\":1,\"b\":[2,3]}",  "{\"a\":1,\"b\":[2,3]}");
    show("{\"b\":1,\"a\":2}",      "{\"b\":1,\"a\":2}");
    show("\"\\u00e9\"",            "\"\\u00e9\"");
    show("\"\\ud83d\\ude00\"",     "\"\\ud83d\\ude00\"");

    std::printf("\nwhat it refuses\n");
    std::printf("---------------\n");
    show("123abc  (trailing text)",      "123abc");
    show("01  (leading zero)",           "01");
    show("nan",                          "nan");
    show("+5  (leading plus)",           "+5");
    show(".5  (no whole part)",          ".5");
    show("1e  (no exponent)",            "1e");
    show("{\"a\":1,}  (trailing comma)", "{\"a\":1,}");
    show("{a:1}  (bare key)",            "{a:1}");
    show("{\"a\" 1}  (no colon)",        "{\"a\" 1}");
    show("'hi'  (single quotes)",        "'hi'");
    show("\"a\\xb\"  (bad escape)",      "\"a\\xb\"");
    show("\"\\ud83d\"  (lone high)",     "\"\\ud83d\"");
    show("\"unterminated",               "\"unterminated");

    /* The raw newline cannot go in the table above: it would break the row. */
    std::printf("  a raw newline in a string       -> %s\n",
                Json::parse("\"a\nb\"") ? "accepted" : "refused");

    std::printf("\nnesting depth\n");
    std::printf("-------------\n");
    const std::string deep = std::string(40, '[') + std::string(40, ']');
    std::printf("  40 deep, limit 32               -> %s\n",
                Json::parse(deep) ? "accepted" : "refused");
    std::printf("  40 deep, limit 64               -> %s\n",
                Json::parse(deep, 64) ? "accepted" : "refused");

    std::printf("\nthe payload\n");
    std::printf("-----------\n");
    std::printf("  %s\n", items_payload().dump().c_str());

    std::printf("\n");
    dump("GET /api/items on the wire",
         render_json(items_payload(), 200, "OK"));
}

std::string dispatch(const std::string &path) {
    if (path == "/api/items") return render_json(items_payload(), 200, "OK");

    if (path.rfind("/api/items/", 0) == 0 && path.size() > 11) {
        const std::string id = path.substr(11);
        if (const std::optional<Json> item = item_payload(id)) {
            return render_json(*item, 200, "OK");
        }
        return render_json(error_payload(404, "no item " + id), 404, "Not Found");
    }

    return render_json(error_payload(404, "no route for " + path), 404, "Not Found");
}

}  // namespace

int main(int argc, char **argv) {
    if (argc == 2 && std::strcmp(argv[1], "--help") == 0) {
        std::printf("usage: %s            run the built-in self-test\n", argv[0]);
        std::printf("       %s PATH       answer one path and dump it\n", argv[0]);
        return 0;
    }

    if (argc >= 2) {
        dump("GET " + std::string(argv[1]), dispatch(argv[1]));
        return 0;
    }

    selftest();
    return 0;
}
