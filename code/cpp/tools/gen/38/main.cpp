#include "db.h"

#include <cstdio>

int main() {
    try {
        Db db(":memory:");
        db.exec("CREATE TABLE notes ("
                "  id    INTEGER PRIMARY KEY,"
                "  title TEXT NOT NULL,"
                "  body  TEXT);");

        Stmt insert(db, "INSERT INTO notes (title, body) VALUES (?, ?);");
        insert.bind(1, "first").bind(2, "written by the RAII wrapper").step();
        insert.reset();
        insert.bind(1, "second").bind(2, "same statement, rebound").step();
        std::printf("inserted, last rowid = %lld\n", db.last_row_id());

        Stmt select(db, "SELECT id, title, body FROM notes ORDER BY id;");
        while (select.step()) {
            std::printf("  %d. %s -- %s\n", select.integer(0), select.text(1).c_str(),
                        select.text(2).c_str());
        }

        // A failed statement is an exception, not a return code nobody checks.
        db.exec("INSERT INTO notes (title) VALUES (NULL);");
        std::printf("this line is never reached\n");
    } catch (const DbError &error) {
        std::printf("caught: %s\n", error.what());
    }
    return 0;
}
