// ch45 generator project — unit tests: every module alone, in the order it was built.
#include "framework.hpp"

#include <sys/socket.h>
#include <unistd.h>

#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

#include "auth.hpp"
#include "config.hpp"
#include "http.hpp"
#include "log.hpp"
#include "views.hpp"

TEST(config_layers_record_provenance) {
    Config c;
    std::string err;
    CHECK(apply_pair(c, "port", "9000", "file", err));
    CHECK(apply_pair(c, "workers", "8", "env", err));
    CHECK(apply_pair(c, "rounds", "1000", "argv", err));
    CHECK(c.port == 9000);
    CHECK(c.workers == 8);
    CHECK(c.rounds == 1000);
    CHECK(c.source.at("port") == "file");
    CHECK(c.source.at("workers") == "env");
    CHECK(c.source.at("rounds") == "argv");
    // A key nobody set stays on its default, and says so -- which is the difference
    // between "the default is 8080" and "I have no idea why it is listening there".
    CHECK(c.db_path == "notes.db");
    CHECK(c.source.find("db") == c.source.end());
    // The later layer wins, and the provenance moves with it.
    CHECK(apply_pair(c, "port", "7000", "argv", err));
    CHECK(c.port == 7000);
    CHECK(c.source.at("port") == "argv");
}

TEST(config_refuses_to_start_on_nonsense) {
    Config c;
    std::string err;
    CHECK(!apply_pair(c, "prt", "9000", "file", err));
    CHECK(err.find("unknown key") != std::string::npos);
    CHECK(!apply_pair(c, "port", "ninety", "file", err));
    CHECK(err.find("not valid") != std::string::npos);

    CHECK(apply_pair(c, "port", "0", "file", err));
    CHECK(validate(c).find("port must be") != std::string::npos);
    CHECK(apply_pair(c, "port", "8080", "file", err));
    CHECK(validate(c).empty());

    CHECK(apply_pair(c, "workers", "4096", "env", err));
    CHECK(validate(c).find("workers must be") != std::string::npos);
    CHECK(apply_pair(c, "workers", "4", "env", err));
    CHECK(apply_pair(c, "level", "loud", "env", err));
    CHECK(validate(c).find("level must be") != std::string::npos);
}

TEST(config_json_says_where_each_value_came_from) {
    Config c;
    std::string err;
    CHECK(apply_pair(c, "port", "9090", "argv", err));
    CHECK(apply_pair(c, "db", "prod.db", "file", err));
    const std::string json = to_json(c);
    CHECK(json.find("\"port\": {\"value\": 9090, \"from\": \"argv\"}") != std::string::npos);
    CHECK(json.find("\"db\": {\"value\": \"prod.db\", \"from\": \"file\"}") != std::string::npos);
    CHECK(json.find("\"rounds\": {\"value\": 100000, \"from\": \"default\"}") != std::string::npos);
}

TEST(log_escaping_defeats_a_forged_line) {
    const std::string raw = "GET /search?q=a\n{\"level\":\"error\",\"msg\":\"forged\"}";
    const std::string safe = json_escape(raw);
    CHECK(safe.find('\n') == std::string::npos);
    CHECK(safe.find("\\n") != std::string::npos);
    CHECK(safe.find("&quot;") == std::string::npos);
    CHECK(json_escape("a\"b\\c\td").find("\\t") != std::string::npos);
}

TEST(log_level_is_a_filter_not_a_suggestion) {
    Config c;
    c.log_path = "unit-log.jsonl";
    c.level = "warn";
    std::remove("unit-log.jsonl");
    {
        Logger logger(c);
        logger.emit("debug", "too quiet");
        logger.emit("info", "ordinary");
        logger.emit("warn", "noticed");
        logger.emit("error", "stopped");
    }
    std::ifstream in("unit-log.jsonl");
    std::string line;
    int lines = 0;
    while (std::getline(in, line)) ++lines;
    CHECK(lines == 2);
    std::remove("unit-log.jsonl");
}

TEST(log_access_never_reaches_the_body) {
    Config c;
    c.log_path = "unit-access.jsonl";
    c.level = "debug";
    std::remove("unit-access.jsonl");
    {
        Logger logger(c);
        // The method, the status and the timing: three fields, chosen once, at the
        // call site. A logger handed the whole request is a logger waiting to leak.
        logger.access("POST", "/login", 401, 812);
    }
    std::ifstream in("unit-access.jsonl");
    const std::string line((std::istreambuf_iterator<char>(in)),
                           std::istreambuf_iterator<char>());
    CHECK(line.find("\"status\": \"401\"") != std::string::npos);
    CHECK(line.find("password") == std::string::npos);
    CHECK(line.find("hunter") == std::string::npos);
    std::remove("unit-access.jsonl");
}

TEST(html_escape_neutralises_the_five_that_matter) {
    CHECK(html_escape("<script>") == "&lt;script&gt;");
    CHECK(html_escape("a & b") == "a &amp; b");
    CHECK(html_escape("\"quoted\"") == "&quot;quoted&quot;");
    CHECK(html_escape("it's") == "it&#39;s");
    CHECK(html_escape("<>&\"'") == "&lt;&gt;&amp;&quot;&#39;");
    CHECK(html_escape("plain text") == "plain text");
}

TEST(form_values_come_back_decoded) {
    CHECK(url_decode("a+b") == "a b");
    CHECK(url_decode("a%20b") == "a b");
    CHECK(url_decode("%2B") == "+");
    CHECK(url_decode("100%25") == "100%");
    CHECK(url_decode("%zz") == "%zz");
    const std::string body = "title=Hello%20world&body=a+b%26more&plain=x";
    CHECK(form_value(body, "title") == "Hello world");
    CHECK(form_value(body, "body") == "a b&more");
    CHECK(form_value(body, "plain") == "x");
    CHECK(form_value(body, "missing").empty());
}

TEST(cookie_parser_tolerates_real_browsers) {
    Request req;
    req.headers.push_back({"cookie", " theme=dark ; sid=abc123 ; lang=en"});
    CHECK(req.cookie("sid") == "abc123");
    CHECK(req.cookie("theme") == "dark");
    CHECK(req.cookie("lang") == "en");
    CHECK(req.cookie("nope").empty());
    Request bare;
    CHECK(bare.cookie("sid").empty());
}

TEST(request_parser_reads_one_socket) {
    int fds[2] = {-1, -1};
    CHECK(::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0);
    const std::string raw =
        "POST /notes HTTP/1.1\r\nHost: test\r\nCookie: sid=abc123\r\n"
        "Content-Length: 11\r\n\r\ntitle=a%20b";
    CHECK(::write(fds[0], raw.data(), raw.size()) > 0);
    ::close(fds[0]);
    Request req;
    CHECK(read_request(fds[1], req));
    CHECK(req.method == "POST");
    CHECK(req.target == "/notes");
    CHECK(req.body == "title=a%20b");
    CHECK(req.header("host") == "test");
    CHECK(req.cookie("sid") == "abc123");
    ::close(fds[1]);
}

TEST(response_says_how_many_bytes_it_sends) {
    Response r;
    r.status = 404;
    r.body = "no such route\n";
    r.set_cookie = session_cookie("abc123", 3600);
    const std::string wire = render_response(r);
    CHECK(wire.find("HTTP/1.1 404 Not Found\r\n") == 0);
    CHECK(wire.find("Content-Length: 14\r\n") != std::string::npos);
    CHECK(wire.find("HttpOnly") != std::string::npos);
    CHECK(wire.find("SameSite=Strict") != std::string::npos);
    CHECK(wire.substr(wire.find("\r\n\r\n") + 4) == r.body);
    // Multi-byte characters are bytes too, and Content-Length is a byte count.
    Response unicode;
    unicode.body = "héllo";
    CHECK(render_response(unicode).find("Content-Length: 6\r\n") != std::string::npos);
}

TEST(password_records_carry_their_own_recipe) {
    const std::string record = make_record("correct horse", 1000);
    CHECK(verify_record(record, "correct horse"));
    CHECK(!verify_record(record, "correct horsf"));
    CHECK(split_fields(record, '$').size() == 4);
    CHECK(split_fields(record, '$')[1] == "1000");
    CHECK(split_fields(record, '$')[2].size() == 32);
    CHECK(split_fields(record, '$')[3].size() == 64);
    CHECK(!verify_record("", "correct horse"));
    CHECK(!verify_record("rot13$1000$abc$def", "correct horse"));
}

TEST(constant_eq_reads_every_byte) {
    CHECK(constant_eq("abc", "abc"));
    CHECK(!constant_eq("abc", "abd"));
    CHECK(!constant_eq("abc", "ab"));
    CHECK(!constant_eq("ab", "abc"));
    CHECK(constant_eq("", ""));
    CHECK(constant_eq(random_token(), random_token()) == false);
}
