#include <sqlite3.h>

#include <cstdio>
#include <string>

static void plan(sqlite3 *db, const char *label, const char *sql) {
    const std::string explained = std::string("EXPLAIN QUERY PLAN ") + sql;
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, explained.c_str(), -1, &stmt, nullptr);
    std::printf("%s\n", label);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("  %s\n", sqlite3_column_text(stmt, 3));
    }
    sqlite3_finalize(stmt);
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE events (id INTEGER PRIMARY KEY, kind TEXT, at INTEGER);",
                 nullptr, nullptr, &err);

    sqlite3_stmt *fill = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO events (kind, at) VALUES (?, ?);", -1, &fill, nullptr);
    for (int i = 0; i < 500; ++i) {
        sqlite3_bind_text(fill, 1, i % 2 ? "click" : "view", -1, SQLITE_TRANSIENT);
        sqlite3_bind_int(fill, 2, i);
        sqlite3_step(fill);
        sqlite3_reset(fill);
    }
    sqlite3_finalize(fill);

    const char *query = "SELECT id FROM events WHERE kind = 'click';";
    plan(db, "before the index:", query);

    sqlite3_exec(db, "CREATE INDEX events_kind ON events (kind);", nullptr, nullptr, &err);
    plan(db, "after the index:", query);

    // ANALYZE tells the planner how the data is distributed, which is what it
    // uses to decide whether the index is worth using at all.
    sqlite3_exec(db, "ANALYZE;", nullptr, nullptr, &err);
    plan(db, "after ANALYZE:", query);

    sqlite3_close(db);
    return 0;
}
