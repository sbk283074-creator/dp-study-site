// ch45 generator project — credentials and sessions.
#pragma once

#include <CommonCrypto/CommonCryptoError.h>
#include <CommonCrypto/CommonKeyDerivation.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <sys/random.h>

inline std::string to_hex_impl(const unsigned char *data, std::size_t n) {
    static const char *digits = "0123456789abcdef";
    std::string out(n * 2, '0');
    for (std::size_t i = 0; i < n; ++i) {
        out[2 * i] = digits[data[i] >> 4];
        out[2 * i + 1] = digits[data[i] & 15];
    }
    return out;
}

inline std::string random_token() {
    unsigned char buf[16];
    if (::getentropy(buf, sizeof buf) != 0) std::abort();
    return to_hex_impl(buf, sizeof buf);
}

// Compares every byte. `==` on strings stops at the first difference, which leaks the
// position of that difference in the time it takes to answer -- small, but a session
// id is exactly the kind of secret an attacker gets to try billions of times.
inline bool constant_eq(const std::string &a, const std::string &b) {
    if (a.size() != b.size()) return false;
    unsigned char diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i)
        diff |= static_cast<unsigned char>(a[i] ^ b[i]);
    return diff == 0;
}

// The work factor is an argument, not a constant, because the only two callers want
// different things: production wants it slow, the test suite runs it forty times.
inline std::string pbkdf2(const std::string &password, const std::string &salt, unsigned rounds) {
    unsigned char digest[32];
    const int rc = CCKeyDerivationPBKDF(
        kCCPBKDF2, password.data(), password.size(),
        reinterpret_cast<const std::uint8_t *>(salt.data()), salt.size(),
        kCCPRFHmacAlgSHA256, rounds, digest, sizeof digest);
    if (rc != kCCSuccess) { std::fprintf(stderr, "PBKDF2 failed\n"); std::exit(1); }
    return to_hex_impl(digest, sizeof digest);
}

inline std::vector<std::string> split_fields(const std::string &s, char sep) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i <= s.size()) {
        const std::size_t p = s.find(sep, i);
        out.push_back(s.substr(i, p == std::string::npos ? std::string::npos : p - i));
        if (p == std::string::npos) break;
        i = p + 1;
    }
    return out;
}

// The record carries everything needed to check it again later, including how many
// rounds were used. Without the count, raising the work factor locks out every
// existing user -- which is how "we improved our security" becomes an outage.
inline std::string make_record(const std::string &password, unsigned rounds) {
    const std::string salt = random_token().substr(0, 32);
    return "pbkdf2-sha256$" + std::to_string(rounds) + "$" + salt + "$" +
           pbkdf2(password, salt, rounds);
}

inline bool verify_record(const std::string &record, const std::string &password) {
    const std::vector<std::string> fields = split_fields(record, '$');
    if (fields.size() != 4 || fields[0] != "pbkdf2-sha256") return false;
    try {
        const unsigned rounds = static_cast<unsigned>(std::stoul(fields[1]));
        return constant_eq(fields[3], pbkdf2(password, fields[2], rounds));
    } catch (const std::exception &) {
        return false;
    }
}

inline std::string session_cookie(const std::string &id, long max_age) {
    return std::string("sid=") + id + "; Max-Age=" + std::to_string(max_age) +
           "; Path=/; HttpOnly; SameSite=Strict";
}
