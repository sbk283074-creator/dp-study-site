#include <sqlite3.h>

#include <cstdio>

static int count_rows(sqlite3 *db) {
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "SELECT count(*) FROM accounts;", -1, &stmt, nullptr);
    int n = -1;
    if (sqlite3_step(stmt) == SQLITE_ROW) n = sqlite3_column_int(stmt, 0);
    sqlite3_finalize(stmt);
    return n;
}

static void try_insert(sqlite3 *db, const char *name, const char *label) {
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO accounts (name) VALUES (?);", -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, name, -1, SQLITE_TRANSIENT);
    const int rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        std::printf("  %s -> rejected (%s)\n", label, sqlite3_errmsg(db));
    } else {
        std::printf("  %s -> stored\n", label);
    }
    sqlite3_finalize(stmt);
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;

    // ---- no transaction: every statement commits on its own -----------------
    sqlite3_exec(db, "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT UNIQUE);",
                 nullptr, nullptr, &err);
    try_insert(db, "ada", "insert ada");
    try_insert(db, "bob", "insert bob");
    try_insert(db, "ada", "insert ada again");
    std::printf("autocommit: rows = %d\n", count_rows(db));

    // ---- one transaction: all of it lands or none of it does ---------------
    sqlite3_exec(db, "DROP TABLE accounts;", nullptr, nullptr, &err);
    sqlite3_exec(db, "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT UNIQUE);",
                 nullptr, nullptr, &err);
    sqlite3_exec(db, "BEGIN;", nullptr, nullptr, &err);
    try_insert(db, "ada", "insert ada");
    try_insert(db, "bob", "insert bob");
    try_insert(db, "ada", "insert ada again");
    sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, &err);
    std::printf("after rollback: rows = %d\n", count_rows(db));

    // ---- and a transaction that does commit --------------------------------
    sqlite3_exec(db, "BEGIN;", nullptr, nullptr, &err);
    try_insert(db, "cleo", "insert cleo");
    try_insert(db, "dana", "insert dana");
    sqlite3_exec(db, "COMMIT;", nullptr, nullptr, &err);
    std::printf("after commit: rows = %d\n", count_rows(db));

    sqlite3_close(db);
    return 0;
}
