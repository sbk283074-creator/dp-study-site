#include <sqlite3.h>

#include <cstdio>

static int count_rows(sqlite3 *db) {
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "SELECT count(*) FROM ledger;", -1, &stmt, nullptr);
    int n = -1;
    if (sqlite3_step(stmt) == SQLITE_ROW) n = sqlite3_column_int(stmt, 0);
    sqlite3_finalize(stmt);
    return n;
}

static void run(const char *sql) {
    sqlite3 *db = nullptr;
    sqlite3_open("ledger.db", &db);
    char *err = nullptr;
    sqlite3_exec(db, sql, nullptr, nullptr, &err);
    if (err) {
        std::printf("  error: %s\n", err);
        sqlite3_free(err);
    }
    std::printf("  rows visible here = %d\n", count_rows(db));
    sqlite3_close(db);
}

int main() {
    std::remove("ledger.db");
    run("CREATE TABLE ledger (id INTEGER PRIMARY KEY, note TEXT);"
        "INSERT INTO ledger (note) VALUES ('committed');");

    // BEGIN without COMMIT: sqlite3_close rolls the transaction back.
    run("BEGIN; INSERT INTO ledger (note) VALUES ('never committed');");

    std::printf("reopened:\n");
    run("SELECT 1;");

    // WAL changes who can read while someone writes, not whether COMMIT means
    // durable -- so it has to be asked for explicitly, per connection.
    sqlite3 *db = nullptr;
    sqlite3_open("ledger.db", &db);
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "PRAGMA journal_mode = WAL;", -1, &stmt, nullptr);
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("journal_mode after pragma = %s\n", sqlite3_column_text(stmt, 0));
    }
    sqlite3_finalize(stmt);
    sqlite3_close(db);

    std::remove("ledger.db");
    std::remove("ledger.db-wal");
    std::remove("ledger.db-shm");
    return 0;
}
