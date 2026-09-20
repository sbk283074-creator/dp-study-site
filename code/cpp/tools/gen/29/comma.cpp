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
