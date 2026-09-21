#include <sqlite3.h>

#include <cstdio>

static void exec(sqlite3 *db, const char *sql) {
    char *err = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::printf("  rejected: %s\n", err);
        sqlite3_free(err);
    } else {
        std::printf("  accepted: %s\n", sql);
    }
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    exec(db, "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);");
    exec(db, "CREATE TABLE books (id INTEGER PRIMARY KEY,"
             " author_id INTEGER REFERENCES authors(id));");
    exec(db, "INSERT INTO authors VALUES (1, 'Ada');");

    int fk = 0;
    sqlite3_stmt *q = nullptr;
    sqlite3_prepare_v2(db, "PRAGMA foreign_keys;", -1, &q, nullptr);
    if (sqlite3_step(q) == SQLITE_ROW) fk = sqlite3_column_int(q, 0);
    sqlite3_finalize(q);
    std::printf("foreign_keys at startup = %d\n", fk);

    std::printf("with the pragma off:\n");
    exec(db, "INSERT INTO books VALUES (1, 99);");  // author 99 does not exist

    exec(db, "PRAGMA foreign_keys = ON;");
    std::printf("with the pragma on:\n");
    exec(db, "INSERT INTO books VALUES (2, 99);");

    sqlite3_prepare_v2(db, "SELECT count(*) FROM books;", -1, &q, nullptr);
    if (sqlite3_step(q) == SQLITE_ROW) {
        std::printf("books stored = %d\n", sqlite3_column_int(q, 0));
    }
    sqlite3_finalize(q);

    sqlite3_close(db);
    return 0;
}
