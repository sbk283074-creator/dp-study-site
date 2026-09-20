#include "store.h"

#include <cstdint>
#include <cstdio>

#include <fcntl.h>
#include <unistd.h>

namespace {

std::uint32_t fnv1a(const std::string &s) {
    std::uint32_t h = 2166136261u;
    for (unsigned char c : s) {
        h ^= c;
        h *= 16777619u;
    }
    return h;
}

}  // namespace

std::string frame(const std::string &payload) {
    char head[64];
    std::snprintf(head, sizeof head, "%zu %08x ", payload.size(), fnv1a(payload));
    return std::string(head) + payload + "\n";
}

Scan scan_log(const std::string &path) {
    Scan out;
    std::FILE *f = std::fopen(path.c_str(), "rb");
    if (!f) return out;   /* no file yet: an empty log */

    std::fseek(f, 0, SEEK_END);
    const long size = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);

    for (;;) {
        std::size_t len = 0;
        unsigned crc = 0;
        if (std::fscanf(f, "%zu %08x ", &len, &crc) != 2) break;

        /* The length comes from the file, so it is attacker-controlled. A
           payload larger than this is not a record, it is corruption. */
        if (len > 1024 * 1024) {
            out.refused++;
            break;
        }
        std::string payload(len, '\0');
        const std::size_t got = std::fread(&payload[0], 1, len, f);
        const int nl = std::fgetc(f);
        if (got != len || nl != '\n') {
            out.refused++;
            break;
        }
        if (fnv1a(payload) != crc) {
            out.refused++;
            break;
        }
        out.records.push_back(payload);
        out.good_bytes = std::ftell(f);
    }

    /* Bytes after the last good record are not "nothing", they are damage.
       Reporting them as a clean log would let a real record that follows some
       garbage disappear without a word. */
    out.junk_bytes = size - std::ftell(f);
    std::fclose(f);
    return out;
}

bool append_record(const std::string &path, const std::string &payload) {
    const int fd = ::open(path.c_str(), O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0) return false;

    const std::string record = frame(payload);
    const char *p = record.data();
    std::size_t left = record.size();
    while (left > 0) {
        const ssize_t n = ::write(fd, p, left);
        if (n <= 0) {
            ::close(fd);
            return false;
        }
        p += n;
        left -= static_cast<std::size_t>(n);
    }
    if (::fsync(fd) != 0) {
        ::close(fd);
        return false;
    }
    return ::close(fd) == 0;
}

bool truncate_to(const std::string &path, long bytes) {
    return ::truncate(path.c_str(), static_cast<off_t>(bytes)) == 0;
}
