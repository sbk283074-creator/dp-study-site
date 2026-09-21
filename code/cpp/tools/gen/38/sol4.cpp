#include <sqlite3.h>

#include <cstdio>
#include <string>

static void exec(sqlite3 *db, const char *sql) {
    char *err = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::printf("  rejected: %s\n", err);
        sqlite3_free(err);
    }
}

static int count(sqlite3 *db, const char *table) {
    sqlite3_stmt *stmt = nullptr;
    const std::string sql = std::string("SELECT count(*) FROM ") + table + ";";
    sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    int n = -1;
    if (sqlite3_step(stmt) == SQLITE_ROW) n = sqlite3_column_int(stmt, 0);
    sqlite3_finalize(stmt);
    return n;
}

static void add(sqlite3 *db, const char *table, const char *note) {
    sqlite3_stmt *stmt = nullptr;
    const std::string sql = std::string("INSERT INTO ") + table + " (note) VALUES (?);";
    sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, note, -1, SQLITE_TRANSIENT);
    const int rc = sqlite3_step(stmt);
    std::printf("  add %-8s -> %s\n", note, rc == SQLITE_DONE ? "ok" : sqlite3_errmsg(db));
    sqlite3_finalize(stmt);
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    exec(db, "CREATE TABLE ledger (id INTEGER PRIMARY KEY, note TEXT UNIQUE);");

    // One outer transaction, one savepoint inside it. Rolling back to the
    // savepoint keeps the work done before it and discards only what came after.
    exec(db, "BEGIN;");
    add(db, "ledger", "alpha");

    exec(db, "SAVEPOINT risky;");
    add(db, "ledger", "bravo");
    add(db, "ledger", "alpha");  // UNIQUE violation, inside the savepoint
    exec(db, "ROLLBACK TO risky;");
    exec(db, "RELEASE risky;");
    std::printf("after ROLLBACK TO: rows = %d\n", count(db, "ledger"));

    add(db, "ledger", "charlie");
    exec(db, "COMMIT;");
    std::printf("after COMMIT:      rows = %d\n", count(db, "ledger"));

    sqlite3_close(db);
    return 0;
}
