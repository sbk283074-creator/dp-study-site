// ch45 generator project — everything wired together, and the reason the wiring is
// explicit: `App` is the whole set of things a handler is allowed to touch. A handler
// that needs something new has to be handed it here, in one place, where a test can
// supply a different one.
#pragma once

#include <ctime>
#include <mutex>
#include <optional>
#include <string>

#include "auth.hpp"
#include "config.hpp"
#include "http.hpp"
#include "log.hpp"
#include "store.hpp"
#include "views.hpp"

struct App {
    Config cfg;
    Logger log;
    Db db;
    // SQLite serialises writers anyway; this mutex makes that a fact the code states
    // instead of a fact it depends on. It also covers the four workers the server
    // runs, which have no other reason to agree about anything.
    std::mutex store_mutex;

    // Opening the App migrates the schema, so there is no such thing as an App whose
    // tables are not ready. The migration is idempotent (it is gated on user_version),
    // which is what lets a second process open the same file safely.
    explicit App(const Config &c) : cfg(c), log(c), db(c.db_path) { db.migrate(); }
};

inline long long now_seconds() { return static_cast<long long>(std::time(nullptr)); }

inline std::optional<long long> current_user(App &app, const Request &req) {
    const std::string sid = req.cookie("sid");
    // Rejecting the wrong shape before touching the database is not an optimisation,
    // it is refusing to let a client spend a disk read on a guess.
    if (sid.size() != 32) return std::nullopt;
    std::lock_guard<std::mutex> guard(app.store_mutex);
    return app.db.session_user(sid, now_seconds());
}

inline bool valid_name(const std::string &s) { return !s.empty() && s.size() <= 64; }

inline Response text_response(int status, const std::string &body) {
    Response r;
    r.status = status;
    r.content_type = "text/plain; charset=utf-8";
    r.body = body;
    return r;
}

inline Response html_response(int status, const std::string &body) {
    Response r;
    r.status = status;
    r.body = body;
    return r;
}

// A session remembers a user id, not a name; the name comes back from one extra read
// per page. That costs a microsecond and saves keeping a second copy of the truth.
inline std::string name_for(App &app, long long user_id) {
    std::lock_guard<std::mutex> guard(app.store_mutex);
    const std::optional<User> user = app.db.user_by_id(user_id);
    return user ? user->name : "someone";
}

inline Response handle(App &app, const Request &req) {
    if (req.target == "/healthz") return text_response(200, "ok\n");

    if (req.target == "/signup" && req.method == "POST") {
        const std::string name = form_value(req.body, "user");
        const std::string password = form_value(req.body, "password");
        if (!valid_name(name))
            return text_response(400, "name must be 1..64 characters\n");
        if (password.size() < 8)
            return text_response(400, "password must be at least 8 characters\n");
        const std::string record = make_record(password, app.cfg.rounds);
        std::lock_guard<std::mutex> guard(app.store_mutex);
        // The unique index is the real defence; checking first only turns a crash into
        // a message. Both are needed, and only one of them is a guarantee.
        if (app.db.user_by_name(name)) return text_response(409, "that name is taken\n");
        if (!app.db.create_user(name, record)) return text_response(409, "that name is taken\n");
        app.log.emit("info", "signup", {{"user", name}, {"password", Logger::redact(password)}});
        return text_response(201, "created " + name + "\n");
    }

    if (req.target == "/login" && req.method == "POST") {
        const std::string name = form_value(req.body, "user");
        const std::string password = form_value(req.body, "password");
        std::optional<User> user;
        {
            std::lock_guard<std::mutex> guard(app.store_mutex);
            user = app.db.user_by_name(name);
        }
        if (!user || !verify_record(user->record, password))
            return text_response(401, "bad credentials\n");
        const std::string sid = random_token();
        {
            std::lock_guard<std::mutex> guard(app.store_mutex);
            app.db.create_session(sid, user->id, now_seconds() + 3600);
        }
        Response r = text_response(200, "signed in as " + name + "\n");
        r.set_cookie = session_cookie(sid, 3600);
        return r;
    }

    if (req.target == "/logout" && req.method == "POST") {
        const std::string sid = req.cookie("sid");
        if (sid.size() == 32) {
            std::lock_guard<std::mutex> guard(app.store_mutex);
            app.db.destroy_session(sid);
        }
        Response r = text_response(200, "signed out\n");
        r.set_cookie = session_cookie("", 0);
        return r;
    }

    if (req.target == "/" && req.method == "GET") {
        const std::optional<long long> who = current_user(app, req);
        if (!who) return html_response(200, render_login({}));
        std::vector<Note> notes;
        {
            std::lock_guard<std::mutex> guard(app.store_mutex);
            notes = app.db.notes_for(*who);
        }
        return html_response(200, render_notes(name_for(app, *who), notes));
    }

    if (req.target == "/notes" && req.method == "POST") {
        const std::optional<long long> who = current_user(app, req);
        if (!who) return html_response(401, render_message("Not signed in", "Sign in first."));
        const std::string title = form_value(req.body, "title");
        const std::string body = form_value(req.body, "body");
        if (title.empty() || body.empty())
            return text_response(400, "a note needs a title and a body\n");
        {
            std::lock_guard<std::mutex> guard(app.store_mutex);
            app.db.add_note(*who, title, body, now_seconds());
        }
        Response r = text_response(303, "");
        r.location = "/";
        return r;
    }

    if (req.target.rfind("/notes/", 0) == 0 && req.method == "GET") {
        const std::optional<long long> who = current_user(app, req);
        if (!who) return html_response(401, render_message("Not signed in", "Sign in first."));
        const std::string digits = req.target.substr(std::string("/notes/").size());
        long long id = 0;
        try {
            id = std::stoll(digits);
        } catch (const std::exception &) {
            return html_response(404, render_message("No such note", "Nothing here."));
        }
        std::optional<Note> note;
        {
            std::lock_guard<std::mutex> guard(app.store_mutex);
            // Scoped by owner: a note you do not own does not exist as far as this
            // route is concerned, and answering 404 rather than 403 is deliberate --
            // 403 would confirm that the id was right.
            note = app.db.note_for_owner(id, *who);
        }
        if (!note) return html_response(404, render_message("No such note", "Nothing here."));
        return html_response(200, render_note_view(name_for(app, *who), *note));
    }

    return html_response(404, render_message("No such route", req.target));
}
