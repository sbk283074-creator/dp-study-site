#include <nlohmann/json.hpp>

#include <cstdio>

int main() {
    nlohmann::json value;
    value["ok"] = true;
    std::printf("%s\n", value.dump().c_str());
    return 0;
}
