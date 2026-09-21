#include <sqlite3.h>

#include <cstdio>

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);",
                 nullptr, nullptr, &err);

    // Positional `?` is anonymous; `:name`, `@name` and `$name` are named.
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO users (name, age) VALUES (:who, :years);", -1, &stmt,
                       nullptr);
    std::printf("parameter count = %d\n", sqlite3_bind_parameter_count(stmt));
    std::printf("index of :who   = %d\n", sqlite3_bind_parameter_index(stmt, ":who"));
    std::printf("index of :years = %d\n", sqlite3_bind_parameter_index(stmt, ":years"));
    std::printf("index of :nope  = %d\n", sqlite3_bind_parameter_index(stmt, ":nope"));
    std::printf("name of 1       = %s\n", sqlite3_bind_parameter_name(stmt, 1));

    sqlite3_bind_text(stmt, sqlite3_bind_parameter_index(stmt, ":who"), "ada", -1,
                      SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, sqlite3_bind_parameter_index(stmt, ":years"), 36);
    std::printf("step rc=%d\n", sqlite3_step(stmt));
    sqlite3_finalize(stmt);

    sqlite3_close(db);
    return 0;
}
