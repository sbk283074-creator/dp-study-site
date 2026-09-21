#include <sqlite3.h>

#include <cstdio>

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    char *err = nullptr;
    sqlite3_exec(db,
                 "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);",
                 nullptr, nullptr, &err);

    // ---- write: bind, step once, expect DONE --------------------------------
    sqlite3_stmt *insert = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO users (name, age) VALUES (?, ?);", -1, &insert, nullptr);
    std::printf("parameter count = %d\n", sqlite3_bind_parameter_count(insert));

    sqlite3_bind_text(insert, 1, "ada", -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(insert, 2, 36);
    int rc = sqlite3_step(insert);
    std::printf("insert step rc=%d (SQLITE_DONE=%d)\n", rc, SQLITE_DONE);
    std::printf("last_insert_rowid=%lld\n", (long long)sqlite3_last_insert_rowid(db));
    std::printf("changes=%d\n", sqlite3_changes(db));

    // A prepared statement is reusable: reset, rebind, step again.
    sqlite3_reset(insert);
    sqlite3_bind_text(insert, 1, "grace", -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(insert, 2, 45);
    rc = sqlite3_step(insert);
    std::printf("second insert rc=%d, rowid=%lld\n", rc,
                (long long)sqlite3_last_insert_rowid(db));
    sqlite3_finalize(insert);

    // ---- read: step until it stops returning rows ---------------------------
    sqlite3_stmt *select = nullptr;
    sqlite3_prepare_v2(db, "SELECT id, name, age FROM users ORDER BY id;", -1, &select, nullptr);
    std::printf("column count = %d\n", sqlite3_column_count(select));
    int rows = 0;
    while ((rc = sqlite3_step(select)) == SQLITE_ROW) {
        ++rows;
        std::printf("  %d: %s (%d)\n", sqlite3_column_int(select, 0),
                    sqlite3_column_text(select, 1), sqlite3_column_int(select, 2));
    }
    std::printf("rows=%d, final rc=%d (SQLITE_ROW=%d SQLITE_DONE=%d)\n", rows, rc,
                SQLITE_ROW, SQLITE_DONE);
    sqlite3_finalize(select);

    sqlite3_close(db);
    return 0;
}
