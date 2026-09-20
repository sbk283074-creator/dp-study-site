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
