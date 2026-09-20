#!/usr/bin/env python3
"""Compile every solution in chapter 29 against the real module.

A solution inside a `:::solution` callout is usually a fragment, so the chapter
harness never compiles it. This script does: it applies each solution to a copy of
`proj/` and builds it, so the chapter cannot teach code that does not work.

Run from anywhere:  python3 code/cpp/tools/gen/29/verify_solutions.py
"""
import pathlib
import shutil
import subprocess
import sys

SRC = pathlib.Path(__file__).resolve().parent
PROJ = SRC / "proj"
WORK = SRC / ".solutions"
CXX = "clang++ -std=c++17 -Wall -Wextra -Werror"


def sh(cmd, cwd=WORK):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return p.stdout + p.stderr, p.returncode


def compile_or_die(label, cmd):
    out, rc = sh(cmd)
    if rc:
        print(f"{label}: COMPILE FAIL")
        print(out)
        sys.exit(1)
    print(f"{label}: compiled clean")
    return out


shutil.rmtree(WORK, ignore_errors=True)
WORK.mkdir()
for name in ("json.h", "json.cpp"):
    shutil.copy(PROJ / name, WORK / name)

h = (WORK / "json.h").read_text()
c = (WORK / "json.cpp").read_text()

# ---- solutions 2 and 5: two new members -----------------------------------------
anchor = "    const Object &as_object() const;\n"
assert anchor in h
h = h.replace(anchor, anchor + "    int as_int() const;\n    std::optional<Json> at(const std::string &key) const;\n")

impl = '''int Json::as_int() const {
    if (!is_number()) throw std::bad_variant_access();
    return static_cast<int>(std::lround(as_number()));
}

std::optional<Json> Json::at(const std::string &key) const {
    if (!is_object()) return std::nullopt;
    const auto it = as_object().find(key);
    if (it == as_object().end()) return std::nullopt;
    return it->second;
}

'''
assert "void Json::dump_into" in c
c = c.replace("void Json::dump_into", impl + "void Json::dump_into", 1)

# ---- solution 3: no integer special case ----------------------------------------
old_num = '''    if (!std::isfinite(d)) return "null";
    if (d == static_cast<double>(static_cast<long long>(d)) && std::fabs(d) < 1e15) {
        return std::to_string(static_cast<long long>(d));
    }
    char buf[32];
    std::snprintf(buf, sizeof buf, "%.15g", d);
    return buf;'''
new_num = '''    if (!std::isfinite(d)) return "null";
    char buf[32];
    std::snprintf(buf, sizeof buf, "%.17g", d);
    return buf;'''
assert old_num in c, "solution 3 patch did not apply"
c = c.replace(old_num, new_num)

# ---- solution 4: the first duplicate wins ---------------------------------------
old_dup = "            fields.insert_or_assign(std::move(*key), std::move(*value));"
new_dup = "            if (fields.find(*key) == fields.end()) fields.emplace(std::move(*key), std::move(*value));"
assert old_dup in c, "solution 4 patch did not apply"
c = c.replace(old_dup, new_dup)

(WORK / "json.h").write_text(h)
(WORK / "json.cpp").write_text(c)

(WORK / "test_solutions.cpp").write_text(r'''#include "json.h"

#include <cstdio>

int main() {
    /* Solution 2 */
    const Json number = 3.7;
    std::printf("as_int(3.7) = %d\n", number.as_int());
    bool threw = false;
    try {
        const Json text = "x";
        text.as_int();
    } catch (const std::bad_variant_access &) {
        threw = true;
    }
    std::printf("as_int on a string threw: %s\n", threw ? "yes" : "no");

    /* Solution 3 */
    std::printf("json_number(0.1)  = %s\n", json_number(0.1).c_str());
    std::printf("json_number(1e16) = %s\n", json_number(1e16).c_str());

    /* Solution 4 */
    const std::optional<Json> dup = Json::parse("{\"a\":1,\"a\":2}");
    std::printf("duplicate keeps: %s\n", dup ? dup->dump().c_str() : "refused");

    /* Solution 5 */
    const std::optional<Json> doc = Json::parse("{\"count\":4}");
    const std::optional<Json> missing = doc->at("nope");
    const std::optional<Json> on_array = Json::parse("[1,2]")->at("count");
    std::printf("at(\"count\")     = %s\n", doc->at("count")->dump().c_str());
    std::printf("at(\"nope\")      = %s\n", missing ? "something" : "nothing");
    std::printf("at on an array = %s\n", on_array ? "something" : "nothing");
    return 0;
}
''')

compile_or_die("solutions 2-5", f"{CXX} -o sols json.cpp test_solutions.cpp")
print(sh("./sols")[0].rstrip())

# ---- solution 6: substitute the replacement character ---------------------------
# Three separate rejection points, because a lone half can arrive at any of them.
for old, new in [
    ("                return std::nullopt;\n            }", "                return utf8(0xFFFD);\n            }"),
    ("            if (*second < 0xDC00 || *second > 0xDFFF) return std::nullopt;",
     "            if (*second < 0xDC00 || *second > 0xDFFF) return utf8(0xFFFD);"),
    ("        } else if (cp >= 0xDC00 && cp <= 0xDFFF) {\n            return std::nullopt;",
     "        } else if (cp >= 0xDC00 && cp <= 0xDFFF) {\n            return utf8(0xFFFD);"),
]:
    assert old in c, f"solution 6 patch did not apply:\n{old}"
    c = c.replace(old, new, 1)
(WORK / "json6.cpp").write_text(c)
(WORK / "test_six.cpp").write_text(r'''#include "json.h"

#include <cstdio>
#include <string>

static void show(const char *label, const char *text) {
    const std::optional<Json> value = Json::parse(text);
    if (!value) {
        std::printf("  %-13s -> refused\n", label);
        return;
    }
    const std::string bytes = value->as_string();
    std::printf("  %-13s ->", label);
    for (unsigned char b : bytes) std::printf(" %02x", b);
    std::printf("   %zu byte(s)\n", bytes.size());
}

int main() {
    show("lone high", "\"\\ud83d\"");
    show("lone low", "\"\\udc00\"");
    show("high+non-low", "\"\\ud83d\\u0041\"");
    show("a real pair", "\"\\ud83d\\ude00\"");
    show("ordinary", "\"\\u00e9\"");
    return 0;
}
''')
compile_or_die("solution 6", f"{CXX} -o six json6.cpp test_six.cpp")
print(sh("./six")[0].rstrip())

# ---- solution 1: the validity program -------------------------------------------
(WORK / "valid.cpp").write_text(r'''#include "json.h"

#include <cstdio>
#include <string>

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    const std::string text = argv[1];
    std::printf("%s -> %s\n", text.c_str(), Json::parse(text) ? "valid" : "invalid");
    return 0;
}
''')
compile_or_die("solution 1", f"{CXX} -o valid json.cpp valid.cpp")

# Pass the arguments as a list: a shell would eat the backslash in \u0041, and then
# the measurement would be of the shell rather than of the parser.
cases = ["[1,2,3]", "[1,2,3,]", '{"a":}', chr(92) + "u0041", '"' + chr(92) + 'u0041"']
for case in cases:
    p = subprocess.run(["./valid", case], cwd=WORK, capture_output=True, text=True)
    print(p.stdout.rstrip())

shutil.rmtree(WORK, ignore_errors=True)
print("\nall six solutions compiled and ran")
