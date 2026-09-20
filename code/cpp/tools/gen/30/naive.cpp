/* What a "write the whole file" snapshot looks like when the process dies
   part way through. */
#include <cstdio>
#include <string>

#include <fcntl.h>
#include <unistd.h>

namespace {

std::string snapshot(int count) {
    std::string out = "{\"items\":[";
    for (int i = 0; i < count; i++) {
        if (i > 0) out += ",";
        out += "{\"id\":" + std::to_string(i + 1) + "}";
    }
    out += "]}";
    return out;
}

std::string read_all(const char *path) {
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return "(no such file)";
    std::string out;
    int c;
    while ((c = std::fgetc(f)) != EOF) out += static_cast<char>(c);
    std::fclose(f);
    return out;
}

void write_bytes(const char *path, const std::string &data) {
    int fd = ::open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        std::perror("open");
        return;
    }
    ssize_t n = ::write(fd, data.data(), data.size());
    ::close(fd);
    std::printf("write() returned %lld\n", static_cast<long long>(n));
}

}  // namespace

int main() {
    const std::string data = snapshot(3);

    write_bytes("store.json", data);
    std::printf("the file reads: %s\n\n", read_all("store.json").c_str());

    /* Now the same write, except the process died after 60% of it. truncate()
       is exactly what a kill -9 leaves on disk. */
    write_bytes("store.json", data);
    if (::truncate("store.json", static_cast<off_t>(data.size() * 6 / 10)) != 0) {
        std::perror("truncate");
        return 1;
    }
    std::printf("after dying 60%% of the way through:\n");
    std::printf("the file reads: %s\n", read_all("store.json").c_str());
    return 0;
}
