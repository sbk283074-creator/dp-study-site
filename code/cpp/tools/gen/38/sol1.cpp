#include <sqlite3.h>

#include <cstdio>

int main() {
    std::remove("visits.db");
    sqlite3 *db = nullptr;
    sqlite3_open("visits.db", &db);
    char *err = nullptr;

    sqlite3_exec(db,
                 "CREATE TABLE visits ("
                 "  url  TEXT PRIMARY KEY,"
                 "  hits INTEGER NOT NULL DEFAULT 0);"
                 "INSERT INTO visits (url) VALUES ('/'), ('/about'), ('/pricing');",
                 nullptr, nullptr, &err);
    std::printf("total_changes after setup = %d\n", sqlite3_total_changes(db));

    sqlite3_exec(db, "UPDATE visits SET hits = hits + 1 WHERE url = '/';", nullptr, nullptr, &err);
    std::printf("total_changes after update = %d\n", sqlite3_total_changes(db));

    // An upsert: insert, or fold into the existing row. No SELECT-then-decide.
    sqlite3_exec(db,
                 "INSERT INTO visits (url, hits) VALUES ('/', 1)"
                 " ON CONFLICT (url) DO UPDATE SET hits = hits + 1;",
                 nullptr, nullptr, &err);
    std::printf("total_changes after upsert = %d\n", sqlite3_total_changes(db));

    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "SELECT url, hits FROM visits ORDER BY url;", -1, &stmt, nullptr);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("  %-10s %d\n", sqlite3_column_text(stmt, 0), sqlite3_column_int(stmt, 1));
    }
    sqlite3_finalize(stmt);

    sqlite3_close(db);
    std::remove("visits.db");
    return 0;
}
