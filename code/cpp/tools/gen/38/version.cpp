#include <sqlite3.h>

#include <cstdio>

int main() {
    std::printf("SQLite %s\n", sqlite3_libversion());
    std::printf("version number %d\n", sqlite3_libversion_number());

    sqlite3 *db = nullptr;
    const int rc = sqlite3_open(":memory:", &db);
    std::printf("open(:memory:) rc=%d\n", rc);
    // An in-memory database has no filename; that empty string is the tell.
    std::printf("filename of main db = [%s]\n", sqlite3_db_filename(db, "main"));

    sqlite3_close(db);
    return 0;
}
