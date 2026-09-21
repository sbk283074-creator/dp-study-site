#ifndef PAGE_H
#define PAGE_H

#include <map>
#include <stdexcept>
#include <string>
#include <string_view>

// Two types, because the difference between them is the entire security
// property: an Untrusted value has not been through `escape`, an Html one has.
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

// The only two doors from Untrusted into Html.
Html escape(Untrusted value);                 // for HTML text and attributes
Html trusted(std::string markup);             // for markup we wrote ourselves
Html safe_url(Untrusted value, std::string_view fallback);  // for href/src

// Throws std::runtime_error on an unknown or unterminated placeholder: a typo
// in a template should be a failed render, not an empty paragraph.
std::string render(std::string_view tpl, const std::map<std::string, Html> &vars);

class TemplateError : public std::runtime_error {
public:
    explicit TemplateError(const std::string &message) : std::runtime_error(message) {}
};

#endif
