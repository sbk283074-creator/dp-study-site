---
chapter: 29
part: 5
title: JSON by Hand
summary: Build a JSON writer and a recursive-descent parser, and use them to answer an /api/ route with real application/json.
minutes: 80
tags: [json, parsing, escaping, variant, recursion, api, unicode]
---

Chapter 28's router answered `/health` and `/items` with bodies that were string literals:

```cpp
return text(Status::Ok, "{\"status\":\"ok\"}\n");
```

Every quote on that line was escaped by a human, and the shape was checked by nobody. That is fine for
four words that will never change. It stops being fine the moment the value comes from somewhere else
— a file, a socket, a struct field a user typed. An item called `nut "heavy duty"` turns into
`{"name":"nut "heavy duty""}`, which is not JSON, and the browser reports it as a blank page and one
line in a console you are not looking at.

This chapter builds the thing that writes those bytes and the thing that reads them back. There is no
JSON library on this machine, and that is a fact about the machine rather than a preference:


```cpp bad
#include <nlohmann/json.hpp>

#include <cstdio>

int main() {
    nlohmann::json value;
    value["ok"] = true;
    std::printf("%s\n", value.dump().c_str());
    return 0;
}
```

```text
'nlohmann/json.hpp' file not found
```

`nlohmann/json.hpp` is the library most C++ projects reach for, and it is excellent. It is also not
installed here, and it is not going to be — this book is self-contained, and a chapter that begins
with *install a package* is a chapter that stops working the day the package changes. So you will
write it. Escaping, a value type and a recursive-descent parser are the three skills every
serialization format needs, and JSON is the smallest format that has all three.

If your machine does have the library, read the chapter anyway. Being able to say what your JSON
library is doing — and what it is *not* doing — is most of the reason to use one.

## Escaping: two characters you must, and thirty-two you must not forget

A JSON string is a run of characters between two `"`. Inside it, exactly two characters cannot appear
as themselves: the double quote, because it would end the string, and the backslash, because it is the
escape character itself. Everything else is allowed *except* the thirty-two control characters
`U+0000` to `U+001F`, which the specification forbids outright. Five of those have short forms; the
rest are written `\u00XX`.

Here is what that means for every kind of character you might find in real data:


```cpp run
#include <cstdio>
#include <string>

/* ---------- the version that "works" until the data has a newline in it ---------- */
std::string naive(const std::string &s) {
    return "{\"msg\":\"" + s + "\"}";
}

/* ---------- the version that is actually JSON ---------- */
std::string escape(const std::string &s) {
    std::string out;
    for (unsigned char c : s) {
        switch (c) {
        case '"':  out += "\\\"";  break;
        case '\\': out += "\\\\";  break;
        case '\n': out += "\\n";   break;
        case '\r': out += "\\r";   break;
        case '\t': out += "\\t";   break;
        case '\b': out += "\\b";   break;
        case '\f': out += "\\f";   break;
        default:
            if (c < 0x20) {
                char buf[8];
                std::snprintf(buf, sizeof buf, "\\u%04x", c);
                out += buf;
            } else {
                out += static_cast<char>(c);
            }
        }
    }
    return out;
}

std::string proper(const std::string &s) {
    return "{\"msg\":\"" + escape(s) + "\"}";
}

/* Count the bytes a JSON parser is not allowed to find inside a string. */
std::size_t raw_controls(const std::string &s) {
    std::size_t n = 0;
    for (unsigned char c : s) {
        if (c < 0x20) ++n;
    }
    return n;
}

struct Case {
    const char *label;
    const char *raw;
};

int main() {
    std::printf("what happens to each character\n");
    std::printf("-----------------------------\n");
    const Case cases[] = {
        {"plain letters", "hello"},
        {"a double quote", "he said \"hi\""},
        {"a backslash", "C:\\temp"},
        {"a forward slash", "a/b"},
        {"a tab", "a\tb"},
        {"a newline", "a\nb"},
        {"a bell", "a\ab"},
    };
    for (const Case &c : cases) {
        std::printf("  %-16s -> %s\n", c.label, escape(c.raw).c_str());
    }

    std::printf("\nwhat the client actually receives\n");
    std::printf("--------------------------------\n");
    const std::string msg = "line one\nline two";
    const std::string a = naive(msg);
    const std::string b = proper(msg);
    std::printf("  naive  output : %zu bytes, %zu raw control character(s)\n",
                a.size(), raw_controls(a));
    std::printf("  proper output : %zu bytes, %zu raw control character(s)\n",
                b.size(), raw_controls(b));
    std::printf("  a string in JSON may contain no raw control character at all\n");
    return 0;
}
```

```text
what happens to each character
-----------------------------
  plain letters    -> hello
  a double quote   -> he said \"hi\"
  a backslash      -> C:\\temp
  a forward slash  -> a/b
  a tab            -> a\tb
  a newline        -> a\nb
  a bell           -> a\u0007b

what the client actually receives
--------------------------------
  naive  output : 27 bytes, 1 raw control character(s)
  proper output : 28 bytes, 0 raw control character(s)
  a string in JSON may contain no raw control character at all
```

Read the middle of the first table, because it is where a hand-written escaper usually goes wrong. The
forward slash is **not** escaped. Some encoders write it as `\/` — that is legal JSON, and pointless,
and it is why a naive "escape everything that is not alphanumeric" loop produces output nobody can
read. The bell, `U+0007`, has no short form, so it becomes `\u0007`; the tab and the newline do.

The second table is the point of the whole function. The naive writer — the one that just puts the
string between quotes — emitted a body containing **one raw control character**. That body is not
JSON, and a parser is required to reject it, so the failure is not subtle; it is total, and it happens
on the client, far from the line that caused it. The escaped version contains none, and it is one byte
longer, which is the trade: one extra byte for each character that needed escaping.

Two things `json_escape` deliberately does not do, and you should know both:

- **It does not validate UTF-8.** Non-ASCII characters pass through as their original bytes, which is
  correct — JSON strings are sequences of Unicode characters and UTF-8 is the encoding everyone uses.
  But if the bytes arriving were never valid UTF-8, the bytes leaving are not either, and the document
  is invalid in a way no amount of escaping would have fixed. Validation is a separate job, done at
  the boundary where the bytes enter the program.
- **It does not escape the forward slash**, for the reason above. If you need a `</script>` sequence to
  be safe inside an HTML `<script>` block, that is an HTML problem, and it is solved by writing `<` as
  `\u003c` on the way out — which this function also does not do, and which the next chapter will.

## Building a value instead of a string

Escaping handles one string. An array of them has a second problem, and it is the one that survives
testing because an empty list never triggers it:


```cpp run
#include <cstdio>
#include <string>
#include <vector>

/* The naive writer: put a comma after every element. */
std::string naive_array(const std::vector<std::string> &items) {
    std::string out = "[";
    for (const std::string &item : items) {
        out += "\"" + item + "\",";
    }
    out += "]";
    return out;
}

/* The writer that knows whether it has written anything yet. */
std::string joined_array(const std::vector<std::string> &items) {
    std::string out = "[";
    bool first = true;
    for (const std::string &item : items) {
        if (!first) out += ",";
        first = false;
        out += "\"" + item + "\"";
    }
    out += "]";
    return out;
}

int main() {
    const std::vector<std::string> three = {"alpha", "beta", "gamma"};
    const std::vector<std::string> none;

    std::printf("three elements\n");
    std::printf("  naive  : %s\n", naive_array(three).c_str());
    std::printf("  joined : %s\n", joined_array(three).c_str());
    std::printf("no elements\n");
    std::printf("  naive  : %s\n", naive_array(none).c_str());
    std::printf("  joined : %s\n", joined_array(none).c_str());
    return 0;
}
```

```text
three elements
  naive  : ["alpha","beta","gamma",]
  joined : ["alpha","beta","gamma"]
no elements
  naive  : []
  joined : []
```

`["alpha","beta","gamma",]` is not JSON. The rule is that commas go *between* elements, and "put a
comma after every element" is not the same rule — it only looks the same until the last one.

Notice that the naive version gets the empty array right. That is the trap. A test that builds an empty
list, or a list with one element, passes; the bug appears the first time real data arrives, and it is a
client-side syntax error again.

The fix is a `bool` that remembers whether anything has been written yet. It is three lines, and it is
the same three lines at every level of nesting — which is why the right move is to stop writing strings
and start writing a **value type**. A value knows its own shape, so it knows whether it needs a comma
in front of it:


```cpp
class Json {
public:
    using Array = std::vector<Json>;
    using Object = std::map<std::string, Json>;

    Json();
    Json(std::nullptr_t);
    Json(bool b);
    Json(int i);
    Json(double d);
    Json(const char *s);
    Json(std::string s);
    Json(Array a);
    Json(Object o);

    bool is_null() const;
    bool is_bool() const;
    bool is_number() const;
    bool is_string() const;
    bool is_array() const;
    bool is_object() const;

    /* These throw std::bad_variant_access if the shape is not what you asked for. */
    bool as_bool() const;
    double as_number() const;
    const std::string &as_string() const;
    const Array &as_array() const;
    const Object &as_object() const;

    std::string dump() const;

    /* Returns nothing when the text is not JSON, or when it nests deeper
       than max_depth. Never recurses past max_depth. */
    static std::optional<Json> parse(const std::string &text, std::size_t max_depth = 32);

private:
    using Value = std::variant<std::nullptr_t, bool, double, std::string, Array, Object>;

    void dump_into(std::string &out) const;

    Value value_;
};
```

Six shapes, one class. The storage is a `std::variant`, so a `Json` is exactly one of those six at any
moment and `is_*()` tells you which. The two container alternatives mention `Json` inside their own
definition, which looks circular and is not: `std::vector<Json>` and `std::map<std::string, Json>` are
complete types even while `Json` is still being declared, because the standard library containers are
specified to work with an incomplete element type. That is what makes a recursive type like this
possible at all.

Writing one out is a recursion over the shape, and the comma logic falls out of it:


```cpp
void Json::dump_into(std::string &out) const {
    if (is_null())   { out += "null"; return; }
    if (is_bool())   { out += as_bool() ? "true" : "false"; return; }
    if (is_number()) { out += json_number(as_number()); return; }
    if (is_string()) { out += '"' + json_escape(as_string()) + '"'; return; }

    if (is_array()) {
        out += '[';
        bool first = true;
        for (const Json &item : as_array()) {
            if (!first) out += ',';
            first = false;
            item.dump_into(out);
        }
        out += ']';
        return;
    }

    out += '{';
    bool first = true;
    for (const auto &pair : as_object()) {
        if (!first) out += ',';
        first = false;
        out += '"' + json_escape(pair.first) + "\":";
        pair.second.dump_into(out);
    }
    out += '}';
}
```

Two things in there are worth more than they look.

**A string goes through `json_escape` on the way out, not on the way in.** This is the most important
design decision in the chapter. If you escape when you *build* the value, you have to remember to do it
at every place that builds one, and you have to know not to do it twice when a value is copied. If you
escape when you *write* it, there is exactly one place in the program where a character becomes a byte,
and it is the line above.

**Object keys go through it too.** A key is a string, and a key containing a quote is exactly as
illegal as a value containing one. `json_escape(pair.first)` is easy to forget, because keys usually
look like identifiers.

The keys come out **sorted**, because the storage is a `std::map`. That is worth knowing and worth not
caring about: JSON says the members of an object are unordered, so a client that depends on the order
they arrive in is already broken. You will see it in the transcript below, where `{"b":1,"a":2}` comes
back as `{"a":2,"b":1}`.

It is also worth knowing that JavaScript does not sort. `JSON.stringify({b:1,a:2})` in Node prints
`{"b":1,"a":2}`, in insertion order, and both answers are correct. The two implementations agree on the
*value* and disagree on the bytes, which is exactly why comparing JSON as text is a mistake — and why
the next time you write a test that asserts on a JSON response, it should parse both sides first.

## Reading it back: a recursive-descent parser

Writing JSON is a walk over a tree you already have. Reading it is a walk over text you do not trust,
and that is the harder half of the chapter.

The parser is one class holding the text and a position, with one method per shape. `parse_value` looks
at the next character and decides which of the others to call:


```cpp
    std::optional<Json> parse_value(std::size_t depth) {
        if (depth > max_depth_) return std::nullopt;
        skip_ws();
        if (eof()) return std::nullopt;

        const char c = peek();
        if (c == '{') return parse_object(depth);
        if (c == '[') return parse_array(depth);
        if (c == '"') {
            std::optional<std::string> s = parse_string();
            if (!s) return std::nullopt;
            return Json(std::move(*s));
        }
        if (literal("true"))  return Json(true);
        if (literal("false")) return Json(false);
        if (literal("null"))  return Json();
        return parse_number();
    }

    /* Four hex digits, or nothing. */
    std::optional<unsigned> hex4() {
        if (pos_ + 4 > text_.size()) return std::nullopt;
        unsigned value = 0;
        for (int i = 0; i < 4; ++i) {
            const char c = text_[pos_++];
            value <<= 4;
            if (c >= '0' && c <= '9')      value |= static_cast<unsigned>(c - '0');
            else if (c >= 'a' && c <= 'f') value |= static_cast<unsigned>(c - 'a' + 10);
            else if (c >= 'A' && c <= 'F') value |= static_cast<unsigned>(c - 'A' + 10);
            else return std::nullopt;
        }
        return value;
    }

    /* \uXXXX, including the case where one character is written as two escapes. */
    std::optional<std::string> parse_unicode() {
        std::optional<unsigned> first = hex4();
        if (!first) return std::nullopt;
        unsigned cp = *first;

        if (cp >= 0xD800 && cp <= 0xDBFF) {
            /* A high half. It is only a character once its low half arrives. */
            if (pos_ + 2 > text_.size() || text_[pos_] != '\\' || text_[pos_ + 1] != 'u') {
                return std::nullopt;
            }
            pos_ += 2;
            std::optional<unsigned> second = hex4();
            if (!second) return std::nullopt;
            if (*second < 0xDC00 || *second > 0xDFFF) return std::nullopt;
            cp = 0x10000u + ((cp - 0xD800u) << 10) + (*second - 0xDC00u);
        } else if (cp >= 0xDC00 && cp <= 0xDFFF) {
            return std::nullopt;      /* a low half with nothing in front of it */
        }
        return utf8(cp);
    }

    std::optional<std::string> parse_string() {
        if (peek() != '"') return std::nullopt;
        ++pos_;
        std::string out;
        while (true) {
            if (eof()) return std::nullopt;
            const unsigned char c = static_cast<unsigned char>(text_[pos_++]);
            if (c == '"') return out;
            if (c != '\\') {
                if (c < 0x20) return std::nullopt;    /* raw control character */
                out += static_cast<char>(c);
                continue;
            }
            if (eof()) return std::nullopt;
            switch (text_[pos_++]) {
            case '"':  out += '"';  break;
            case '\\': out += '\\'; break;
            case '/':  out += '/';  break;
            case 'b':  out += '\b'; break;
            case 'f':  out += '\f'; break;
            case 'n':  out += '\n'; break;
            case 'r':  out += '\r'; break;
            case 't':  out += '\t'; break;
            case 'u': {
                std::optional<std::string> encoded = parse_unicode();
                if (!encoded) return std::nullopt;
                out += *encoded;
                break;
            }
            default: return std::nullopt;             /* \x is not a JSON escape */
            }
        }
    }

    static bool is_digit(char c) { return c >= '0' && c <= '9'; }

    /* Scans the shape JSON allows first, then converts. Handing the whole
       remaining text to strtod would accept "nan", "0x10" and "1e999". */
    std::optional<Json> parse_number() {
        const std::size_t start = pos_;
        if (peek() == '-') ++pos_;
        if (!is_digit(peek())) return std::nullopt;
        if (peek() == '0') {
            ++pos_;                        /* a leading zero has to stand alone */
        } else {
            while (is_digit(peek())) ++pos_;
        }
        if (peek() == '.') {
            ++pos_;
            if (!is_digit(peek())) return std::nullopt;
            while (is_digit(peek())) ++pos_;
        }
        if (peek() == 'e' || peek() == 'E') {
            ++pos_;
            if (peek() == '+' || peek() == '-') ++pos_;
            if (!is_digit(peek())) return std::nullopt;
            while (is_digit(peek())) ++pos_;
        }
        const std::string digits = text_.substr(start, pos_ - start);
        return Json(std::strtod(digits.c_str(), nullptr));
    }

    std::optional<Json> parse_array(std::size_t depth) {
        ++pos_;                                   /* '[' */
        Json::Array items;
        skip_ws();
        if (peek() == ']') { ++pos_; return Json(std::move(items)); }
        while (true) {
            std::optional<Json> item = parse_value(depth + 1);
            if (!item) return std::nullopt;
            items.push_back(std::move(*item));
            skip_ws();
            if (peek() == ',') { ++pos_; continue; }
            if (peek() == ']') { ++pos_; return Json(std::move(items)); }
            return std::nullopt;
        }
    }

    std::optional<Json> parse_object(std::size_t depth) {
        ++pos_;                                   /* '{' */
        Json::Object fields;
        skip_ws();
        if (peek() == '}') { ++pos_; return Json(std::move(fields)); }
        while (true) {
            skip_ws();
            std::optional<std::string> key = parse_string();
            if (!key) return std::nullopt;
            skip_ws();
            if (peek() != ':') return std::nullopt;
            ++pos_;
            std::optional<Json> value = parse_value(depth + 1);
            if (!value) return std::nullopt;
            /* A repeated key keeps the last one, which is what JavaScript does. */
            fields.insert_or_assign(std::move(*key), std::move(*value));
            skip_ws();
            if (peek() == ',') { ++pos_; continue; }
            if (peek() == '}') { ++pos_; return Json(std::move(fields)); }
            return std::nullopt;
        }
    }
```

Everything returns `std::optional`. There is no exception, no error code to forget to check, and no
half-built value to leak — a failure at any depth propagates out as an empty optional, and the caller
has one decision to make. For a parser that will be fed bytes from a network, that is the right
default: invalid input is an ordinary outcome, not an exceptional one.

Note the first line: `if (depth > max_depth_) return std::nullopt;`. It is the guard against input that
is not malicious but is 200,000 characters of `[`, and it gets its own section below.

### Numbers: scan the shape, then convert

The obvious way to parse a number is to find where it ends and hand the text to `strtod`. The problem is
that `strtod` accepts a *superset* of JSON: `nan`, `inf`, `+5`, `.5`, `0x10` and `1e999` all convert
happily. So the parser scans the shape JSON allows first, and only then converts:


```cpp
    std::optional<Json> parse_number() {
        const std::size_t start = pos_;
        if (peek() == '-') ++pos_;
        if (!is_digit(peek())) return std::nullopt;
        if (peek() == '0') {
            ++pos_;                        /* a leading zero has to stand alone */
        } else {
            while (is_digit(peek())) ++pos_;
        }
        if (peek() == '.') {
            ++pos_;
            if (!is_digit(peek())) return std::nullopt;
            while (is_digit(peek())) ++pos_;
        }
        if (peek() == 'e' || peek() == 'E') {
            ++pos_;
            if (peek() == '+' || peek() == '-') ++pos_;
            if (!is_digit(peek())) return std::nullopt;
            while (is_digit(peek())) ++pos_;
        }
        const std::string digits = text_.substr(start, pos_ - start);
        return Json(std::strtod(digits.c_str(), nullptr));
    }
```

The grammar being enforced here is narrower than C's, and every rejection is a real case:

| Rejected | Why JSON says no | What `strtod` would have done |
|---|---|---|
| `01` | a leading zero has to stand alone | returned `1` |
| `+5` | no leading plus sign | returned `5` |
| `.5` | the whole-number part is required | returned `0.5` |
| `1.` | a decimal point needs a digit after it | returned `1` |
| `1e` | an exponent needs digits | returned `1`, leaving the `e` behind |
| `nan`, `inf` | not JSON values at all | returned a NaN or an infinity |

Every one of those is in the transcript below, marked `refused`. This is the difference between a
parser and a converter: a converter takes what it can, and a parser decides what is allowed.

### Strings, and the escape that is really four bytes

Strings are the fiddly half. The scanner has to reject a raw control character, reject an unknown
escape such as `\x`, and handle `\uXXXX` — which is not a character but a **code point**, and has to
become the one, two, three or four bytes that UTF-8 writes for it:


```cpp run
#include <cstdio>
#include <string>

/* One code point in, the bytes UTF-8 writes for it out. */
std::string utf8(unsigned cp) {
    std::string out;
    if (cp < 0x80) {
        out += static_cast<char>(cp);
    } else if (cp < 0x800) {
        out += static_cast<char>(0xC0 | (cp >> 6));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        out += static_cast<char>(0xE0 | (cp >> 12));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else {
        out += static_cast<char>(0xF0 | (cp >> 18));
        out += static_cast<char>(0x80 | ((cp >> 12) & 0x3F));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    }
    return out;
}

/* The arithmetic that turns \ud83d\ude00 into one character. */
unsigned from_surrogates(unsigned high, unsigned low) {
    return 0x10000u + ((high - 0xD800u) << 10) + (low - 0xDC00u);
}

int main() {
    const unsigned points[] = {0x41, 0xE9, 0x20AC, 0x1F600};
    std::printf("code point -> the bytes on the wire\n");
    std::printf("-----------------------------------\n");
    for (unsigned cp : points) {
        const std::string bytes = utf8(cp);
        std::printf("  U+%04X -> %zu byte(s):", cp, bytes.size());
        for (unsigned char b : bytes) std::printf(" %02x", b);
        std::printf("   %s\n", bytes.c_str());
    }

    std::printf("\ntwo escapes, one character\n");
    std::printf("--------------------------\n");
    const unsigned high = 0xD83D, low = 0xDE00;
    const unsigned cp = from_surrogates(high, low);
    std::printf("  U+%04X and U+%04X together are U+%05X\n", high, low, cp);
    std::printf("  which is %s\n", utf8(cp).c_str());
    std::printf("  and it needs %zu bytes, not 2\n", utf8(cp).size());
    return 0;
}
```

```text
code point -> the bytes on the wire
-----------------------------------
  U+0041 -> 1 byte(s): 41   A
  U+00E9 -> 2 byte(s): c3 a9   é
  U+20AC -> 3 byte(s): e2 82 ac   €
  U+1F600 -> 4 byte(s): f0 9f 98 80   😀

two escapes, one character
--------------------------
  U+D83D and U+DE00 together are U+1F600
  which is 😀
  and it needs 4 bytes, not 2
```

That arithmetic is the whole of UTF-8, and it is worth reading twice. `U+00E9` is `é`, two bytes.
`U+1F600` is an emoji, four bytes. The second table is the part that catches people out: a character
outside the first 65,536 is written in JSON as **two** `\u` escapes, because one `\uXXXX` can only
carry sixteen bits. `\ud83d\ude00` is one character, four bytes on the wire, and a parser that treats
each escape as a character of its own produces two pieces of garbage.

That is why `parse_unicode` does arithmetic instead of a table lookup:


```cpp
    std::optional<std::string> parse_unicode() {
        std::optional<unsigned> first = hex4();
        if (!first) return std::nullopt;
        unsigned cp = *first;

        if (cp >= 0xD800 && cp <= 0xDBFF) {
            /* A high half. It is only a character once its low half arrives. */
            if (pos_ + 2 > text_.size() || text_[pos_] != '\\' || text_[pos_ + 1] != 'u') {
                return std::nullopt;
            }
            pos_ += 2;
            std::optional<unsigned> second = hex4();
            if (!second) return std::nullopt;
            if (*second < 0xDC00 || *second > 0xDFFF) return std::nullopt;
            cp = 0x10000u + ((cp - 0xD800u) << 10) + (*second - 0xDC00u);
        } else if (cp >= 0xDC00 && cp <= 0xDFFF) {
            return std::nullopt;      /* a low half with nothing in front of it */
        }
        return utf8(cp);
    }
```

The range checks are not decoration. `0xD800`–`0xDFFF` is the block Unicode reserves for exactly this
encoding trick, and a code point in that range is **not a character**. A lone high half, a lone low
half, or a high half followed by anything other than a low half is invalid input — so the function
returns nothing rather than inventing a replacement. Three of those cases are in the transcript as
`refused`. Rejecting is a choice; silently substituting `?` is also a choice, and it is the one that
turns a bug in your client into a mystery.

The object parser is the last piece, and it holds one small decision:


```cpp
    std::optional<Json> parse_object(std::size_t depth) {
        ++pos_;                                   /* '{' */
        Json::Object fields;
        skip_ws();
        if (peek() == '}') { ++pos_; return Json(std::move(fields)); }
        while (true) {
            skip_ws();
            std::optional<std::string> key = parse_string();
            if (!key) return std::nullopt;
            skip_ws();
            if (peek() != ':') return std::nullopt;
            ++pos_;
            std::optional<Json> value = parse_value(depth + 1);
            if (!value) return std::nullopt;
            /* A repeated key keeps the last one, which is what JavaScript does. */
            fields.insert_or_assign(std::move(*key), std::move(*value));
            skip_ws();
            if (peek() == ',') { ++pos_; continue; }
            if (peek() == '}') { ++pos_; return Json(std::move(fields)); }
            return std::nullopt;
        }
```

`fields.insert_or_assign(...)` means a repeated key keeps the **last** value. JSON's specification does
not say what should happen, implementations disagree, and JavaScript keeps the last one — so matching
JavaScript is the least surprising choice. But it is a choice. If your protocol depends on what a
duplicate key means, your protocol is under-specified, and the fix belongs in the protocol.

### Depth is a limit, not a detail

The `max_depth_` check costs one comparison per value. Without it, this is what a 200,000-character body
does to your server:


```cpp run-san-catch
#include <cstdio>
#include <string>

/* The shape of the bug on its own: one frame per bracket, and no limit. */
std::size_t depth_of(const std::string &s, std::size_t i) {
    if (i >= s.size()) return 0;
    if (s[i] == '[') return 1 + depth_of(s, i + 1);
    return 0;
}

int main() {
    const std::string bomb(200000, '[');
    std::printf("nesting = %zu\n", depth_of(bomb, 0));
    return 0;
}
```

```text
stack-overflow
```

The program above has the same shape as the real parser: one stack frame per nesting level, no limit,
and text that is nothing but opening brackets. The output before the crash is missing because the
`printf` never ran — the recursion was already 200,000 frames deep, and the process died on the way in.
AddressSanitizer names it `stack-overflow` and prints the frames that led there.

A stack overflow is not an exception. It cannot be caught, it does not unwind, and it does not run a
destructor — the guard page at the end of the stack is hit and the process is gone. There is no
recovery from inside the program, so the only defence is to refuse the input before recursing, which is
what the one-line check does.

The project's self-test shows both halves of that: 40 levels of nesting are refused at the default
limit of 32, and accepted when the limit is raised to 64. The parser did not get smarter; it was told
how deep it was allowed to go.

### Trailing text

The last rule is the one that separates a parser from a scanner:

```cpp
std::optional<Json> parse_document() {
    std::optional<Json> value = parse_value(0);
    if (!value) return std::nullopt;
    skip_ws();
    /* Anything left over means the text was not JSON, however good the start was. */
    if (pos_ != text_.size()) return std::nullopt;
    return value;
}
```

`123abc` begins with a perfectly good number. A parser that stopped when the number ended would return
`123` and leave `abc` for the next caller to trip over. Checking that the position reached the end is
the difference between "this text begins with JSON" and "this text is JSON" — and for a request body,
only the second is safe to act on. Node agrees, and says so in its own words:

```text
Unexpected non-whitespace character after JSON at position 3 (line 1 column 4)
```

## Check the shape before you read it

A `Json` can hold six different things, and asking for the wrong one is not a conversion:


```cpp run-abort
#include <cstdio>
#include <string>
#include <variant>

int main() {
    std::variant<int, std::string> value = std::string("hello");

    /* The value holds a string. std::get<int> does not convert it, and does not
       return zero. It throws. */
    std::printf("the number is %d\n", std::get<int>(value));
    return 0;
}
```

```text
std::bad_variant_access
```

`std::get<int>` on a variant holding a string throws `std::bad_variant_access`. It does not return zero
and it does not convert. That is the correct behaviour — a silent `0` would be a bug that surfaces three
functions later as a wrong price — but it does mean the check is your job:

```cpp
if (value.is_number()) {
    use(value.as_number());
} else {
    /* The client sent something else. Say so. */
}
```

`is_*()` and then `as_*()`. Every `as_*()` in this class is a promise that you already checked, and the
one time you forget, the exception names the problem precisely.

## The project

Six files: the JSON module, a small API layer that builds the payloads, a `main` that exercises both,
and a `Makefile`. It is a model of the service rather than the service — no sockets — so the output is
deterministic and the HTTP layer is visible as bytes rather than as behaviour.

The `/* ===== name ===== */` lines are listing separators, not file contents. Everything between two of
them is exactly what you would type into the file it names.


```cpp make-files
/* ===== json.h ===== */
#ifndef JSON_H
#define JSON_H

#include <cstddef>
#include <map>
#include <optional>
#include <string>
#include <variant>
#include <vector>

/* A JSON value. One class, six shapes, and every one of them is checked
   before it is read. */
class Json {
public:
    using Array = std::vector<Json>;
    using Object = std::map<std::string, Json>;

    Json();
    Json(std::nullptr_t);
    Json(bool b);
    Json(int i);
    Json(double d);
    Json(const char *s);
    Json(std::string s);
    Json(Array a);
    Json(Object o);

    bool is_null() const;
    bool is_bool() const;
    bool is_number() const;
    bool is_string() const;
    bool is_array() const;
    bool is_object() const;

    /* These throw std::bad_variant_access if the shape is not what you asked for. */
    bool as_bool() const;
    double as_number() const;
    const std::string &as_string() const;
    const Array &as_array() const;
    const Object &as_object() const;

    std::string dump() const;

    /* Returns nothing when the text is not JSON, or when it nests deeper
       than max_depth. Never recurses past max_depth. */
    static std::optional<Json> parse(const std::string &text, std::size_t max_depth = 32);

private:
    using Value = std::variant<std::nullptr_t, bool, double, std::string, Array, Object>;

    void dump_into(std::string &out) const;

    Value value_;
};

/* The two pieces worth reusing on their own. */
std::string json_escape(const std::string &s);
std::string json_number(double d);

#endif
/* ===== json.cpp ===== */
#include "json.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <utility>

/* ------------------------------------------------------------------ writing */

std::string json_escape(const std::string &s) {
    std::string out;
    for (unsigned char c : s) {
        switch (c) {
        case '"':  out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\n': out += "\\n";  break;
        case '\r': out += "\\r";  break;
        case '\t': out += "\\t";  break;
        case '\b': out += "\\b";  break;
        case '\f': out += "\\f";  break;
        default:
            if (c < 0x20) {
                char buf[8];
                std::snprintf(buf, sizeof buf, "\\u%04x", c);
                out += buf;
            } else {
                out += static_cast<char>(c);
            }
        }
    }
    return out;
}

std::string json_number(double d) {
    /* JSON has no way to write NaN or Infinity, so neither may reach the wire. */
    if (!std::isfinite(d)) return "null";
    if (d == static_cast<double>(static_cast<long long>(d)) && std::fabs(d) < 1e15) {
        return std::to_string(static_cast<long long>(d));
    }
    char buf[32];
    std::snprintf(buf, sizeof buf, "%.15g", d);
    return buf;
}

Json::Json() : value_(nullptr) {}
Json::Json(std::nullptr_t) : value_(nullptr) {}
Json::Json(bool b) : value_(b) {}
Json::Json(int i) : value_(static_cast<double>(i)) {}
Json::Json(double d) : value_(d) {}
Json::Json(const char *s) : value_(std::string(s)) {}
Json::Json(std::string s) : value_(std::move(s)) {}
Json::Json(Array a) : value_(std::move(a)) {}
Json::Json(Object o) : value_(std::move(o)) {}

bool Json::is_null() const { return std::holds_alternative<std::nullptr_t>(value_); }
bool Json::is_bool() const { return std::holds_alternative<bool>(value_); }
bool Json::is_number() const { return std::holds_alternative<double>(value_); }
bool Json::is_string() const { return std::holds_alternative<std::string>(value_); }
bool Json::is_array() const { return std::holds_alternative<Array>(value_); }
bool Json::is_object() const { return std::holds_alternative<Object>(value_); }

bool Json::as_bool() const { return std::get<bool>(value_); }
double Json::as_number() const { return std::get<double>(value_); }
const std::string &Json::as_string() const { return std::get<std::string>(value_); }
const Json::Array &Json::as_array() const { return std::get<Array>(value_); }
const Json::Object &Json::as_object() const { return std::get<Object>(value_); }

void Json::dump_into(std::string &out) const {
    if (is_null())   { out += "null"; return; }
    if (is_bool())   { out += as_bool() ? "true" : "false"; return; }
    if (is_number()) { out += json_number(as_number()); return; }
    if (is_string()) { out += '"' + json_escape(as_string()) + '"'; return; }

    if (is_array()) {
        out += '[';
        bool first = true;
        for (const Json &item : as_array()) {
            if (!first) out += ',';
            first = false;
            item.dump_into(out);
        }
        out += ']';
        return;
    }

    out += '{';
    bool first = true;
    for (const auto &pair : as_object()) {
        if (!first) out += ',';
        first = false;
        out += '"' + json_escape(pair.first) + "\":";
        pair.second.dump_into(out);
    }
    out += '}';
}

std::string Json::dump() const {
    std::string out;
    dump_into(out);
    return out;
}

/* ------------------------------------------------------------------ reading */

namespace {

/* Turns a code point into the bytes UTF-8 writes for it. */
std::string utf8(unsigned cp) {
    std::string out;
    if (cp < 0x80) {
        out += static_cast<char>(cp);
    } else if (cp < 0x800) {
        out += static_cast<char>(0xC0 | (cp >> 6));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        out += static_cast<char>(0xE0 | (cp >> 12));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else {
        out += static_cast<char>(0xF0 | (cp >> 18));
        out += static_cast<char>(0x80 | ((cp >> 12) & 0x3F));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    }
    return out;
}

class Parser {
public:
    Parser(const std::string &text, std::size_t max_depth)
        : text_(text), max_depth_(max_depth) {}

    std::optional<Json> parse_document() {
        std::optional<Json> value = parse_value(0);
        if (!value) return std::nullopt;
        skip_ws();
        /* Anything left over means the text was not JSON, however good the start was. */
        if (pos_ != text_.size()) return std::nullopt;
        return value;
    }

private:
    const std::string &text_;
    std::size_t pos_ = 0;
    std::size_t max_depth_;

    bool eof() const { return pos_ >= text_.size(); }
    char peek() const { return eof() ? '\0' : text_[pos_]; }

    void skip_ws() {
        while (!eof()) {
            const char c = text_[pos_];
            if (c == ' ' || c == '\t' || c == '\n' || c == '\r') ++pos_;
            else break;
        }
    }

    bool literal(const char *word) {
        const std::size_t n = std::strlen(word);
        if (text_.compare(pos_, n, word) != 0) return false;
        pos_ += n;
        return true;
    }

    std::optional<Json> parse_value(std::size_t depth) {
        if (depth > max_depth_) return std::nullopt;
        skip_ws();
        if (eof()) return std::nullopt;

        const char c = peek();
        if (c == '{') return parse_object(depth);
        if (c == '[') return parse_array(depth);
        if (c == '"') {
            std::optional<std::string> s = parse_string();
            if (!s) return std::nullopt;
            return Json(std::move(*s));
        }
        if (literal("true"))  return Json(true);
        if (literal("false")) return Json(false);
        if (literal("null"))  return Json();
        return parse_number();
    }

    /* Four hex digits, or nothing. */
    std::optional<unsigned> hex4() {
        if (pos_ + 4 > text_.size()) return std::nullopt;
        unsigned value = 0;
        for (int i = 0; i < 4; ++i) {
            const char c = text_[pos_++];
            value <<= 4;
            if (c >= '0' && c <= '9')      value |= static_cast<unsigned>(c - '0');
            else if (c >= 'a' && c <= 'f') value |= static_cast<unsigned>(c - 'a' + 10);
            else if (c >= 'A' && c <= 'F') value |= static_cast<unsigned>(c - 'A' + 10);
            else return std::nullopt;
        }
        return value;
    }

    /* \uXXXX, including the case where one character is written as two escapes. */
    std::optional<std::string> parse_unicode() {
        std::optional<unsigned> first = hex4();
        if (!first) return std::nullopt;
        unsigned cp = *first;

        if (cp >= 0xD800 && cp <= 0xDBFF) {
            /* A high half. It is only a character once its low half arrives. */
            if (pos_ + 2 > text_.size() || text_[pos_] != '\\' || text_[pos_ + 1] != 'u') {
                return std::nullopt;
            }
            pos_ += 2;
            std::optional<unsigned> second = hex4();
            if (!second) return std::nullopt;
            if (*second < 0xDC00 || *second > 0xDFFF) return std::nullopt;
            cp = 0x10000u + ((cp - 0xD800u) << 10) + (*second - 0xDC00u);
        } else if (cp >= 0xDC00 && cp <= 0xDFFF) {
            return std::nullopt;      /* a low half with nothing in front of it */
        }
        return utf8(cp);
    }

    std::optional<std::string> parse_string() {
        if (peek() != '"') return std::nullopt;
        ++pos_;
        std::string out;
        while (true) {
            if (eof()) return std::nullopt;
            const unsigned char c = static_cast<unsigned char>(text_[pos_++]);
            if (c == '"') return out;
            if (c != '\\') {
                if (c < 0x20) return std::nullopt;    /* raw control character */
                out += static_cast<char>(c);
                continue;
            }
            if (eof()) return std::nullopt;
            switch (text_[pos_++]) {
            case '"':  out += '"';  break;
            case '\\': out += '\\'; break;
            case '/':  out += '/';  break;
            case 'b':  out += '\b'; break;
            case 'f':  out += '\f'; break;
            case 'n':  out += '\n'; break;
            case 'r':  out += '\r'; break;
            case 't':  out += '\t'; break;
            case 'u': {
                std::optional<std::string> encoded = parse_unicode();
                if (!encoded) return std::nullopt;
                out += *encoded;
                break;
            }
            default: return std::nullopt;             /* \x is not a JSON escape */
            }
        }
    }

    static bool is_digit(char c) { return c >= '0' && c <= '9'; }

    /* Scans the shape JSON allows first, then converts. Handing the whole
       remaining text to strtod would accept "nan", "0x10" and "1e999". */
    std::optional<Json> parse_number() {
        const std::size_t start = pos_;
        if (peek() == '-') ++pos_;
        if (!is_digit(peek())) return std::nullopt;
        if (peek() == '0') {
            ++pos_;                        /* a leading zero has to stand alone */
        } else {
            while (is_digit(peek())) ++pos_;
        }
        if (peek() == '.') {
            ++pos_;
            if (!is_digit(peek())) return std::nullopt;
            while (is_digit(peek())) ++pos_;
        }
        if (peek() == 'e' || peek() == 'E') {
            ++pos_;
            if (peek() == '+' || peek() == '-') ++pos_;
            if (!is_digit(peek())) return std::nullopt;
            while (is_digit(peek())) ++pos_;
        }
        const std::string digits = text_.substr(start, pos_ - start);
        return Json(std::strtod(digits.c_str(), nullptr));
    }

    std::optional<Json> parse_array(std::size_t depth) {
        ++pos_;                                   /* '[' */
        Json::Array items;
        skip_ws();
        if (peek() == ']') { ++pos_; return Json(std::move(items)); }
        while (true) {
            std::optional<Json> item = parse_value(depth + 1);
            if (!item) return std::nullopt;
            items.push_back(std::move(*item));
            skip_ws();
            if (peek() == ',') { ++pos_; continue; }
            if (peek() == ']') { ++pos_; return Json(std::move(items)); }
            return std::nullopt;
        }
    }

    std::optional<Json> parse_object(std::size_t depth) {
        ++pos_;                                   /* '{' */
        Json::Object fields;
        skip_ws();
        if (peek() == '}') { ++pos_; return Json(std::move(fields)); }
        while (true) {
            skip_ws();
            std::optional<std::string> key = parse_string();
            if (!key) return std::nullopt;
            skip_ws();
            if (peek() != ':') return std::nullopt;
            ++pos_;
            std::optional<Json> value = parse_value(depth + 1);
            if (!value) return std::nullopt;
            /* A repeated key keeps the last one, which is what JavaScript does. */
            fields.insert_or_assign(std::move(*key), std::move(*value));
            skip_ws();
            if (peek() == ',') { ++pos_; continue; }
            if (peek() == '}') { ++pos_; return Json(std::move(fields)); }
            return std::nullopt;
        }
    }
};

}  // namespace

std::optional<Json> Json::parse(const std::string &text, std::size_t max_depth) {
    Parser parser(text, max_depth);
    return parser.parse_document();
}
/* ===== api.h ===== */
#ifndef API_H
#define API_H

#include "json.h"

#include <string>

/* The payloads the service answers with. */
Json items_payload();

/* Returns nothing when there is no such item. It deliberately does not return
   an error payload: a function that builds a body cannot also choose the status
   code, and a body that says 404 inside a 200 response is worse than no answer. */
std::optional<Json> item_payload(const std::string &id);

Json error_payload(int status, const std::string &message);

/* The whole response, headers included, exactly as it goes on the wire. */
std::string render_json(const Json &body, int status, const char *reason);

#endif
/* ===== api.cpp ===== */
#include "api.h"

#include <utility>

namespace {

struct Item {
    int id;
    std::string name;
    double price;
};

/* Note the third name. It holds a double quote, and the fourth holds a newline.
   Both are perfectly ordinary in data a user typed, and both are illegal in a
   JSON string. Nothing here escapes them: json_escape does that, on the way out. */
const Item kItems[] = {
    {1, "bolt", 0.12},
    {2, "washer", 0.03},
    {3, "nut \"heavy duty\"", 0.08},
    {4, "spacer\npack", 0.05},
};

Json item_to_json(const Item &item) {
    Json::Object out;
    out["id"] = Json(item.id);
    out["name"] = Json(item.name);
    out["price"] = Json(item.price);
    return Json(std::move(out));
}

}  // namespace

Json items_payload() {
    Json::Array items;
    for (const Item &item : kItems) items.push_back(item_to_json(item));

    Json::Object out;
    out["count"] = Json(static_cast<int>(items.size()));
    out["items"] = Json(std::move(items));
    return Json(std::move(out));
}

std::optional<Json> item_payload(const std::string &id) {
    for (const Item &item : kItems) {
        if (std::to_string(item.id) == id) return item_to_json(item);
    }
    return std::nullopt;
}

Json error_payload(int status, const std::string &message) {
    Json::Object out;
    out["error"] = Json(message);
    out["status"] = Json(status);
    return Json(std::move(out));
}

std::string render_json(const Json &body, int status, const char *reason) {
    /* One trailing newline, so the payload is also pleasant to read in a terminal.
       It counts towards Content-Length, which is why it is added before measuring. */
    const std::string payload = body.dump() + "\n";

    std::string out;
    out += "HTTP/1.1 " + std::to_string(status) + " " + reason + "\r\n";
    out += "Content-Type: application/json\r\n";
    out += "Content-Length: " + std::to_string(payload.size()) + "\r\n";
    out += "Connection: close\r\n";
    out += "\r\n";
    out += payload;
    return out;
}
/* ===== main.cpp ===== */
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
/* ===== Makefile ===== */
CXX      = c++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -O2

OBJS     = main.o json.o api.o

prog: $(OBJS)
	$(CXX) $(CXXFLAGS) -o prog $(OBJS)

main.o: main.cpp api.h json.h
	$(CXX) $(CXXFLAGS) -c main.cpp

json.o: json.cpp json.h
	$(CXX) $(CXXFLAGS) -c json.cpp

api.o: api.cpp api.h json.h
	$(CXX) $(CXXFLAGS) -c api.cpp

clean:
	rm -f prog $(OBJS)

.PHONY: clean
```

```text
what the parser accepts
-----------------------
  "hello"                          -> "hello"
  42                               -> 42
  -3.5                             -> -3.5
  2e3                              -> 2000
  []                               -> []
  {}                               -> {}
  {"a":1,"b":[2,3]}                -> {"a":1,"b":[2,3]}
  {"b":1,"a":2}                    -> {"a":2,"b":1}
  "\u00e9"                         -> "é"
  "\ud83d\ude00"                   -> "😀"

what it refuses
---------------
  123abc  (trailing text)          -> refused
  01  (leading zero)               -> refused
  nan                              -> refused
  +5  (leading plus)               -> refused
  .5  (no whole part)              -> refused
  1e  (no exponent)                -> refused
  {"a":1,}  (trailing comma)       -> refused
  {a:1}  (bare key)                -> refused
  {"a" 1}  (no colon)              -> refused
  'hi'  (single quotes)            -> refused
  "a\xb"  (bad escape)             -> refused
  "\ud83d"  (lone high)            -> refused
  "unterminated                    -> refused
  a raw newline in a string       -> refused

nesting depth
-------------
  40 deep, limit 32               -> refused
  40 deep, limit 64               -> accepted

the payload
-----------
  {"count":4,"items":[{"id":1,"name":"bolt","price":0.12},{"id":2,"name":"washer","price":0.03},{"id":3,"name":"nut \"heavy duty\"","price":0.08},{"id":4,"name":"spacer\npack","price":0.05}]}

=== GET /api/items on the wire ===
HTTP/1.1 200 OK\r\n
Content-Type: application/json\r\n
Content-Length: 190\r\n
Connection: close\r\n
\r\n
{"count":4,"items":[{"id":1,"name":"bolt","price":0.12},{"id":2,"name":"washer","price":0.03},{"id":3,"name":"nut \"heavy duty\"","price":0.08},{"id":4,"name":"spacer\npack","price":0.05}]}\n
```

Read the transcript in three places.

**The two tables.** Every accepted input comes back as a `dump()` of the value it became, and the
differences are the lessons. `2e3` comes back as `2000` — a round trip preserves the *value*, not the
spelling, so never compare JSON text for equality. `{"b":1,"a":2}` comes back as `{"a":2,"b":1}`
because of the `std::map`. `\u00e9` and `\ud83d\ude00` come back as the actual characters, which is
the only way to see that the decoding worked.

**The refusals.** Fourteen inputs that look plausible and are not JSON. A parser is defined by what it
turns down at least as much as by what it accepts, and every line here is a decision made deliberately
rather than a case that happened not to be thought about.

**The payload and the wire dump.** `count` comes first and `items` follows it — alphabetical, not the
order they were inserted. Item 3's name shows `\"` where the quote is, and item 4's shows `\n` where
the newline is. Those are the two characters `json_escape` exists for, visible in the bytes that would
leave the socket. And `Content-Length: 190` counts the **escaped** body, which is longer than the
source text of the names — the length header has to describe what is actually sent, not what it came
from.

## Driving it from the shell


```sh run-project
#!/bin/sh
./prog --help
echo "---"
./prog /api/items/2
./prog /api/items/99
./prog /nope
exit 0
```

```text
usage: ./prog            run the built-in self-test
       ./prog PATH       answer one path and dump it
---
=== GET /api/items/2 ===
HTTP/1.1 200 OK\r\n
Content-Type: application/json\r\n
Content-Length: 38\r\n
Connection: close\r\n
\r\n
{"id":2,"name":"washer","price":0.03}\n
=== GET /api/items/99 ===
HTTP/1.1 404 Not Found\r\n
Content-Type: application/json\r\n
Content-Length: 36\r\n
Connection: close\r\n
\r\n
{"error":"no item 99","status":404}\n
=== GET /nope ===
HTTP/1.1 404 Not Found\r\n
Content-Type: application/json\r\n
Content-Length: 44\r\n
Connection: close\r\n
\r\n
{"error":"no route for /nope","status":404}\n
```

The command line answers one path at a time and prints the response exactly as the socket would carry
it, with `\r` spelled out so the carriage returns are visible. `GET /api/items/2` is a hit and answers
`200 OK`. `GET /api/items/99` is a miss and answers `404 Not Found` — with a *body* that is also valid
JSON, because an API's errors are part of its protocol and a client should not have to parse HTML to
find out what went wrong. That pair is the subject of the pitfall below, because the first version of
this project got it wrong in a way worth seeing.

:::scenario The item that blanked the page

A user saves an item named `nut "heavy duty"`. The handler builds its response with the obvious line:

```cpp
const std::string body = "{\"name\":\"" + item.name + "\"}";
```

The server logs `200 OK` and no error. The browser shows a blank page, and its console has one line —
this one is from Node 22, which is the same V8 engine a browser runs:

```text
Expected ',' or '}' after property value in JSON at position 14 (line 1 column 15)
```

Why is the page blank rather than showing a mangled name, and what is the smallest change that fixes
it?

:::solution Unescaping is not a formatting problem

The body that went out was `{"name":"nut "heavy duty""}`. A JSON parser reads the key `name`, then the
string `"nut "`, then expects `,` or `}` — and finds `h`. The parse fails at the very first object, so
there is no partial result to render. Nothing is displayed because nothing could be decoded, which is
why the page is empty rather than wrong.

The smallest change is to route the value through the escaper at the one place where it becomes bytes:

```cpp
const std::string body = "{\"name\":" + Json(item.name).dump() + "}";
```

That is the whole fix, and it is small because the escaping lives in `dump()` rather than at the call
site. Compare the alternative — escaping at every site that builds a body — where the fix is "remember
to escape, everywhere, forever", and the next new handler is a new chance to forget.

Two details make this worse than it looks. The server sent `200 OK`, because building a body by
concatenation cannot fail; there is nothing in the server's logs to notice. And the `Content-Length`
that went with the broken body was computed from the *unescaped* text, so it was wrong too — which
means a client that reads exactly `Content-Length` bytes gets a truncated body and a *different*
error. One unescaped character produces two independent protocol failures.

:::

:::

:::pitfall The status code that disagreed with the body

The first version of this chapter's project looked up an item like this:

```cpp
Json item_payload(const std::string &id) {
    for (const Item &item : kItems) {
        if (std::to_string(item.id) == id) return item_to_json(item);
    }
    return error_payload(404, "no item " + id);   // <- the fallback is an error body
}
```

and the caller used it like this:

```cpp
return render_json(item_payload(path.substr(11)), 200, "OK");
```

So `GET /api/items/99` answered this:

```text
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 36

{"error":"no item 99","status":404}
```

One response, two statements about what happened, and they disagree. The status line says success; the
body says 404. A client that trusts the status line caches the failure as a success. A client that
trusts the body shows an error. Both behaviours are defensible, which means the bug will be found by
whichever kind of client you did not test with — and the code that produced it looks entirely
reasonable, because every function did what its name said.

The problem is that `item_payload` is answering a question it was not asked. It knows whether the item
exists; it does not know what the *route* should say about that, and it cannot know, because the status
code belongs to the response and the response belongs to the dispatcher. The fix is to let the function
that builds a body decline to build one:

```cpp
std::optional<Json> item_payload(const std::string &id);   // nothing when there is no such item
```

and let the one place that knows the path choose the status:

```cpp
if (const std::optional<Json> item = item_payload(id)) {
    return render_json(*item, 200, "OK");
}
return render_json(error_payload(404, "no item " + id), 404, "Not Found");
```

That version is in the listing above, and the `./prog /api/items/99` transcript shows it answering
`404 Not Found` with a matching body. The rule generalises: **a function that returns a payload must
not also decide the status code.** The moment it can, you have two authorities on one question.

:::

## Key takeaways

- Inside a JSON string, escape `"`, `\\`, and every character below `U+0020`. Do not escape `/`, and
  do not assume anything else needs escaping.
- **Escape on the way out, never on the way in.** One place in the program turns a character into a
  byte, and that is the place that escapes.
- Commas go *between* elements. The "comma after every element" version passes an empty-list test and
  fails on real data — so write the `bool first` version, or use a value type that cannot get it wrong.
- A round trip preserves the **value**, not the text: `2e3` becomes `2000`, and object keys come back
  sorted from a `std::map` and unsorted from JavaScript. Never compare JSON text for equality.
- Scan a number's shape before converting it. `strtod` accepts `nan`, `+5`, `.5` and `1e999`, none of
  which are JSON.
- `\uXXXX` is a code point, not a character. Anything outside the first 65,536 arrives as two escapes,
  and lone surrogates must be rejected rather than substituted.
- Recursion over untrusted input needs a depth limit. A stack overflow cannot be caught, so the check
  has to happen before the recursive call.
- Check that the position reached the end. `123abc` is not JSON, and a parser that returns `123` is a
  scanner.
- `is_*()` before `as_*()`. Reading the wrong shape throws, by design.
- A function that builds a body must not also choose the status code.

## Practice

- [ ] Write a program that takes a string as `argv[1]` and prints `valid` or `invalid` depending on
      whether `Json::parse` accepts it. Feed it `[1,2,3]`, `[1,2,3,]`, `{"a":}` and `\u0041`.
- [ ] Add a `Json::as_int()` that returns the number rounded to the nearest `int`, and throws when the
      value is not a number. Explain why it must not silently return `0`.
- [ ] `json_number` writes an integral `double` as a bare integer, and everything else with `%.15g`.
      Find a `double` that `%.15g` does **not** round-trip, and change the function so that it does.
- [ ] The parser accepts `{"a":1,"a":2}` and keeps the last value. Change it to keep the *first*, and
      say which behaviour you would ship and why.
- [ ] Add a `Json::at(const std::string &key)` that returns `std::optional<Json>` for an object and
      nothing for any other shape. Use it to read `count` out of `items_payload()`.
- [ ] `parse_unicode` rejects a lone surrogate. Change it to substitute `U+FFFD`, the replacement
      character, and explain in one sentence why the original choice is the safer default for a server.

## Solutions

:::solution Exercise 1

The whole program is the parse call and a branch.

```cpp
#include "json.h"

#include <cstdio>
#include <string>

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    const std::string text = argv[1];
    std::printf("%s -> %s\n", text.c_str(), Json::parse(text) ? "valid" : "invalid");
    return 0;
}
```

Compiled and run on five inputs:

| Input | Result | Why |
|---|---|---|
| `[1,2,3]` | `valid` | three numbers |
| `[1,2,3,]` | `invalid` | a trailing comma is not allowed in an array, exactly as it is not in an object |
| `{"a":}` | `invalid` | a value is required after the colon |
| `\u0041` | `invalid` | an escape is only meaningful inside a string, and there is no opening quote |
| `"\u0041"` | `valid` | the same escape, quoted — and it is the string `A` |

The last two rows are the pair worth having. `\u0041` on its own is not JSON at all; the escape only
means something once a parser is inside a string. Nothing about the four characters changed between the
two rows — only the context they arrived in — which is the whole reason a parser is a state machine
rather than a list of regular expressions.

:::

:::solution Exercise 2

Rounding is the easy part; the decision is what to do when the value is not a number at all.

```cpp
int Json::as_int() const {
    if (!is_number()) throw std::bad_variant_access();
    return static_cast<int>(std::lround(as_number()));
}
```

It must not return `0`, because `0` is a perfectly good value that a caller cannot distinguish from a
failure. A function that reports failure by returning a legal value has moved the problem to every call
site, and the one that forgets is the one that ships. `std::bad_variant_access` is not the ideal
exception type here — a `JsonError` would say more — but it is the right *shape*: refuse loudly.

Compiled against the module, this prints `as_int(3.7) = 4` and `as_int on a string threw: yes`. Note
that `4` is the rounded value and not a truncation: `std::lround` rounds half away from zero, where a
plain `static_cast<int>` would give `3`. Pick one deliberately, because a JSON number that is 3.5 and
comes back as 3 has lost a bit that somebody may have meant.

:::

:::solution Exercise 3

The loss is in `%.15g`, not in the integer branch. Fifteen significant digits is not always enough to
name a `double` again. Measured, with `strtod` on the printed text compared back to the original:

| `double` | `%.15g` writes | round-trips? | `%.17g` writes |
|---|---|---|---|
| `0.1` | `0.1` | yes | `0.10000000000000001` |
| `0.1 + 0.2` | `0.3` | **no** | `0.30000000000000004` |
| `1.0 / 3.0` | `0.333333333333333` | **no** | `0.33333333333333331` |
| `1e16` | `1e+16` | yes | `10000000000000000` |

`0.1 + 0.2` is the one to remember: `%.15g` writes `0.3`, and parsing `0.3` back gives a different
`double` than the one you started with. The fix is one character:

```cpp
char buf[32];
std::snprintf(buf, sizeof buf, "%.17g", d);
return buf;
```

Seventeen significant digits always suffice to round-trip any `double`; fifteen do not. It is uglier —
`0.1` comes out as `0.10000000000000001`, a number that looks wrong and is exactly right — which is why
real libraries ship a shortest-round-trip algorithm instead: the shortest text that still names the same
`double`. `0.1` has one, and it is `0.1`. That algorithm is a genuine piece of work, and it is the honest
reason to use a library for anything that has to be exact.

Two notes on the integer branch while you are in there. `1e16 == 1e16 + 1` is **true** for `double`,
because above `2^53` the spacing between representable values is greater than one, so writing
`10000000000000000` as digits suggests a precision that is not there. And the `std::fabs(d) < 1e15` guard
is what keeps the branch away from that range — a guard that is correct, and that nobody reading
`std::to_string(static_cast<long long>(d))` would guess was load-bearing.

:::

:::solution Exercise 4

Replace `insert_or_assign` with a check, so the first value wins:

```cpp
if (fields.find(*key) == fields.end()) fields.emplace(std::move(*key), std::move(*value));
```

Which to ship depends on the protocol. Keeping the last matches JavaScript, so a browser and the server
agree on what a duplicated key meant. Keeping the first is what a strict validator wants, because a
duplicate key is almost always a bug in the producer and silently discarding one of the two values
hides it. The two defensible positions are "reject the document" and "match the client". Keeping
either one silently, without deciding, is the only wrong answer.

Compiled against the module, the patched parser turns `{"a":1,"a":2}` into `{"a":1}` — the opposite of
the version in the listing, which gives `{"a":2}`. Both are one line apart, and neither announces
itself, which is the whole reason to write the choice down somewhere a reader will find it.

:::

:::solution Exercise 5

```cpp
std::optional<Json> Json::at(const std::string &key) const {
    if (!is_object()) return std::nullopt;
    const auto it = as_object().find(key);
    if (it == as_object().end()) return std::nullopt;
    return it->second;
}
```

`items_payload().at("count")` gives a `Json` holding `4`. Note that a missing key and a wrong shape both
give `std::nullopt` — convenient here, but worth a second thought: a caller that needs to tell "no such
key" from "this is an array" has to check `is_object()` itself first.

Compiled against the module, the three cases come out as `at("count") = 4`, `at("nope") = nothing`, and
`at on an array = nothing`. The last one is the design decision: `.at()` on an array is not an error and
not an exception, it is simply "no such key", because an array has no keys. If you would rather that be
a bug, throw — but decide, and put the reason in the comment.

:::

:::solution Exercise 6

Substituting is not one line. There are three places where a surrogate is rejected, and a lone half can
arrive at any of them, so every one of them has to change:

```cpp
/* 1. a high half with no low half after it */
if (pos_ + 2 > text_.size() || text_[pos_] != '\\' || text_[pos_ + 1] != 'u') {
    return utf8(0xFFFD);
}

/* 2. a high half followed by something that is not a low half */
if (*second < 0xDC00 || *second > 0xDFFF) return utf8(0xFFFD);

/* 3. a low half with nothing in front of it */
} else if (cp >= 0xDC00 && cp <= 0xDFFF) {
    return utf8(0xFFFD);
}
```

Compiled and run against all five cases, the result is:

| Input | What comes out | Bytes |
|---|---|---|
| `"\ud83d"` — a lone high half | `U+FFFD` | `ef bf bd` |
| `"\udc00"` — a lone low half | `U+FFFD` | `ef bf bd` |
| `"\ud83d\u0041"` — high, then not a low half | `U+FFFD` | `ef bf bd` |
| `"\ud83d\ude00"` — a real pair | the emoji | `f0 9f 98 80` |
| `"\u00e9"` — an ordinary escape | `é` | `c3 a9` |

`ef bf bd` is the three-byte UTF-8 encoding of `U+FFFD`, the replacement character — the question mark
in a diamond you have seen when a file's encoding is wrong.

The last two rows are the ones that matter. A valid pair still decodes to four bytes, so the substitution
did not break the good case. And this is why the obvious one-line version is wrong: putting
`if (cp >= 0xD800 && cp <= 0xDFFF) return utf8(0xFFFD);` at the top of the function looks like it does
the job, and it fails the fourth row — it fires before the parser has looked for a low half, so every
real emoji in the input gets replaced too. A patch that passes the tests you thought of and corrupts the
data you did not is worse than the refusal it replaced.

The original is safer because a lone surrogate means the input is **not valid JSON**, and a server's job
is to say so. Substituting produces a document that parses and is quietly wrong — the client sees a name
with a replacement character in it and has no way to know the server discarded something. Refusing gives
the client an error it can act on; substituting gives it corrupted data and no signal. For a library a
person is debugging, substituting is friendlier. For a server parsing bytes from a network, refuse.

:::
