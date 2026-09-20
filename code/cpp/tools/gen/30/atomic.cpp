/* Write to a temporary name, then rename() over the real one. rename() is
   atomic, so a crash at any instant leaves either the old file or the new
   one -- never a mixture. */
#include <cstdio>
#include <string>

namespace {

std::string read_all(const char *path) {
    std::FILE *f = std::fopen(path, "rb");
    if (!f) return "(no such file)";
    std::string out;
    int c;
    while ((c = std::fgetc(f)) != EOF) out += static_cast<char>(c);
    std::fclose(f);
    return out;
}

void write_all(const char *path, const std::string &data) {
    std::FILE *f = std::fopen(path, "wb");
    if (!f) {
        std::perror("fopen");
        return;
    }
    std::fwrite(data.data(), 1, data.size(), f);
    std::fclose(f);
}

}  // namespace

int main() {
    write_all("store.json", "{\"version\":1}");
    std::printf("before:   %s\n", read_all("store.json").c_str());

    /* Stage version 2 under a temporary name. */
    write_all("store.json.tmp", "{\"version\":2}");
    std::printf("staged:   store.json.tmp = %s\n", read_all("store.json.tmp").c_str());
    std::printf("a crash now would leave store.json = %s\n",
                read_all("store.json").c_str());

    if (std::rename("store.json.tmp", "store.json") != 0) {
        std::perror("rename");
        return 1;
    }
    std::printf("renamed:  %s\n", read_all("store.json").c_str());
    std::printf("temp is gone: %s\n", read_all("store.json.tmp").c_str());
    return 0;
}
