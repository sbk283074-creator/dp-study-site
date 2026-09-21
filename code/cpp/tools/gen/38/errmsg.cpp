#include <sqlite3.h>

#include <cstdio>

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    sqlite3_stmt *stmt = nullptr;
    const int rc = sqlite3_prepare_v2(db, "SELECT * FROM nope;", -1, &stmt, nullptr);
    std::printf("prepare rc=%d (SQLITE_OK=%d, SQLITE_ERROR=%d)\n", rc, SQLITE_OK, SQLITE_ERROR);
    std::printf("sqlite3_errmsg: %s\n", sqlite3_errmsg(db));
    std::printf("extended code:  %d\n", sqlite3_extended_errcode(db));
    std::printf("handle is %s\n", stmt == nullptr ? "null" : "not null");

    // A constraint failure is reported the same way, with its own code.
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE t (n INTEGER CHECK (n > 0));", nullptr, nullptr, &err);
    const int bad = sqlite3_exec(db, "INSERT INTO t VALUES (-1);", nullptr, nullptr, &err);
    std::printf("\nconstraint rc=%d: %s\n", bad, err);
    std::printf("extended code:  %d\n", sqlite3_extended_errcode(db));
    sqlite3_free(err);

    sqlite3_close(db);
    return 0;
}
