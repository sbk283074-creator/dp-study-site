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
