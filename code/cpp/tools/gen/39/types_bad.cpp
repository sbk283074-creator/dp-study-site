#include <cstdio>
#include <map>
#include <string>
#include <string_view>
#include <utility>

class Untrusted {
public:
    explicit Untrusted(std::string text) : text_(std::move(text)) {}
    std::string_view text() const { return text_; }

private:
    std::string text_;
};

class Html {
public:
    explicit Html(std::string text) : text_(std::move(text)) {}
    std::string_view text() const { return text_; }

private:
    std::string text_;
};

Html escape(const Untrusted &value);

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

    // No implicit way to turn an Untrusted into an Html, so this never
    // compiles -- which is the whole point of giving them different types.
    std::printf("%s", render("<p>{{name}}</p>", {{"name", Untrusted(from_user)}}).c_str());
    return 0;
}
