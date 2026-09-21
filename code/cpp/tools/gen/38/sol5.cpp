#include <sqlite3.h>

#include <cstdio>
#include <optional>
#include <string>

// A missing row and a row holding NULL are different facts, and collapsing them
// into "" is how a service ends up reporting a zero that was never recorded.
static std::optional<std::string> scalar(sqlite3 *db, const std::string &sql) {
    sqlite3_stmt *stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) return std::nullopt;
    const int rc = sqlite3_step(stmt);
    std::optional<std::string> out;
    if (rc == SQLITE_ROW) {
        if (sqlite3_column_type(stmt, 0) == SQLITE_NULL) {
            out = std::nullopt;  // there is a row, and its value is NULL
        } else {
            const unsigned char *text = sqlite3_column_text(stmt, 0);
            out = std::string(reinterpret_cast<const char *>(text),
                              static_cast<std::size_t>(sqlite3_column_bytes(stmt, 0)));
        }
    }
    sqlite3_finalize(stmt);
    return out;
}

static void report(const char *label, const std::optional<std::string> &value) {
    if (!value.has_value()) {
        std::printf("%s -> (no value)\n", label);
    } else {
        std::printf("%s -> %s\n", label, value->c_str());
    }
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db,
                 "CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);"
                 "INSERT INTO settings VALUES ('theme', 'dark'), ('tz', NULL);",
                 nullptr, nullptr, &err);

    report("theme", scalar(db, "SELECT value FROM settings WHERE key = 'theme';"));
    report("tz    ", scalar(db, "SELECT value FROM settings WHERE key = 'tz';"));
    report("missing", scalar(db, "SELECT value FROM settings WHERE key = 'nope';"));
    report("bad sql", scalar(db, "SELECT value FROM no_such_table;"));

    sqlite3_close(db);
    return 0;
}
