#include <sqlite3.h>

#include <cstdio>
#include <string>

// SQLITE_STATIC tells SQLite "this buffer outlives the statement, do not copy
// it". That is a promise about memory, and breaking it is use-after-free.
int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE notes (body TEXT);", nullptr, nullptr, &err);

    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO notes VALUES (?);", -1, &stmt, nullptr);
    {
        std::string temporary = "a string long enough to live on the heap";
        sqlite3_bind_text(stmt, 1, temporary.c_str(), -1, SQLITE_STATIC);
    }  // `temporary` is destroyed here; SQLite still holds the pointer.

    const int rc = sqlite3_step(stmt);  // reads the dead buffer
    std::printf("step rc=%d\n", rc);
    sqlite3_finalize(stmt);

    sqlite3_stmt *check = nullptr;
    sqlite3_prepare_v2(db, "SELECT body FROM notes;", -1, &check, nullptr);
    if (sqlite3_step(check) == SQLITE_ROW) {
        std::printf("stored: %s\n", sqlite3_column_text(check, 0));
    }
    sqlite3_finalize(check);

    sqlite3_close(db);
    return 0;
}
