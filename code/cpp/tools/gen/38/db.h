#ifndef DB_H
#define DB_H

#include <sqlite3.h>

#include <stdexcept>
#include <string>

// Every SQLite handle is a resource whose cleanup has a destructor-shaped rule,
// so this header is the one place the rule is written down.
class DbError : public std::runtime_error {
public:
    explicit DbError(const std::string &message) : std::runtime_error(message) {}
};

class Db {
public:
    explicit Db(const std::string &path);
    ~Db();
    Db(const Db &) = delete;
    Db &operator=(const Db &) = delete;

    void exec(const std::string &sql);
    long long last_row_id() const;
    sqlite3 *handle() const { return handle_; }

private:
    sqlite3 *handle_ = nullptr;
};

class Stmt {
public:
    Stmt(Db &db, const std::string &sql);
    ~Stmt();
    Stmt(const Stmt &) = delete;
    Stmt &operator=(const Stmt &) = delete;

    Stmt &bind(int index, const std::string &value);
    Stmt &bind(int index, int value);
    bool step();  // true while there is another row
    std::string text(int column) const;
    int integer(int column) const;
    void reset();

private:
    sqlite3 *db_;
    sqlite3_stmt *stmt_ = nullptr;
};

#endif
