// ch45 generator project — a thin RAII layer over the SQLite C API.
#pragma once

#include <sqlite3.h>

#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

struct User { long long id; std::string name; std::string record; };
struct Note { long long id; std::string title; std::string body; long long created_at; };

class Stmt {
public:
    Stmt(sqlite3 *db, const std::string &sql) {
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &st_, nullptr) != SQLITE_OK)
            throw std::runtime_error(std::string("prepare: ") + sqlite3_errmsg(db));
    }
    ~Stmt() { if (st_) sqlite3_finalize(st_); }
    Stmt(const Stmt &) = delete;
    Stmt &operator=(const Stmt &) = delete;

    // Positional on purpose: every caller names the column *and* its index, and the
    // SQLITE_TRANSIENT copy is what makes binding a temporary std::string safe.
    Stmt &bind(int pos, const std::string &value) {
        sqlite3_bind_text(st_, pos, value.data(), static_cast<int>(value.size()), SQLITE_TRANSIENT);
        return *this;
    }
    int step() { return sqlite3_step(st_); }
    sqlite3_stmt *raw() const { return st_; }

private:
    sqlite3_stmt *st_ = nullptr;
};

class Db {
public:
    explicit Db(const std::string &path) {
        if (sqlite3_open(path.c_str(), &db_) != SQLITE_OK) {
            std::string msg = db_ ? sqlite3_errmsg(db_) : "cannot allocate a connection";
            if (db_) { sqlite3_close(db_); db_ = nullptr; }
            throw std::runtime_error("open " + path + ": " + msg);
        }
        sqlite3_busy_timeout(db_, 5000);
    }
    ~Db() { if (db_) sqlite3_close(db_); }
    Db(const Db &) = delete;
    Db &operator=(const Db &) = delete;

    void exec(const std::string &sql) {
        char *err = nullptr;
        if (sqlite3_exec(db_, sql.c_str(), nullptr, nullptr, &err) != SQLITE_OK) {
            std::string msg = err ? err : "unknown error";
            sqlite3_free(err);
            throw std::runtime_error("exec: " + msg);
        }
    }

    // The schema has a version because the alternative -- trying every ALTER TABLE on
    // every boot and ignoring the failures -- destroys the one thing a migration has
    // to give you: knowing where you are.
    int version() {
        Stmt s(db_, "PRAGMA user_version;");
        return s.step() == SQLITE_ROW ? sqlite3_column_int(s.raw(), 0) : 0;
    }
    void set_version(int v) { exec("PRAGMA user_version = " + std::to_string(v) + ";"); }

    void migrate() {
        if (version() >= 1) return;
        exec("BEGIN;");
        exec("CREATE TABLE users ("
             "  id     INTEGER PRIMARY KEY,"
             "  name   TEXT NOT NULL UNIQUE,"
             "  record TEXT NOT NULL);");
        exec("CREATE TABLE sessions ("
             "  id         TEXT PRIMARY KEY,"
             "  user_id    INTEGER NOT NULL REFERENCES users(id),"
             "  expires_at INTEGER NOT NULL);");
        exec("CREATE TABLE notes ("
             "  id         INTEGER PRIMARY KEY,"
             "  user_id    INTEGER NOT NULL REFERENCES users(id),"
             "  title      TEXT NOT NULL,"
             "  body       TEXT NOT NULL,"
             "  created_at INTEGER NOT NULL);");
        exec("CREATE INDEX notes_by_owner ON notes (user_id, created_at DESC);");
        exec("COMMIT;");
        set_version(1);
    }

    bool create_user(const std::string &name, const std::string &record) {
        Stmt s(db_, "INSERT INTO users (name, record) VALUES (?, ?);");
        s.bind(1, name).bind(2, record);
        return s.step() == SQLITE_DONE;
    }

    std::optional<User> user_by_name(const std::string &name) {
        Stmt s(db_, "SELECT id, name, record FROM users WHERE name = ?;");
        s.bind(1, name);
        if (s.step() != SQLITE_ROW) return std::nullopt;
        return User{sqlite3_column_int64(s.raw(), 0),
                    reinterpret_cast<const char *>(sqlite3_column_text(s.raw(), 1)),
                    reinterpret_cast<const char *>(sqlite3_column_text(s.raw(), 2))};
    }

    std::optional<User> user_by_id(long long id) {
        Stmt s(db_, "SELECT id, name, record FROM users WHERE id = ?;");
        sqlite3_bind_int64(s.raw(), 1, id);
        if (s.step() != SQLITE_ROW) return std::nullopt;
        return User{sqlite3_column_int64(s.raw(), 0),
                    reinterpret_cast<const char *>(sqlite3_column_text(s.raw(), 1)),
                    reinterpret_cast<const char *>(sqlite3_column_text(s.raw(), 2))};
    }

    bool create_session(const std::string &id, long long user_id, long long expires_at) {
        Stmt s(db_, "INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?);");
        s.bind(1, id);
        sqlite3_bind_int64(s.raw(), 2, user_id);
        sqlite3_bind_int64(s.raw(), 3, expires_at);
        return s.step() == SQLITE_DONE;
    }

    std::optional<long long> session_user(const std::string &id, long long now) {
        Stmt s(db_, "SELECT user_id FROM sessions WHERE id = ? AND expires_at > ?;");
        s.bind(1, id);
        sqlite3_bind_int64(s.raw(), 2, now);
        if (s.step() != SQLITE_ROW) return std::nullopt;
        return sqlite3_column_int64(s.raw(), 0);
    }

    void destroy_session(const std::string &id) {
        Stmt s(db_, "DELETE FROM sessions WHERE id = ?;");
        s.bind(1, id);
        s.step();
    }

    long long add_note(long long user_id, const std::string &title, const std::string &body,
                       long long now) {
        Stmt s(db_, "INSERT INTO notes (user_id, title, body, created_at) VALUES (?, ?, ?, ?);");
        sqlite3_bind_int64(s.raw(), 1, user_id);
        s.bind(2, title);
        s.bind(3, body);
        sqlite3_bind_int64(s.raw(), 4, now);
        if (s.step() != SQLITE_DONE) return 0;
        return sqlite3_last_insert_rowid(db_);
    }

    // Every read is scoped by owner. Authorization written as a WHERE clause is harder
    // to forget than authorization written as an if statement six lines further down.
    std::vector<Note> notes_for(long long user_id) {
        Stmt s(db_, "SELECT id, title, body, created_at FROM notes WHERE user_id = ? "
                    "ORDER BY created_at DESC, id DESC;");
        sqlite3_bind_int64(s.raw(), 1, user_id);
        std::vector<Note> out;
        while (s.step() == SQLITE_ROW)
            out.push_back(Note{sqlite3_column_int64(s.raw(), 0),
                               reinterpret_cast<const char *>(sqlite3_column_text(s.raw(), 1)),
                               reinterpret_cast<const char *>(sqlite3_column_text(s.raw(), 2)),
                               sqlite3_column_int64(s.raw(), 3)});
        return out;
    }

    std::optional<Note> note_for_owner(long long id, long long owner) {
        Stmt s(db_, "SELECT id, title, body, created_at FROM notes WHERE id = ? AND user_id = ?;");
        sqlite3_bind_int64(s.raw(), 1, id);
        sqlite3_bind_int64(s.raw(), 2, owner);
        if (s.step() != SQLITE_ROW) return std::nullopt;
        return Note{sqlite3_column_int64(s.raw(), 0),
                    reinterpret_cast<const char *>(sqlite3_column_text(s.raw(), 1)),
                    reinterpret_cast<const char *>(sqlite3_column_text(s.raw(), 2)),
                    sqlite3_column_int64(s.raw(), 3)};
    }

    int count_notes(long long user_id) {
        Stmt s(db_, "SELECT COUNT(*) FROM notes WHERE user_id = ?;");
        sqlite3_bind_int64(s.raw(), 1, user_id);
        return s.step() == SQLITE_ROW ? sqlite3_column_int(s.raw(), 0) : 0;
    }

    sqlite3 *raw() const { return db_; }

private:
    sqlite3 *db_ = nullptr;
};
