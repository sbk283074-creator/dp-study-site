#include <sqlite3.h>

#include <string>

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO notes VALUES (?);", -1, &stmt, nullptr);

    // sqlite3_bind_text wants a const char *, not a std::string. There is no
    // implicit conversion, so this is a hard compile error -- which is exactly
    // what you want, because the "working" version would be a dangling pointer.
    const std::string body = "hello";
    sqlite3_bind_text(stmt, 1, body, -1, SQLITE_TRANSIENT);

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return 0;
}
