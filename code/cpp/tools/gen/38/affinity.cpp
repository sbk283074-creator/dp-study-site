#include <sqlite3.h>

#include <cstdio>

// SQLite columns have *affinity*, not a fixed type: the declared type is a
// preference applied when a value is stored, not a constraint enforced forever.
int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    char *err = nullptr;
    sqlite3_exec(db,
                 "CREATE TABLE t (n INTEGER, r REAL, b BLOB, s TEXT);"
                 "INSERT INTO t VALUES ('abc', '3.5', 42, 42);"
                 "INSERT INTO t VALUES ('42',  'x',   42, 42);",
                 nullptr, nullptr, &err);

    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "SELECT typeof(n), n, typeof(r), r, typeof(b), b, typeof(s), s FROM t;",
                       -1, &stmt, nullptr);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("n: %-7s %-5s | r: %-7s %-5s | b: %-7s %-5s | s: %-7s %s\n",
                    sqlite3_column_text(stmt, 0), sqlite3_column_text(stmt, 1),
                    sqlite3_column_text(stmt, 2), sqlite3_column_text(stmt, 3),
                    sqlite3_column_text(stmt, 4), sqlite3_column_text(stmt, 5),
                    sqlite3_column_text(stmt, 6), sqlite3_column_text(stmt, 7));
    }
    sqlite3_finalize(stmt);

    // A BLOB column has no affinity at all, so nothing is ever converted.
    sqlite3_exec(db, "INSERT INTO t VALUES (1, 1, 'still text', 1);", nullptr, nullptr, &err);
    std::printf("blob column kept: %s\n", "see last row");
    sqlite3_prepare_v2(db, "SELECT typeof(b), b FROM t WHERE rowid = 3;", -1, &stmt, nullptr);
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("row 3 -> typeof=%s value=%s\n", sqlite3_column_text(stmt, 0),
                    sqlite3_column_text(stmt, 1));
    }
    sqlite3_finalize(stmt);

    sqlite3_close(db);
    return 0;
}
