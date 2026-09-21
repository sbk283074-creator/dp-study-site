#include <sqlite3.h>

#include <cstdio>

// sqlite3_exec is the "do exactly what I typed" entry point. The callback runs
// once per result row; the fourth argument is the column name array.
static int print_row(void *unused, int columns, char **values, char **names) {
    (void)unused;
    for (int i = 0; i < columns; ++i) {
        std::printf("  %s = %s\n", names[i], values[i] ? values[i] : "NULL");
    }
    return 0;
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    char *err = nullptr;
    int rc = sqlite3_exec(db,
                          "CREATE TABLE users ("
                          "  id   INTEGER PRIMARY KEY,"
                          "  name TEXT NOT NULL,"
                          "  age  INTEGER);"
                          "INSERT INTO users (name, age) VALUES"
                          "  ('ada', 36), ('grace', 45), ('alan', 41);",
                          nullptr, nullptr, &err);
    std::printf("setup rc=%d\n", rc);
    if (rc != SQLITE_OK) {
        std::printf("setup failed: %s\n", err);
        sqlite3_free(err);
    }

    rc = sqlite3_exec(db, "SELECT name, age FROM users WHERE age > 40 ORDER BY name;",
                      print_row, nullptr, &err);
    std::printf("select rc=%d\n", rc);

    sqlite3_close(db);
    return 0;
}
