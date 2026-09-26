// ch45 generator project — HTML built from data.
#pragma once

#include <string>
#include <vector>

#include "store.hpp"

// Every value that reaches a page goes through here. Not the interesting ones -- all
// of them, including ones only you can type, because the page that renders them does
// not know where they came from.
inline std::string html_escape(const std::string &in) {
    std::string out;
    for (char c : in) {
        switch (c) {
            case '&':  out += "&amp;";  break;
            case '<':  out += "&lt;";   break;
            case '>':  out += "&gt;";   break;
            case '"':  out += "&quot;"; break;
            case '\'': out += "&#39;";  break;
            default:   out += c;
        }
    }
    return out;
}

inline std::string page(const std::string &title, const std::string &inner) {
    return "<!doctype html>\n<html lang=\"en\">\n<head>\n"
           "<meta charset=\"utf-8\">\n"
           "<title>" + html_escape(title) + "</title>\n"
           "</head>\n<body>\n" + inner + "</body>\n</html>\n";
}

inline std::string render_login(const std::string &notice) {
    std::string inner = "<h1>Notes</h1>\n";
    if (!notice.empty()) inner += "<p class=\"notice\">" + html_escape(notice) + "</p>\n";
    inner += "<h2>Sign in</h2>\n"
             "<form method=\"post\" action=\"/login\">\n"
             "  <label>name <input name=\"user\"></label>\n"
             "  <label>password <input name=\"password\" type=\"password\"></label>\n"
             "  <button>sign in</button>\n"
             "</form>\n"
             "<form method=\"post\" action=\"/signup\">\n"
             "  <h2>Or create an account</h2>\n"
             "  <label>name <input name=\"user\"></label>\n"
             "  <label>password <input name=\"password\" type=\"password\"></label>\n"
             "  <button>create</button>\n"
             "</form>\n";
    return page("Notes — sign in", inner);
}

inline std::string render_notes(const std::string &user, const std::vector<Note> &notes) {
    std::string inner = "<h1>" + html_escape(user) + "'s notes</h1>\n";
    inner += "<p>" + std::to_string(notes.size()) + " note(s)</p>\n";
    inner += "<ul class=\"notes\">\n";
    for (const Note &n : notes) {
        inner += "  <li><a href=\"/notes/" + std::to_string(n.id) + "\">" +
                 html_escape(n.title) + "</a></li>\n";
    }
    inner += "</ul>\n"
             "<form method=\"post\" action=\"/notes\">\n"
             "  <label>title <input name=\"title\"></label>\n"
             "  <label>body <textarea name=\"body\"></textarea></label>\n"
             "  <button>add</button>\n"
             "</form>\n"
             "<form method=\"post\" action=\"/logout\"><button>sign out</button></form>\n";
    return page("Notes — " + user, inner);
}

inline std::string render_note_view(const std::string &user, const Note &n) {
    std::string inner = "<h1>" + html_escape(n.title) + "</h1>\n";
    inner += "<pre>" + html_escape(n.body) + "</pre>\n";
    inner += "<p><a href=\"/\">back to " + html_escape(user) + "'s notes</a></p>\n";
    return page("Note — " + n.title, inner);
}

inline std::string render_message(const std::string &heading, const std::string &detail) {
    std::string inner = "<h1>" + html_escape(heading) + "</h1>\n";
    inner += "<p>" + html_escape(detail) + "</p>\n";
    inner += "<p><a href=\"/\">start again</a></p>\n";
    return page(heading, inner);
}
