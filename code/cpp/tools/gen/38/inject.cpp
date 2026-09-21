#include <sqlite3.h>

#include <cstdio>
#include <string>

static void exec(sqlite3 *db, const std::string &sql) {
    char *err = nullptr;
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::printf("  error: %s\n", err);
        sqlite3_free(err);
    }
}

static int print_text(void *unused, int columns, char **values, char **names) {
    (void)unused;
    (void)names;
    for (int i = 0; i < columns; ++i) std::printf("  row: %s\n", values[i] ? values[i] : "NULL");
    return 0;
}

static void count(sqlite3 *db, const char *label) {
    char *err = nullptr;
    const int rc = sqlite3_exec(db, "SELECT text FROM secrets;", print_text, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::printf("%s: %s\n", label, err);
        sqlite3_free(err);
    }
}

int main() {
    // What a hostile user types into the "note" field of a web form.
    const std::string input = "x'); DROP TABLE secrets; --";

    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    // ---- 1. the naive way: build SQL by pasting strings together -------------
    exec(db, "CREATE TABLE secrets (text TEXT); INSERT INTO secrets VALUES ('alpha');");
    const std::string naive = "INSERT INTO secrets VALUES ('" + input + "');";
    std::printf("naive SQL: %s\n", naive.c_str());
    exec(db, naive);
    count(db, "after naive");

    // ---- 2. the same input, bound as a value --------------------------------
    exec(db, "CREATE TABLE secrets (text TEXT); INSERT INTO secrets VALUES ('alpha');");
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO secrets VALUES (?);", -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, input.c_str(), -1, SQLITE_TRANSIENT);
    const int rc = sqlite3_step(stmt);
    std::printf("bound step rc=%d\n", rc);
    sqlite3_finalize(stmt);
    count(db, "after bound");

    sqlite3_close(db);
    return 0;
}
