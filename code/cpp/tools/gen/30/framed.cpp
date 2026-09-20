/* Length + checksum framing: a torn tail is detectable, and the records
   before it are untouched. */
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <vector>

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

std::string frame(const std::string &payload) {
    char head[64];
    std::snprintf(head, sizeof head, "%zu %08x ", payload.size(), fnv1a(payload));
    return std::string(head) + payload + "\n";
}

void append(const char *path, const std::string &payload) {
    std::FILE *f = std::fopen(path, "ab");
    if (!f) {
        std::perror("fopen");
        std::exit(1);
    }
    std::fputs(frame(payload).c_str(), f);
    std::fclose(f);
}

struct Scan {
    std::vector<std::string> records;
    long good_bytes = 0;   /* bytes covered by complete, verified records */
    long refused = 0;      /* count of records that failed verification */
    long junk_bytes = 0;   /* bytes left over after the last good record */
};

Scan scan(const char *path) {
    Scan out;
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return out;

    std::fseek(f, 0, SEEK_END);
    const long size = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);

    for (;;) {
        std::size_t len = 0;
        unsigned crc = 0;
        if (std::fscanf(f, "%zu %08x ", &len, &crc) != 2) break;
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
    out.junk_bytes = size - std::ftell(f);
    std::fclose(f);
    return out;
}

std::string raw(const char *path) {
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return "(no such file)";
    std::string out;
    int c;
    while ((c = std::fgetc(f)) != EOF) {
        if (c == '\n') out += "\\n";
        else           out += static_cast<char>(c);
    }
    std::fclose(f);
    return out;
}

void report(const char *path) {
    const Scan s = scan(path);
    std::printf("  recovered %zu record(s), refused %ld, %ld good byte(s), %ld junk byte(s)\n",
                s.records.size(), s.refused, s.good_bytes, s.junk_bytes);
    for (const std::string &r : s.records) std::printf("    %s\n", r.c_str());
}

}  // namespace

int main() {
    std::remove("data.log");
    append("data.log", "widget");
    append("data.log", "gasket");
    append("data.log", "bolt");
    std::printf("the log on disk:\n  %s\n\n", raw("data.log").c_str());

    std::printf("reading it back:\n");
    report("data.log");

    /* A crash half way through the third record: five bytes short. */
    const Scan before = scan("data.log");
    ::truncate("data.log", before.good_bytes - 5);
    std::printf("\nafter losing the last 5 bytes:\n  %s\n", raw("data.log").c_str());
    report("data.log");

    /* Throw away the torn tail, then carry on. */
    const Scan after = scan("data.log");
    ::truncate("data.log", after.good_bytes);
    append("data.log", "washer");
    std::printf("\nafter truncating to the last good record and appending:\n");
    report("data.log");
    return 0;
}
