#include <sqlite3.h>

#include <cstdio>
#include <string>
#include <vector>

// The shape the exercise starts from: the caller's string is part of the SQL.
static std::vector<std::string> find_by_name_unsafe(sqlite3 *db, const std::string &name) {
    const std::string sql = "SELECT email FROM people WHERE name = '" + name + "';";
    std::vector<std::string> out;
    sqlite3_stmt *stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
        std::printf("  rejected: %s\n", sqlite3_errmsg(db));
        return out;
    }
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        out.emplace_back(reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0)));
    }
    sqlite3_finalize(stmt);
    return out;
}

// The fix: the caller's string becomes a value the engine binds, never text it parses.
static std::vector<std::string> find_by_name(sqlite3 *db, const std::string &name) {
    std::vector<std::string> out;
    sqlite3_stmt *stmt = nullptr;
    if (sqlite3_prepare_v2(db, "SELECT email FROM people WHERE name = ?;", -1, &stmt, nullptr) !=
        SQLITE_OK) {
        std::printf("  rejected: %s\n", sqlite3_errmsg(db));
        return out;
    }
    sqlite3_bind_text(stmt, 1, name.c_str(), -1, SQLITE_TRANSIENT);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char *text = sqlite3_column_text(stmt, 0);
        out.emplace_back(reinterpret_cast<const char *>(text),
                         static_cast<std::size_t>(sqlite3_column_bytes(stmt, 0)));
    }
    sqlite3_finalize(stmt);
    return out;
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db,
                 "CREATE TABLE people (name TEXT, email TEXT);"
                 "INSERT INTO people VALUES ('ada', 'ada@example.com');",
                 nullptr, nullptr, &err);

    const std::string attack = "' OR '1' = '1";

    std::printf("unsafe, with %s:\n", attack.c_str());
    for (const std::string &s : find_by_name_unsafe(db, attack)) std::printf("  hit: %s\n", s.c_str());

    std::printf("bound, with the same string:\n");
    const std::vector<std::string> hits = find_by_name(db, attack);
    std::printf("  hits: %zu\n", hits.size());
    for (const std::string &s : hits) std::printf("  hit: %s\n", s.c_str());

    std::printf("bound, with a real name:\n");
    for (const std::string &s : find_by_name(db, "ada")) std::printf("  hit: %s\n", s.c_str());

    sqlite3_close(db);
    return 0;
}
