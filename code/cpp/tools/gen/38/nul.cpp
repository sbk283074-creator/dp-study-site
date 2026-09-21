#include <sqlite3.h>

#include <cstdio>
#include <cstring>

// A SQLite TEXT value is a counted byte string, not a C string. It can contain
// a zero byte, and every C API that treats it as one will silently truncate.
int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE blobs (payload TEXT);", nullptr, nullptr, &err);

    const char payload[] = {'a', '\0', 'b', 'c'};  // 4 bytes, one of them NUL
    sqlite3_stmt *insert = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO blobs VALUES (?);", -1, &insert, nullptr);
    sqlite3_bind_text(insert, 1, payload, static_cast<int>(sizeof(payload)), SQLITE_TRANSIENT);
    sqlite3_step(insert);
    sqlite3_finalize(insert);

    sqlite3_stmt *select = nullptr;
    sqlite3_prepare_v2(db, "SELECT payload FROM blobs;", -1, &select, nullptr);
    if (sqlite3_step(select) == SQLITE_ROW) {
        const unsigned char *text = sqlite3_column_text(select, 0);
        const int bytes = sqlite3_column_bytes(select, 0);
        std::printf("sqlite3_column_bytes = %d\n", bytes);
        std::printf("strlen               = %zu\n", std::strlen(reinterpret_cast<const char *>(text)));
        std::printf("bytes:");
        for (int i = 0; i < bytes; ++i) std::printf(" %02x", text[i]);
        std::printf("\n");
    }
    sqlite3_finalize(select);

    sqlite3_close(db);
    return 0;
}
