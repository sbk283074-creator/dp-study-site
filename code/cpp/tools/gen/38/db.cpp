#include "db.h"

#include <cstddef>

namespace {

void check(int rc, sqlite3 *db, const char *what) {
    if (rc != SQLITE_OK && rc != SQLITE_DONE && rc != SQLITE_ROW) {
        throw DbError(std::string(what) + ": " + sqlite3_errmsg(db));
    }
}

}  // namespace

Db::Db(const std::string &path) {
    const int rc = sqlite3_open(path.c_str(), &handle_);
    if (rc != SQLITE_OK) {
        // sqlite3_open still hands back a handle on most failures, and that
        // handle is the only place the real message lives.
        const std::string message =
            handle_ ? sqlite3_errmsg(handle_) : "could not allocate a handle";
        if (handle_) sqlite3_close(handle_);
        handle_ = nullptr;
        throw DbError("open " + path + ": " + message);
    }
}

Db::~Db() {
    // close() can fail (an unfinalised statement, a busy database) and a
    // destructor must not throw, so the code is dropped on purpose.
    if (handle_) sqlite3_close(handle_);
}

void Db::exec(const std::string &sql) {
    char *err = nullptr;
    const int rc = sqlite3_exec(handle_, sql.c_str(), nullptr, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::string message = err ? err : "unknown error";
        sqlite3_free(err);
        throw DbError("exec: " + message);
    }
}

long long Db::last_row_id() const { return sqlite3_last_insert_rowid(handle_); }

Stmt::Stmt(Db &db, const std::string &sql) : db_(db.handle()) {
    const int rc = sqlite3_prepare_v2(db_, sql.c_str(), -1, &stmt_, nullptr);
    if (rc != SQLITE_OK) {
        throw DbError("prepare: " + std::string(sqlite3_errmsg(db_)));
    }
}

Stmt::~Stmt() {
    if (stmt_) sqlite3_finalize(stmt_);
}

Stmt &Stmt::bind(int index, const std::string &value) {
    // SQLITE_TRANSIENT tells SQLite to copy now. The alternative,
    // SQLITE_STATIC, is a promise that the buffer outlives the statement --
    // see the pitfall in this chapter for what happens when it does not.
    check(sqlite3_bind_text(stmt_, index, value.c_str(), -1, SQLITE_TRANSIENT), db_, "bind text");
    return *this;
}

Stmt &Stmt::bind(int index, int value) {
    check(sqlite3_bind_int(stmt_, index, value), db_, "bind int");
    return *this;
}

bool Stmt::step() {
    const int rc = sqlite3_step(stmt_);
    if (rc == SQLITE_ROW) return true;
    if (rc == SQLITE_DONE) return false;
    throw DbError("step: " + std::string(sqlite3_errmsg(db_)));
}

std::string Stmt::text(int column) const {
    const unsigned char *value = sqlite3_column_text(stmt_, column);
    if (value == nullptr) return std::string();
    return std::string(reinterpret_cast<const char *>(value),
                       static_cast<std::size_t>(sqlite3_column_bytes(stmt_, column)));
}

int Stmt::integer(int column) const { return sqlite3_column_int(stmt_, column); }

void Stmt::reset() {
    // reset() reports the error from the *previous* execution, which is why a
    // serious wrapper checks it instead of assuming it succeeded.
    check(sqlite3_reset(stmt_), db_, "reset");
}
